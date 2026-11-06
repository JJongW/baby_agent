"""신: 그릇. 카페24 그릇 쇼핑몰 5곳(정적 크롤링) + 29CM 그릇/커트러리(Playwright).
수집 결정과 이유는 수집결정 문서(DECISION.md)에 있다. 데이터를 새로 받으려면 crawl_*.py 를 돌린다."""
import importlib.util
from pathlib import Path

import pandas as pd

# 앱은 이 파일을 경로로 직접 읽는다. 다른 조원 폴더의 common.py와 섞이지 않게 고유한 이름으로 불러온다
_spec = importlib.util.spec_from_file_location("shin_common", Path(__file__).parent / "common.py")
_common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_common)
categorize, is_tableware = _common.categorize, _common.is_tableware

TITLE = "그릇"
SOURCE = "그릇114, 한국도자기, 로사, 소소모소, 소로이, 29CM"
METHOD = "정적 크롤링, Playwright"

DATA = Path(__file__).parent / "data"


def load() -> pd.DataFrame:
    df = pd.concat([pd.read_csv(f) for f in sorted(DATA.glob("*.csv"))], ignore_index=True)
    # 분류 규칙(common.py)을 고치면 다시 수집하지 않아도 여기서 새 규칙이 적용된다
    df = df[df["name"].map(is_tableware)].copy()
    df["category"] = df["name"].map(categorize)
    # 어느 쇼핑몰 상품인지 이름 앞에 붙인다 (radar 표준 열에는 쇼핑몰 칸이 없다)
    df["name"] = "[" + df["shop"] + "] " + df["name"]
    return df
