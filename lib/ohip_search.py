"""
OHIP API 한글 검색 라이브러리
Oracle Hospitality Integration Platform API를 한글로 검색할 수 있는 유틸리티

사용법:
    from lib.ohip_search import OhipApiSearch

    search = OhipApiSearch()

    # 한글 키워드로 검색
    results = search.find("예약")
    results = search.find("체크인")
    results = search.find("정산")

    # 카테고리별 조회
    results = search.byCategory("유통")

    # API 타입별 조회
    results = search.byType("워크플로우")  # 또는 "API 모듈"

    # 전체 목록 출력
    search.listAll()

    # 특정 API 상세 조회
    search.detail(1)
"""

import json
import os
from pathlib import Path
from typing import Optional


class OhipApiSearch:
    """OHIP API 한글 검색 클래스"""

    def __init__(self, dataDir: Optional[str] = None):
        if dataDir is None:
            dataDir = str(Path(__file__).parent.parent / "data")

        koPath = os.path.join(dataDir, "ohip-apis-ko.json")
        rawPath = os.path.join(dataDir, "ohip-apis-raw.json")

        # 한글 데이터가 있으면 사용, 없으면 원본 사용
        if os.path.exists(koPath):
            with open(koPath, "r", encoding="utf-8") as f:
                self.apis = json.load(f)
        elif os.path.exists(rawPath):
            with open(rawPath, "r", encoding="utf-8") as f:
                self.apis = json.load(f)
        else:
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {koPath} 또는 {rawPath}")

    def find(self, keyword: str) -> list:
        """한글/영문 키워드로 API 검색"""
        keyword = keyword.lower()
        results = []

        for api in self.apis:
            searchFields = [
                api.get("title", "").lower(),
                api.get("titleKo", "").lower(),
                api.get("description", "").lower(),
                api.get("descriptionKo", "").lower(),
                api.get("category", "").lower(),
                api.get("categoryKo", "").lower(),
            ]
            # keywords 배열 검색
            keywords = api.get("keywords", [])
            searchFields.extend([k.lower() for k in keywords])

            # operations 검색
            operations = api.get("operations", [])
            searchFields.extend([op.lower() for op in operations])

            if any(keyword in field for field in searchFields):
                results.append(api)

        self._printResults(results, keyword)
        return results

    def byCategory(self, category: str) -> list:
        """카테고리별 API 조회 (property/distribution/nor1 또는 한글)"""
        category = category.lower()
        results = [
            api for api in self.apis
            if category in api.get("category", "").lower()
            or category in api.get("categoryKo", "").lower()
        ]
        self._printResults(results, f"카테고리: {category}")
        return results

    def byType(self, apiType: str) -> list:
        """타입별 API 조회 (Operation/Step 또는 API 모듈/워크플로우)"""
        apiType = apiType.lower()
        typeMap = {
            "api 모듈": "operation", "모듈": "operation", "api": "operation",
            "워크플로우": "step", "workflow": "step", "플로우": "step"
        }
        searchType = typeMap.get(apiType, apiType)

        results = [
            api for api in self.apis
            if searchType in api.get("type", "").lower()
            or apiType in api.get("typeKo", "").lower()
        ]
        self._printResults(results, f"타입: {apiType}")
        return results

    def detail(self, apiId: int) -> Optional[dict]:
        """특정 API 상세 정보 출력"""
        for api in self.apis:
            if api.get("id") == apiId:
                self._printDetail(api)
                return api
        print(f"  ID {apiId}에 해당하는 API를 찾을 수 없습니다.")
        return None

    def listAll(self):
        """전체 API 목록 출력"""
        print(f"\n{'='*80}")
        print(f"  OHIP API 전체 목록 ({len(self.apis)}개)")
        print(f"{'='*80}")

        # 카테고리별 그룹핑
        categories = {}
        for api in self.apis:
            cat = api.get("categoryKo", api.get("category", "기타"))
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(api)

        for cat, apis in categories.items():
            print(f"\n  [{cat}] ({len(apis)}개)")
            print(f"  {'-'*60}")
            for api in apis:
                titleKo = api.get("titleKo", "")
                titleEn = api.get("title", "")
                opsCount = api.get("operationsCount", 0)
                deprecated = api.get("deprecatedCount", 0)
                apiType = api.get("typeKo", api.get("type", ""))

                deprecatedStr = f" (deprecated: {deprecated})" if deprecated > 0 else ""
                title = f"{titleKo} ({titleEn})" if titleKo else titleEn

                print(f"  {api.get('id', ''):>3}. [{apiType}] {title} - {opsCount}개{deprecatedStr}")

    def summary(self):
        """전체 요약 통계 출력"""
        totalOps = sum(api.get("operationsCount", 0) for api in self.apis)
        totalDeprecated = sum(api.get("deprecatedCount", 0) for api in self.apis)

        modules = [a for a in self.apis if a.get("type", "").lower() == "operation"]
        workflows = [a for a in self.apis if a.get("type", "").lower() == "step"]

        categories = {}
        for api in self.apis:
            cat = api.get("categoryKo", api.get("category", "기타"))
            categories[cat] = categories.get(cat, 0) + 1

        # HTTP 메서드별 통계 집계
        methodCounts = {}
        totalEndpoints = 0
        totalDeprecatedEndpoints = 0
        for api in self.apis:
            endpoints = api.get("endpoints", [])
            totalEndpoints += len(endpoints)
            for ep in endpoints:
                m = ep.get("method", "UNKNOWN")
                methodCounts[m] = methodCounts.get(m, 0) + 1
                if ep.get("deprecated", False):
                    totalDeprecatedEndpoints += 1

        print(f"\n{'='*60}")
        print(f"  OHIP API 요약")
        print(f"{'='*60}")
        print(f"  전체 API 모듈/워크플로우: {len(self.apis)}개")
        print(f"  - API 모듈: {len(modules)}개")
        print(f"  - 워크플로우: {len(workflows)}개")
        print(f"  전체 Operations: {totalOps}개")
        print(f"  Deprecated: {totalDeprecated}개")
        print(f"\n  전체 Endpoints: {totalEndpoints}개")
        if totalDeprecatedEndpoints > 0:
            print(f"  Deprecated Endpoints: {totalDeprecatedEndpoints}개")
        print(f"\n  HTTP 메서드별 통계:")
        for m in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            if m in methodCounts:
                print(f"    - {m}: {methodCounts[m]}개")
        # 기타 메서드 출력
        for m, c in sorted(methodCounts.items()):
            if m not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
                print(f"    - {m}: {c}개")
        print(f"\n  카테고리별:")
        for cat, count in categories.items():
            print(f"    - {cat}: {count}개")
        print(f"{'='*60}")

    def findOperation(self, opName: str) -> list:
        """특정 operation 이름으로 소속 API 검색"""
        opName = opName.lower()
        results = []
        for api in self.apis:
            ops = api.get("operations", [])
            if any(opName in op.lower() for op in ops):
                results.append(api)

        if results:
            print(f"\n  '{opName}' operation이 포함된 API:")
            for api in results:
                titleKo = api.get("titleKo", "")
                title = f"{titleKo} ({api['title']})" if titleKo else api["title"]
                print(f"    - [{api.get('id', '')}] {title}")
        else:
            print(f"  '{opName}' operation을 찾을 수 없습니다.")

        return results

    def findEndpoint(self, keyword: str) -> list:
        """URI 경로 또는 operationId로 endpoint 검색

        Args:
            keyword: 검색할 URI 경로 일부 또는 operationId

        Returns:
            매칭된 endpoint와 소속 API 정보를 포함한 리스트
        """
        keyword = keyword.lower()
        results = []

        for api in self.apis:
            endpoints = api.get("endpoints", [])
            for ep in endpoints:
                uri = ep.get("uri", "").lower()
                opId = ep.get("operationId", "").lower()

                if keyword in uri or keyword in opId:
                    # 소속 API 이름과 한글명 추가
                    result = {
                        "apiTitle": api.get("title", ""),
                        "apiTitleKo": api.get("titleKo", ""),
                        "apiId": api.get("id", ""),
                        "method": ep.get("method", ""),
                        "uri": ep.get("uri", ""),
                        "operationId": ep.get("operationId", ""),
                        "deprecated": ep.get("deprecated", False),
                    }
                    results.append(result)

        # 결과 출력
        if results:
            print(f"\n  '{keyword}' endpoint 검색 결과: {len(results)}건")
            print(f"  {'-'*70}")
            for r in results:
                deprecatedTag = " [DEPRECATED]" if r["deprecated"] else ""
                apiName = f"{r['apiTitleKo']} ({r['apiTitle']})" if r["apiTitleKo"] else r["apiTitle"]
                print(f"  {r['method']:>6} {r['uri']}{deprecatedTag}")
                print(f"         operationId: {r['operationId']}")
                print(f"         소속 API: [{r['apiId']}] {apiName}")
                print()
        else:
            print(f"  '{keyword}'에 해당하는 endpoint를 찾을 수 없습니다.")

        return results

    def findByMethod(self, method: str) -> list:
        """HTTP 메서드별 endpoint 검색

        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE)

        Returns:
            해당 메서드의 endpoint 리스트
        """
        method = method.upper()
        results = []

        for api in self.apis:
            endpoints = api.get("endpoints", [])
            for ep in endpoints:
                if ep.get("method", "").upper() == method:
                    result = {
                        "apiTitle": api.get("title", ""),
                        "apiTitleKo": api.get("titleKo", ""),
                        "apiId": api.get("id", ""),
                        "method": ep.get("method", ""),
                        "uri": ep.get("uri", ""),
                        "operationId": ep.get("operationId", ""),
                        "deprecated": ep.get("deprecated", False),
                    }
                    results.append(result)

        # 결과 출력
        print(f"\n  {method} 메서드 endpoint: {len(results)}건")
        print(f"  {'-'*70}")
        for r in results:
            deprecatedTag = " [DEPRECATED]" if r["deprecated"] else ""
            apiName = f"{r['apiTitleKo']}" if r["apiTitleKo"] else r["apiTitle"]
            print(f"  {r['uri']}{deprecatedTag}")
            print(f"    operationId: {r['operationId']} | 소속: {apiName}")

        return results

    def _printResults(self, results: list, keyword: str):
        """검색 결과 출력"""
        print(f"\n  '{keyword}' 검색 결과: {len(results)}건")
        print(f"  {'-'*60}")
        for api in results:
            titleKo = api.get("titleKo", "")
            titleEn = api.get("title", "")
            title = f"{titleKo} ({titleEn})" if titleKo else titleEn
            descKo = api.get("descriptionKo", api.get("description", ""))[:80]

            print(f"  [{api.get('id', ''):>3}] {title}")
            print(f"        {descKo}")
            print()

    def _printDetail(self, api: dict):
        """API 상세 정보 출력"""
        titleKo = api.get("titleKo", "")

        print(f"\n{'='*70}")
        print(f"  [{api.get('id', '')}] {api.get('title', '')}")
        if titleKo:
            print(f"  한글: {titleKo}")
        print(f"{'='*70}")
        print(f"  카테고리: {api.get('categoryKo', api.get('category', ''))}")
        print(f"  타입: {api.get('typeKo', api.get('type', ''))}")
        print(f"  Operations: {api.get('operationsCount', 0)}개")
        if api.get("deprecatedCount", 0) > 0:
            print(f"  Deprecated: {api.get('deprecatedCount', 0)}개")
        print(f"\n  설명:")
        descKo = api.get("descriptionKo", "")
        descEn = api.get("description", "")
        if descKo:
            print(f"  [한글] {descKo}")
        print(f"  [원문] {descEn}")

        # endpoints 상세 정보 출력
        endpoints = api.get("endpoints", [])
        if endpoints:
            # HTTP 메서드별 통계
            methodCounts = {}
            deprecatedCount = 0
            for ep in endpoints:
                m = ep.get("method", "UNKNOWN")
                methodCounts[m] = methodCounts.get(m, 0) + 1
                if ep.get("deprecated", False):
                    deprecatedCount += 1

            methodSummary = ", ".join(f"{m}: {c}개" for m, c in sorted(methodCounts.items()))
            print(f"\n  Endpoints ({len(endpoints)}개) [{methodSummary}]")
            if deprecatedCount > 0:
                print(f"  (deprecated: {deprecatedCount}개)")
            print(f"  {'-'*66}")
            for ep in endpoints:
                deprecatedTag = " [DEPRECATED]" if ep.get("deprecated", False) else ""
                print(f"    {ep.get('method', ''):>6} {ep.get('uri', '')}{deprecatedTag}")
                print(f"           operationId: {ep.get('operationId', '')}")
        else:
            print(f"\n  Endpoints: 없음")

        keywords = api.get("keywords", [])
        if keywords:
            print(f"\n  검색 키워드: {', '.join(keywords)}")
        print(f"{'='*70}")


# CLI 모드 지원
if __name__ == "__main__":
    import sys

    search = OhipApiSearch()

    if len(sys.argv) < 2:
        search.summary()
        print("\n  사용법:")
        print("    python ohip_search.py <검색어>          # 키워드 검색")
        print("    python ohip_search.py --list            # 전체 목록")
        print("    python ohip_search.py --detail <id>     # 상세 조회")
        print("    python ohip_search.py --category <cat>  # 카테고리별")
        print("    python ohip_search.py --op <name>       # operation 검색")
        print("    python ohip_search.py --endpoint <kw>   # endpoint URI/operationId 검색")
        print("    python ohip_search.py --method <method> # HTTP 메서드별 검색")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "--list":
        search.listAll()
    elif cmd == "--detail" and len(sys.argv) > 2:
        search.detail(int(sys.argv[2]))
    elif cmd == "--category" and len(sys.argv) > 2:
        search.byCategory(sys.argv[2])
    elif cmd == "--op" and len(sys.argv) > 2:
        search.findOperation(sys.argv[2])
    elif cmd == "--endpoint" and len(sys.argv) > 2:
        search.findEndpoint(sys.argv[2])
    elif cmd == "--method" and len(sys.argv) > 2:
        search.findByMethod(sys.argv[2])
    elif cmd == "--summary":
        search.summary()
    else:
        search.find(cmd)
