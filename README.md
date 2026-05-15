# Kontrol V6 VIP (Premium Coffee Automation & Analysis)

Kontrol V6 VIP, yepyeni **Coffee / Espresso** tasarım diliyle (Karamel, Mocha ve Cream vurguları) yeniden inşa edilmiş, üst düzey bir Instagram Otomasyon, Yorum/Beğeni Kontrol ve Token Yönetim platformudur. Orijinal Instagram mobil uygulamasının (Android) API başlıklarını ve session yönetimini birebir taklit ederek çalışan, son derece kararlı, güvenli ve sinematik estetiğe sahip bir sistemdir.

## 🚀 Proje Ne İşe Yarıyor?
Bu proje, **Instagram yardımlaşma ve etkileşim gruplarını** profesyonel bir düzeyde yönetmek için tasarlanmıştır. Üyelerin görevlerini (beğeni/yorum) yapıp yapmadıklarını saniyeler içinde tespit eder.

*   **Toplu Beğeni ve Yorum Denetimi:** Birden fazla gönderiyi aynı anda tarar, kimin eksik olduğunu detaylı raporlar.
*   **Kopya Yorum Tespiti:** "Toplu Kontrol" modunda, kullanıcıların farklı postlara aynı (kopyala-yapıştır) yorumu atıp atmadığını otomatik belirler ve uyarır.
*   **Favori Gruplar:** Sık kullandığınız Instagram gruplarını favoriye ekleyerek listenin en üstünde tutabilirsiniz.
*   **Premium UI/UX (Coffee Theme):** Özel renk paleti, cam dokulu (glassmorphism) bileşenler ve sinematik bulanıklık (blur) geçişleriyle donatılmış lüks bir arayüz.
*   **DM Grubu Entegrasyonu:** Bağlı hesapların bulunduğu grupları otomatik tespit eder, üye listelerini ve paylaşılan postları anında çeker.

---

## ✨ Yeni Nesil Özellikler (v6 VIP)
-   **Coffee / Espresso Design:** Saf, şık kahve tonları (`--accent-caramel`, `--accent-mocha`) kullanılarak baştan aşağı yenilenen premium bir deneyim.
-   **Sinematik Animasyonlar:** Sayfalar arası geçişlerde ve "Kontrol Et" bekleme anlarında devreye giren 1.5 saniyelik harika bulanıklık (blur) ve fade-in efektleriyle gerçek bir SPA hissi.
-   **Zarif Etkileşimler:** Grup ve paylaşım seçimi yapıldığında ekranda oluşan göz yormayan, kısa süreli bulanıklık efektleri. UI içi gereksiz zıplamalar tamamen temizlendi.
-   **Kopya Yorum Analizi:** Toplu kontrollerde aynı metni kullanan "spam" davranışlarını anında yakalar.
-   **Failover Mekanizması:** Instagram'ın `429` (Rate Limit) veya `403` hatalarını akıllıca yönetir, sadece gerçek oturum kayıplarında token'ı pasife alır.

---

## 🛠️ Kurulum

### Tek Komutla Kurulum (Linux/Bash/PythonAnywhere)
```bash
bash -c "$(curl -sL https://raw.githubusercontent.com/seghobs/kontrolyeni-v6vip/main/setup.sh)"
```

### Manuel Kurulum
```bash
git clone https://github.com/seghobs/kontrolyeni-v6vip.git kontrol
cd kontrol
pip install -r requirements.txt
python flask_app.py
```

---

## 💻 Kullanım
Sunucu veya lokal makinede projeyi başlattıktan sonra:

**Ana Kontrol Paneli:**
```text
http://localhost:5000
```

**Admin Paneli (Token & Muafiyetler):**
```text
http://localhost:5000/admin
```

---

## 📁 Proje Yapısı
-   `flask_app.py`: Uygulamanın giriş noktası.
-   `app_core/`: Sistemin mantıksal çekirdeği (Routes, API, Storage).
-   `static/css/`: Coffee/Karamel tabanlı modernize edilmiş, kusursuz UI stil dosyaları.
-   `static/js/`: Dinamik arama, sinematik geçişler, sürükle-bırak (SortableJS) ve favorileme mantığı.
-   `templates/`: Animasyonla yüklenen, akıcı Jinja2 HTML şablonları.

---

## 🔒 Güvenlik Notu
Bu proje eğitim ve analiz amaçlıdır. Instagram kullanım koşullarına uygun şekilde kullanılması kullanıcının sorumluluğundadır. Verileriniz (Tokenlar, muafiyetler) yerel bir SQLite veritabanında (`app.db`) şifrelenmiş veya güvenli şekilde saklanır.
