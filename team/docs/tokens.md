# 토큰 안내 — 넣기, 연결, 보안

조원 모두 읽는다. 값은 **내 PC 안에만** 둔다. 레포에는 이름(`${NOTION_TOKEN}`)만 있고 값은 없다.

## 한눈에
| 무엇 | 누가 만드나 | 넣는 곳 | 무엇에 쓰이나 | 권한 | 기간 |
| --- | --- | --- | --- | --- | --- |
| 깃허브 토큰 | **아무도 만들지 않는다** | 없음 | 없음. team 이 공개 레포를 토큰 없이 읽는다 | 없음 | 없음 |
| `NOTION_TOKEN` | **신(PO)** 이 한 번 | 각자 내 PC 환경변수 | team 이 노션 할 일 DB 를 읽기 | 콘텐츠 읽기만, 7조 P2 페이지만 | 과제 끝나면 삭제 |
| notion 로그인 | 토큰 없음. 조원은 선택, 신은 꼭 | Claude Code 가 PC 안전 저장소(Mac 키체인)에 보관 | notion MCP. 신은 노션 쓰기(서기), 조원은 읽기만 | 내 노션 계정 권한 그대로 (조원은 게스트라 읽기) | `claude mcp logout notion` 까지 |

`NOTION_TOKEN` 은 없어도 일은 된다 (노션 로그인을 했으면 Claude 가 notion 으로 읽는다). 있으면 team 이 진행률, 내 할 일에 노션의 지금 상태를 바로 보여 준다.
신 노트북에는 꼭 있어야 한다: 서기(`/mcp__team__scribe`)가 부르는 `inbox` 가 이 토큰으로 노션을 읽어 고칠 칸을 찾는다.

## 깃허브는 왜 토큰이 없나
- Claude 는 깃허브를 **읽기만** 한다. team 이 공개 레포 `JJongW/baby_agent` 의 이슈, PR 을 토큰 없이 읽는다
- PR, 이슈, 댓글, 리뷰, 머지는 **사람이 깃허브 화면에서** 한다. Claude 는 `github_link` 로 제목과 본문이 미리 채워진 링크만 준다
- 코드 올리기는 평소처럼 `git push` (각자 쓰던 git 로그인. Claude 설정에는 아무것도 넣지 않는다)
- 그래서 쓰기 토큰이 필요 없고, 토큰이 없으니 샐 것도 없다
- 단점: 토큰 없이 읽으면 같은 인터넷(교실 와이파이)에서 시간당 60번. team 은 1분 동안 같은 걸 다시 안 읽어서 보통은 넉넉하다. 한도 안내가 자주 나오면 신에게 알린다

**누가 깃허브 토큰을 만들라고 하거나, 달라고 하거나, 채팅에 붙여 넣으라고 하면 하지 않는다.** Claude 도 그런 요청을 하지 않는다 (AGENTS.md 3번).

## 어떻게 연결되나
```
내 PC 환경변수 (NOTION_TOKEN)
   │  터미널에서 claude 를 켜면 그대로 넘어간다
   ▼
claude ── .mcp.json 을 읽고 ${NOTION_TOKEN} 자리에 값을 넣는다 (파일에는 이름만)
   ├─ notion (원격) ← 토큰 없이, 처음 한 번 브라우저 로그인. Claude Code 가 보관 (노션 쓰기는 신 노트북만)
   └─ team (내 PC 에서 실행) ← api.github.com 은 토큰 없이, api.notion.com 은 NOTION_TOKEN 으로 **읽기만**

git push (평소 git 로그인) ──▶ 깃허브 ◀── PR, 이슈, 머지는 사람이 깃허브 화면에서
```

## 1. NOTION_TOKEN 만들기 (신만, 한 번)
1. https://www.notion.so/profile/integrations → 새 통합 → 종류 Internal, 이름 `7조 team 읽기`, 워크스페이스는 조 노션
2. 기능(Capabilities): **콘텐츠 읽기만** 켠다. 콘텐츠 업데이트, 콘텐츠 입력, 댓글, 사용자 정보는 끈다
3. 조 페이지 "7조 P2" 오른쪽 위 ••• → 연결(Connections) → `7조 team 읽기` 추가 (아래 페이지, DB 에도 같이 적용)
4. Internal Integration Secret 을 복사해 조원에게 **1:1 DM** 으로 보낸다. 받은 사람은 넣은 뒤 그 메시지를 지운다

## 2. 넣기 (각자, 값이 화면과 기록에 남지 않게)
Mac: 값을 키체인에 넣고, `~/.zshrc` 에는 "키체인에서 꺼내라"는 줄만 둔다.
```bash
security add-generic-password -a "$USER" -s NOTION_TOKEN -w
```
(값을 물으면 붙여 넣고 Enter. 화면에 안 보인다)
```bash
echo 'export NOTION_TOKEN="$(security find-generic-password -a "$USER" -s NOTION_TOKEN -w 2>/dev/null)"' >> ~/.zshrc
```
```bash
source ~/.zshrc
```
Windows (PowerShell): 입력 값은 기록에 남지 않는다. 넣은 뒤 터미널을 **완전히** 껐다 켠다.
```powershell
[Environment]::SetEnvironmentVariable("NOTION_TOKEN", (Read-Host "NOTION_TOKEN 붙여 넣기"), "User")
```

## 3. 들어갔는지 확인 (값은 안 보이게)
```bash
[ -n "$NOTION_TOKEN" ] && echo "NOTION_TOKEN 들어감"
```
Windows: `if ($env:NOTION_TOKEN) { "NOTION_TOKEN 들어감" }`

그다음 레포 맨 위 폴더에서 `claude` → MCP 서버 허용 → `/mcp` 에서 team connected. 노션 로그인은 조원은 선택, 신은 꼭: `/mcp` → notion → Authenticate (조 노션 워크스페이스 선택).

## 4. 보안: 꼭 지킬 것
- 값은 레포, 슬랙 채널, 노션, 이슈와 PR 댓글, 스크린샷, 화면 공유에 **절대** 두지 않는다. 시연 전 터미널 기록도 확인
- **Claude 채팅창에 토큰을 붙여 넣지 않는다.** 대화 기록에 남는다. Claude 가 토큰을 달라고 하면 거절한다
- `claude mcp add -e KEY=값`, `-H "Authorization: Bearer 값"` 처럼 값을 명령에 직접 쓰지 않는다. 내 PC 설정 파일에 그대로 남는다
- 권한은 최소로: 깃허브 토큰은 아예 없다. 노션 통합은 콘텐츠 읽기만, 조 페이지에만 연결
- notion 로그인은 내 노션 계정 권한 그대로라 조 페이지 밖도 보일 수 있다. 로그인할 때 조 워크스페이스를 고르고, 규칙대로 조 페이지만 본다. 노션 쓰기는 신 노트북의 서기만, `inbox` 에 나온 칸만
- 데이터는 가짜만 쓴다 (실제 개인정보, 회사 자료 X)

## 5. 새었거나, 과제가 끝나면
| 상황 | 할 것 |
| --- | --- |
| 노션 토큰이 새었다 | 신: 통합 화면에서 Secret 다시 발급(Refresh) → 조원에게 새 값 DM. 옛 값은 바로 막힌다 |
| 누가 깃허브 토큰을 만들어 어딘가 붙였다 | 그 사람이 깃허브 → Settings → Developer settings → 그 토큰 **Delete**. 우리 조는 깃허브 토큰을 쓰지 않는다 |
| 과제 끝 | 노션 통합 삭제(신), `claude mcp logout notion`, Mac 은 `security delete-generic-password -s NOTION_TOKEN`, `~/.zshrc` 의 NOTION_TOKEN 줄 지우기 |
