# team — 7조 조 과제 틀과 도구

> **처음 받았으면 [START.html](START.html) 부터** (Mac `open team/START.html`, Windows `start team\START.html`). 10분 따라 하면 준비 끝.

서비스를 만들기 전에, 조원 5명이 같은 MCP 세트와 같은 규칙으로 일하기 위한 폴더.
터미널에서 `claude` 를 열면 "누구세요?"를 묻고, `shin-team-orchestrator` 가 github, notion, team 을 같이 읽어 진행 현황과 내 다음 할 일을 알려 준다.
할 일을 시작하거나 끝내면 Claude 에게 말만 하면 된다. 노션 할 일 DB 의 **내 줄**을 Claude 가 맞춰 준다 (먼저 보여 주고).

**구조도**: [docs/architecture.html](docs/architecture.html) (내려받아 브라우저로 열기). 왜 이렇게 만들었는지는 [docs/mcp-design.md](docs/mcp-design.md).

| 파일 | 뜻 |
| --- | --- |
| `AGENTS.md` | 조 규칙 원본. 루트 `CLAUDE.md` 가 불러온다 |
| `members.csv` | 조원 명단 (이름, 폴더, 직군, 깃허브, 조 과제 역할) |
| `tasks.csv` | 할 일 배정 (번호, 할 일, 직군, 담당자, 마감). PO 만 PR 로. `상태` 열은 노션을 못 읽을 때 쓰는 처음 값 |
| `roles/<폴더>.md` | 사람별 오늘 순서, 바로 쓸 말, 하지 말 것 |
| `docs/` | 회의록, 설계 문서, 노션 보드 설계, 구조도 |
| `START.html` | 처음 받으면 가장 먼저 여는 안내 페이지 (준비, 토큰, MCP 연결, 매일 쓰는 말) |
| `mcp/server.py` | team MCP 서버 (읽기 전용 도구 8개 + 명령 틀 6개) |

| 이름 | 폴더 | 직군 | 조 과제 역할 |
| --- | --- | --- | --- |
| 신 | shin | PO | 조장, 데이터, 노션 (업무 배정) |
| 노 | noh | 개발 | 서버 리뷰, 도전 도구 |
| 윤 | yoon | 개발 | 처음 받기 검증, 데스크톱 연결 |
| 권 | kwon | 디자인 | 규칙, 테스트 3번, 화면 구성안 |
| 어 | eo | 디자인 | 시연, PR 리뷰, 페르소나 |

## 무엇을 어디서 바꾸나
| 무엇 | 원본 | 누가, 어떻게 |
| --- | --- | --- |
| 배정 (번호, 할 일, 담당, 마감) | `team/tasks.csv` | PO 가 고쳐 PR |
| 상태 (할 일 → 진행 중 → 완료) | 노션 할 일 DB | 각자 Claude 에게 "9번 시작했어", "9번 PR 머지됐어" → Claude 가 노션 **내 줄**만 고친다 |
| 이슈, PR | 깃허브 | 이슈는 PO, PR 은 각자 |

세 곳은 **할 일 번호**로 잇는다: `tasks.csv` 번호 = 이슈 제목 앞 `[T번호]` = 노션 할 일 DB `번호`.
team 은 세 곳을 모두 읽어 맞춰 보고, 노션에서 고칠 것을 찾아 준다 (`notion_board`). 고치기는 각자 로그인한 notion MCP 가 한다.

## 처음 받으면 (터미널)
준비물: Claude Code CLI (`claude --version`), Python 3.10 이상 (`python --version`), git

1. 받고, team 서버에 필요한 패키지 깔기 (이미 있으면 `git pull` 만)
   ```bash
   git clone https://github.com/JJongW/baby_agent.git
   cd baby_agent
   pip install -r team/mcp/requirements.txt
   ```
2. 토큰 넣기: **[docs/tokens.md](docs/tokens.md)** 를 처음부터 따라 한다 (만들기, 넣기, 연결, 보안). `GITHUB_PAT` 는 꼭, `NOTION_TOKEN` 은 신에게 받으면
3. 레포 맨 위 폴더에서 `claude` → "이 프로젝트의 MCP 서버를 쓸까요?" 가 나오면 github, notion, team 모두 **허용**
4. 노션 로그인 (notion MCP 는 토큰 대신 로그인): 세션 안에서 `/mcp` → notion → **Authenticate** → 브라우저에서 조 노션 워크스페이스 허용
5. 확인: `/mcp` 에서 셋 다 connected (터미널에서는 `claude mcp list`)
6. 아무 말이나 입력 (예: `시작`) → Claude 가 누구인지 확인하고 내 할 일을 보여 준다

## MCP 는 어떻게 붙나 (CLI)
MCP 서버는 Claude Code 에 "어디에 무엇이 있는지"를 적어 두면 붙는다. 적어 두는 곳(범위)이 셋이다.

| 범위 | 적히는 곳 | 누가 쓰나 | 우리 조 |
| --- | --- | --- | --- |
| project | 레포의 `.mcp.json` | 이 레포를 받은 **조원 모두** | github, notion, team 이 여기 있다. pull 만 받으면 같은 세트 |
| local | 내 PC 설정 (이 폴더에서만) | 나만 | 내 PC 에서만 다르게 돌려야 할 때 (예: `python3`) |
| user | 내 PC 설정 (모든 폴더) | 나만 | 쓰지 않음 |

같은 이름이면 local 이 project 를 덮는다. 그래서 `.mcp.json` 은 그대로 두고 내 PC 에만 바꿀 수 있다.

`.mcp.json` 에 적힌 우리 조 세트:
| 서버 | 종류 | 연결 방법 |
| --- | --- | --- |
| github | 원격 (http) | `https://api.githubcopilot.com/mcp/` + 헤더 `Authorization: Bearer ${GITHUB_PAT}` (환경변수가 그 자리에 들어간다) |
| notion | 원격 (http) | `https://mcp.notion.com/mcp`. 토큰 없이 처음 한 번 로그인 |
| team | 내 PC 에서 실행 (stdio) | `python team/mcp/server.py`. 환경변수 `GITHUB_PAT`, `NOTION_TOKEN` 을 넘겨받는다 (없으면 빈 값) |

자주 쓰는 명령 (레포 맨 위 폴더에서):
| 하고 싶은 것 | 명령 |
| --- | --- |
| 붙은 서버와 상태 보기 | `claude mcp list` |
| 서버 하나 자세히 | `claude mcp get team` |
| 세션 안에서 상태, 로그인, 다시 연결 | `/mcp` |
| 노션 로그인 / 로그아웃 (세션 밖에서) | `claude mcp login notion` / `claude mcp logout notion` |
| 처음 "허용"을 잘못 눌렀을 때 | `claude mcp reset-project-choices` → `claude` 다시 열고 허용 |
| 내 PC 에만 team 을 `python3` 로 | `claude mcp add --scope local team -- python3 team/mcp/server.py` |
| 내 PC 에만 붙인 걸 지우기 | `claude mcp remove team -s local` |
| 조 모두에게 새 서버 붙이기 | `claude mcp add --scope project <이름> ...` 가 `.mcp.json` 을 고친다 → 브랜치에서 PR (토큰 값은 `${이름}` 으로만) |

토큰 값은 `-e KEY=값` 이나 `-H "Authorization: Bearer 값"` 으로 직접 넣지 않는다. 내 PC 설정 파일에 그대로 남는다. 환경변수에 넣고 `${이름}` 으로 가리킨다.
`claude` 를 켠 터미널의 환경변수는 team 서버에 그대로 넘어간다 (11/17 확인).

## 토큰
만들기, 넣기, 어떻게 연결되는지, 보안, 새었을 때: [docs/tokens.md](docs/tokens.md).

## 막히면
| 증상 | 해결 |
| --- | --- |
| team ✗ failed | `pip install -r team/mcp/requirements.txt` → `python team/mcp/server.py` 직접 실행 (멈춰 있으면 정상, Ctrl+C) |
| Mac 에 `python` 이 없음 (`command not found`) | 내 PC 에만: `claude mcp add --scope local team -- python3 team/mcp/server.py` (`.mcp.json` 은 그대로) |
| `pip install` 때 다른 패키지와 버전 충돌 경고 (예: fastapi 와 starlette) | 기본 파이썬에 깔지 말고 전용 가상환경으로: `python3 -m venv ~/.venvs/team-mcp` → `~/.venvs/team-mcp/bin/pip install -r team/mcp/requirements.txt` → 내 PC 에만 `claude mcp add --scope local team -- ~/.venvs/team-mcp/bin/python team/mcp/server.py` (Windows 는 `Scripts\python.exe`) |
| github 401 | `GITHUB_PAT` 가 안 들어감 → `source ~/.zshrc` 또는 터미널 완전히 재시작 후 `claude`. 7일 지났으면 새로 ([docs/tokens.md](docs/tokens.md) 6번) |
| github 403, 레포가 안 보임 | 토큰의 Resource owner, 레포 선택, 협업자 초대 수락 |
| notion "Needs authentication" | `/mcp` → notion → Authenticate, 또는 `claude mcp login notion` |
| team 이 "NOTION_TOKEN 이 필요해요" | 토큰이 없어도 일은 된다 (Claude 가 notion MCP 로 읽는다). 넣으려면 [docs/tokens.md](docs/tokens.md) |
| team 이 "HTTP Error 401" (노션) | 토큰 값이 틀렸거나 다시 발급됨 → PO 에게 새 값 |
| team 이 "할 일 DB 를 못 찾았어요" | 조 페이지 ••• → 연결에 `7조 team 읽기` 가 있는지, 보드가 만들어졌는지 (PO) |
| `git pull` 했는데 team 이 옛날 그대로 | `claude` 를 껐다 켜기 (서버를 다시 실행) |
| "누구세요?"를 안 물어요 | 레포 **맨 위 폴더**에서 `claude` 를 열었는지 확인 |

## 시험 (개발)
```bash
npx @modelcontextprotocol/inspector python team/mcp/server.py
```
도구 8개(`whoami`, `list_tasks`, `progress`, `search_docs`, `link_status`, `report`, `notion_board`, `search_notion`)와 Prompts 탭의 명령 틀 6개(`next_steps`, `finish`, `my_board`, `standup`, `sync_board`, `meeting_to_issues`)가 보이고 눌러지면 정상.
`NOTION_TOKEN` 없이 `notion_board` 를 누르면 토큰 안내가 나와야 정상이다. 설계와 "만들지 않은 도구"는 [docs/mcp-design.md](docs/mcp-design.md).
