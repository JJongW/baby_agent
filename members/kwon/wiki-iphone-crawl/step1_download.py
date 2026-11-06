"""1단계: 위키백과 '아이폰' 문서를 딱 1번만 받아서 파일로 저장한다.

지키는 규칙 (Wikimedia 로봇 정책 / API 예절):
- 일반 문서 주소(/wiki/문서이름)를 파라미터 없이 요청
- User-Agent에 이름과 연락처 표시 (안 하면 403 차단)
- gzip 압축 요청
- 한 번에 하나씩, 이미 저장돼 있으면 다시 요청하지 않음
- 429/503 오류가 나면 Retry-After 만큼 기다리지 않고 멈춤 (연습이라 재시도 안 함)
"""
import os
import sys
from datetime import date
from pathlib import Path

import requests

URL = "https://ko.wikipedia.org/wiki/IPhone"
SAVE_DIR = Path(__file__).parent / "data"
SAVE_PATH = SAVE_DIR / "iphone_ko.html"
META_PATH = SAVE_DIR / "iphone_ko.meta.txt"

# 내 연락처를 환경변수 CONTACT 에 넣어두면 명찰에 표시된다. (예: 이메일 또는 웹주소)
# 지정하지 않으면 '학생 연습용'이라고만 표시한다.
CONTACT = os.environ.get("CONTACT", "student crawling practice, no commercial use")
HEADERS = {
    "User-Agent": f"IphoneCrawlPracticeBot/0.1 ({CONTACT}) python-requests",
    "Accept-Encoding": "gzip",
}


def main() -> int:
    SAVE_DIR.mkdir(exist_ok=True)

    if SAVE_PATH.exists():
        print(f"이미 저장돼 있어서 요청하지 않습니다: {SAVE_PATH}")
        return 0

    print("위키백과에 1번 요청합니다...")
    resp = requests.get(URL, headers=HEADERS, timeout=30)

    if resp.status_code in (429, 503):
        print(f"서버가 바쁘다고 합니다({resp.status_code}). Retry-After={resp.headers.get('Retry-After')}")
        print("지금 멈춥니다. 한참 뒤에 다시 시도하세요.")
        return 1
    resp.raise_for_status()

    SAVE_PATH.write_text(resp.text, encoding="utf-8")
    META_PATH.write_text(
        f"source_url={URL}\nfetched_on={date.today().isoformat()}\n"
        f"license=CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/deed.ko)\n",
        encoding="utf-8",
    )
    print(f"저장 완료: {SAVE_PATH} ({len(resp.text):,}자)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
