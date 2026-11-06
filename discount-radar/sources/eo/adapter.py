"""어: 야구 티켓 (SeatGeek 공식 API). 어가 만든 members/eo/eo_crawling_1106/ 의 결과 CSV를 그대로 읽는다.

할인 데이터가 아니다: 경기마다 티켓 최저가와 최고가(달러)만 있다. 둘은 좌석이 달라 정가와 할인가로 볼 수 없다.
그래서 앱은 이 항목을 고르면 할인 계산 대신 표를 보여 주고, 원화가 아니라 전체 보기 합계에서도 뺀다.
어 폴더는 고치지 않는다. 다시 받으려면 그 폴더에서 export_giants_dodgers_schedule.py 를 돌린다(.env에 키 필요).
"""
from pathlib import Path

import pandas as pd

TITLE = "야구 티켓"
SOURCE = "SeatGeek API"
METHOD = "API"
UNIT = "달러"

CSV = Path(__file__).parents[3] / "members" / "eo" / "eo_crawling_1106" / "sf_giants_vs_la_dodgers_schedule.csv"


def dollars(col: pd.Series) -> pd.Series:
    """"$1,234" → 1234. "티켓 오픈 대기 중" 같은 글자는 빈칸."""
    return pd.to_numeric(col.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")


def load() -> pd.DataFrame:
    raw = pd.read_csv(CSV, encoding="utf-8-sig")
    return pd.DataFrame({
        "name": raw["경기명"],
        "category": raw["홈팀"],
        "price": dollars(raw["티켓 최저가(추정)"]),  # 가장 싼 좌석 값
        "최고가(달러)": dollars(raw["티켓 최고가(추정)"]),
        "경기 날짜": raw["경기 날짜"],
        "경기 시간": raw["경기 시간"],
        "경기장": raw["경기장 위치"],
        "url": raw["좌석 및 티켓 확인 링크"],
    })
