"""관리자 계정을 환경변수로 생성하는 커맨드 (비밀번호 검증 우회)."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "환경변수 기반 관리자 계정 생성 (이미 존재하면 비밀번호 갱신)"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not password:
            self.stdout.write("  DJANGO_SUPERUSER_PASSWORD 미설정 - 건너뜀")
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        action = "생성" if created else "비밀번호 갱신"
        self.stdout.write(self.style.SUCCESS(f"  관리자 계정 {action}: {username}"))
