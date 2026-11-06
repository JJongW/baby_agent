"""카카오 책 검색 API로 분야별 도서 가격을 모아 data/books.csv로 저장한다.

파이썬 기본 기능만 쓴다 (설치할 것 없음).

키 넣는 법 (둘 중 하나)
- 파워셸: $env:KAKAO_REST_API_KEY="키"  후 같은 창에서 실행
- 이 파일 옆 .env 에 KAKAO_REST_API_KEY=키  한 줄 (git에 올리지 않는다)

실행
    python discount-radar/sources/books/kakao_books.py          # 분야 5개 전부
    python discount-radar/sources/books/kakao_books.py 소설     # 한 분야만 (분포 확인용)

열 이름은 공통 앱 약속을 따른다: 판매가 → price, 정가 → original_price
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "data" / "books.csv"

API_URL = "https://dapi.kakao.com/v3/search/book"
CATEGORIES = ["소설", "경제", "자기계발", "과학", "여행"]  # 검색어 = 분야. 나중에 바꾼다
PAGES = 10  # 분야당 최대 페이지
SIZE = 10   # 페이지당 권수

COLUMNS = [
    "name", "category", "price", "original_price", "review_count", "url", "note",
    "isbn", "thumbnail", "collected_at",
]


class KakaoError(RuntimeError):
    """수집 실패. 앱(adapter.py)에서 불러도 앱 전체가 멈추지 않게 sys.exit 대신 이걸 낸다."""


def read_key() -> str:
    """키를 찾는다. 없으면 빈 문자열."""
    key = os.environ.get("KAKAO_REST_API_KEY", "").strip()
    env_file = HERE / ".env"
    if not key and env_file.exists():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "KAKAO_REST_API_KEY":
                key = value.strip().strip('"').strip("'")
    return key


def search(key: str, query: str, page: int) -> dict:
    params = urllib.parse.urlencode({"query": query, "page": page, "size": SIZE})
    req = urllib.request.Request(
        f"{API_URL}?{params}", headers={"Authorization": f"KakaoAK {key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        hints = {
            401: "키가 틀렸어요. 플랫폼 키 화면에서 REST API 키를 다시 복사해 주세요.",
            403: "권한 문제예요. 플랫폼 키의 '호출 허용 IP' 설정을 확인해 주세요.",
            429: "호출이 너무 많아요. 잠시 뒤에 다시 돌려 주세요.",
        }
        raise KakaoError(f"[{e.code}] {hints.get(e.code, e.read().decode('utf-8', 'replace'))}") from e
    except urllib.error.URLError as e:
        raise KakaoError(f"카카오에 연결하지 못했어요: {e.reason}") from e


def to_row(doc: dict, category: str, today: str) -> dict | None:
    """카카오 응답 한 권 → 공통 앱 표준 열. 가격이 없으면 None."""
    sale = doc.get("sale_price")
    list_price = doc.get("price")
    if not isinstance(sale, int) or sale <= 0:      # -1 = 판매가 없음
        return None
    if not isinstance(list_price, int) or list_price <= 0:
        return None
    if sale > list_price:  # 판매가가 정가보다 비쌈 = 데이터 오류 (실제로 -245% 할인이 나온 적 있음)
        return None
    return {
        "name": doc.get("title", "").strip(),
        "category": category,
        "price": sale,                 # 지금 파는 값
        "original_price": list_price,  # 정가
        "review_count": "",            # 카카오가 주지 않음
        "url": doc.get("url", ""),
        "note": "",                    # 비워 둔다 (값이 있으면 공통 앱이 '확인 필요'로 표시)
        "isbn": doc.get("isbn", "").strip(),
        "thumbnail": doc.get("thumbnail", ""),
        "collected_at": today,
    }


def collect(key: str, category: str, today: str) -> list[dict]:
    rows, seen, skipped = [], set(), 0
    for page in range(1, PAGES + 1):
        data = search(key, category, page)
        for doc in data.get("documents", []):
            row = to_row(doc, category, today)
            if row is None:
                skipped += 1
                continue
            dedup = row["isbn"] or row["url"]
            if dedup in seen:
                continue
            seen.add(dedup)
            rows.append(row)
        if data.get("meta", {}).get("is_end", True):
            break
        time.sleep(0.2)
    print(f"  {category}: {len(rows)}권 (가격 없어 뺀 책 {skipped}권)")
    return rows


def collect_all(key: str, categories: list[str] = CATEGORIES) -> list[dict]:
    """분야 여러 개를 모은다. adapter.py도 이걸 부른다."""
    today = date.today().isoformat()
    rows = []
    for category in categories:
        rows += collect(key, category, today)
    return rows


def summary(rows: list[dict]) -> None:
    print("\n분야별 할인율 (공통 앱과 같은 계산)")
    for category in dict.fromkeys(r["category"] for r in rows):
        rates = [
            (r["original_price"] - r["price"]) / r["original_price"] * 100
            for r in rows if r["category"] == category
        ]
        if not rates:
            continue
        on_sale = sum(1 for x in rates if x > 0)
        print(
            f"  {category}: 평균 {sum(rates) / len(rates):.1f}% · "
            f"최소 {min(rates):.1f}% · 최대 {max(rates):.1f}% · 할인 중 {on_sale}/{len(rates)}권"
        )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # 윈도우 터미널에서 한글이 깨지지 않게
    sys.stderr.reconfigure(encoding="utf-8")
    categories = sys.argv[1:] or CATEGORIES
    key = read_key()
    if not key:
        sys.exit(
            "키가 없어요. 파워셸에서 $env:KAKAO_REST_API_KEY=\"키\" 를 입력하거나\n"
            f"{HERE / '.env'} 에 KAKAO_REST_API_KEY=키 를 한 줄 써 주세요."
        )

    print(f"수집 시작: {', '.join(categories)}")
    try:
        rows = collect_all(key, categories)
    except KakaoError as e:
        sys.exit(str(e))

    if not rows:
        sys.exit("모은 책이 없어요. 검색어를 확인해 주세요.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    summary(rows)
    print(f"\n저장: {OUT} ({len(rows)}권)")


if __name__ == "__main__":
    main()
