import os
import secrets


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "app.db")

# Legacy JSON paths (one-time migration only)
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
EXEMPTIONS_FILE = os.path.join(BASE_DIR, "exemptions.json")

IG_APP_ID = "567067343352427"


class BaseConfig:
    APP_ENV = os.getenv("APP_ENV", "dev")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "seho")
    SECRET_KEY = os.getenv("SECRET_KEY", "") or secrets.token_hex(32)
    HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "1") == "1"
    HEALTH_CHECK_INTERVAL_SECONDS = int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "180"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevConfig(BaseConfig):
    DEBUG = True


class StageConfig(BaseConfig):
    DEBUG = False


class ProdConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


def get_config():
    env = os.getenv("APP_ENV", "dev").lower().strip()
    if env == "prod":
        return ProdConfig
    if env == "stage":
        return StageConfig
    return DevConfig


_active_config = get_config()
ADMIN_PASSWORD = _active_config.ADMIN_PASSWORD
SECRET_KEY = _active_config.SECRET_KEY
