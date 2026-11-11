# ONDO (온도): 종이 조명 브랜드 페이지

대나무 살과 한지로 만드는 가상의 조명 브랜드 **ONDO**의 소개 사이트. 다섯 명이 페이지를 하나씩 맡아 만들었다.
수업 과제라 실제로 판매하지 않는다.

- **사이트:** https://baby-agent.onrender.com
- **기획:** [PRD.md](PRD.md)
- **디자인 규칙:** [pages/home/DESIGN.md](pages/home/DESIGN.md) (상경, 시안 v3)
- **철학:** 와비사비. 디자인은 일본의 덜어내는 디자인. 장식, 그림자, 색, 문구를 줄이고 빈 곳을 넉넉히 둔다

## 페이지와 맡은 사람

| 페이지 | 주소 | 맡은 사람 | 브랜치 앞 | 들어 있는 것 |
| --- | --- | --- | --- | --- |
| 홈 | `/pages/` | 상경 | `eo` | 불 켜진 조명 첫 화면(디졸브), 대표 제품 3개, 스토리 맛보기, 최신 매거진 글 3편 |
| 제품 | `/pages/product/` | 정연 | `yoon` | 제품 4개(T-01, T-02, S-01, P-02), 모든 카드의 불을 한 번에 켜고 끄는 벽 스위치 |
| 스토리 | `/pages/story/` | 지혜 | `jihye` (깃허브 `Jihye-kr`) | 첫 화면 불 켜짐, 이어지는 세 장면, 기록 사진 넘겨 보기, 3D로 지어지는 등 |
| 매거진 | `/pages/magazine/` | 지영 | `kwon` | 글 목록과 글 세 편(공간 꾸미기, 인터뷰, 관리 팁) |
| FAQ | `/pages/faq/` | 신 (PO) | `shin` | 주제 4개, 질문 16개, 낱말 검색, 한 번에 하나만 펼쳐지는 질문 |

신(PO)은 공통 틀(메뉴, 바닥, 색과 글꼴 반영, 아이콘, 배포)도 맡는다. 상경은 사이트 전체 디자인 규칙을 정한다.

## 폴더 지도

```
lighting-brand/
  index.html              첫 주소(/)로 오면 홈(/pages/)으로 보낸다
  favicon.ico             사이트 아이콘 (밤색 바탕에 매달린 한지 등, 16, 32, 48px). 각 페이지 <head>에 적는다
  favicon.svg             아이콘 원본 그림
  apple-touch-icon.png    휴대폰 홈 화면 아이콘 (180px)
  PRD.md                  기획 (무엇을 왜 만드나, 페이지별 기능)
  CLAUDE.md               Claude가 먼저 읽는 규칙 ("본인은 누구신가요?"를 묻고, 그 사람 폴더만 고친다)
  common/
    style.css             공통 스타일. 색, 글꼴, 여백 값(토큰)은 맨 위 :root 에만 있다
    layout.js             머리 메뉴와 바닥을 모든 페이지에 똑같이 그린다. 메뉴는 PAGES만 고친다
    products.js           제품 목록과 제품 카드. 홈과 제품 페이지가 같이 쓴다 (정연)
  images/                 공통 사진: products/ 제품 켜짐, 꺼짐 한 쌍, concept/ 분위기 컷. 규칙은 images/README.md
  pages/
    index.html            홈 화면 (상경)
    home/                 홈 문서: DESIGN.md(디자인 규칙), showcase.md, 첫 화면 사진. index.html은 /pages/로 보낸다
    product/              제품
    story/                스토리. images/에 기록 사진 (출처는 그 페이지 바닥과 showcase.md)
    magazine/             매거진. article-1~3.html이 글, MAGAZINE.md가 글 쓰는 규칙
    faq/                  FAQ
    <페이지>/CLAUDE.md    그 페이지에서 만들 것 (Claude가 읽는다)
    <페이지>/showcase.md  작품 게시
```

## 디자인 한눈에

값은 모두 `common/style.css`의 토큰만 쓴다. 새 색이나 새 간격을 만들지 않는다. 자세히는 [DESIGN.md](pages/home/DESIGN.md).

| 무엇 | 값 |
| --- | --- |
| 색 6개 | `--hanji` 바탕, `--hanji-deep` 사진 자리, `--ink` 글자, `--ink-soft` 보조 글자, `--line` 장식 선, `--earth` 유일한 강조색 (한 화면에 한 곳만) |
| 글꼴 | 로고, 제목, 메뉴는 마루 부리. 본문은 IBM Plex Sans KR |
| 여백 | `--space-1`~`--space-5` (8, 16, 24, 40, 64px), 구역 사이 `--space-section` |
| 모양 | 모서리 0, 화면 폭 기준 640px, 960px 두 개 |
| 초점 | 키보드로 움직일 때 1px 먹색 테두리. 지우지 않는다 (지울 땐 다른 표시로 바꾼다) |
| 사진 | 제품 카드는 4:5. 켜짐, 꺼짐 사진 한 쌍을 겹쳐 켜짐 사진 투명도만 바꾼다. 한 장 300KB 이하 |

사진은 AI로 만든 이미지나 무료 사진만 쓰고 출처를 `showcase.md`에 적는다. 예외로 스토리 페이지는 참고한 브랜드의 기록 사진을 쓰고, 그 페이지 바닥에 출처를 적는다.

## 일하는 순서

1. 최신 main을 받는다: `git switch main && git pull origin main`
2. 이슈를 만든다 (무엇을, 왜, 확인할 항목)
3. 브랜치를 만든다: `<브랜치 앞>/<종류>-lighting-<주제>` (예: `shin/fix-lighting-faq-qa`)
4. 내 페이지 폴더 안에서만 고친다. 공통 파일(`common/`, `PRD.md`, 이 파일)은 신에게 요청한다
5. 내 컴퓨터에서 띄워 **실제 브라우저로** 확인한다 (데스크톱, 휴대폰 375px)
6. 레포 맨 위에서 `bash scripts/check.sh`
7. PR 직전에 main을 한 번 더 받아 겹치는 게 없는지 본다
8. PR에 이슈를 잇고(`Closes #번호`), 고친 파일과 확인한 것을 적는다. 리뷰 1명 승인 뒤 squash 머지

내 컴퓨터에서 보기:
```bash
cd lighting-brand && python3 -m http.server 3320
```
브라우저에서 `http://localhost:3320` 을 연다.

## 만들면서 배운 것 (같은 실수 안 하기)

- **"열린다"와 "보인다"는 다르다.** 파일이 200으로 열려도 브라우저가 못 그릴 수 있다. 화면에 보이는 것은 실제 브라우저에서 그려지는지까지 본다
- **SVG 주석 안에 하이픈 두 개(`--`)를 쓰지 않는다.** `--ink` 같은 토큰 이름을 SVG 주석에 적었다가 파일 전체가 깨져 아이콘이 안 떴다
- **아이콘을 바꾸면 주소 끝 숫자를 올린다** (`favicon.ico?v=3` → `?v=4`). 브라우저가 옛 아이콘을 오래 기억한다
- **아이콘과 `<link>`는 HTML `<head>`에 직접 적는다.** 자바스크립트로 붙이면 브라우저가 늦게 알아챈다
- **`display: grid`를 준 요소는 `[hidden]`이 안 먹는다.** `.이름[hidden] { display: none; }`을 같이 쓴다
- **사진 비율을 맞춘다.** 비율이 다른 사진을 `object-fit: cover`로 넣으면 조명이 잘린다
- **시크릿 창도 열려 있는 시크릿 창끼리 캐시를 같이 쓴다.** 캐시 없이 보려면 시크릿 창을 모두 닫고 새로 연다

## Render 배포 (신)

- **Static Site**, 저장소 `JJongW/baby_agent`, 브랜치 `main`
- Root Directory `lighting-brand`, Build Command 비움, Publish Directory `.`
- main에 머지되면 1~2분 안에 자동으로 다시 배포된다

## 다음에 할 것

- 제품: 종류 필터(테이블, 스탠드, 펜던트), 가격 정렬, 제품 9~12개로 늘리기 (사진: T-03, S-02, S-03, P-01, P-03)
- 제품 상세 화면, 영어 버전, 매거진 글 늘리기 (PRD 8)
- `common/style.css`의 옛 토큰 이름(`--paper`, `--paper-deep`, `--space`)은 다섯 페이지가 모두 새 이름으로 바뀌면 지운다
- 1차에서 하지 않는 것: 결제, 장바구니, 로그인, 관리자 화면
