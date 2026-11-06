"""윤: Steam 세일 게임. 윤이 만든 members/yoon/discount-radar/ 의 결과 CSV를 그대로 읽는다 (윤 폴더는 안 고침).

윤 데이터에는 장르 칸이 없어 카테고리를 Steam 평가 등급(압도적으로 긍정적 등)으로 쓴다.
→ ① 질문이 "평가가 어떤 게임이 할인을 많이 하나"가 된다.
윤 데이터 카드(data/README.md)의 조건: 출처(Steam)와 수집 시각 표기, Valve와 무관하다고 표기. SOURCE에 넣어 화면 아래에 나온다.
다시 받으려면 그 폴더에서 python collect.py 를 돌린다.
"""
from pathlib import Path

import pandas as pd

TITLE = "게임"
SOURCE = "Steam 스토어, 2026-11-06 수집, Valve와 무관"
METHOD = "정적 크롤링"

CSV = Path(__file__).parents[3] / "members" / "yoon" / "discount-radar" / "data" / "games.csv"


def load() -> pd.DataFrame:
    raw = pd.read_csv(CSV, encoding="utf-8-sig")
    return pd.DataFrame({
        "name": raw["제목"],
        "category": raw["리뷰등급"].fillna("리뷰 없음"),
        "price": raw["할인가"],
        "original_price": raw["정가"],
        "review_count": raw["리뷰수"],
        "url": raw["Steam링크"],
        "note": "",
    })
