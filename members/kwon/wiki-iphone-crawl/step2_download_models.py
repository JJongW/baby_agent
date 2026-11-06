"""2단계: 모델별 위키백과 문서 7개를 차례대로(한 번에 하나씩, 3초 간격) 받아서 저장한다.

이미 저장된 파일은 다시 요청하지 않는다. 429/503이 나오면 즉시 멈춘다.
"""
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

BASE = "https://ko.wikipedia.org/wiki/"
# (위키백과 문서 제목, 저장할 영어 파일 이름). 이 저장소는 파일 이름에 한글을 못 쓴다.
PAGES = [("아이폰_15", "iphone_15"), ("아이폰_15_프로", "iphone_15_pro"),
         ("아이폰_16", "iphone_16"), ("아이폰_16_프로", "iphone_16_pro"),
         ("아이폰_16e", "iphone_16e"), ("아이폰_17_프로", "iphone_17_pro"),
         ("아이폰_에어", "iphone_air")]
SAVE_DIR = Path(__file__).parent / "data" / "models"
DELAY_SECONDS = 3

CONTACT = os.environ.get("CONTACT", "student crawling practice, no commercial use")
HEADERS = {
    "User-Agent": f"IphoneCrawlPracticeBot/0.1 ({CONTACT}) python-requests",
    "Accept-Encoding": "gzip",
}


def main() -> int:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    first_request = True
    for title, slug in PAGES:
        path = SAVE_DIR / f"{slug}.html"
        if path.exists():
            print(f"건너뜀(이미 있음): {title}")
            continue
        if not first_request:
            time.sleep(DELAY_SECONDS)  # 천천히
        first_request = False

        resp = requests.get(BASE + quote(title), headers=HEADERS, timeout=30)
        if resp.status_code in (429, 503):
            print(f"서버가 바쁘다고 합니다({resp.status_code}). 멈춥니다. Retry-After={resp.headers.get('Retry-After')}")
            return 1
        if resp.status_code == 404:
            print(f"문서 없음(404): {title}")
            continue
        resp.raise_for_status()
        path.write_text(resp.text, encoding="utf-8")
        print(f"저장: {title} ({len(resp.text):,}자)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
