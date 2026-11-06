"""여러 크롤러가 같이 쓰는 '예의 있는 요청' 함수.

사용법:
    from iphone import iphone_get
    html = iphone_get("https://www.gsmarena.com/apple-phones-48.php")   # 글자(HTML)를 돌려준다
"""
import hashlib
import os
import random
import time
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parent / "cache_iphone"   # 받은 페이지를 저장해 두는 폴더
MIN_WAIT, MAX_WAIT = 3.0, 5.0                 # 요청 사이에 쉬는 시간(초): 3~5초 사이 무작위
TIMEOUT_SECONDS = 10                          # 이보다 늦으면 포기

# 내 이름표. 연락처를 환경변수 CONTACT 에 넣어두면 같이 표시된다.
CONTACT = os.environ.get("CONTACT", "student crawling practice, no commercial use")
HEADERS = {
    "User-Agent": f"IphoneListPracticeBot/0.1 ({CONTACT})",
    "Accept-Encoding": "gzip",
}

_last_request_time = None  # 마지막으로 인터넷에 요청한 시각


class BlockedError(Exception):
    """사이트가 접근을 거절(403, 429)했을 때. 프로그램을 멈추게 하는 신호."""


def _cache_path(url: str) -> Path:
    # 주소를 영어·숫자 이름표로 바꿔 파일 이름으로 쓴다.
    return CACHE_DIR / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".html")


def _rest_a_little() -> None:
    """직전 요청 뒤 3~5초(매번 조금씩 다르게)가 지나도록 기다린다."""
    if _last_request_time is None:
        return  # 첫 요청은 기다릴 필요 없다
    wanted_gap = random.uniform(MIN_WAIT, MAX_WAIT)
    remaining = wanted_gap - (time.monotonic() - _last_request_time)
    if remaining > 0:
        time.sleep(remaining)


def iphone_get(url: str, timeout: float = TIMEOUT_SECONDS) -> str | None:
    """예의 있게 페이지를 가져온다. 글자(HTML)를 돌려주고, 못 가져오면 None.

    - 이미 저장된 페이지는 인터넷에 묻지 않고 저장본을 돌려준다.
    - 403, 429를 받으면 BlockedError 를 일으켜 프로그램을 멈춘다.
    - 너무 늦거나 다른 문제가 있으면 그 페이지는 포기하고 None.
    """
    global _last_request_time

    # 1) 이미 받아둔 페이지면 그대로 꺼내 쓴다 (요청 안 함)
    path = _cache_path(url)
    if path.exists():
        return path.read_text(encoding="utf-8")

    # 2) 인터넷에 묻기 전에 잠깐 쉰다
    _rest_a_little()
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.Timeout:
        print(f"[포기] {timeout}초 안에 응답이 없어 포기합니다: {url}")
        return None
    except requests.RequestException as e:
        print(f"[포기] 연결에 문제가 있어 포기합니다({type(e).__name__}): {url}")
        return None
    finally:
        _last_request_time = time.monotonic()

    # 3) 거절당했으면 다시 시도하지 않고 바로 멈춘다
    if resp.status_code in (403, 429):
        raise BlockedError(
            f"사이트가 접근을 거절했습니다(코드 {resp.status_code}). 다시 시도하지 않고 멈춥니다. "
            f"Retry-After={resp.headers.get('Retry-After')} / 주소: {url}"
        )

    # 4) 그 밖의 문제(없는 페이지, 서버 오류 등)는 이 페이지만 포기
    if resp.status_code != 200:
        print(f"[포기] 정상 응답이 아니라 건너뜁니다(코드 {resp.status_code}): {url}")
        return None

    # 5) 성공: 글자가 깨지지 않게 맞추고, 저장한 뒤 돌려준다
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(resp.text, encoding="utf-8")
    return resp.text
