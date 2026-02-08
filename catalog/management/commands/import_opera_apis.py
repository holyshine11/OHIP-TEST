"""OHIP API 데이터를 DB에 적재하는 관리 커맨드.

사용법:
    python manage.py import_opera_apis data/ohip-apis-ko.json
"""
import json
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import ApiModule, Endpoint

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "JSON 파일에서 OHIP API 데이터를 DB에 적재합니다 (upsert)"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="JSON 데이터 파일 경로")

    def handle(self, *args, **options):
        filePath = options["json_file"]

        with open(filePath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.stdout.write(f"  {len(data)}개 API 데이터 로드 완료")

        created = 0
        updated = 0
        endpointTotal = 0

        with transaction.atomic():
            for item in data:
                apiId = item.get("id")
                defaults = {
                    "title": item.get("title", ""),
                    "titleKo": item.get("titleKo", ""),
                    "description": item.get("description", ""),
                    "descriptionKo": item.get("descriptionKo", ""),
                    "moduleType": item.get("type", ""),
                    "moduleTypeKo": item.get("typeKo", ""),
                    "category": item.get("category", ""),
                    "categoryKo": item.get("categoryKo", ""),
                    "operationsCount": item.get("operationsCount", 0),
                    "deprecatedCount": item.get("deprecatedCount", 0),
                    "keywords": item.get("keywords", []),
                    "operations": item.get("operations", []),
                }

                obj, isCreated = ApiModule.objects.update_or_create(
                    apiId=apiId,
                    defaults=defaults,
                )

                if isCreated:
                    created += 1
                else:
                    updated += 1

                # 엔드포인트: 기존 삭제 후 벌크 생성
                obj.endpoints.all().delete()
                endpoints = item.get("endpoints", [])
                if endpoints:
                    endpointObjs = [
                        Endpoint(
                            apiModule=obj,
                            method=ep.get("method", ""),
                            uri=ep.get("uri", ""),
                            operationId=ep.get("operationId", ""),
                            deprecated=ep.get("deprecated", False),
                        )
                        for ep in endpoints
                    ]
                    Endpoint.objects.bulk_create(endpointObjs)
                    endpointTotal += len(endpointObjs)

        self.stdout.write(self.style.SUCCESS(
            f"  완료: 생성 {created}개, 수정 {updated}개, "
            f"엔드포인트 {endpointTotal}개"
        ))
