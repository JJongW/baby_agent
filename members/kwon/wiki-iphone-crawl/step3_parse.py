"""3단계: 저장된 HTML 파일에서 값을 뽑아 CSV로 만든다. (인터넷 요청 없음)

뽑는 항목: 모델명, 출시일, 화면 크기, 칩셋, 출시 시 iOS
문서에 없는 값은 지어내지 않고 '정보 없음'으로 적는다.
"""
import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
MODEL_DIR = ROOT / "data" / "models"
OUT_CSV = ROOT / "iphone_models.csv"
NO_INFO = "정보 없음"
LICENSE = "CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/deed.ko)"

# (모델명, 문서 제목, 그 문서 안에서 몇 번째 모델인지: 0=첫째, 1=둘째). 문서가 없으면 None.
MODELS = [
    ("아이폰 15",           "아이폰_15", 0),
    ("아이폰 15 플러스",     "아이폰_15", 1),
    ("아이폰 15 프로",       "아이폰_15_프로", 0),
    ("아이폰 15 프로 맥스",   "아이폰_15_프로", 1),
    ("아이폰 16",           "아이폰_16", 0),
    ("아이폰 16 플러스",     "아이폰_16", 1),
    ("아이폰 16 프로",       "아이폰_16_프로", 0),
    ("아이폰 16 프로 맥스",   "아이폰_16_프로", 1),
    ("아이폰 16e",          "아이폰_16e", 0),
    ("아이폰 17",           None, 0),
    ("아이폰 17 프로",       "아이폰_17_프로", 0),
    ("아이폰 17 프로 맥스",   "아이폰_17_프로", 1),
    ("아이폰 에어",          "아이폰_에어", 0),
    ("아이폰 18 프로",       None, 0),
    ("아이폰 18 프로 맥스",   None, 0),
    ("듀오",               None, 0),
]


# 위키백과 문서 제목 -> 저장된 영어 파일 이름 (step2_download_models.py 와 같아야 한다)
FILE_NAMES = {
    "아이폰_15": "iphone_15", "아이폰_15_프로": "iphone_15_pro",
    "아이폰_16": "iphone_16", "아이폰_16_프로": "iphone_16_pro",
    "아이폰_16e": "iphone_16e", "아이폰_17_프로": "iphone_17_pro",
    "아이폰_에어": "iphone_air",
}

# 문서 본문 문장에 적힌 '미국 출시 시작가(USD)'. 문서에 가격이 없는 모델은 일부러 넣지 않는다(빈칸).
# 값은 저장된 HTML의 '출시 및 가격' 문장을 보고 직접 확인해서 적었다.
PRICES_USD = {
    "아이폰 16":         ("799",   "아이폰 16 문서 '출시 및 가격'"),
    "아이폰 16 플러스":   ("899",   "아이폰 16 문서 '출시 및 가격'"),
    "아이폰 16 프로":     ("999",   "아이폰 16 프로 문서 '출시 및 가격'"),
    "아이폰 16 프로 맥스": ("1199",  "아이폰 16 프로 문서 '출시 및 가격'"),
    "아이폰 16e":        ("599",   "아이폰 16e 문서 본문"),
}


def infobox_rows(html: str) -> dict:
    """정보 상자를 {항목이름: 내용} 딕셔너리로 바꾼다."""
    soup = BeautifulSoup(html, "html.parser")
    box = soup.find("table", class_=lambda c: c and "infobox" in c)
    rows = {}
    if box:
        for tr in box.find_all("tr"):
            th, td = tr.find("th"), tr.find("td")
            if th and td:
                rows[th.get_text(" ", strip=True)] = td.get_text(" ", strip=True)
    return rows


def first_date(text: str) -> str | None:
    m = re.search(r"(\d{4})년 (\d{1,2})월 (\d{1,2})일", text)
    return f"{int(m[1]):04d}-{int(m[2]):02d}-{int(m[3]):02d}" if m else None


def parse_page(title: str, idx: int) -> dict:
    rows = infobox_rows((MODEL_DIR / f"{FILE_NAMES[title]}.html").read_text(encoding="utf-8"))

    # 출시일: 판매 시작일('가능' 행)이 있으면 그것, 없으면 '발매' 행
    release = first_date(rows.get("가능", "")) or first_date(rows.get("발매", "")) or NO_INFO

    sizes = re.findall(r"(\d\.\d)\s*(?:in|인치)", rows.get("디스플레이", ""))
    size = sizes[idx] if idx < len(sizes) else NO_INFO

    m = re.search(r"iOS\s*[\d.]+", rows.get("운영 체제", ""))
    return {
        "출시일": release,
        "화면 크기(인치)": size,
        "칩셋": rows.get("프로세서", NO_INFO),
        "출시 시 iOS": m.group(0) if m else NO_INFO,
    }


def main() -> None:
    today = date.today().isoformat()
    fields = ["모델명", "출시일", "화면 크기(인치)", "칩셋", "출시 시 iOS",
              "출시 가격(USD, 미국 시작가)", "가격 근거", "출처 URL", "수집일", "라이선스"]
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: 엑셀에서 한글 안 깨짐
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, title, idx in MODELS:
            if title is None:
                row = {k: NO_INFO for k in fields[1:5]}
                url = NO_INFO
            else:
                row = parse_page(title, idx)
                url = "https://ko.wikipedia.org/wiki/" + quote(title)
            price, basis = PRICES_USD.get(name, ("", ""))  # 문서에 없으면 빈칸
            w.writerow({"모델명": name, **row,
                        "출시 가격(USD, 미국 시작가)": price, "가격 근거": basis,
                        "출처 URL": url,
                        "수집일": today, "라이선스": LICENSE if title else NO_INFO})
    print(f"저장 완료: {OUT_CSV}")


if __name__ == "__main__":
    main()
