# 할인 레이더 — 도서 (카카오 책 검색 API)

> **한 줄 목표:** 도서는 **어떤 분야가 할인을 가장 많이 하는가**에 답한다.

공통 앱(`discount-radar/app.py`, `radar.py`)의 약속을 따른다. 약속 원문은 [../README.md](../README.md).
이 폴더가 하는 일은 **카카오에서 도서 가격을 가져와 공통 앱에 넘기는 것까지**다. 할인율 계산과 화면은 공통 앱이 한다.

---

## 1. 정하는 4가지

| 항목 | 결정 |
|---|---|
| 수집처 | 카카오(Daum) 책 검색 API — `https://dapi.kakao.com/v3/search/book` |
| 수집 방법 | API (REST API 키 인증) |
| 품목 · 범위 | 도서 5개 분야 × 최대 10페이지 × 페이지당 10권 = 분야당 최대 100권 |
| 할인 기준 | **정가 대비** — 공통 앱이 `(original_price − price) ÷ original_price × 100`으로 계산 |

---

## 2. 공통 앱에 넘기는 데이터

### 카카오 응답 → CSV 열 (공통 앱 표준 열)

| CSV 열 | 카카오 응답에서 | 비고 |
|---|---|---|
| `name` | `title` | |
| `category` | 검색한 분야 이름 (예: 경제) | 카카오 응답에는 분야 필드가 없어서 검색어를 쓴다 |
| `price` | `sale_price` | ⚠️ 공통 앱의 `price`는 **지금 파는 값(판매가)** 이다 |
| `original_price` | `price` | ⚠️ 정가는 `original_price`에 넣는다 |
| `review_count` | (없음) | 카카오가 주지 않으므로 빈칸 |
| `url` | `url` | |
| `note` | (빈칸) | 값이 있으면 공통 앱이 "확인 필요"로 표시하므로 비워 둔다 |

- 할인율(`discount_rate`)과 "확인 필요"(`caution`)는 **CSV에 넣지 않는다.** 공통 앱 `radar.py`가 모든 조원에게 똑같이 계산한다.
- 중복 제거용 `isbn`, 표지 `thumbnail`은 CSV에 같이 둬도 된다 (공통 앱은 모르는 열을 무시한다).

### 수집할 때 거르는 것
- `sale_price`가 `-1`이거나 비어 있는 책 (판매가 없음) → 뺀다.
- `price`(정가)가 0이거나 비어 있는 책 → 뺀다.
- 같은 ISBN이 여러 번 나오면 하나만 남긴다.

---

## 3. 기능 3개 (공통 앱이 그대로 돌림)

| # | 기능 | 공통 앱 동작 | 도서에서 보이는 모습 |
|---|---|---|---|
| 1 | 카테고리별 할인율 | 분야별 평균 할인율 · 상품 수, 할인율 높은 순 | 5개 분야 비교 (**질문의 답**) |
| 2 | 예산으로 고르기 | 판매가 ≤ 예산(+분야) 중 할인율 높은 순 3권 | 그대로 |
| 3 | 할인 TOP 5 | 할인율 높은 순 5권, `caution`에 확인 필요 이유 | 리뷰 수 · 조건이 없어서 도서는 ⚠️가 뜨지 않는다 |

화면은 공통 앱 그대로 시연한다.

---

## 4. 파일 구성

```
discount-radar/sources/books/
├── README.md          # 이 기획서
├── kakao_books.py     # 카카오 호출. 직접 실행하면 data/books.csv 저장, adapter.py도 이걸 부른다
├── data/books.csv     # 예비 데이터 (카카오 호출이 안 될 때 공통 앱이 읽는다)
├── adapter.py         # 공통 앱 연결: TITLE, SOURCE, METHOD, load()
├── .gitignore         # .env를 git에서 뺀다
└── .env               # 실제 키 — ❌ git에 올리지 않기
```

### adapter.py 동작
1. 키가 있으면 앱이 켜질 때 카카오를 바로 불러 최신 가격을 쓴다.
2. 키가 없거나 호출이 실패하면 `data/books.csv`(예비 데이터)를 읽는다.
3. 둘 다 없으면 오류를 낸다. 공통 앱은 사이드바에 "불러오지 못함"으로 보여 주고 멈추지 않는다.
   (빈 표를 돌려주면 공통 앱이 1등 분야를 뽑다가 멈추므로 빈 표는 돌려주지 않는다.)

배포 사이트에서도 카카오를 바로 부르려면 배포 서버에 `KAKAO_REST_API_KEY`를 넣어야 한다. 넣지 않으면 예비 데이터로 돈다.

---

## 5. 실행 방법

1. 카카오 디벨로퍼스 → 내 앱 → **[앱] > [플랫폼 키] > REST API 키** 복사
2. `discount-radar/sources/books/.env` 파일에 `KAKAO_REST_API_KEY=복사한키` 한 줄 작성 (띄어쓰기 · 따옴표 없이)
3. 수집 코드는 설치할 것 없음 (파이썬 기본 기능만 씀). 앱을 볼 때만 `pip install -r discount-radar/requirements.txt`
4. `python discount-radar/sources/books/kakao_books.py` → `data/books.csv` 생성
5. `streamlit run discount-radar/app.py` → 사이드바에서 "도서" 선택

### 에러가 나면
| 증상 | 원인 | 해결 |
|---|---|---|
| 401 | 키가 틀림 / REST API 키가 아닌 다른 키 | 플랫폼 키 화면에서 **REST API 키** 다시 복사 |
| 403 | 권한 · 허용 IP 설정 문제 | 플랫폼 키의 "호출 허용 IP" 설정 확인 |
| 키 없음 메시지 | `.env` 위치 · 이름 오류 | `kakao_books.py`와 같은 폴더인지 확인 |
| 앱 사이드바에 "도서"가 없음 | `adapter.py`가 없거나 오류 | 폴더 안에 `adapter.py`가 있는지 확인 |
| 할인율이 전부 0% | `price`와 `original_price`를 반대로 넣음 | 2장 표대로 판매가 → `price`, 정가 → `original_price` |

---

## 6. 한계 (발표 때 먼저 말하기)

- **도서정가제:** 새 책은 법으로 할인 폭이 정가의 10% 안팎으로 묶여 있다. 분야별 평균 할인율이 거의 같게 나올 수 있다 → **먼저 한 분야만 수집해서 분포를 확인**하고, 비슷하면 그 자체를 발표 포인트로 쓴다 (다른 조 품목과 비교).
- 카카오 책 검색에는 분야 필드가 없어 **검색어를 분야로 사용** → 서점의 실제 분야 분류와 다를 수 있음.
- 검색 결과 기준이라 해당 분야의 **전체 도서가 아닌 일부 표본**.
- 수집 시점의 가격 → 가격은 바뀔 수 있으므로 수집일을 남긴다.

---

## 7. 내 역할 체크리스트

- [ ] **한 분야 먼저 수집:** 할인율 분포 확인 (도서정가제 영향)
- [ ] **수집 코드 + adapter.py:** `kakao_books.py`, `data/books.csv`, `adapter.py`
- [ ] **단계별 수집 화면 공유:** ① 키 발급 화면 ② 실행 로그 ③ books.csv ④ 공통 앱 화면 (키는 가리기)
- [ ] **PR:** `.env`가 포함되지 않았는지 확인 후 제출

---

## 8. Plan B

- 카카오 호출이 실패하면 **미리 저장한 `data/books.csv`**를 자동으로 읽는다 (와이파이 · 쿼터 문제 대비). 시연 전에 `kakao_books.py`로 한 번 새로 저장해 둔다.
- 키 문제로 수집이 막히면 DummyJSON(키 불필요) 데이터를 같은 열 형식으로 저장해 화면을 먼저 확인하고, 나중에 CSV만 교체.

---

## 9. 발표 스토리 (18:20 시연)

1. 할인 기준은 **정가 대비**
2. 결과: **○○ 분야가 할인을 가장 많이 했다** (또는: 도서정가제 때문에 분야별 차이가 작았다)
3. 한계: 분야 = 검색어, 일부 표본
4. 다른 조 품목과 비교하면 도서의 할인 폭은 어떤가?

---

## 참고 출처

- 카카오 Daum 검색 API (책 검색): https://developers.kakao.com/docs/ko/daum-search/dev-guide
- 카카오 앱 키(플랫폼 키) 안내: https://developers.kakao.com/docs/latest/ko/app-setting/app
- 카카오 REST API 테스트 도구: https://developers.kakao.com/docs/latest/ko/tool/rest-api-test
- 공통 앱 약속: `discount-radar/sources/README.md`, `discount-radar/radar.py` (브랜치 `shin/feat-discount-radar`)
