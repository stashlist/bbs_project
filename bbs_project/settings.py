
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY を環境変数から取得（デフォルト値は空）
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-@#104$8e1^oztiyvu#z5_9)m^b08c0!h)=+%^9x3@3ai9g+y*d")

# 本番環境では DEBUG を False にする
DEBUG = os.environ.get("DEBUG", "False") == "True"

# ALLOWED_HOSTS を環境変数から取得（カンマ区切りで指定）
ALLOWED_HOSTS = [
    "bbs-project.onrender.com",
    "www.bbs-project.onrender.com",
    "127.0.0.1",
    "localhost"
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

AUTH_USER_MODEL = "board.CustomUser"

LOGOUT_REDIRECT_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# WebSocket対応
ASGI_APPLICATION = "bbs_project.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # デプロイ時は Redis へ変更
    },
}

CSRF_COOKIE_SECURE = False  # HTTPS でない場合は False にする
SESSION_COOKIE_SECURE = False  # これも False にする

CSRF_TRUSTED_ORIGINS = [
    "https://bbs-project.onrender.com",  # Render のドメイン
    "https://www.bbs-project.onrender.com"
]

# メディアファイルの保存先
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# 静的ファイルの設定
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

AUTHENTICATION_BACKENDS = ["board.authentication.CustomUserAuthBackend"]

# Celery 設定（デプロイ時は Redis を推奨）
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# Application definition
INSTALLED_APPS = [
    "django_celery_beat",
    "daphne",
    "channels",
    "board",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bbs_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bbs_project.wsgi.application"

# ✅ 本番環境用のデータベース設定
DATABASES = {
    "default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))
}

# パスワードバリデーション
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 言語とタイムゾーン
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_TZ = True
USE_I18N = True
USE_L10N = True

# デフォルトのプライマリキー
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# メール設定（Gmail を使用する場合）
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "sandbox.smtp.mailtrap.io"  # `Mailtrap` のホスト
EMAIL_PORT = 2525  # `Mailtrap` の推奨ポート
EMAIL_USE_TLS = True  # `STARTTLS` を使用
EMAIL_USE_SSL = False  # `SSL` は不要
EMAIL_HOST_USER = "ab8b8bc1d1813b"  # `Mailtrap` のユーザー名
EMAIL_HOST_PASSWORD = "f5143d9b3e254b"  # `Mailtrap` のパスワード
DEFAULT_FROM_EMAIL = "noreply@example.com"  # 送信元メールアドレス


