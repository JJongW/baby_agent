"""권: 아이폰 모델 (위키백과). 권이 만든 members/kwon/wiki-iphone-crawl/ 의 결과 CSV를 그대로 읽는다.

할인 데이터가 아니다: 모델별 스펙과 미국 출시 시작가(달러)만 있고, 정가 대비 할인가가 없다.
그래서 앱은 이 항목을 고르면 할인 계산 대신 표를 보여 주고, 원화가 아니라 전체 보기 합계에서도 뺀다.
권 폴더는 고치지 않는다. 수집을 다시 하려면 그 폴더의 step1~3 을 차례로 돌린다.
"""
import re
from pathlib import Path

import pandas as pd

TITLE = "아이폰"
SOURCE = "한국어 위키백과 (CC BY-SA 4.0)"
METHOD = "정적 크롤링"
UNIT = "달러"  # 원화가 아닌 데이터라는 표시. app.py 가 읽는다

CSV = Path(__file__).parents[3] / "members" / "kwon" / "wiki-iphone-crawl" / "iphone_models.csv"
NO_INFO = "정보 없음"


def series(name: str) -> str:
    m = re.search(r"아이폰 (\d+)", name)
    return f"아이폰 {m[1]} 시리즈" if m else "기타"


def load() -> pd.DataFrame:
    raw = pd.read_csv(CSV, encoding="utf-8-sig").replace(NO_INFO, "")
    return pd.DataFrame({
        "name": raw["모델명"],
        "category": raw["모델명"].map(series),
        "price": raw["출시 가격(USD, 미국 시작가)"],  # 문서에 가격이 없는 모델은 빈칸
        "url": raw["출처 URL"],
        "출시일": raw["출시일"],
        "화면(인치)": raw["화면 크기(인치)"],
        "칩셋": raw["칩셋"],
        "출시 iOS": raw["출시 시 iOS"],
    })
