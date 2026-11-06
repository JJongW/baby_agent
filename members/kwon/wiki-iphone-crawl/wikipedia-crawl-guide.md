# 위키백과(ko.wikipedia.org) 크롤링 가이드

> 확인일: 2026-11-06 · 대상: 한국어 위키백과 아이폰 관련 문서
> 이 문서는 법률 자문이 아닙니다. 규칙은 바뀔 수 있으니 수집 전에 원문을 다시 확인하세요.

## 1. 한 줄 결론

**조건을 지키면 수집해도 됩니다.** 신분을 밝히고(User-Agent), 천천히, 일반 문서 주소(`/wiki/문서이름`)로만 접근하고, 가져온 내용에는 출처를 표시하면 됩니다.

> 비교: Apple 사이트(`apple.com/kr/iphone`)는 robots.txt가 막지 않아도 **이용약관이 자동 수집(로봇, 스크래핑)을 명시적으로 금지**해서 하지 않기로 했습니다.

## 2. 규칙 세 가지 문서

크롤링에는 서로 다른 세 종류의 규칙이 있습니다. 쉬운 비유로 정리하면 이렇습니다.

| 종류 | 비유 | 위키백과의 경우 |
|---|---|---|
| robots.txt | 문 앞의 출입 안내문 | 일반 문서는 열려 있음 |
| 이용약관 | 사이트와 맺는 계약서 | 서비스를 방해하지만 않으면 자동 사용 허용 |
| 로봇 정책 / API 예절 | 방문 매너 안내서 | 속도, 신분 표시 방법을 구체적으로 안내 |

### 2-1. robots.txt (`https://ko.wikipedia.org/robots.txt`)

| 구분 | 경로 | 설명 |
|---|---|---|
| ✅ 가능 | `/wiki/문서이름` (일반 문서) | 막혀 있지 않음 |
| ❌ 금지 | `/wiki/특수:...`, `/wiki/Special:...` | 검색 등 특수 기능 페이지 |
| ❌ 금지 | `/trap/` | 로봇을 걸러내는 함정 경로 |
| ❌ 금지 | `/w/` (api.php, index.php 포함) | 일부 예외만 허용 |
| ❌ 금지 | `/api/` | 문서 설명 페이지만 예외 |
| ❌ 로봇 차단 | wget, HTTrack, WebCopier 등 | 사이트 통째 복사 도구 |
| 간격 지정 | 일반 로봇은 없음 | SemrushBot만 5초 |

### 2-2. 이용약관 (`https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use`)

| 구분 | 내용 |
|---|---|
| ❌ 금지 | 서비스를 방해하거나 해가 되는 자동 사용 |
| ❌ 금지 | API나 사이트에 과도한 부담을 주는 것, 트래픽을 쏟아붓는 것 |
| ❌ 금지 | 비공개 영역 접근, 보안 취약점 점검 |
| ✅ 허용 | 내용 재사용 (텍스트는 CC BY-SA 4.0 라이선스) |
| ⚠️ 조건 | 출처 표시: 문서 링크(URL)로 표시 가능 |
| ⚠️ 조건 | 수정했다면 수정했다고 표시 |
| ⚠️ 조건 | 가공한 결과를 공개할 때는 같은 라이선스(ShareAlike) |

### 2-3. 로봇 정책 (`https://wikitech.wikimedia.org/wiki/Robot_policy`)

| 항목 | 규칙 |
|---|---|
| 권장 방식 | `/wiki/문서이름` 형식으로, 쿼리 파라미터 없이 요청 |
| 속도 한도(웹 문서) | 평균 초당 20회 미만, 동시 요청 10개 미만 |
| 속도 한도(REST API, 비로그인) | 동시 3개, 초당 5회 미만 |
| 속도 한도(Action API, 비로그인) | 동시 1개, 초당 5회 미만, 1초 넘게 걸린 요청 뒤에는 5초 대기 |
| 신분 표시 | User-Agent에 이름과 연락처 필수 |
| 압축 | `Accept-Encoding: gzip` 사용 |
| 429 응답 | `Retry-After` 시간만큼 기다림 |
| 금지 | `oldid`, `curid` 파라미터 사용 |
| 대량 수집 | 위키백과가 제공하는 덤프 파일 사용 권장 |
| 위반 시 | 속도 제한, 심하면 차단 |

### 2-4. API 예절 (`https://www.mediawiki.org/wiki/API:Etiquette`)

- 요청은 **병렬이 아니라 차례대로(직렬)** 보내기
- 여러 제목은 `|`로 묶어서 한 번에 요청하기
- 받은 데이터는 **캐시(저장)해서 재사용**하기
- 설명 있는 User-Agent를 쓰고, 브라우저 것을 그대로 복사하지 않기
- 대량 다운로드는 API 대신 덤프 파일 사용

### 2-5. User-Agent 정책 (`https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy`)

- 모든 요청에 **설명이 있는 User-Agent**가 필요합니다.
- 형식 예시: `CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org) generic-library/0.0`
- 이름에 `bot`을 넣는 것을 권장합니다.
- `python-requests/...`, `curl` 같은 **기본값은 403으로 차단될 수 있습니다.**

## 3. 이번 프로젝트에서 지킨 방법

| 규칙 | 우리가 한 일 |
|---|---|
| 일반 문서 주소만 사용 | `/wiki/문서이름` 8개만 요청 (API 사용 안 함) |
| User-Agent | `IphoneCrawlPracticeBot/0.1 (연락처) python-requests` |
| 천천히 | 모델 문서는 한 번에 하나씩, 3초 간격 |
| 직렬 요청 | 반복문으로 차례대로, 동시 요청 없음 |
| gzip | `Accept-Encoding: gzip` 헤더 |
| 캐시(저장) | 받은 HTML을 `data\`에 저장, 다시 요청하지 않음 |
| 429/503 | 받으면 즉시 멈춤 |
| 출처 표시 | CSV 모든 줄에 출처 URL, 수집일, 라이선스 |

총 요청 횟수는 **8번**입니다.

## 4. 결과물

| 파일 | 내용 |
|---|---|
| `step1_download.py` | 메인 문서 1개 저장 |
| `step2_download_models.py` | 모델 문서 7개 저장 (3초 간격) |
| `step3_parse.py` | 저장된 HTML에서 값을 뽑아 CSV 생성 (요청 없음) |
| `data/` | 받은 원본 HTML 8개. **이 저장소에는 올리지 않음(.gitignore).** `step1`, `step2`를 실행하면 다시 생김 |
| `iphone_models.csv` | 결과 (모델명, 출시일, 화면 크기, 칩셋, 출시 시 iOS, 출시 가격 등) |

### 수집 범위와 한계

- 요청한 16개 중 **12개만** 위키백과에서 찾았습니다.
- **정보 없음 4개:** 아이폰 17(기본형), 18 프로, 18 프로 맥스, 듀오. 해당 문서를 찾지 못했습니다.
- **"지원하는 iOS 버전"은 "출시 시 iOS"입니다.** 위키백과 문서에 현재 지원 최고 버전이 없습니다.
- **가격은 5개 모델만** 있습니다(16, 16 플러스, 16 프로, 16 프로 맥스, 16e). 미국 달러 출시 시작가입니다. 최근 모델의 추정 가격은 문서에 없어서 비워뒀습니다.
- 16 시리즈 출시일은 발표일(9월 9일)이 아닌 **판매 시작일(9월 20일)**로 통일했습니다.

## 5. 출처 표시 문구 (결과물을 공유할 때 붙이기)

> **출처:** 위키백과 「아이폰」 관련 문서 (https://ko.wikipedia.org/wiki/IPhone 외 모델별 문서), 수집일 2026-11-06
> **라이선스:** CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/deed.ko)
> **변경 사항:** 정보 상자의 값을 추출하여 표로 정리함

가공한 표를 공개할 때는 **같은 라이선스(CC BY-SA 4.0)**를 붙여야 합니다.

## 6. 하지 말아야 할 것

- wget, HTTrack 같은 사이트 통째 복사 도구 사용
- 위키백과 전체를 긁어오기 (필요하면 공식 덤프 파일 사용)
- 요청 속도 조절 없이 반복문 돌리기, 병렬 요청
- `oldid`, `curid` 파라미터 사용
- 출처 없이 내 글처럼 올리기
- `/w/`, `/api/`, `/wiki/특수:` 경로 접근
- User-Agent를 기본값(`python-requests`)이나 브라우저 것으로 보내기

## 7. 확인이 덜 된 부분

- 위 규칙은 문서를 요약해서 읽어오는 도구로 확인했습니다. 원문의 세부 표현은 다를 수 있습니다.
- "요청 사이 3초"는 **공식 수치가 아니라 이번 프로젝트의 안전 기준**입니다. 공식 한도는 이보다 훨씬 넉넉합니다.
- 이번에는 일반 문서 방식만 썼고, API로 수집하는 방법은 직접 해보지 않았습니다.
- 대량 수집이나 반복 실행을 할 때는 연락처를 User-Agent에 넣고(환경변수 `CONTACT`), 위 원문 문서를 다시 읽어보세요.

## 8. 원문 링크

- robots.txt: https://ko.wikipedia.org/robots.txt
- 이용약관: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use
- 로봇 정책: https://wikitech.wikimedia.org/wiki/Robot_policy
- API 예절: https://www.mediawiki.org/wiki/API:Etiquette
- User-Agent 정책: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
