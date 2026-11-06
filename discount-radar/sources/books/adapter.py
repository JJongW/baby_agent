"""도서 (카카오 책 검색 API).

- 키(KAKAO_REST_API_KEY)가 있으면 앱이 뜰 때 카카오를 바로 불러 최신 가격을 쓴다.
- 키가 없거나 카카오 호출이 실패하면 미리 저장한 data/books.csv를 읽는다 (시연 대비).
- 둘 다 없으면 오류를 낸다. 공통 앱은 이 오류를 사이드바에 "불러오지 못함"으로 보여 주고 멈추지 않는다.
  (빈 표를 돌려주면 공통 앱이 1등 분야를 뽑다가 멈춘다.)
"""
import importlib.util
from pathlib import Path

import pandas as pd

TITLE = "도서"
SOURCE = "카카오 책 검색"
METHOD = "API"

HERE = Path(__file__).parent
CSV = HERE / "data" / "books.csv"


def _kakao():
    # 공통 앱은 이 파일을 경로로 읽어서, 같은 폴더의 kakao_books.py를 그냥 import할 수 없다.
    spec = importlib.util.spec_from_file_location("books_kakao", HERE / "kakao_books.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load() -> pd.DataFrame:
    kakao = _kakao()
    key = kakao.read_key()
    api_error = ""
    if key:
        try:
            rows = kakao.collect_all(key)
            if rows:
                return pd.DataFrame(rows)
            api_error = "카카오 결과가 비어 있어요"
        except kakao.KakaoError as e:
            api_error = str(e)

    if CSV.exists():
        df = pd.read_csv(CSV, encoding="utf-8-sig")
        if not df.empty:
            return df

    if api_error:
        raise RuntimeError(f"카카오 호출 실패, 저장된 CSV도 없어요: {api_error}")
    raise FileNotFoundError("키도 CSV도 없어요. KAKAO_REST_API_KEY를 넣고 앱을 다시 켜 주세요.")
