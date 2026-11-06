"""카페24로 만든 그릇 쇼핑몰 5곳을 정적 크롤링(requests)으로 모은다.

robots.txt 확인(2026-11-06): 다섯 곳 모두 상품 목록(/product/list.html)은 허용,
/member/ /myshop/ /api /exec/front/ 는 금지라 건드리지 않는다.
실행: python discount-radar/sources/shin/crawl_cafe24.py
"""
import re
import time

import requests
from bs4 import BeautifulSoup

from common import DELAY, MAX_PAGES, UA, categorize, is_tableware, save, won

# 쇼핑몰 이름: (주소, 그릇 목록 카테고리 번호들)
SHOPS = {
    "그릇114": ("https://dish114.com", [652]),  # 재질별 > 도자기
    "한국도자기": ("https://mallhankook.com", [988]),  # 스토어 전체
    "로사": ("https://rosamall.co.kr", [23]),  # 전체상품
    "소소모소": ("https://www.sosomoso.com", [356, 357]),  # SIGNATURE(그릇) 먼저, 남는 페이지로 BASIC
    "소로이": ("https://soroishop.com", [506]),  # all
}


def label(text: str, name: str) -> str | None:
    """'소비자가 : 24,500원' 같은 칸에서 값을 꺼낸다."""
    m = re.search(name + r"\s*:\s*([\d,]+)\s*원", text)
    return m.group(1) if m else None


def parse(li, base: str, shop: str) -> dict | None:
    text = re.sub(r"\s+", " ", li.get_text(" ", strip=True))
    m = re.search(r"상품명\s*:\s*(.+?)(?=\s(?:판매가|소비자가|할인판매가|쿠폰적용가)\s*:|$)", text)
    name_el = li.select_one(".name a, .name, .prdName, .description .name")
    # 이름 칸을 먼저 쓰고, 없을 때만 '상품명 :' 글자에서 꺼낸다 (로사는 이름 옆에 정기구독 가격이 붙어 있다)
    name = name_el.get_text(" ", strip=True) if name_el else (m.group(1) if m else "")
    name = re.sub(r"^상품명\s*:\s*", "", name).strip()

    # 가격: data 속성이 있으면 그걸, 없으면 글자 칸, 그것도 없으면 첫 '원' 숫자
    price = won(li.get("data-price")) or won(label(text, "할인판매가")) or won(label(text, "판매가"))
    if price is None:
        first = re.search(r"([\d,]{3,})\s*원", text)
        price = won(first.group(1)) if first else None
    original = won(li.get("data-custom")) or won(label(text, "소비자가"))
    coupon = won(label(text, "쿠폰적용가"))
    review = re.search(r"리뷰\s*:?\s*\(?([\d,]+)\)?", text)
    link = li.select_one("a[href*='/product/']")
    if not name or not price or not is_tableware(name):
        return None
    return {
        "name": name,
        "category": categorize(name),
        "price": price,
        "original_price": original or "",  # 정가를 안 보여 주는 곳은 빈칸(할인 모름), 0%와 구분한다
        "review_count": won(review.group(1)) if review else "",
        "url": base + link["href"] if link and link["href"].startswith("/") else (link["href"] if link else ""),
        "note": f"쿠폰 적용 시 {coupon:,}원" if coupon and coupon < price else "",
        "shop": shop,
    }


def crawl_shop(shop: str, base: str, categories: list[int], session: requests.Session) -> list[dict]:
    rows, seen, budget = [], set(), MAX_PAGES  # 카테고리가 여러 개여도 쇼핑몰 하나에 10페이지까지
    for cate in categories:
        for page in range(1, MAX_PAGES + 1):
            if budget == 0:
                return rows
            budget -= 1
            r = session.get(f"{base}/product/list.html", params={"cate_no": cate, "page": page}, timeout=20)
            if r.status_code != 200:  # 403, 429 등이 오면 멈춘다. 다시 시도하지 않는다
                print(f"  {shop} cate {cate} p{page}: HTTP {r.status_code}, 멈춤")
                return rows
            items = BeautifulSoup(r.text, "html.parser").select("li[id^=anchorBoxId_]")
            new = [li for li in items if li["id"] not in seen]
            if not new:  # 마지막 페이지를 지나면 같은 상품이 반복되거나 비어 있다
                break
            for li in new:
                seen.add(li["id"])
                row = parse(li, base, shop)
                if row:
                    rows.append(row)
            print(f"  {shop} cate {cate} p{page}: {len(new)}개")
            time.sleep(DELAY)
    return rows


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = UA
    rows = []
    for shop, (base, cats) in SHOPS.items():
        rows += crawl_shop(shop, base, cats, session)
    path = save(rows, "cafe24.csv")
    print(f"저장: {path} ({len(rows)}행)")


if __name__ == "__main__":
    main()
