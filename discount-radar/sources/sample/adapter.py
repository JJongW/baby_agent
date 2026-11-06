"""예시 데이터 (가짜). 사이트가 도는지 보려는 용도. 조원 데이터가 들어오면 이 폴더는 지운다."""
from pathlib import Path

import pandas as pd

TITLE = "예시 데이터"
SOURCE = "가짜 데이터"
METHOD = "없음"


def load() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parent / "data" / "sample.csv")
