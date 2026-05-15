from flask import Flask, jsonify, request

from app_core.config import get_config
from app_core.routes.admin import admin_bp
from app_core.routes.main import main_bp
from app_core.storage import init_storage


def create_app():
    config = get_config()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config)

    # Static dosyalar icin sunucu tarafli cache tamamen kapali
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    init_storage()

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # -------------------------------------------------------
    # Tum yanıtlara no-cache header ekle
    # Chrome, Safari, Firefox ve tum eski tarayicilar
    # hicbir sayfayi, JSON'u veya JS dosyasini onbelleklemesin
    # -------------------------------------------------------
    @app.after_request
    def add_no_cache_headers(response):
        # HTML sayfalar ve diger iceriklerin onbelleklenmesini engelle
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "proxy-revalidate, max-age=0, s-maxage=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Surrogate-Control"] = "no-store"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Sayfa bulunamadi"}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"success": False, "message": "Sunucu hatasi"}), 500

    return app
