"""권: 아이폰 모델 (GSMArena). 권이 만든 members/kwon/wiki-iphone-crawl/iphone_crawl/ 의 결과 CSV를 그대로 읽는다.

권이 위키백과 CSV(iphone_models.csv)를 GSMArena 결과(iphone_specs.csv)로 바꿨다 (권 CHANGES.md).
할인 데이터가 아니다: 모델별 스펙과 가격(달러)만 있다. 그래서 앱은 할인 계산 대신 표를 보여 주고, 전체 보기 합계에서 뺀다.
GSMArena 약관은 허락 없는 재배포를 금지한다. PO가 알고 싣기로 정했고(2026-11-06), 화면에 출처와 학습용임을 밝힌다.
권 폴더는 고치지 않는다. 다시 받으려면 그 폴더에서 iphone_crawl/save_iphone_csv.py 를 돌린다.
"""
import re
from pathlib import Path

import pandas as pd

TITLE = "아이폰"
SOURCE = "GSMArena (개인 학습용, 사이트 약관상 재배포 금지)"
METHOD = "정적 크롤링"
UNIT = "달러"  # 원화가 아닌 데이터라는 표시. app.py 가 읽는다
NOTE = ("가격은 GSMArena가 나라별 가격을 달러로 환산한 값이 섞여 있어 미국 출시가와 다를 수 있어요. "
        "iPhone Duo 가격(1,999달러)은 GSMArena에 없어 출시 보도를 보고 권이 직접 넣은 값이에요.")

CSV = Path(__file__).parents[3] / "members" / "kwon" / "wiki-iphone-crawl" / "iphone_crawl" / "iphone_specs.csv"


def series(name: str) -> str:
    m = re.search(r"iPhone (\d+)", name)
    return f"iPhone {m[1]} 시리즈" if m else "기타"


def load() -> pd.DataFrame:
    raw = pd.read_csv(CSV, encoding="utf-8-sig")
    return pd.DataFrame({
        "name": raw["이름"],
        "category": raw["이름"].map(series),
        "price": raw["가격(USD)"],
        "url": raw["주소"],
        "출시일": raw["출시일"],
        "화면(인치)": raw["화면(인치)"],
        "칩셋": raw["칩셋"],
        "출시 iOS": raw["출시 iOS"],
    })
