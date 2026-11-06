"""29CM 주방/생활 > 그릇/커트러리 를 브라우저 자동화(Playwright)로 모은다.

29CM 상품 목록은 화면을 연 뒤 자바스크립트가 그린다. 그래서 진짜 브라우저로 페이지를 열고,
그 페이지가 스스로 불러오는 상품 데이터(listing/items 응답)만 받아 적는다. 데이터 주소를 직접 부르지 않는다.
robots.txt 확인(2026-11-06): /store/category/ 는 허용 (/my-page/ /order/ /auth/ 등만 금지).
한 페이지에 50개, 최대 10페이지(500개)까지만.

실행: python discount-radar/sources/shin/crawl_29cm.py
처음 한 번: pip install -r discount-radar/sources/shin/requirements-crawl.txt && python -m playwright install chromium
"""
from playwright.sync_api import sync_playwright

from common import DELAY, MAX_PAGES, UA, categorize, is_tableware, save

URL = "https://www.29cm.co.kr/store/category/list?categoryLargeCode=292100100&categoryMediumCode=292122100"


def to_row(item: dict) -> dict | None:
    info = item.get("itemInfo") or {}
    event = (item.get("itemEvent") or {}).get("eventProperties") or {}
    if item.get("itemType") != "PRODUCT" or info.get("isSoldOut") or event.get("isAd"):
        return None  # 품절과 광고 칸은 뺀다
    name = info.get("productName", "").strip()
    price = info.get("sellPrice")
    original = info.get("originalPrice")
    shown = info.get("displayPrice")  # 쿠폰까지 적용한 값. 할인 기준에는 넣지 않고 조건으로 적는다
    badges = [b.get("text", "") for b in info.get("textBadges") or []]
    notes = []
    if shown and price and shown < price:
        notes.append(f"쿠폰 적용 시 {shown:,}원")
    if "첫구매" in " ".join(badges) or info.get("isCategoryFirstPurchaseOnly"):
        notes.append("첫 구매 한정")
    if not name or not price or not is_tableware(name):
        return None
    return {
        # 29CM 상품명은 대개 앞에 [브랜드]가 이미 붙어 있다. 없을 때만 붙인다
        "name": name if name.startswith("[") or not info.get("brandName") else f"[{info['brandName']}] {name}",
        "category": categorize(name),
        "price": price,
        "original_price": original or "",
        "review_count": info.get("reviewCount", ""),
        "url": f"https://www.29cm.co.kr/products/{item['itemId']}",
        "note": ", ".join(notes),
        "shop": "29CM",
    }


def main() -> None:
    pages: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=UA, locale="ko-KR", viewport={"width": 1280, "height": 1800})

        def on_response(resp):
            if "/listing/items" in resp.url and resp.status == 200:
                try:
                    data = resp.json()["data"]
                except Exception:
                    return
                if "pagination" in data:  # 같은 주소로 오는 다른 칸(추천 등)은 빼고 본 목록만
                    pages.append(data)
            elif "/listing/items" in resp.url:
                print(f"  HTTP {resp.status}, 더 불러오지 않는다")

        page.on("response", on_response)
        for n in range(1, MAX_PAGES + 1):  # 목록은 번호 페이지(&page=N)라 하나씩 연다
            before = len(pages)
            page.goto(f"{URL}&page={n}", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            if len(pages) == before:
                print(f"  29CM p{n}: 목록이 안 왔다, 멈춤")
                break
            print(f"  29CM p{n}: {len(pages[-1]['list'])}개")
            if not pages[-1]["pagination"].get("hasNext"):
                break
            page.wait_for_timeout(int(DELAY * 1000))
        browser.close()

    rows = [r for d in pages for r in map(to_row, d["list"]) if r]
    path = save(rows, "29cm.csv")
    print(f"저장: {path} ({len(rows)}행, 목록 {len(pages)}페이지)")


if __name__ == "__main__":
    main()
