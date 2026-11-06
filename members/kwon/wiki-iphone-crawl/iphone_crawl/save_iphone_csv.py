"""GSMArena Apple 목록(첫 페이지)에서 iPhone만 골라 상세 스펙을 CSV로 저장한다.

실행: booklist/ 에서  python iphone_crawl/save_iphone_csv.py
- 요청은 모두 iphone.py 의 iphone_get 으로 한다 (3~5초 대기, 캐시, 403/429면 중단).
- 개인 학습용(비상업) 전용. CSV와 cache_iphone/ 을 공개 저장소에 올리지 않는다.
"""
import csv
import html
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from iphone import BlockedError, iphone_get  # noqa: E402

BASE = "https://www.gsmarena.com/"
LIST_URL = BASE + "apple-phones-48.php"
OUT = Path(__file__).parent / "iphone_specs.csv"
FIELDS = ["이름", "가격(USD)", "출시일", "화면(인치)", "칩셋", "출시 iOS", "주소"]
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def list_iphones(page: str):
    items = re.findall(r'<li><a href="(apple_[^"]+-\d+\.php)"><img[^>]*><strong>([^<]*)</strong>', page)
    return [(html.unescape(n).strip(), BASE + h) for h, n in items if n.strip().lower().startswith("iphone")]


def parse(page: str) -> dict:
    rows = {}
    for k, v in re.findall(r'<td class="ttl"><a[^>]*>([^<]*)</a></td>\s*<td class="nfo"[^>]*>(.*?)</td>', page, re.S):
        rows.setdefault(k, clean(v))  # 같은 이름 칸은 처음 것만 쓴다

    price = re.search(r"\$\s*([\d,]+(?:\.\d+)?)", rows.get("Price", ""))
    size = re.search(r"([\d.]+)\s*inches", rows.get("Size", ""))
    ios = re.search(r"iOS\s*([\d.]+)", rows.get("OS", ""))
    rel = re.search(r"Released\s+(\d{4}),\s*([A-Za-z]+)(?:\s+(\d{1,2}))?", rows.get("Status", ""))
    released = ""
    if rel and rel.group(2) in MONTHS:
        released = f"{rel.group(1)}-{MONTHS[rel.group(2)]:02d}" + (f"-{int(rel.group(3)):02d}" if rel.group(3) else "")
    return {
        "가격(USD)": price.group(1).replace(",", "") if price else "",
        "출시일": released,
        "화면(인치)": size.group(1) if size else "",
        "칩셋": rows.get("Chipset", ""),
        "출시 iOS": ios.group(1) if ios else "",
    }


def main() -> None:
    page = iphone_get(LIST_URL)
    if page is None:
        raise SystemExit("목록 페이지를 받지 못했습니다")
    iphones = list_iphones(page)
    print(f"iPhone {len(iphones)}개 발견")

    result = []
    try:
        for i, (name, url) in enumerate(iphones, 1):
            detail = iphone_get(url)
            if detail is None:
                print(f"[{i}/{len(iphones)}] 건너뜀: {name}")
                continue
            result.append({"이름": name, **parse(detail), "주소": url})
            print(f"[{i}/{len(iphones)}] {name}")
    except BlockedError as e:
        print("[중단]", e)

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: 엑셀에서 한글 안 깨짐
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(result)
    print(f"{len(result)}행 저장: {OUT}")


if __name__ == "__main__":
    main()
