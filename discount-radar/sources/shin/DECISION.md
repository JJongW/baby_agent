# 수집 결정: 그릇 (신)

## 질문
그릇 중 어느 카테고리(접시, 볼/공기, 컵/잔, 커트러리, 세트)가 할인을 가장 많이 하나?

## 후보와 판정 (2026-11-06 확인)
| 후보 | 판정 | 이유 |
| --- | --- | --- |
| 그릇114 (dish114.com) | 수집 | robots.txt가 상품 목록 허용. 카페24 |
| 한국도자기 (mallhankook.com) | 수집 | 위와 같음 |
| 로사 (rosamall.co.kr) | 수집 | 위와 같음 |
| 소소모소 (sosomoso.com) | 수집 | 위와 같음. 그릇이 아닌 생활용품은 뺀다 |
| 소로이 (soroishop.com) | 수집 | 위와 같음 |
| 29CM 그릇/커트러리 | 수집 | `/store/category/` 허용. 화면을 연 뒤 그려져 Playwright 사용 |
| 쿠팡 | 탈락 | 접속 차단(403). 우회하지 않는다 |
| 오늘의집 | 탈락 | 접속 차단(403) |
| 웨스트엘름 | 탈락 | robots.txt가 일반 봇 전부 금지 |
| 풍경 스마트스토어 | 탈락 | smartstore.naver.com robots.txt가 일반 봇 전부 금지 |
| 아주키친 | 탈락 | robots.txt가 일반 봇 전부 금지 |
| 네이버 검색광고 결과 | 탈락 | 쇼핑몰이 아니라 광고 목록. 네이버 검색은 봇 금지이고, 광고 링크를 따라가면 광고주에게 비용이 생긴다 |

이용약관: 카페24 5곳은 약관이 `/member/`(robots 금지 경로) 아래에 있어 사람이 브라우저로 읽어 확인한다. **(확인 필요)**
29CM 약관은 화면을 연 뒤 그려져 아직 읽지 못했다. **(확인 필요)**

## 방법과 범위
- 카페24 5곳: `crawl_cafe24.py`, requests + BeautifulSoup. 쇼핑몰마다 최대 10페이지
- 29CM: `crawl_29cm.py`, Playwright로 목록 페이지를 열고 그 페이지가 스스로 불러오는 상품 데이터만 받는다. 최대 10페이지(500개)
- 요청 사이 1.5초 쉬기, 봇임을 밝히는 User-Agent, 403과 429가 오면 멈추고 다시 시도하지 않는다
- 로그인 영역, 개인정보(리뷰 작성자 등)는 모으지 않는다. 상품 이름, 가격, 리뷰 수, 링크만

## "할인"의 기준
- 할인율 = (소비자가 - 판매가) / 소비자가. 모든 곳에 같은 기준
- 쿠폰가는 할인율에 넣지 않고 `note`에 "쿠폰 적용 시 N원"으로 적는다 → TOP 5에서 확인 필요 표시
- 그릇114, 소로이는 소비자가를 보여 주지 않는다 → 할인율 "모름"(빈칸). 0%로 치지 않고 평균에서 뺀다
- 카테고리는 쇼핑몰마다 이름이 달라 상품 이름의 낱말로 나눈다 (`common.py`의 `CATEGORY_WORDS`)

## 다시 수집
```bash
pip install -r discount-radar/sources/shin/requirements-crawl.txt
python -m playwright install chromium
cd discount-radar/sources/shin && python crawl_cafe24.py && python crawl_29cm.py
```
