"""OHIP API 카탈로그 모델."""
from django.db import models


class ApiModule(models.Model):
    """API 모듈/워크플로우 단위."""

    apiId = models.IntegerField(unique=True, verbose_name="원본 ID")
    title = models.CharField(max_length=200, verbose_name="영문 제목")
    titleKo = models.CharField(max_length=200, blank=True, default="", verbose_name="한글 제목")
    description = models.TextField(blank=True, default="", verbose_name="영문 설명")
    descriptionKo = models.TextField(blank=True, default="", verbose_name="한글 설명")
    moduleType = models.CharField(max_length=20, verbose_name="타입(영문)")
    moduleTypeKo = models.CharField(max_length=20, blank=True, default="", verbose_name="타입(한글)")
    category = models.CharField(max_length=50, verbose_name="카테고리(영문)")
    categoryKo = models.CharField(max_length=50, blank=True, default="", verbose_name="카테고리(한글)")
    operationsCount = models.IntegerField(default=0, verbose_name="Operations 수")
    deprecatedCount = models.IntegerField(default=0, verbose_name="Deprecated 수")
    keywords = models.JSONField(default=list, blank=True, verbose_name="검색 키워드")
    operations = models.JSONField(default=list, blank=True, verbose_name="Operation 목록")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["titleKo", "title"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["moduleType"]),
            models.Index(fields=["title", "titleKo"]),
        ]
        verbose_name = "API 모듈"
        verbose_name_plural = "API 모듈"

    def __str__(self):
        return self.titleKo or self.title

    @property
    def displayTitle(self):
        return self.titleKo if self.titleKo else self.title

    @property
    def displayDescription(self):
        return self.descriptionKo if self.descriptionKo else self.description

    @property
    def activeCount(self):
        return self.operationsCount - self.deprecatedCount


class Endpoint(models.Model):
    """개별 REST 엔드포인트."""

    METHOD_CHOICES = [
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("HEAD", "HEAD"),
        ("PATCH", "PATCH"),
    ]

    apiModule = models.ForeignKey(
        ApiModule,
        on_delete=models.CASCADE,
        related_name="endpoints",
        verbose_name="소속 API",
    )
    method = models.CharField(max_length=10, verbose_name="HTTP 메서드")
    uri = models.CharField(max_length=500, verbose_name="URI 경로")
    operationId = models.CharField(max_length=200, verbose_name="Operation ID")
    deprecated = models.BooleanField(default=False, verbose_name="Deprecated 여부")

    class Meta:
        ordering = ["method", "uri"]
        indexes = [
            models.Index(fields=["method"]),
            models.Index(fields=["deprecated"]),
            models.Index(fields=["apiModule", "method"]),
        ]
        verbose_name = "엔드포인트"
        verbose_name_plural = "엔드포인트"

    def __str__(self):
        return f"{self.method} {self.uri}"
