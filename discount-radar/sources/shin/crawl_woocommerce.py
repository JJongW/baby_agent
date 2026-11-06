"""워드프레스(WooCommerce)로 만든 그릇 쇼핑몰을 정적 크롤링(requests)으로 모은다. 지금은 포트메리온 한 곳.

robots.txt 확인(2026-11-06): /category, /wp-admin 등은 금지, 상품 목록 /product-category/ 는 허용.
목록 칸(article.product)마다 정가(<del>)와 할인가(<ins>)가 같이 나온다.
실행: python crawl_woocommerce.py
바꿀 시점: WooCommerce 쇼핑몰이 더 생기면 SHOPS 에 한 줄씩 더한다.
"""
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

from common import DELAY, MAX_PAGES, UA, categorize, is_tableware, save, won

SHOPS = {
    "포트메리온": ("https://portmeirion.co.kr", ["portmeirion/pm-dinnerware", "portmeirion/pm-serveware"]),
}


def first_amount(el) -> int | None:
    """가격 칸에서 첫 금액. '53,200원 – 60,000원' 같은 범위면 낮은 쪽."""
    amount = el.select_one(".woocommerce-Price-amount") if el else None
    return won(amount.get_text()) if amount else None


def parse(item, shop: str) -> dict | None:
    title = item.select_one(".product-title, .woocommerce-loop-product__title")
    link = item.select_one(".product-title a, a.woocommerce-LoopProduct-link")
    price_box = item.select_one(".price")
    if not title or not price_box:
        return None
    name = title.get_text(" ", strip=True)
    sale = first_amount(price_box.select_one("ins"))
    regular = first_amount(price_box.select_one("del"))
    price = sale or first_amount(price_box)
    if not price or not is_tableware(name):
        return None
    return {
        "name": name,
        "category": categorize(name),
        "price": price,
        "original_price": regular or price,  # 할인 표시가 없으면 정가 = 판매가(0%)
        "review_count": "",
        "url": link["href"] if link else "",
        "note": "",
        "shop": shop,
    }


def crawl_one(shop: str) -> list[dict]:
    base, categories = SHOPS[shop]
    session = requests.Session()
    session.headers["User-Agent"] = UA
    rows, seen, budget = [], set(), MAX_PAGES  # 카테고리가 여러 개여도 쇼핑몰 하나에 10페이지까지
    for cat in categories:
        for page in range(1, MAX_PAGES + 1):
            if budget == 0:
                return rows
            budget -= 1
            url = f"{base}/product-category/{cat}/" + (f"page/{page}/" if page > 1 else "")
            r = session.get(url, timeout=20)
            if r.status_code == 404:  # 마지막 페이지를 지났다
                break
            if r.status_code != 200:  # 403, 429 등은 멈추고 다시 시도하지 않는다
                print(f"  {shop} {cat} p{page}: HTTP {r.status_code}, 멈춤")
                return rows
            items = BeautifulSoup(r.text, "html.parser").select("article.product, li.product")
            new = 0
            for item in items:
                row = parse(item, shop)
                if row and row["url"] not in seen:  # 같은 상품이 두 카테고리에 다 있으면 한 번만
                    seen.add(row["url"])
                    rows.append(row)
                    new += 1
            print(f"  {shop} {cat} p{page}: 칸 {len(items)}개, 새 그릇 {new}개")
            if not items:
                break
            time.sleep(DELAY)
    return rows


def main() -> None:
    with ThreadPoolExecutor(max_workers=len(SHOPS)) as pool:
        rows = [r for rs in pool.map(crawl_one, SHOPS) for r in rs]
    path = save(rows, "woocommerce.csv")
    print(f"저장: {path} ({len(rows)}행)")


if __name__ == "__main__":
    main()
