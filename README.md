# baby_agent

PO, 개발, 디자인 직군이 각자 만든 Claude Code 에이전트를 한 레포에 모은다.
레포를 받아 Claude Code로 열면 모두의 에이전트가 바로 인식된다.

## 누가 무엇을 맡나

| 폴더 이름 | 사람 | 직군 | 에이전트 이름 앞에 붙이는 말 |
| --- | --- | --- | --- |
| `shin` | 신 | PO | `shin-` |
| `noh` | 노 | 개발 | `noh-` |
| `yoon` | 윤 | 개발 | `yoon-` |
| `kwon` | 권 | 디자인 | `kwon-` |
| `eo` | 어 | 디자인 | `eo-` |

폴더 이름은 영어로 쓴다. 한글 폴더 이름은 macOS와 Windows, git 사이에서 글자가 다르게 저장되어 같은 폴더가 둘로 갈라질 수 있다.

## 폴더 지도

```
.claude/
  agents/<사람>/<사람>-<이름>.md      에이전트 본체 (Claude Code가 자동으로 읽는 곳)
  skills/<사람>-<이름>/SKILL.md      스킬 (있을 때만)
members/<사람>/
  README.md                         이 사람의 에이전트 목록
  CLAUDE.md                         이 폴더에서 일할 때 Claude가 지킬 것
  cards/<사람>-<이름>.md             에이전트 소개 카드 (누가, 왜, 근거, 사용법)
docs/
  rules.md                          브랜치, 커밋, PR, 머지 규칙
  agent-card-template.md            소개 카드 양식
scripts/check.sh                    이름 규칙 검사 (CI도 같은 스크립트를 돌린다)
```

에이전트 파일은 `members/` 안이 아니라 `.claude/agents/<사람>/`에 둔다.
Claude Code는 레포 루트의 `.claude/agents/` 아래만 읽고, `members/<사람>/.claude/`처럼 안쪽 폴더는 읽지 않는다 (2026-11-05 Claude Code 2.1.318로 확인).

## 처음 받았을 때

```bash
git clone https://github.com/JJongW/baby_agent.git
cd baby_agent
claude
```

Claude Code 안에서 `/agents`를 열면 모두의 에이전트가 보인다. 다른 사람이 새 에이전트를 올리면 `git pull`만 받으면 된다.
에이전트를 부를 때는 이름으로 부른다. 예: "shin-prd-reviewer로 이 PRD 봐줘"

## 내 에이전트를 올리는 법

1. `main`에서 브랜치를 딴다: `<사람>/<종류>-<주제>` (예: `noh/feat-api-reviewer`)
2. `.claude/agents/<사람>/<사람>-<이름>.md`에 에이전트를 만든다. 파일 이름과 frontmatter의 `name`이 같아야 한다
3. `docs/agent-card-template.md`를 복사해 `members/<사람>/cards/<사람>-<이름>.md`에 소개 카드를 쓴다
4. `members/<사람>/README.md` 목록에 한 줄 추가한다
5. `bash scripts/check.sh`가 통과하면 PR을 올린다. 자세한 규칙은 [docs/rules.md](docs/rules.md)
