"""카탈로그 템플릿 태그/필터."""
from django import template

register = template.Library()

METHOD_CLASSES = {
    "GET": "badge-get",
    "POST": "badge-post",
    "PUT": "badge-put",
    "DELETE": "badge-delete",
    "HEAD": "badge-head",
    "PATCH": "badge-patch",
}


@register.filter
def methodBadgeClass(method):
    """HTTP 메서드에 맞는 CSS 클래스 반환."""
    return METHOD_CLASSES.get(method.upper(), "bg-secondary")


@register.simple_tag(takes_context=True)
def queryString(context, **kwargs):
    """현재 GET 파라미터를 유지하면서 특정 값만 변경한 쿼리스트링 생성."""
    request = context["request"]
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    return f"?{params.urlencode()}" if params else ""
