"""사내용 로그인 필수 미들웨어."""
from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """REQUIRE_LOGIN=True 일 때 인증 안 된 사용자를 로그인 페이지로 리다이렉트."""

    EXEMPT_URLS = [
        settings.LOGIN_URL,
        "/admin/",
    ]

    def __init__(self, getResponse):
        self.getResponse = getResponse

    def __call__(self, request):
        if not getattr(settings, "REQUIRE_LOGIN", True):
            return self.getResponse(request)

        if request.user.is_authenticated:
            return self.getResponse(request)

        path = request.path
        if any(path.startswith(url) for url in self.EXEMPT_URLS):
            return self.getResponse(request)

        return redirect(f"{settings.LOGIN_URL}?next={path}")
