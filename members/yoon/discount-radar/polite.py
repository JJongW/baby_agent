"""예의 있는 요청: 랜덤 지연 · 캐시 · 403/429 즉시 중단 · 타임아웃 · 신원 표시

알아 둘 점
- 캐시: 기본값(cache_ttl=None)에서는 캐시가 만료되지 않아요. 한 번 받은 페이지는
  계속 같은 내용으로 돌아와요. 가격처럼 바뀌는 데이터는 cache_ttl(초)을 주거나
  use_cache=False로 부르세요. 캐시를 통째로 지우려면 .cache/ 폴더를 삭제하면 돼요.
- 지연: 마지막 요청 시각(_last)이 모듈 전역 변수라 한 프로세스 안에서만 간격이
  지켜져요. 크롤러를 동시에 여러 개 돌리면 서로의 간격을 모르니, 같은 사이트에는
  한 번에 하나만 돌리세요.
- 재시도: 403/429는 사이트가 "그만"이라고 한 것이라 일부러 재시도하지 않아요.
  타임아웃 같은 네트워크 오류도 재시도 없이 예외를 그대로 올려요.
- Playwright로 연 브라우저의 요청은 이 함수를 거치지 않아요. 클릭 사이 지연은 따로 넣으세요.
"""
import hashlib, random, time
from pathlib import Path
import requests

CACHE = Path(__file__).parent / ".cache"
UA = "Mozilla/5.0 (compatible; camp-d18-crawler/1.0; +https://github.com/uyeon0)"
_last = 0.0  # 이 프로세스 안에서만 유효해요 (위 "지연" 참고)


class Refused(Exception):
    pass


def polite_get(url, params=None, min_wait=1.0, max_wait=2.0, timeout=10,
               use_cache=True, cache_ttl=None):
    """cache_ttl: 캐시 유효 시간(초). None이면 만료 없음."""
    global _last
    req = requests.Request("GET", url, params=params).prepare()
    key = CACHE / (hashlib.sha1(req.url.encode()).hexdigest() + ".html")

    if use_cache and key.exists():
        age = time.time() - key.stat().st_mtime
        if cache_ttl is None or age < cache_ttl:
            return key.read_text(encoding="utf-8")

    wait = random.uniform(min_wait, max_wait) - (time.time() - _last)
    if wait > 0:
        time.sleep(wait)
    try:
        r = requests.get(req.url, headers={"User-Agent": UA}, timeout=timeout)
    finally:
        _last = time.time()  # 실패한 요청도 요청이니 간격 계산에 넣어요

    if r.status_code in (403, 429):
        raise Refused(f"{r.status_code} 거절: {req.url} — 수집을 멈춥니다")
    r.raise_for_status()
    # 리다이렉트로 다른 페이지(예: 첫 화면)에 도착했으면, 그 페이지는 내가 원한 게 아니에요.
    # 그대로 캐시하면 엉뚱한 HTML이 데이터인 척 남으니 멈춰요.
    if r.history:
        raise Refused(f"{r.history[0].status_code} 리다이렉트: {req.url} → {r.url} — 의도한 응답이 아니라서 멈춥니다")

    # 서버가 charset을 안 알려 주면 requests는 ISO-8859-1로 읽어서 한글이 깨져요.
    # 그럴 땐 본문을 보고 인코딩을 추정해요.
    if "charset" not in r.headers.get("Content-Type", "").lower():
        r.encoding = r.apparent_encoding or "utf-8"

    if use_cache:
        CACHE.mkdir(exist_ok=True)
        key.write_text(r.text, encoding="utf-8")
    return r.text


def cached_at(url, params=None):
    """이 요청의 캐시가 저장된 시각(유닉스 초). 캐시가 없으면 None.
    이어 받기로 다시 돌려도 '처음 받은 시각'을 수집 시각으로 남기려고 쓴다."""
    req = requests.Request("GET", url, params=params).prepare()
    key = CACHE / (hashlib.sha1(req.url.encode()).hexdigest() + ".html")
    return key.stat().st_mtime if key.exists() else None
