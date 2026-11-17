# 윤 (개발) — 처음 받기 검증, 데스크톱 연결

다른 조원이 막히지 않게 "처음 받으면" 순서를 실제로 따라 해 보고 고치는 사람.

## 순서
1. Lv1 연결 확인. 이때 막힌 곳을 전부 메모한다 (이게 #7의 재료)
2. (#7) `team/README.md` "처음 받으면"을 내 PC(OS 적기)에서 따라 하고, 틀리거나 빠진 곳을 고친다
   → 시작하면 내 `[T7]` 이슈에 `/시작` 댓글 (Claude 에게 "7번 시작했어" 하면 링크를 준다. 노션은 신 노트북이 옮긴다) → 브랜치 `yoon/docs-team-setup` → PR 본문 `Closes #이슈번호`
3. (#8) 도전: 데스크톱 앱에도 team 연결. 설정 파일에 절대 경로가 필요한 이유를 한 줄로 README에
4. 하루 끝 스탠드업

## 바로 쓸 말
```
team 으로 내 할 일(담당자: uyeon0) 보여 주고, team link_status 로 내 이슈, PR 과 맞춰 봐.
```
```
내 이슈 #__ 하자. 새 브랜치 yoon/docs-team-setup 에서
team/README.md 의 "처음 받으면" 을 내가 막힌 곳 기준으로 고쳐 커밋, 푸시하고 team github_link 로 PR 만들기 링크 줘 (PR 은 내가 화면에서). 먼저 보여 줘.
```
데스크톱 연결 (Mac 예시, Windows 는 `C:\\Users\\...` 와 `python`):
```json
"team": { "command": "python3", "args": ["/Users/내이름/baby_agent/team/mcp/server.py"] }
```

## 하지 말 것
- 설정 파일 안의 내 컴퓨터 경로를 레포에 커밋하지 않기 (docs/rules.md 7번)
