from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

INSTALLED_APPS = [
    # local apps (커스텀 유저면 accounts를 먼저 두는 게 안전)
    "accounts",
    "game",

    # Django 기본
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    'allauth.socialaccount.providers.kakao',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # 루트 templates 사용
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # allauth 필수
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# static 폴더가 있을 때만 STATICFILES_DIRS 설정
STATIC_DIR = BASE_DIR / "static"
STATICFILES_DIRS = [STATIC_DIR] if STATIC_DIR.exists() else []

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ✅ 커스텀 유저
AUTH_USER_MODEL = "accounts.User"

# allauth
# settings.py 하단부 교체

# ==========================================
# Allauth 설정 (Email 로그인 & 닉네임 사용)
# ==========================================

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# 1. 로그인/가입 기본 정책
# [중요] 모델에 username 필드가 있다면 'username'으로 지정해야 DB 에러가 안 납니다.
# (사용자에게 입력만 안 받을 뿐, 내부적으로는 자동 생성해서 채워 넣습니다)
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username' 

ACCOUNT_EMAIL_REQUIRED = True             # 이메일 필수
ACCOUNT_USERNAME_REQUIRED = False         # [핵심] 사용자에게 아이디 입력창을 띄우지 않음
ACCOUNT_AUTHENTICATION_METHOD = "email"   # 로그인할 때 이메일 사용
ACCOUNT_EMAIL_VERIFICATION = "none"       # 이메일 인증 메일 발송 안 함

# 2. 소셜 로그인 설정
SOCIALACCOUNT_AUTO_SIGNUP = True          # 추가 정보 입력 없이 자동 가입
SOCIALACCOUNT_LOGIN_ON_GET = True         # 중간 확인 페이지 없이 즉시 로그인 진행
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

# 3. 소셜 프로바이더 설정 (닉네임/이메일 가져오기 필수)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        # Client ID/Secret은 .env에서 가져옵니다
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        }
    },
    "kakao": {
        "SCOPE": [
            "profile_nickname",
            "account_email",
        ],
        "APP": {
            "client_id": os.getenv("KAKAO_CLIENT_ID", ""),
            "secret": os.getenv("KAKAO_CLIENT_SECRET", ""),
            "key": "",
        }
    }
}