#!/usr/bin/env bash
# Render 빌드 스크립트
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py import_opera_apis data/ohip-apis-ko.json

# 관리자 계정 자동 생성 (환경변수로 제어)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi
