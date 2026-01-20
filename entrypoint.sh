#!/usr/bin/env sh
set -e

# 기본값 (환경변수 없으면)
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}
export PORT=${PORT:-8000}

# 마이그레이션 + 정적 파일 수집
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# gunicorn 실행
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers 2 \
  --timeout 60
