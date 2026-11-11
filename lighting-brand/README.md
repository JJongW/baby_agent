# 조명 브랜드 페이지

가구 중 조명을 파는 브랜드의 소개 사이트. 페이지 다섯 개를 다섯 명이 하나씩 맡는다.
이 폴더는 `discount-radar/`와 따로 **Render**에 배포한다 (Render의 Root Directory = `lighting-brand`).

## 누가 무엇을 맡나

| 페이지 | 폴더 | 맡은 사람 | 레포 폴더 이름 |
| --- | --- | --- | --- |
| 홈 | `pages/home/` | 상경 | `eo` (어) |
| 제품 | `pages/product/` | 정연 | `yoon` (윤) |
| FAQ | `pages/faq/` | 신 | `shin` (신) |
| 스토리 | `pages/story/` | 지혜 | `jihye` (깃허브 `Jihye-kr`) |
| 매거진 | `pages/magazine/` | 지영 | `kwon` (권) |

각자 자기 페이지 폴더 안에서만 작업하고, 자기 브랜치(`<사람>/<종류>-<주제>`)로 PR을 올린다.
공통 틀(메뉴, 색, 글꼴, 배포 설정)은 신이 맞춘다. 기획은 [PRD.md](PRD.md).

## 폴더 지도

```
lighting-brand/
  index.html              첫 주소(/)로 오면 홈으로 보낸다
  common/
    style.css             공통 스타일. 색, 글꼴, 여백 값은 맨 위 :root 에만 있다 (디자인: 어)
    layout.js             머리 메뉴와 바닥을 모든 페이지에 똑같이 그린다. 메뉴를 바꾸려면 PAGES만 고친다
    products.js           제품 목록과 제품 카드 모양. 홈과 제품 페이지가 같이 쓴다 (담당: 윤, 지금은 가짜 값)
  images/                 공통 사진 (제품 켜짐, 꺼짐 한 쌍, 분위기 컷). 출처와 쓰는 법은 images/README.md
  CLAUDE.md               Claude가 먼저 읽는 규칙 (시작할 때 "본인은 누구신가요?"를 묻고, 내 폴더만 고친다)
  pages/<페이지>/
    index.html            각자 맡은 페이지
    CLAUDE.md             이 페이지에서 만들 것 (Claude가 읽는다)
    showcase.md           작품 게시. 다 만들면 채워 PR에 같이 올린다
```

## 내 페이지 만드는 법
0. 최신 main을 받고 Claude Code를 연다. Claude가 "본인은 누구신가요?"라고 물으면 이름을 답한다
1. `pages/<내 페이지>/index.html`을 연다. 회색 점선 상자(`.todo`)가 PRD에 적힌 만들 곳이다. 채우면 상자를 지운다
2. 사진 자리는 `<div class="ph">`. 사진이 생기면 `<img>`로 바꾼다 (사진 한 장 300KB 이하, 출처 기록)
3. 내 페이지에만 필요한 모양은 그 파일 `<style>` 안에 쓴다. 색과 글꼴은 `var(--ink)`, `var(--hanji)`처럼 공통 값만 쓴다. 값과 쓰는 규칙은 상경의 [디자인 규칙](pages/home/DESIGN.md)
4. `<header data-site-header>`, `<footer data-site-footer>`, 맨 아래 `<script>` 두 줄은 지우지 않는다 (메뉴와 바닥이 사라진다)
5. 공통 파일(`common/`)을 바꾸고 싶으면 신에게 말한다. 모든 페이지가 같이 바뀐다

## 내 컴퓨터에서 보기
```bash
cd lighting-brand && python3 -m http.server 3320
```
브라우저에서 `http://localhost:3320` 을 연다. (파일을 더블클릭해 열어도 대부분 보인다)

## Render 배포 (신)
- New → **Static Site** → 저장소 `JJongW/baby_agent`, 브랜치 `main`
- Root Directory: `lighting-brand`
- Build Command: 비움 (빌드 없음), Publish Directory: `.`
- main에 머지되면 자동으로 다시 배포된다

## 아직 정할 것
- 공통 메뉴와 디자인 규칙
