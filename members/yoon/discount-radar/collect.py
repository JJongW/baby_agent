"""할인 레이더 수집기 — Steam 세일 중인 게임 (한 번만 수집)

1단계 목록: 세일 목록을 평가순 5페이지 + 관련도순 5페이지 (최대 10페이지 · 500개)
2단계 상세: 게임마다 appdetails 1번 (type 확인 · 한국어 지원)
결과: data/games.csv

사용:  python collect.py                 # 전체
       python collect.py --pages 1 --details 3   # 시험 (각 정렬 1페이지 · 상세 3개)
다시 돌리면 polite_get 캐시로 이어 받는다 (이미 받은 페이지는 요청하지 않는다).
"""
import argparse, json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from polite import polite_get, cached_at, Refused

KST = timezone(timedelta(hours=9))
SEARCH = "https://store.steampowered.com/search/results/"
DETAIL = "https://store.steampowered.com/api/appdetails"
PER_PAGE = 50
MAX_PAGES_PER_SORT = 5          # 정렬마다 5페이지 → 합계 10페이지 상한
MAX_DETAILS = 500               # 상세 요청 상한 (목록 최대 500개)
WAIT = dict(min_wait=1.5, max_wait=2.5)
SORTS = {"평가순": "Reviews_DESC", "관련도순": None}   # None = Steam 기본 정렬


def kst(ts):
    return datetime.fromtimestamp(ts, KST).isoformat(timespec="seconds")


def won(text):
    digits = re.sub(r"\D", "", text or "")
    return int(digits) if digits else None


def search_params(sort_by, page):
    p = {"specials": 1, "infinite": 1, "cc": "kr", "l": "korean",
         "count": PER_PAGE, "start": page * PER_PAGE}
    if sort_by:
        p["sort_by"] = sort_by
    return p


def parse_row(a):
    """세일 목록 한 줄 → dict. 번들 · 가격 없는 줄은 None"""
    appid = a.get("data-ds-appid", "")
    if not appid or "," in appid or a.get("data-ds-bundleid") or a.get("data-ds-packageid"):
        return None                                      # 번들 · 패키지
    orig = won(getattr(a.select_one(".discount_original_price"), "text", ""))
    final = won(getattr(a.select_one(".discount_final_price"), "text", ""))
    pct = won(getattr(a.select_one(".discount_pct"), "text", ""))
    if orig is None or final is None or pct is None:
        return None
    rv = a.select_one(".search_review_summary")
    tip = rv.get("data-tooltip-html", "") if rv else ""
    m = re.search(r"([\d,]+)개 중 (\d+)%", tip)
    os_ = {c for img in a.select(".platform_img") for c in img.get("class", [])}
    return {
        "appid": int(appid),
        "제목": a.select_one(".title").get_text(strip=True),
        "Steam링크": f"https://store.steampowered.com/app/{appid}/",
        "정가": orig, "할인가": final, "할인율": pct,
        "리뷰수": int(m.group(1).replace(",", "")) if m else 0,
        "긍정%": int(m.group(2)) if m else None,
        "리뷰등급": tip.split("<br>")[0] if tip else "",
        "windows": "win" in os_, "mac": "mac" in os_,
    }


def collect_list(pages):
    rows = {}
    for name, sort_by in SORTS.items():
        for page in range(min(pages, MAX_PAGES_PER_SORT)):
            params = search_params(sort_by, page)
            data = json.loads(polite_get(SEARCH, params, **WAIT))
            got = 0
            for a in BeautifulSoup(data["results_html"], "html.parser").select("a.search_result_row"):
                r = parse_row(a)
                if not r:
                    continue
                got += 1
                if r["appid"] in rows:
                    rows[r["appid"]]["수집출처"] = "평가순+관련도순"
                else:
                    r["수집출처"] = name
                    r["수집시각"] = kst(cached_at(SEARCH, params))
                    rows[r["appid"]] = r
            print(f"  {name} {page + 1}페이지: {got}개 (누적 {len(rows)})")
            if got == 0:
                break
    return list(rows.values())


def korean_of(langs):
    if langs is None:
        return None
    return "한국어" in re.sub(r"<[^>]+>", "", langs)


def add_details(rows, limit):
    limit = min(limit, MAX_DETAILS)
    for i, r in enumerate(rows[:limit]):
        params = {"appids": r["appid"], "cc": "kr", "l": "korean"}
        body = json.loads(polite_get(DETAIL, params, **WAIT)).get(str(r["appid"]), {})
        d = body.get("data") if body.get("success") else None
        r["type"] = d.get("type") if d else None
        r["한국어"] = korean_of(d.get("supported_languages")) if d else None
        if (i + 1) % 25 == 0:
            print(f"  상세 {i + 1}/{min(limit, len(rows))}")
    return rows[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=MAX_PAGES_PER_SORT, help="정렬마다 몇 페이지 (최대 5)")
    ap.add_argument("--details", type=int, default=MAX_DETAILS, help=f"상세를 몇 개까지 (최대 {MAX_DETAILS})")
    ap.add_argument("--out", default="data/games.csv")
    args = ap.parse_args()

    try:
        print("1단계 목록")
        rows = collect_list(args.pages)
        print(f"2단계 상세 ({min(args.details, len(rows))}개)")
        rows = add_details(rows, args.details)
    except Refused as e:
        print(f"⛔ {e}")
        print("   여기서 멈춥니다. 재시도하지 않아요. 지금까지 받은 페이지는 캐시에 남아 있어요.")
        sys.exit(1)

    df = pd.DataFrame(rows)
    before = len(df)
    # 상세 요청이 실패해 type을 모르는 게임은 남기고 한국어 = 모름(빈칸)으로 둔다 (plan.md)
    df = df[(df["type"].isna() | (df["type"] == "game")) & (df["정가"] > 0)]
    cols = ["appid", "제목", "Steam링크", "정가", "할인가", "할인율", "리뷰수", "긍정%", "리뷰등급",
            "windows", "mac", "한국어", "수집출처", "수집시각"]
    # 빈칸이 섞인 정수 칸은 pandas가 소수(99.0)로 바꾸므로, 빈칸을 허용하는 정수형(Int64)으로 고정한다
    df["긍정%"] = df["긍정%"].astype("Int64")
    Path(args.out).parent.mkdir(exist_ok=True)
    df[cols].to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"\n저장: {args.out} · {len(df)}개 (게임이 아니거나 정가 0원이라 뺀 것 {before - len(df)}개)")
    print(df[cols].isna().sum().to_string())


if __name__ == "__main__":
    main()
