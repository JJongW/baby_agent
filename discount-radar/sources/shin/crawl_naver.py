"""네이버 쇼핑 검색 API(공식)로 스마트스토어 등 그릇 상품을 모은다.

쿠팡, 오늘의집, 스마트스토어 페이지는 직접 긁으면 안 되는 곳이라, 네이버가 열어 둔 공식 API만 쓴다.
키: 네이버 개발자센터(developers.naver.com)에서 앱 등록, "검색" API 선택 → Client ID/Secret.
    이 폴더의 .env 에 넣는다 (.gitignore 로 레포에 안 올라간다). 양식은 .env.example.

"할인"의 기준: API는 정가를 주지 않는다. 대신 가격 비교 상품은 최저가(lprice)와 최고가(hprice)를 준다.
    → 같은 상품을 파는 가게 중 가장 비싼 값 대비 최저가. hprice 가 없으면 할인율 모름(빈칸).
실행: python crawl_naver.py
"""
import html
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from common import categorize, is_tableware, save

API = "https://openapi.naver.com/v1/search/shop.json"
QUERIES = ["그릇", "접시", "그릇 세트", "공기 대접", "머그컵", "수저 세트", "풍경 그릇"]
PER_PAGE = 100  # API 한 번에 최대 100개
MAX_PAGES = 10  # 검색어마다 최대 10번(1,000개). API가 허용하는 끝(start 1000)과 같다
DELAY = 0.3  # 네이버 권장 호출 속도(초당 10회) 안쪽
WORKERS = 3  # 검색어 3개를 동시에. 3 / 0.3초 = 초당 10회 이하


def load_keys() -> tuple[str, str]:
    env = Path(__file__).parent / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))
    cid, secret = os.environ.get("NAVER_CLIENT_ID"), os.environ.get("NAVER_CLIENT_SECRET")
    if not cid or not secret:
        raise SystemExit(".env 에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 을 넣어 주세요 (.env.example 참고)")
    return cid, secret


def to_row(item: dict, query: str) -> dict | None:
    name = html.unescape(re.sub(r"<[^>]+>", "", item.get("title", ""))).strip()
    low = int(item["lprice"]) if item.get("lprice") else None
    high = int(item["hprice"]) if item.get("hprice") else None
    if not name or not low or not is_tableware(name):
        return None
    return {
        "name": name,
        "category": categorize(name),
        "price": low,
        "original_price": high or "",  # 다른 가게 최고가. 정가가 아니다
        "review_count": "",  # API가 주지 않는다
        "url": item.get("link", ""),
        "note": "",
        "shop": item.get("mallName") or "네이버쇼핑",
        "product_id": item.get("productId", ""),
    }


def crawl_query(query: str, headers: dict) -> list[dict]:
    rows = []
    for page in range(MAX_PAGES):
        start = page * PER_PAGE + 1
        r = requests.get(API, params={"query": query, "display": PER_PAGE, "start": start, "sort": "sim"},
                         headers=headers, timeout=15)
        if r.status_code != 200:  # 401 키 오류, 429 한도 초과 등. 다시 시도하지 않는다
            print(f"  '{query}' {start}: HTTP {r.status_code} {r.text[:120]}, 멈춤")
            break
        items = r.json().get("items", [])
        rows += [x for x in (to_row(i, query) for i in items) if x]
        print(f"  '{query}' {start}~: {len(items)}개")
        if len(items) < PER_PAGE:
            break
        time.sleep(DELAY)
    return rows


def main() -> None:
    cid, secret = load_keys()
    headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(lambda q: crawl_query(q, headers), QUERIES))
    # 여러 검색어에 같은 상품이 걸리므로 상품 번호로 한 번만 남긴다
    seen, rows = set(), []
    for row in (r for rs in results for r in rs):
        key = row.pop("product_id") or row["url"]
        if key not in seen:
            seen.add(key)
            rows.append(row)
    path = save(rows, "naver.csv")
    print(f"저장: {path} ({len(rows)}행, 겹친 것 빼고)")


if __name__ == "__main__":
    main()
