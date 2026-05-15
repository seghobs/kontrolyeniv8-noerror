import datetime
import json
import logging
import os
import threading
import time
import uuid

import pytz
import requests
try:
    from curl_cffi import requests as curl_requests
    _CURL_AVAILABLE = True
except ImportError:
    curl_requests = requests  # fallback
    _CURL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Otomasyon yapılandırma dosyasının yolu
_AUTO_FILE = None


def _get_auto_file():
    global _AUTO_FILE
    if _AUTO_FILE is None:
        try:
            from app_core.config import DB_FILE
            _AUTO_FILE = os.path.join(os.path.dirname(DB_FILE), "automations.json")
        except Exception:
            _AUTO_FILE = os.path.join(os.path.dirname(__file__), "automations.json")
    return _AUTO_FILE


def load_automations():
    path = _get_auto_file()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_automations(data):
    path = _get_auto_file()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error("Otomasyon kayit hatasi: %s", e)
        return False


IG_APP_ID = "567067343352427"


def _get_user_id_by_username(username, token_record):
    """Instagram kullanıcı adından user_id alır."""
    token = token_record.get("token", "")
    user_agent = token_record.get("user_agent", "")
    android_id = token_record.get("android_id_yeni", "")
    device_id = token_record.get("device_id", "")
    from app_core.instagram_api import build_auth_headers
    headers = build_auth_headers(token, user_agent, android_id, device_id, username=username)
    try:
        if _CURL_AVAILABLE:
            resp = curl_requests.get(
                f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
                headers=headers,
                timeout=10,
                impersonate="chrome110",
            )
        else:
            resp = requests.get(
                f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
                headers=headers,
                timeout=10,
            )
        from app_core.instagram_api import _update_session_from_response
        _update_session_from_response(token_record.get("username", ""), resp)
        data = resp.json()
        user_id = data.get("data", {}).get("user", {}).get("id")
        return str(user_id) if user_id else None
    except Exception as e:
        logger.error("User ID alima hatasi (%s): %s", username, e)
        return None


def _send_dm_to_user(recipient_user_id, text, token_record):
    """Belirli bir kullanıcıya (thread yeriıne user ID ile) DM gönderir."""
    token = token_record.get("token", "")
    user_agent = token_record.get("user_agent", "")
    android_id = token_record.get("android_id_yeni", "")
    device_id = token_record.get("device_id", "")
    username = token_record.get("username", "")
    from app_core.instagram_api import build_auth_headers
    headers = build_auth_headers(token, user_agent, android_id, device_id, username=username)
    headers["content-type"] = "application/x-www-form-urlencoded"
    payload = {
        "text": text,
        "recipient_users": f"[[{recipient_user_id}]]",
        "action": "send_item",
        "client_context": str(uuid.uuid4()),
    }
    try:
        if _CURL_AVAILABLE:
            resp = curl_requests.post(
                "https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/",
                headers=headers,
                data=payload,
                timeout=15,
                impersonate="chrome110",
            )
        else:
            resp = requests.post(
                "https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/",
                headers=headers,
                data=payload,
                timeout=15,
            )
        from app_core.instagram_api import _update_session_from_response
        _update_session_from_response(token_record.get("username", ""), resp)
        logger.info("Bildirim DM sonucu user=%s status=%s", recipient_user_id, resp.status_code)
        return resp.status_code == 200
    except Exception as e:
        logger.error("Bildirim DM hatasi: %s", e)
        return False


def _send_dm(thread_id, text, token_record):
    token = token_record.get("token", "")
    user_agent = token_record.get("user_agent", "")
    android_id = token_record.get("android_id_yeni", "")
    device_id = token_record.get("device_id", "")
    username = token_record.get("username", "")
    from app_core.instagram_api import build_auth_headers
    headers = build_auth_headers(token, user_agent, android_id, device_id, username=username)
    headers["content-type"] = "application/x-www-form-urlencoded"
    payload = {
        "text": text,
        "thread_ids": f"[{thread_id}]",
        "action": "send_item",
        "client_context": str(uuid.uuid4()),
    }
    try:
        if _CURL_AVAILABLE:
            resp = curl_requests.post(
                "https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/",
                headers=headers,
                data=payload,
                timeout=15,
                impersonate="chrome110",
            )
        else:
            resp = requests.post(
                "https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/",
                headers=headers,
                data=payload,
                timeout=15,
            )
        from app_core.instagram_api import _update_session_from_response
        _update_session_from_response(token_record.get("username", ""), resp)
        logger.info("DM sonucu thread=%s status=%s", thread_id, resp.status_code)
        return resp.status_code == 200
    except Exception as e:
        logger.error("DM gonderme hatasi: %s", e)
        return False


def _fetch_comment_usernames(media_id, token_record):
    token = token_record.get("token", "")
    user_agent = token_record.get("user_agent", "")
    android_id = token_record.get("android_id_yeni", "")
    device_id = token_record.get("device_id", "")
    username = token_record.get("username", "")
    from app_core.instagram_api import build_auth_headers
    headers = build_auth_headers(token, user_agent, android_id, device_id, username=username)
    try:
        if _CURL_AVAILABLE:
            resp = curl_requests.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/stream_comments/",
                headers=headers,
                timeout=10,
                impersonate="chrome110",
            )
        else:
            resp = requests.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/stream_comments/",
                headers=headers,
                timeout=10,
            )
        from app_core.instagram_api import _update_session_from_response
        _update_session_from_response(token_record.get("username", ""), resp)
        data = resp.json()
        users = set()
        for c in data.get("comments", []):
            u = c.get("user", {}).get("username")
            if u:
                users.add(u.lower())
        return users
    except Exception:
        return set()


def _normalize(u):
    return u.strip().lower().lstrip("@")


def _fetch_comment_details(media_id, token_record):
    """Yorumları çeker ve (kullanıcı seti, yorum_sayısı, yorumlar_acik_mi) döndürür."""
    token = token_record.get("token", "")
    user_agent = token_record.get("user_agent", "")
    android_id = token_record.get("android_id_yeni", "")
    device_id = token_record.get("device_id", "")
    username = token_record.get("username", "")
    from app_core.instagram_api import build_auth_headers
    headers = build_auth_headers(token, user_agent, android_id, device_id, username=username)
    try:
        if _CURL_AVAILABLE:
            resp = curl_requests.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/stream_comments/",
                headers=headers,
                timeout=10,
                impersonate="chrome110",
            )
        else:
            resp = requests.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/stream_comments/",
                headers=headers,
                timeout=10,
            )
        from app_core.instagram_api import _update_session_from_response
        _update_session_from_response(token_record.get("username", ""), resp)
        comments_disabled = False
        comment_count = 0
        users = set()

        if resp.status_code == 200:
            for line in resp.text.splitlines():
                try:
                    json_data = json.loads(line)
                    if "comments_disabled" in json_data:
                        comments_disabled = json_data.get("comments_disabled", False)
                    if "comment_count" in json_data:
                        comment_count = json_data.get("comment_count", 0)
                        
                    for comment in json_data.get("comments", []):
                        u = comment.get("user", {}).get("username")
                        if u:
                            users.add(u.lower())
                except json.JSONDecodeError:
                    continue

        if comments_disabled:
            return set(), 0, False

        return users, comment_count, True  # (yorumcular, sayi, acik_mi)
    except Exception as e:
        logger.warning("Yorum detay cekme hatasi media=%s: %s", media_id, e)
        return set(), 0, False


def run_automation_for_thread(thread_id):
    logger.info("Otomasyon baslatildi: %s", thread_id)

    try:
        from app_core.token_service import get_working_active_token
        from app_core.instagram_api import fetch_group_members, fetch_group_media
        from app_core.storage import is_global_exempted, load_exemptions
    except Exception as import_err:
        logger.error("Otomasyon import hatasi: %s", import_err)
        return

    token_record = get_working_active_token()
    if not token_record:
        logger.error("Otomasyon: aktif token yok, iptal edildi.")
        return

    # 1. Grup üyeleri
    members_res = fetch_group_members(token_record, thread_id)
    if not members_res.get("ok"):
        logger.error("Otomasyon: grup uyeleri cekilemedi: %s", members_res)
        return
    member_usernames = {_normalize(u) for u in members_res.get("usernames", []) if u}
    logger.info("Otomasyon: %d grup uyesi bulundu.", len(member_usernames))

    # 2. DÜN'ün postlarını çek (GMT+3)
    tz = pytz.timezone("Europe/Istanbul")
    now = datetime.datetime.now(tz)
    yesterday = now - datetime.timedelta(days=1)
    logger.info("Otomasyon: %s tarihli postlar aranıyor.", yesterday.strftime("%Y-%m-%d"))

    media_res = fetch_group_media(token_record, thread_id, yesterday)
    if not media_res.get("ok"):
        logger.error("Otomasyon: medya cekilemedi: %s", media_res)
        return

    posts = media_res.get("posts", [])
    if not posts:
        logger.info("Otomasyon: dun atilan paylasim yok, iptal.")
        return

    logger.info("Otomasyon: dunden %d paylasim bulundu, filtre uygulanıyor.", len(posts))

    # 3. Uygun postu bul: yorumlar açık VE en az 2 yorum var
    MIN_COMMENT_COUNT = 2
    hedef_post = None
    hedef_commenters = set()

    for post in posts:
        media_id = post.get("id")
        if not media_id:
            continue

        commenters, comment_count, comments_open = _fetch_comment_details(media_id, token_record)
        time.sleep(1)  # rate limit

        logger.info(
            "Post %s: yorum_sayisi=%d, acik=%s",
            post.get("code"), comment_count, comments_open
        )

        if not comments_open:
            logger.info("Post %s: yorumlar kapali, atlaniyor.", post.get("code"))
            continue

        if comment_count < MIN_COMMENT_COUNT:
            logger.info(
                "Post %s: yorum sayisi yetersiz (%d < %d), atlaniyor.",
                post.get("code"), comment_count, MIN_COMMENT_COUNT
            )
            continue

        # İlk uygun postu seç
        hedef_post = post
        hedef_commenters = commenters
        break

    if not hedef_post:
        logger.info(
            "Otomasyon: Uygun paylasim bulunamadi "
            "(yorumlar acik ve en az %d yorum olacak).", MIN_COMMENT_COUNT
        )
        return

    logger.info(
        "Otomasyon: Hedef post secildi: %s (yorum yapanlar: %d kisi)",
        hedef_post.get("code"), len(hedef_commenters)
    )

    # 4. Muafları hesapla
    exemptions_data = load_exemptions()
    all_exempted = set()

    # Post sahibi muaf
    sender = hedef_post.get("username")
    if sender:
        all_exempted.add(_normalize(sender))

    # Post'a özel muaflar
    post_link = f"https://www.instagram.com/p/{hedef_post.get('code', '')}/"
    for ex_user in exemptions_data.get(post_link, []):
        all_exempted.add(_normalize(ex_user))

    # Global muaflar
    for member in member_usernames:
        if is_global_exempted(member):
            all_exempted.add(member)

    # 5. Eksikler = üyeler - muaflar - yorum yapanlar
    eksikler = member_usernames - all_exempted - hedef_commenters

    if not eksikler:
        logger.info("Otomasyon: herkes yorumunu yapmis, eksik yok.")
        return

    logger.info("Otomasyon: %d eksik bulundu, DM gönderiliyor.", len(eksikler))

    # 6. Mesajları gönder
    msg1 = "\n".join(f"@{u}" for u in sorted(eksikler))
    _send_dm(thread_id, msg1, token_record)
    time.sleep(3)

    _send_dm(thread_id, "grup eksikleri", token_record)
    time.sleep(3)

    config = load_automations().get(str(thread_id), {})
    template = config.get(
        "template",
        "@everyone eksik listesindeki tüm arkadaşlarımıza dm üzerinden yazdık "
        "dönüş yapmayanlar gruptan çıkarılacaktır.",
    )
    _send_dm(thread_id, template, token_record)
    time.sleep(2)

    # 7. Admin / sahip hesabına bildirim gönder
    notify_username = config.get("notify_username", "seghob")
    if notify_username:
        post_url = f"https://www.instagram.com/p/{hedef_post.get('code', '')}/"
        group_name = config.get("group_name", thread_id)
        notify_text = (
            f"✅ Otomasyon tamamlandı!\n\n"
            f"📌 Grup: {group_name}\n"
            f"🔗 Kontrol edilen paylaşım:\n{post_url}\n\n"
            f"👥 Toplam üye: {len(member_usernames)}\n"
            f"❌ Eksik yorum: {len(eksikler)}\n"
            f"⏰ Saat: {datetime.datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M')} (GMT+3)"
        )
        user_id = _get_user_id_by_username(notify_username, token_record)
        if user_id:
            _send_dm_to_user(user_id, notify_text, token_record)
            logger.info("Bildirim @%s hesabina gonderildi.", notify_username)
        else:
            logger.warning("Bildirim icin @%s user_id alinamadi.", notify_username)

    logger.info("Otomasyon tamamlandi: %s", thread_id)


def _automation_worker():
    """Arka planda çalışan zamanlayıcı. 30s'de bir saati kontrol eder."""
    last_run_date = {}  # thread_id -> "YYYY-MM-DD"
    tz = pytz.timezone("Europe/Istanbul")

    while True:
        try:
            now = datetime.datetime.now(tz)
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")

            automations = load_automations()
            for thread_id, config in automations.items():
                if not config.get("is_active"):
                    continue
                target_time = config.get("time", "")
                if target_time == current_time:
                    if last_run_date.get(thread_id) != current_date:
                        last_run_date[thread_id] = current_date
                        logger.info(
                            "Otomasyon tetiklendi: thread=%s saat=%s", thread_id, current_time
                        )
                        t = threading.Thread(
                            target=run_automation_for_thread,
                            args=(thread_id,),
                            daemon=True,
                        )
                        t.start()
        except Exception as e:
            logger.error("Otomasyon worker hatasi: %s", e)

        time.sleep(30)


def start_automation():
    """Flask başlarken çağrılır; arka plan thread'ini başlatır."""
    t = threading.Thread(target=_automation_worker, daemon=True)
    t.start()
    logger.info("Otomasyon zamanlayici baslatildi.")
