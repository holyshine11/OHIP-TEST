"""Django Admin 설정."""
from django.contrib import admin
from .models import ApiModule, Endpoint


class EndpointInline(admin.TabularInline):
    model = Endpoint
    extra = 0
    readonly_fields = ("method", "uri", "operationId", "deprecated")


@admin.register(ApiModule)
class ApiModuleAdmin(admin.ModelAdmin):
    list_display = (
        "apiId", "titleKo", "title", "moduleTypeKo",
        "categoryKo", "operationsCount", "deprecatedCount",
    )
    list_filter = ("moduleType", "category")
    search_fields = ("title", "titleKo", "description", "descriptionKo")
    readonly_fields = ("createdAt", "updatedAt")
    inlines = [EndpointInline]


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ("method", "uri", "operationId", "deprecated", "apiModule")
    list_filter = ("method", "deprecated")
    search_fields = ("uri", "operationId")
    raw_id_fields = ("apiModule",)
