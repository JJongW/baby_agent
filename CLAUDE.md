# baby_agent — Claude가 먼저 읽는 공통 규칙

이 레포는 5명(신 PO, 노 개발, 윤 개발, 권 디자인, 어 디자인)이 각자 만든 Claude Code 에이전트 모음이다.
사람과 폴더 대응, 폴더 지도는 [README.md](README.md). 이 파일은 모두에게 똑같이 배포된다. 개인 규칙은 `members/<사람>/CLAUDE.md`에 쓴다.

## 지금 누구의 일인가
- 작업을 시작하기 전에 이번 작업이 누구 폴더의 일인지 정한다. 사용자가 말하지 않았으면 `git config user.name`과 브랜치 이름(`<사람>/...`)으로 짐작하고, 그래도 모르면 묻는다
- 고치는 곳은 그 사람의 것만: `.claude/agents/<사람>/`, `.claude/skills/<사람>-*/`, `members/<사람>/`
- 다른 사람 폴더와 공통 파일(`README.md`, `CLAUDE.md`, `docs/`, `scripts/`, `.github/`)은 사용자가 분명히 요청했을 때만 고치고, PR 설명에 왜 고쳤는지 적는다

## 조명 브랜드 페이지 (`lighting-brand/`)
이 폴더 일이면 먼저 [lighting-brand/CLAUDE.md](lighting-brand/CLAUDE.md)를 읽고 따른다. 그 폴더 일은 위의 `members/<사람>/` 규칙 대신 그 파일의 페이지 폴더 규칙을 쓴다.

## 이름 규칙 (`scripts/check.sh`가 검사)
- 에이전트: `.claude/agents/<사람>/<사람>-<이름>.md`, frontmatter `name`은 파일 이름과 같게, `description`은 꼭 쓴다
- 스킬: `.claude/skills/<사람>-<이름>/SKILL.md`, frontmatter `name`은 폴더 이름과 같게
- `<이름>`은 영어 소문자, 숫자, `-`만 쓴다. 폴더와 파일 이름에 한글을 쓰지 않는다
- 에이전트를 만들거나 바꾸면 소개 카드 `members/<사람>/cards/<같은 이름>.md`도 같이 쓴다 (양식: `docs/agent-card-template.md`)

## 일하는 순서
이슈 → 브랜치 `<사람>/<종류>-<주제>` → 작업 → `bash scripts/check.sh` → PR → 리뷰 1명 승인 → squash 머지.
`main`에 바로 push하지 않는다. 자세히는 [docs/rules.md](docs/rules.md).

## 에이전트 파일을 쓸 때
- 에이전트 하나는 일 하나만 한다. 설명(`description`)에 언제 부르는지 적는다 (Claude가 이걸 보고 고른다)
- 비밀 값(API 키, 토큰), 회사 내부 자료, 개인 정보를 파일에 넣지 않는다
- `tools`로 꼭 필요한 도구만 연다. 읽기만 하는 에이전트는 쓰기 도구를 주지 않는다

## 다 됐다고 말하기 전에
`bash scripts/check.sh`를 실제로 돌리고 결과를 말한다. 안 돌렸으면 안 돌렸다고 말한다.
