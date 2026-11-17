# 7조 팀 도구 설계 — 왜 이렇게 만들었나

서비스를 만들기 전에, 조원 5명이 같은 도구와 같은 규칙으로 일하게 만드는 틀이다.

## 한 장 그림
```
baby_agent (레포)
├ .mcp.json            조원 모두 같은 MCP 3개: github, notion, team
├ CLAUDE.md            Claude Code 가 자동으로 읽는 곳. 세션 시작 절차 + team/AGENTS.md 불러오기
└ team/
  ├ AGENTS.md          조 규칙 원본 (어떤 AI 도구로 열어도 같은 규칙)
  ├ README.md          사람이 읽는 안내 (처음 받으면)
  ├ members.csv        조원 명단: 이름, 폴더, 직군, 깃허브, 조 과제 역할
  ├ tasks.csv          할 일 배정: 담당자 = 깃허브 아이디. PO 만 PR 로 (상태의 지금 값은 노션)
  ├ roles/<폴더>.md     사람별 오늘 순서, 바로 쓸 말, 하지 말 것
  ├ docs/              회의록, 설계 문서 (search_docs 가 찾는 곳)
  └ mcp/server.py      team MCP 서버 (읽기 전용: 파일, 깃허브, 노션을 읽는다)
```

## 세션이 열리면 일어나는 일
1. Claude Code 가 루트 `CLAUDE.md` 를 읽는다 → `team/AGENTS.md` 도 같이 불러온다
2. 첫 답에서 누구인지 확정한다: git 사용자 이름, 브랜치 이름으로 짐작 → `whoami` 로 확인 → "○님 맞으세요?"
3. 확정되면 `shin-team-orchestrator`(`.claude/agents/shin/`)가 team, github, notion 을 같이 읽고 조 진행 현황, 그 사람의 지금 할 일 1~3개, 엇갈린 곳(PR 은 머지됐는데 tasks.csv 가 그대로 등), 바로 쓸 말을 돌려준다
4. 메인 세션이 그 할 일을 시작한다. 이슈, PR, 노션 쓰기는 메인 세션이 사용자 확인을 받고 한다
5. 할 일을 시작하거나 끝내면 사용자가 말만 한다. 메인 세션이 `notion_board(나)` 로 고칠 칸을 찾고, 표로 보여 준 뒤 notion MCP 로 노션 할 일 DB 의 그 사람 줄만 고친다

## AGENTS.md 와 CLAUDE.md 를 나눈 이유
- `team/AGENTS.md`: 조 규칙 원본. AGENTS.md 는 Codex, Cursor 같은 다른 AI 도구도 읽는 공용 이름이라, 조원이 어떤 도구를 써도 같은 규칙을 본다
- 루트 `CLAUDE.md`: Claude Code 는 CLAUDE.md 만 자동으로 읽어서, 여기서 `@team/AGENTS.md` 로 불러온다. 규칙은 한 곳만 고친다
- 내일(D26) Next.js 앱 폴더에 `create-next-app` 이 만드는 `AGENTS.md`("최신 문서를 먼저 읽어라")는 그 앱 전용이다. 지우지 않는다

## 오케스트레이터를 에이전트로 둔 이유
- 세 곳을 읽는 일은 길고 결과는 짧다. 서브에이전트가 읽고 요약만 돌려주면 메인 세션의 맥락이 깨끗하다
- `tools` 에 읽기 도구 이름만 적어(team 7개, github 이슈/PR/커밋 읽기, notion 검색/읽기) 쓰기가 아예 불가능하다. 비워 두면 쓰기 도구까지 물려받는다
- 레포 이름 규칙상 에이전트는 사람 폴더 아래에 둬야 해서 PO 인 `shin` 아래에 두고, 조원 모두 부른다

사람마다 다른 CLAUDE.md 를 두지 않고, 명단과 역할 파일을 데이터로 둔 이유: 배정이 바뀌어도 PO 가 `tasks.csv` 와 `roles/` 만 고치면 모두의 세션이 다음 pull 부터 따라온다.

## 어디가 원본인가: 배정은 tasks.csv, 상태는 노션
| 무엇 | 원본 | 왜 |
| --- | --- | --- |
| 배정 (번호, 할 일, 담당, 마감) | `team/tasks.csv` | 배정은 PO 의 판단이라 PR 리뷰를 거친다. team 이 파일로 바로 읽는다 |
| 상태 (할 일, 진행 중, 완료) | 노션 할 일 DB | 조원이 하루에 몇 번씩 바꾼다. PR 을 거치면 늦고, 노션 보드가 모두가 보는 곳이다. 각자 Claude 로 내 줄만 바꾼다 |
| 이슈, PR | 깃허브 | 상태의 근거. 머지된 PR, 닫힌 이슈 → 완료, 열린 PR → 진행 중 |

team 은 노션을 읽어 상태를 덮어 보여 주고(`whoami`, `list_tasks`, `progress`, `link_status`), 노션을 못 읽으면 tasks.csv 의 처음 값을 쓰면서 그렇다고 적는다.

## team 은 허브다: 조 지식을 찾아 주고, github 와 notion 을 번호로 잇는다
github 와 notion 은 이미 공식 서버가 있어서 다시 만들지 않는다. team 이 하는 일은 그 둘이 모르는 것, 즉 **우리 조만 아는 것**이다.
- 누가 누구인지, 누가 무엇을 맡았는지 (명단, 원본 할 일, 역할 안내문)
- 우리 조 문서 어디에 무엇이 있는지 (레포의 회의록, 설계, 규칙, 역할은 `search_docs`, 노션의 회의록, 스탠드업, 직군 문서는 `search_notion`. 키워드로 찾아 근거 줄을 돌려준다. AI 가 답하기 전에 우리 문서를 먼저 찾아 붙이는 RAG 방식)
- 세 곳이 어떻게 이어지는지 (할 일 번호 = 이슈 `[T번호]` = 노션 할 일 DB 번호. `link_status` 가 깃허브를, `notion_board` 가 노션과 깃허브를 직접 읽어 맞춰 본다)
- 노션에서 누가 무엇을 고치면 되는지 (`notion_board`: 담당자가 내 줄에서 고칠 것, PO 가 맞출 것)
- 노션과 깃허브를 같이 써야 하는 일의 순서 (명령 틀)

### 도구 7개
| 도구 | 하는 일 | 워크북 이름 |
| --- | --- | --- |
| `whoami(who)` | 조원 찾기 + 역할 + 할 일 + 역할 안내문. 비우면 명단 | (우리 조 추가) |
| `list_tasks(assignee, status)` | 할 일 거르기 | 할일_보기 |
| `progress()` | 직군별, 사람별 진행률 | 진행률 |
| `search_docs(keyword)` | docs, roles, AGENTS.md, README, tasks.csv 에서 키워드 줄 찾기 (최대 30) | 문서_찾기 |
| `link_status(assignee)` | 깃허브 이슈, PR 을 읽어(GET 만) 할 일 번호와 맞추고 엇갈린 곳 알리기 | (우리 조 추가) |
| `notion_board(assignee)` | 노션 할 일 DB 를 읽어 "담당자가 내 줄에서 고칠 것"(깃허브 근거보다 늦은 상태, 비어 있는 이슈, PR 칸)과 "PO 가 맞출 것"(없는 줄, 담당, 마감)을 노션 링크와 함께 | (우리 조 추가) |
| `search_notion(keyword)` | 조 노션 페이지(통합이 연결된 곳만)에서 키워드 줄 찾기 (최대 8페이지, 30줄) | 문서_찾기의 노션판 |

### 명령 틀 5개 (MCP Prompts, Claude Code 에서 `/mcp__team__이름`)
| 명령 틀 | 쓰는 곳 | 하는 일 |
| --- | --- | --- |
| `next_steps(who)` | team + github + notion | 내 진행 현황과 지금 할 일 1~3개 (오케스트레이터에게 맡김) |
| `my_board(who)` | team + github → notion | 노션 할 일 DB 의 내 줄(상태, 이슈, PR)을 지금 상태로 (각자) |
| `standup(who)` | team + github → notion | 오늘 한 일, 다음 할 일, 막힌 것을 노션 스탠드업 DB 에 내 줄로 |
| `sync_board()` | team + github → notion | tasks.csv 배정에 맞춰 노션 할 일 DB 의 줄, 담당, 마감 맞추기 (PO) |
| `meeting_to_issues()` | notion + team → github | 노션 회의록의 할 일을 `[T번호]` 이슈로, 링크를 노션에 (PO) |

team 은 노션을 **읽기 전용 통합 토큰**(`NOTION_TOKEN`, 노션 쪽 권한 "콘텐츠 읽기"만)으로 읽는다. 노션 쓰기는 명령 틀 안에서 각자 로그인한 notion MCP 로 한다. 토큰이 없으면 team 은 "토큰이 필요해요"와 대신 할 방법(notion MCP 로 직접 읽기)을 돌려주고 멈추지 않는다.

왜 notion MCP 가 있는데 team 도 노션을 읽나: notion MCP 는 각자의 로그인으로 Claude 가 부르는 도구라 team 서버 안에서는 쓸 수 없다. team 이 노션을 직접 읽어야 진행률, 내 할 일, 깃허브와 노션 비교를 한 번에 같은 답으로 줄 수 있다.

- 도구 이름은 영어. Claude API 도구 이름은 영어, 숫자, `_`, `-` 만 받아서 한글 이름은 앱에 따라 깨질 수 있다. 설명(docstring)은 한국어로 자세히
- 모든 도구에 `readOnlyHint` 표시. 파일을 여는 곳은 CSV, md 읽기뿐, 깃허브에는 GET 요청만, 노션에는 읽기 요청(GET, search, query)만
- mcp SDK 1.x(`FastMCP`)와 2.x(`MCPServer`) 둘 다에서 돈다 (11/17 1.30.0, 2.3.0 으로 확인)

## 일부러 만들지 않은 것 (위임 로그, 시연 2:30 용)
| 안 만든 것 | 이유 |
| --- | --- |
| 할 일 상태 바꾸기 도구 | 상태는 각자 notion MCP 로, 확인을 받고 바꾼다. team 이 바꾸면 누가 바꿨는지 노션에 남지 않는다 (공용 토큰이라) |
| 할 일 추가, 지우기 도구 | 배정은 PO 의 판단. 지우기는 되돌리기 어렵다 |
| 깃허브, 노션에 쓰는 도구 | 공식 서버(notion, github)가 이미 있고, 쓰기는 각자 권한으로 확인받고. team 은 읽기만. 노션 통합도 "콘텐츠 읽기"만 켠다 |
| 임의 경로 파일 읽기 | `search_docs` 는 정해진 조 지식 파일 목록만 연다. 경로를 입력으로 받지 않는다 |

열지 않은 권한: github 토큰은 이 레포 하나, Contents/Issues/Pull requests 만, 7일. 노션 통합은 콘텐츠 읽기만, 조 페이지에만 연결. 이슈 닫기와 머지는 사람이 화면에서.

## 갈아탈 신호
- 조원이 PC 마다 python 설치로 막히는 일이 3번을 넘으면: `uvx` 실행이나 Node 서버로 바꾸는 걸 검토
- 할 일이 50줄을 넘거나 배정 PR 이 밀리면: 배정도 노션 할 일 DB 를 원본으로 옮기고 tasks.csv 를 없애는 걸 검토 (team 은 노션과 깃허브를 읽기만)
- 노션 할 일 DB 가 100줄을 넘으면: `notion_rows` 에 다음 쪽 읽기(start_cursor)를 넣는다 (지금은 첫 100줄)
- 공용 노션 토큰을 돌리는 게 부담이 되면: 토큰은 PO 만 두고, 다른 조원은 notion MCP 로 직접 읽는 길(토큰 없음 안내)로 간다
- 채팅(claude.ai)에서도 써야 하면: 공개 주소 + 인증이 있는 원격 서버가 필요 (지금은 로컬 stdio)
