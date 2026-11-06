# 할인 레이더

조원 5명이 각자 고른 수집처(API, 정적 크롤링, Playwright)에서 모은 할인 데이터를 한 사이트에서 본다.
같은 기능 3개(카테고리별 할인율, 예산으로 고르기, 할인 TOP 5)가 누구 데이터든 똑같이 돈다.

## 실행
```bash
pip install -r discount-radar/requirements.txt
streamlit run discount-radar/app.py
```

## 파일
| 파일 | 하는 일 |
| --- | --- |
| `app.py` | 화면. `sources/`의 조원 폴더를 자동으로 읽는다 |
| `radar.py` | 공통 기능 3개와 할인율 계산 |
| `theme.css`, `.streamlit/config.toml` | 무채색 테마 (TDS 원칙을 따름, 코드 복사 아님) |
| `sources/` | 조원별 데이터. 넣는 방법은 [sources/README.md](sources/README.md) |
| `folders.py`, `components/glass_folder/` | 맨 위 유리 폴더 카드. 받은 React 컴포넌트를 그대로 두고 CDN의 React로 돌린다. 폴더를 열면 그 조원 데이터로 바뀐다 |
