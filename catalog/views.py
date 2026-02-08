"""OHIP API 카탈로그 뷰."""
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import ApiModule, Endpoint


def apiListView(request):
    """API 목록 + 검색 + 필터."""
    qs = ApiModule.objects.all()

    # --- 검색 ---
    query = request.GET.get("q", "").strip()
    if query:
        # 엔드포인트에서 매칭되는 API ID 수집
        epModuleIds = (
            Endpoint.objects
            .filter(Q(uri__icontains=query) | Q(operationId__icontains=query))
            .values_list("apiModule_id", flat=True)
            .distinct()
        )
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(titleKo__icontains=query)
            | Q(description__icontains=query)
            | Q(descriptionKo__icontains=query)
            | Q(keywords__icontains=query)
            | Q(operations__icontains=query)
            | Q(pk__in=epModuleIds)
        )

    # 필터 파라미터가 하나라도 있으면 "사용자가 필터를 조작한 상태"
    hasFilterParams = any(
        k in request.GET for k in ("type", "category", "lifecycle")
    )

    # --- 필터: Content Type ---
    allTypes = ["Operation", "Step"]
    selectedTypes = request.GET.getlist("type") if hasFilterParams else allTypes
    if selectedTypes and set(selectedTypes) != set(allTypes):
        qs = qs.filter(moduleType__in=selectedTypes)

    # --- 필터: Category ---
    allCategories = list(
        ApiModule.objects.values_list("category", flat=True).distinct()
    )
    selectedCategories = request.GET.getlist("category") if hasFilterParams else allCategories
    if selectedCategories and set(selectedCategories) != set(allCategories):
        qs = qs.filter(category__in=selectedCategories)

    # --- 필터: Lifecycle (deprecated 포함 여부) ---
    selectedLifecycle = request.GET.getlist("lifecycle") if hasFilterParams else ["deprecated"]
    if "deprecated" not in selectedLifecycle:
        qs = qs.filter(deprecatedCount=0)

    # --- 정렬 ---
    currentSort = request.GET.get("sort", "name")
    sortMap = {
        "name": "titleKo",
        "-name": "-titleKo",
        "-ops": "-operationsCount",
        "ops": "operationsCount",
    }
    orderBy = sortMap.get(currentSort, "titleKo")
    qs = qs.order_by(orderBy)

    # --- 페이지네이션 ---
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    pageObj = paginator.get_page(page)

    # operation 미리보기 추가
    for api in pageObj:
        ops = api.operations or []
        api.previewOps = ops[:5]

    # --- 필터 선택지 ---
    typeChoices = [
        ("Operation", "API 모듈"),
        ("Step", "워크플로우"),
    ]
    categoryChoices = (
        ApiModule.objects
        .values_list("category", "categoryKo")
        .distinct()
        .order_by("categoryKo")
    )

    context = {
        "page_obj": pageObj,
        "query": query,
        "typeChoices": typeChoices,
        "categoryChoices": categoryChoices,
        "selectedTypes": selectedTypes,
        "selectedCategories": selectedCategories,
        "selectedLifecycle": selectedLifecycle,
        "currentSort": currentSort,
    }
    return render(request, "catalog/list.html", context)


def apiDetailView(request, apiId):
    """API 상세 페이지."""
    api = get_object_or_404(ApiModule, apiId=apiId)
    endpoints = api.endpoints.all()

    # 메서드 필터
    methodFilter = request.GET.get("method", "all")
    if methodFilter == "deprecated":
        filteredEndpoints = endpoints.filter(deprecated=True)
    elif methodFilter != "all":
        filteredEndpoints = endpoints.filter(method=methodFilter.upper())
    else:
        filteredEndpoints = endpoints

    # 메서드별 통계
    methodSummary = []
    for m in ["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"]:
        cnt = endpoints.filter(method=m).count()
        if cnt > 0:
            methodSummary.append((m, cnt))

    deprecatedEndpointCount = endpoints.filter(deprecated=True).count()

    # 뒤로가기 URL (검색/필터 상태 유지)
    backUrl = request.META.get("HTTP_REFERER", "/")
    if "/api/" in backUrl:
        backUrl = "/"

    context = {
        "api": api,
        "endpoints": filteredEndpoints,
        "endpointCount": endpoints.count(),
        "methodSummary": methodSummary,
        "methodFilter": methodFilter,
        "deprecatedEndpointCount": deprecatedEndpointCount,
        "backUrl": backUrl,
    }
    return render(request, "catalog/detail.html", context)
