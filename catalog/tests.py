"""OHIP API 카탈로그 테스트."""
import json
import tempfile

from django.core.management import call_command
from django.test import TestCase, Client, override_settings
from .models import ApiModule, Endpoint


SAMPLE_DATA = [
    {
        "id": 1,
        "title": "Reservation",
        "titleKo": "예약 관리",
        "description": "Reservation management APIs",
        "descriptionKo": "OPERA Cloud 예약 관리 API",
        "type": "Operation",
        "typeKo": "API 모듈",
        "category": "property",
        "categoryKo": "호텔 (자산)",
        "operationsCount": 3,
        "deprecatedCount": 1,
        "keywords": ["예약", "reservation", "booking"],
        "operations": ["getReservation", "postReservation", "putReservation"],
        "endpoints": [
            {"method": "GET", "uri": "/rsv/v1/reservations", "operationId": "getReservation", "deprecated": False},
            {"method": "POST", "uri": "/rsv/v1/reservations", "operationId": "postReservation", "deprecated": False},
            {"method": "PUT", "uri": "/rsv/v1/reservations/{id}", "operationId": "putReservation", "deprecated": True},
        ],
    },
    {
        "id": 2,
        "title": "Cashiering",
        "titleKo": "정산",
        "description": "Cashiering APIs",
        "descriptionKo": "정산 관련 API",
        "type": "Step",
        "typeKo": "워크플로우",
        "category": "property",
        "categoryKo": "호텔 (자산)",
        "operationsCount": 1,
        "deprecatedCount": 0,
        "keywords": ["정산", "캐셔", "cashier"],
        "operations": ["postBilling"],
        "endpoints": [
            {"method": "POST", "uri": "/csh/v1/billing", "operationId": "postBilling", "deprecated": False},
        ],
    },
]


def _loadSampleData():
    """테스트용 샘플 데이터 JSON 파일 생성 후 임포트."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(SAMPLE_DATA, tmp)
    tmp.close()
    call_command("import_opera_apis", tmp.name, verbosity=0)
    return tmp.name


class ModelTest(TestCase):
    """모델 생성 및 관계 테스트."""

    def setUp(self):
        _loadSampleData()

    def test_apiModuleCreated(self):
        self.assertEqual(ApiModule.objects.count(), 2)

    def test_endpointCreated(self):
        self.assertEqual(Endpoint.objects.count(), 4)

    def test_relationship(self):
        rsv = ApiModule.objects.get(apiId=1)
        self.assertEqual(rsv.endpoints.count(), 3)

    def test_displayTitle(self):
        rsv = ApiModule.objects.get(apiId=1)
        self.assertEqual(rsv.displayTitle, "예약 관리")


class ImportCommandTest(TestCase):
    """임포트 커맨드 upsert 테스트."""

    def test_importCreatesData(self):
        _loadSampleData()
        self.assertEqual(ApiModule.objects.count(), 2)
        self.assertEqual(Endpoint.objects.count(), 4)

    def test_upsertSafe(self):
        """두 번 실행해도 중복 없음."""
        _loadSampleData()
        _loadSampleData()
        self.assertEqual(ApiModule.objects.count(), 2)
        self.assertEqual(Endpoint.objects.count(), 4)


@override_settings(REQUIRE_LOGIN=True)
class LoginRequiredTest(TestCase):
    """REQUIRE_LOGIN=True 시 비인증 사용자 차단 테스트."""

    def setUp(self):
        _loadSampleData()
        self.client = Client()

    def test_anonymousRedirectToLogin(self):
        """비로그인 시 목록 페이지 접근 → 로그인으로 리다이렉트."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_anonymousDetailRedirect(self):
        """비로그인 시 상세 페이지 접근 → 로그인으로 리다이렉트."""
        resp = self.client.get("/api/1/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_loginPageAccessible(self):
        """로그인 페이지 자체는 접근 가능."""
        resp = self.client.get("/accounts/login/")
        self.assertEqual(resp.status_code, 200)

    def test_authenticatedAccess(self):
        """로그인 후 목록 페이지 접근 가능."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.create_user(username="tester", password="testpass123")
        self.client.login(username="tester", password="testpass123")
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)


@override_settings(REQUIRE_LOGIN=False)
class ListViewTest(TestCase):
    """목록 뷰 테스트."""

    def setUp(self):
        _loadSampleData()
        self.client = Client()

    def test_listPage200(self):
        resp = self.client.get("/?lifecycle=deprecated")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "예약 관리")

    def test_searchKorean(self):
        resp = self.client.get("/?q=정산")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "정산")
        self.assertNotContains(resp, "예약 관리")

    def test_filterByType(self):
        resp = self.client.get("/?type=Step&lifecycle=deprecated")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "정산")


@override_settings(REQUIRE_LOGIN=False)
class DetailViewTest(TestCase):
    """상세 뷰 테스트."""

    def setUp(self):
        _loadSampleData()
        self.client = Client()

    def test_detailPage200(self):
        resp = self.client.get("/api/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "예약 관리")
        self.assertContains(resp, "getReservation")

    def test_methodFilter(self):
        resp = self.client.get("/api/1/?method=GET")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "getReservation")
        self.assertNotContains(resp, "postReservation")
