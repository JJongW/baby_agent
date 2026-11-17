# 토큰 안내 — 만들기, 넣기, 연결, 보안

조원 모두 읽는다. 값은 **내 PC 안에만** 둔다. 레포에는 이름(`${GITHUB_PAT}`)만 있고 값은 없다.

## 한눈에
| 무엇 | 누가 만드나 | 넣는 곳 | 무엇에 쓰이나 | 권한 | 기간 |
| --- | --- | --- | --- | --- | --- |
| `GITHUB_PAT` | **각자** 자기 깃허브 계정에서 | 내 PC 환경변수 | github MCP(이슈, PR 읽고 쓰기), team 의 깃허브 읽기 | baby_agent 만 (아래 1) | 7일 |
| `NOTION_TOKEN` | **신(PO)** 이 한 번 | 각자 내 PC 환경변수 | team 이 노션 할 일 DB 를 읽기 | 콘텐츠 읽기만, 7조 P2 페이지만 | 과제 끝나면 삭제 |
| notion 로그인 | 토큰 없음 | Claude Code 가 PC 안전 저장소(Mac 키체인)에 보관 | notion MCP(노션 읽고 쓰기) | 내 노션 계정 권한 그대로 | `claude mcp logout notion` 까지 |

`NOTION_TOKEN` 은 없어도 일은 된다 (Claude 가 notion 로그인으로 노션을 읽는다). 있으면 team 이 진행률, 내 할 일에 노션의 지금 상태를 바로 보여 준다.

## 어떻게 연결되나
```
내 PC 환경변수 (GITHUB_PAT, NOTION_TOKEN)
   │  터미널에서 claude 를 켜면 그대로 넘어간다
   ▼
claude ── .mcp.json 을 읽고 ${GITHUB_PAT} 자리에 값을 넣는다 (파일에는 이름만)
   ├─ github (원격) ← 헤더 "Authorization: Bearer 값" 으로 api.githubcopilot.com 에 보냄
   ├─ notion (원격) ← 토큰 없이, 처음 한 번 브라우저 로그인. Claude Code 가 보관
   └─ team (내 PC 에서 실행) ← 환경변수로 두 값을 받아 api.github.com, api.notion.com 을 **읽기만**
```

## 1. GITHUB_PAT 만들기 (각자)
1. 신의 협업자 초대 메일을 먼저 수락한다 (github.com/JJongW/baby_agent 에 들어가지면 된 것)
2. github.com → 오른쪽 위 프로필 → Settings → 맨 아래 Developer settings → Personal access tokens
3. **신(레포 주인)**: Fine-grained tokens → Generate new token
   - 이름 `7jo-baby-agent`, 기간 7 days, Resource owner `JJongW`, Only select repositories → `baby_agent`
   - Repository permissions: Contents, Issues, Pull requests 만 **Read and write** (Metadata 는 자동 Read). 나머지 No access
4. **다른 조원**: Fine-grained 의 Resource owner 목록에 `JJongW` 가 없으면 (협업자는 보통 없다) Tokens (classic) → Generate new token (classic)
   - 이름 `7jo-baby-agent`, 기간 7 days, scope 는 **`public_repo` 하나만** (baby_agent 가 공개 레포라 이것으로 충분. `repo` 전체는 켜지 않는다)
5. Generate → 값은 이 화면에서 **한 번만** 보인다. 바로 아래 "넣기"로

## 2. NOTION_TOKEN 만들기 (신만, 한 번)
1. https://www.notion.so/profile/integrations → 새 통합 → 종류 Internal, 이름 `7조 team 읽기`, 워크스페이스는 조 노션
2. 기능(Capabilities): **콘텐츠 읽기만** 켠다. 콘텐츠 업데이트, 콘텐츠 입력, 댓글, 사용자 정보는 끈다
3. 조 페이지 "7조 P2" 오른쪽 위 ••• → 연결(Connections) → `7조 team 읽기` 추가 (아래 페이지, DB 에도 같이 적용)
4. Internal Integration Secret 을 복사해 조원에게 **1:1 DM** 으로 보낸다. 받은 사람은 넣은 뒤 그 메시지를 지운다

## 3. 넣기 (각자, 값이 화면과 기록에 남지 않게)
Mac: 값을 키체인에 넣고, `~/.zshrc` 에는 "키체인에서 꺼내라"는 줄만 둔다.
```bash
security add-generic-password -a "$USER" -s GITHUB_PAT -w
```
(값을 물으면 붙여 넣고 Enter. 화면에 안 보인다. `NOTION_TOKEN` 도 `-s NOTION_TOKEN` 으로 한 번 더)
```bash
echo 'export GITHUB_PAT="$(security find-generic-password -a "$USER" -s GITHUB_PAT -w 2>/dev/null)"' >> ~/.zshrc
```
```bash
echo 'export NOTION_TOKEN="$(security find-generic-password -a "$USER" -s NOTION_TOKEN -w 2>/dev/null)"' >> ~/.zshrc
```
```bash
source ~/.zshrc
```
Windows (PowerShell): 입력 값은 기록에 남지 않는다. 넣은 뒤 터미널을 **완전히** 껐다 켠다.
```powershell
[Environment]::SetEnvironmentVariable("GITHUB_PAT", (Read-Host "GITHUB_PAT 붙여 넣기"), "User")
```
```powershell
[Environment]::SetEnvironmentVariable("NOTION_TOKEN", (Read-Host "NOTION_TOKEN 붙여 넣기"), "User")
```

## 4. 들어갔는지 확인 (값은 안 보이게)
```bash
[ -n "$GITHUB_PAT" ] && echo "GITHUB_PAT 들어감"; [ -n "$NOTION_TOKEN" ] && echo "NOTION_TOKEN 들어감"
```
Windows: `if ($env:GITHUB_PAT) { "GITHUB_PAT 들어감" }`

그다음 레포 맨 위 폴더에서 `claude` → MCP 서버 허용 → `/mcp` → notion → Authenticate (조 노션 워크스페이스 선택) → `/mcp` 에서 셋 다 connected.

## 5. 보안: 꼭 지킬 것
- 값은 레포, 슬랙 채널, 노션, 이슈와 PR 댓글, 스크린샷, 화면 공유에 **절대** 두지 않는다. 시연 전 터미널 기록도 확인
- **Claude 채팅창에 토큰을 붙여 넣지 않는다.** 대화 기록에 남는다. Claude 가 토큰을 달라고 하면 거절하고 환경변수로
- `claude mcp add -e KEY=값`, `-H "Authorization: Bearer 값"` 처럼 값을 명령에 직접 쓰지 않는다. 내 PC 설정 파일에 그대로 남는다
- 권한은 최소로: 깃허브는 baby_agent 만(또는 `public_repo` 만), 7일. 노션 통합은 콘텐츠 읽기만, 조 페이지에만 연결
- notion 로그인은 내 노션 계정 권한 그대로라 조 페이지 밖도 보일 수 있다. 로그인할 때 조 워크스페이스를 고르고, 규칙대로 조 페이지만 쓴다
- 데이터는 가짜만 쓴다 (실제 개인정보, 회사 자료 X)

## 6. 새었거나, 과제가 끝나면
| 상황 | 할 것 |
| --- | --- |
| 깃허브 토큰이 새었다 | 깃허브 → Developer settings → 그 토큰 **Delete** → 새로 만들어 다시 넣기 |
| 노션 토큰이 새었다 | 신: 통합 화면에서 Secret 다시 발급(Refresh) → 조원에게 새 값 DM. 옛 값은 바로 막힌다 |
| 7일이 지나 github 401 | 새 토큰을 만들어 3번처럼 다시 넣기 (Mac 은 `security delete-generic-password -s GITHUB_PAT` 후 다시 add) |
| 과제 끝 | 깃허브 토큰 Delete, 노션 통합 삭제(신), `claude mcp logout notion`, Mac 은 `security delete-generic-password -s GITHUB_PAT` 와 `-s NOTION_TOKEN`, `~/.zshrc` 의 두 줄 지우기 |
