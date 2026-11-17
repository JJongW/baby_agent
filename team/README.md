# team — 7조 조 과제 틀과 도구

서비스를 만들기 전에, 조원 5명이 같은 MCP 세트와 같은 규칙으로 일하기 위한 폴더.
Claude Code 를 열면 "누구세요?"를 묻고, `shin-team-orchestrator` 가 github, notion, team 을 같이 읽어 진행 현황과 내 다음 할 일을 알려 준다.

**구조도**: [docs/architecture.html](docs/architecture.html) (내려받아 브라우저로 열기). 왜 이렇게 만들었는지는 [docs/mcp-design.md](docs/mcp-design.md).

| 파일 | 뜻 |
| --- | --- |
| `AGENTS.md` | 조 규칙 원본. 루트 `CLAUDE.md` 가 불러온다 |
| `members.csv` | 조원 명단 (이름, 폴더, 직군, 깃허브, 조 과제 역할) |
| `tasks.csv` | 할 일. 배정은 PO, 상태 변경은 각자 PR |
| `roles/<폴더>.md` | 사람별 오늘 순서, 바로 쓸 말, 하지 말 것 |
| `docs/` | 회의록, 설계 문서, 구조도 |
| `mcp/server.py` | team MCP 서버 (읽기 전용 도구 5개 + 명령 틀 4개) |

| 이름 | 폴더 | 직군 | 조 과제 역할 |
| --- | --- | --- | --- |
| 신 | shin | PO | 조장, 데이터, 노션 (업무 배정) |
| 노 | noh | 개발 | 서버 리뷰, 도전 도구 |
| 윤 | yoon | 개발 | 처음 받기 검증, 데스크톱 연결 |
| 권 | kwon | 디자인 | 규칙, 테스트 3번, 화면 구성안 |
| 어 | eo | 디자인 | 시연, PR 리뷰, 페르소나 |

## 처음 받으면
1. 받기 (이미 있으면 `git pull`)
   ```bash
   git clone https://github.com/JJongW/baby_agent.git
   cd baby_agent
   pip install -r team/mcp/requirements.txt
   ```
2. 깃허브 토큰을 환경변수 `GITHUB_PAT` 에 (화면 공유 끄고, 값은 레포, 슬랙 X)
   - 토큰: github.com › Settings › Developer settings › Fine-grained › Resource owner `JJongW`, Only select `baby_agent`, Contents/Issues/Pull requests **Read and write**, 7 days
   - Windows PowerShell: `setx GITHUB_PAT "토큰"` → VS Code, 터미널 **완전히** 껐다 켜기
   - Mac: `echo 'export GITHUB_PAT="토큰"' >> ~/.zshrc` → 터미널 새로
3. 레포 맨 위 폴더에서 `claude` → "이 프로젝트의 MCP 서버를 쓸까요?" **허용**
4. `/mcp` → notion → **Authenticate** (조 노션 페이지 허용)
5. 아무 말이나 입력 (예: `시작`) → Claude 가 누구인지 확인하고 내 할 일을 보여 준다

## 막히면
| 증상 | 해결 |
| --- | --- |
| team ✗ failed | `pip install -r team/mcp/requirements.txt` → `python team/mcp/server.py` 직접 실행 (멈춰 있으면 정상, Ctrl+C) |
| Mac 에 `python` 이 없음 | 내 PC 에만: `claude mcp add --scope local team -- python3 team/mcp/server.py` (`.mcp.json` 은 그대로) |
| `pip install` 때 다른 패키지와 버전 충돌 경고 (예: fastapi 와 starlette) | 기본 파이썬에 깔지 말고 전용 가상환경으로: `python3 -m venv ~/.venvs/team-mcp` → `~/.venvs/team-mcp/bin/pip install -r team/mcp/requirements.txt` → 내 PC 에만 `claude mcp add --scope local team -- ~/.venvs/team-mcp/bin/python team/mcp/server.py` (Windows 는 `Scripts\python.exe`) |
| github 401 | `GITHUB_PAT` 가 안 들어감 → 터미널, VS Code 완전히 재시작. 값은 공유하지 않기 |
| github 403, 레포가 안 보임 | 토큰의 Resource owner, 레포 선택, 협업자 초대 수락 |
| `git pull` 했는데 team 이 옛날 그대로 | `claude` 를 껐다 켜기 (서버를 다시 실행) |
| "누구세요?"를 안 물어요 | 레포 **맨 위 폴더**에서 `claude` 를 열었는지 확인 |

## 시험 (개발)
```bash
npx @modelcontextprotocol/inspector python team/mcp/server.py
```
도구 5개(`whoami`, `list_tasks`, `progress`, `search_docs`, `link_status`)와 Prompts 탭의 명령 틀 4개가 보이고 눌러지면 정상. 설계와 "만들지 않은 도구"는 [docs/mcp-design.md](docs/mcp-design.md).
