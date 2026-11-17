# 노 (개발) — 서버 리뷰, 도전 도구

team MCP 서버(`team/mcp/server.py`)가 안전한지 확인하고, 도구 하나를 더 붙이는 사람.

## 순서
1. Lv1 연결 확인 (AGENTS.md "처음 받으면")
2. (#5) 서버 리뷰: 아래 검증 체크 5개를 직접 확인하고 결과를 PR 댓글이나 이슈에 남긴다
3. (#6) 도전: `due_soon(days)` 도구 추가 → 브랜치 `noh/feat-team-due-soon` → PR
4. 하루 끝 스탠드업

## 검증 체크 5개
| # | 확인 | 어떻게 |
| --- | --- | --- |
| 1 | 쓰기, 지우기, 파일 저장 코드가 없다 | `write`, `unlink`, `open(..., "w")` 검색 |
| 2 | 경로가 파일 위치(`__file__`) 기준 | `TEAM_DIR` 정의 확인 |
| 3 | 도구 5개, 명령 틀 4개가 보이고 눌러진다 | `npx @modelcontextprotocol/inspector python team/mcp/server.py` |
| 4 | 없는 담당자 → 빈 결과 (에러로 멈추지 않음) | Inspector 에서 `list_tasks(assignee="nobody")` |
| 5 | 설명만 읽어도 무엇을 하는지 안다 | Inspector Tools 탭의 설명 |

## 바로 쓸 말
리뷰:
```
team/mcp/server.py 를 읽고 쓰기, 지우기, 파일 저장 코드가 있는지, 경로가 안전한지 리뷰해 줘.
검증 체크 5개(team/roles/noh.md) 기준으로 표로 보여 줘. 고치지는 마.
```
도전 도구:
```
team/mcp/server.py 에 due_soon(days) 읽기 전용 도구를 추가하려고 해. 오늘부터 days 일 안에 마감인, 완료가 아닌 할 일.
마감은 tasks.csv 의 "11/18" 모양(올해 기준). 다른 도구와 같은 READ_ONLY 표시, 한국어 설명, 쉬운 주석.
브랜치 noh/feat-team-due-soon 에서 하고, 바꿀 내용을 먼저 보여 줘.
```

## 하지 말 것
- 쓰기 도구(할 일 상태 바꾸기 등)를 추가하지 않기. 상태 변경은 PR로만
