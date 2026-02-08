# OHIP API 카탈로그

Oracle Hospitality OPERA Developer Portal API를 한글로 검색/조회할 수 있는 사내 웹 카탈로그.

## 빠른 시작

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. DB 마이그레이션
python manage.py migrate

# 3. 데이터 임포트
python manage.py import_opera_apis data/ohip-apis-ko.json

# 4. 관리자 계정 생성
python manage.py createsuperuser

# 5. 서버 실행
python manage.py runserver
```

http://127.0.0.1:8000/ 에서 접속.

## 환경 변수

`.env.example`을 `.env`로 복사 후 수정:

| 변수 | 기본값 | 설명 |
|------|--------|------|
| SECRET_KEY | (개발용 기본값) | Django secret key |
| DEBUG | True | 디버그 모드 |
| ALLOWED_HOSTS | localhost,127.0.0.1 | 허용 호스트 |
| REQUIRE_LOGIN | True | 로그인 필수 여부 (False로 설정 시 anonymous 접근 허용) |

## 주요 기능

- **한글 검색**: API명, 설명, Operation, Endpoint URI 한글/영문 검색
- **필터**: Content Type (API 모듈/워크플로우), Category, Lifecycle (Deprecated)
- **상세 페이지**: Endpoint 테이블, HTTP 메서드별 필터, Deprecated 표시
- **관리자**: Django Admin에서 데이터 편집 가능 (`/admin/`)

## 데이터

- 95개 API 모듈/워크플로우
- 3,768개 REST 엔드포인트
- 카테고리: 호텔(자산), 유통 채널, Nor1(업셀)

### 데이터 갱신

```bash
python manage.py import_opera_apis data/ohip-apis-ko.json
```

upsert 방식으로 재실행 안전합니다.

## Docker

```bash
cp .env.example .env  # SECRET_KEY 변경 필수
docker compose up --build
```

## 테스트

```bash
python manage.py test catalog
```

## 기술 스택

- Python 3.12 + Django 5.1
- Bootstrap 5.3 (로컬 서빙)
- SQLite
