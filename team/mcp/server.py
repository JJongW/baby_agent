"""7조 team MCP 서버 (읽기 전용).

조원 모두가 같은 질문에 같은 답을 받게 하는 우리 조 전용 도구 상자이자, github 와 notion 을 잇는 허브다.

도구 (Tools)
- whoami        : 지금 세션의 사람이 누구인지 찾고, 그 사람의 역할과 할 일을 돌려준다
- list_tasks    : team/tasks.csv 에서 할 일을 거른다 (워크북의 할일_보기)
- progress      : 직군별, 사람별 진행률 (워크북의 진행률)
- search_docs   : 조 지식(docs, roles, AGENTS.md, README, tasks.csv)에서 키워드 줄을 찾는다 (워크북의 문서_찾기)
- link_status   : 깃허브 이슈, PR 을 직접 읽어 할 일 번호와 맞춰 보고 엇갈린 곳을 알려 준다

명령 틀 (Prompts, Claude Code 에서 /mcp__team__이름 으로 부른다)
- next_steps, standup, sync_board, meeting_to_issues
  team 이 아는 것(원본 할 일, 역할, 번호 규칙)으로 github, notion MCP 를 어떻게 쓸지 순서를 만들어 준다.
  노션 API 는 따로 토큰이 필요해서 team 이 직접 부르지 않고, 명령 틀 안에서 notion MCP 를 쓰게 한다.

읽기만 한다. 파일을 쓰거나 지우는 코드, 깃허브에 쓰는 요청(POST, PATCH)은 일부러 없다.
할 일 상태를 바꾸려면 tasks.csv 를 브랜치에서 고쳐 PR 로 올린다.
세 곳을 잇는 열쇠는 할 일 번호다: tasks.csv 번호 = 이슈 제목 앞 [T번호] = 노션 할 일 DB 번호.

도구 이름은 영어로 쓴다. Claude API 의 도구 이름은 영어, 숫자, _, - 만 쓸 수 있어서
한글 이름(할일_보기)은 앱에 따라 깨지거나 거부될 수 있다. 대신 설명(docstring)을 한국어로 자세히 쓴다.

실행: python team/mcp/server.py (stdio. 멈춰 있으면 정상, Ctrl+C 로 끈다)
시험: npx @modelcontextprotocol/inspector python team/mcp/server.py
"""

import csv
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

# mcp 1.x 는 FastMCP, 2.x 는 MCPServer 로 이름이 바뀌었다. 둘 다 되게 한다.
try:
    from mcp.server.mcpserver import MCPServer as Server  # mcp 2.x
except ImportError:
    from mcp.server.fastmcp import FastMCP as Server  # mcp 1.x
from mcp.types import ToolAnnotations

# 경로는 이 파일 위치 기준: team/mcp/server.py → team/
TEAM_DIR = Path(__file__).resolve().parent.parent
MEMBERS_CSV = TEAM_DIR / "members.csv"
TASKS_CSV = TEAM_DIR / "tasks.csv"
DOCS_DIR = TEAM_DIR / "docs"
ROLES_DIR = TEAM_DIR / "roles"

STATUSES = ["할 일", "진행 중", "완료"]
MAX_DOC_HITS = 30

# 우리 조 레포. 다른 레포로 옮기면 환경변수 TEAM_REPO 로 바꾼다 (예: owner/name)
REPO = os.environ.get("TEAM_REPO", "JJongW/baby_agent")
# 이슈 제목 앞의 할 일 번호 표시: "[T3] 할 일 이름"
TASK_TAG = re.compile(r"^\s*\[T(\d+)\]")

# 모든 도구에 붙이는 표시: 읽기만 하고, 같은 입력이면 같은 결과
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

mcp = Server(
    "team",
    instructions=(
        "7조 조 과제용 읽기 전용 도구. 세션을 시작하면 whoami 로 사람을 확정하고, "
        "그 사람의 역할과 할 일을 기준으로 일한다. 이 도구로 확인할 수 없는 내용은 지어내지 않는다."
    ),
)


def read_csv(path: Path) -> list[dict]:
    """CSV 를 줄 목록으로 읽는다. 엑셀이 붙이는 BOM 도 처리(utf-8-sig). 파일이 없으면 빈 목록."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in csv.DictReader(f)]


def task_line(t: dict) -> str:
    """할 일 한 줄을 사람이 읽기 좋은 모양으로."""
    return f"#{t.get('번호')} [{t.get('상태')}] {t.get('할 일')} | {t.get('직군')} | @{t.get('담당자')} | 마감 {t.get('마감')}"


def find_member(who: str) -> dict | None:
    """이름(신), 폴더(shin), 깃허브 아이디(JJongW) 중 무엇으로든 조원을 찾는다. 대소문자 무시."""
    key = who.strip().lstrip("@").lower()
    for m in read_csv(MEMBERS_CSV):
        if key in {m.get("폴더", "").lower(), m.get("이름", "").lower(), m.get("깃허브", "").lower()}:
            return m
    return None


@mcp.tool(annotations=READ_ONLY)
def whoami(who: str = "") -> str:
    """7조 조원 한 명의 정보, 오늘 역할, 맡은 할 일, 역할 안내문을 돌려준다.

    세션을 시작할 때 가장 먼저 쓴다. who 에는 이름(예: 신), 폴더(예: shin),
    깃허브 아이디(예: JJongW) 중 아무거나 넣는다.
    who 를 비우면 조원 전체 명단을 돌려준다 (누구인지 물어볼 때 보기로 쓴다).
    명단에 없는 사람이면 그렇다고 알려 준다.
    """
    members = read_csv(MEMBERS_CSV)
    if not members:
        return "team/members.csv 를 찾지 못했어요. git pull 을 받았는지 확인해 주세요."

    # 비우면 전체 명단
    if not who.strip():
        lines = ["7조 조원 (이름 / 폴더 / 직군 / 깃허브 / 조 과제 역할)"]
        lines += [f"- {m['이름']} / {m['폴더']} / {m['직군']} / @{m['깃허브']} / {m['조과제역할']}" for m in members]
        return "\n".join(lines)

    m = find_member(who)
    if m is None:
        names = ", ".join(f"{x['이름']}({x['폴더']})" for x in members)
        return f"'{who}' 는 7조 명단에 없어요. 명단: {names}"

    # 이 사람의 할 일 (담당자 = 깃허브 아이디)
    mine = [t for t in read_csv(TASKS_CSV) if t.get("담당자", "").lower() == m["깃허브"].lower()]
    todo = [t for t in mine if t.get("상태") != "완료"]

    out = [
        f"{m['이름']} ({m['폴더']}, {m['직군']}, @{m['깃허브']})",
        f"조 과제 역할: {m['조과제역할']}",
        f"브랜치 이름: {m['폴더']}/<종류>-<주제>",
        "",
        f"맡은 할 일 {len(mine)}개 중 남은 것 {len(todo)}개:",
    ]
    out += [f"- {task_line(t)}" for t in mine] or ["- (없음)"]

    # 역할 안내문: 폴더 이름이 영어 소문자일 때만 파일을 연다 (엉뚱한 경로를 막는다)
    folder = m["폴더"]
    role_file = ROLES_DIR / f"{folder}.md"
    if re.fullmatch(r"[a-z0-9-]+", folder) and role_file.exists():
        out += ["", "---- 역할 안내문 (team/roles/" + folder + ".md) ----", role_file.read_text(encoding="utf-8")]
    return "\n".join(out)


@mcp.tool(annotations=READ_ONLY)
def list_tasks(assignee: str = "", status: str = "") -> str:
    """team/tasks.csv 의 할 일을 담당자와 상태로 걸러 보여 준다 (워크북의 할일_보기).

    assignee: 담당자. 깃허브 아이디, 이름(신), 폴더(shin) 모두 된다. 비우면 전체.
    status: '할 일', '진행 중', '완료' 중 하나. 비우면 전체.
    없는 담당자를 넣으면 빈 결과를 돌려준다 (에러로 멈추지 않는다).
    """
    tasks = read_csv(TASKS_CSV)
    if assignee.strip():
        m = find_member(assignee)
        login = (m["깃허브"] if m else assignee.strip().lstrip("@")).lower()
        tasks = [t for t in tasks if t.get("담당자", "").lower() == login]
    if status.strip():
        tasks = [t for t in tasks if t.get("상태") == status.strip()]
    if not tasks:
        return "조건에 맞는 할 일이 없어요."
    return "\n".join(task_line(t) for t in tasks)


@mcp.tool(annotations=READ_ONLY)
def progress() -> str:
    """직군별, 사람별 완료/전체 개수와 전체 진행률(%)을 보여 준다 (워크북의 진행률).

    스탠드업, 주간 진행 보고, 백로그 우선순위를 정할 때 쓴다.
    """
    tasks = read_csv(TASKS_CSV)
    if not tasks:
        return "team/tasks.csv 에 할 일이 없어요."

    def summary(group_key: str) -> list[str]:
        groups: dict[str, list[dict]] = {}
        for t in tasks:
            groups.setdefault(t.get(group_key, "") or "(비어 있음)", []).append(t)
        lines = []
        for name, items in groups.items():
            done = sum(1 for t in items if t.get("상태") == "완료")
            lines.append(f"- {name}: {done}/{len(items)} 완료")
        return lines

    done_all = sum(1 for t in tasks if t.get("상태") == "완료")
    percent = round(done_all * 100 / len(tasks))
    counts = ", ".join(f"{s} {sum(1 for t in tasks if t.get('상태') == s)}" for s in STATUSES)
    return "\n".join(
        [f"전체 진행률 {percent}% ({done_all}/{len(tasks)}) | {counts}", "", "직군별"]
        + summary("직군")
        + ["", "사람별 (깃허브 아이디)"]
        + summary("담당자")
    )


def knowledge_files() -> list[Path]:
    """search_docs 가 찾는 조 지식 파일 목록. 경로를 입력으로 받지 않고 이 목록만 연다."""
    files = sorted(DOCS_DIR.glob("*.md")) + sorted(ROLES_DIR.glob("*.md"))
    files += [TEAM_DIR / "AGENTS.md", TEAM_DIR / "README.md", TASKS_CSV]
    return [f for f in files if f.exists()]


@mcp.tool(annotations=READ_ONLY)
def search_docs(keyword: str) -> str:
    """우리 조 지식에서 키워드가 들어간 줄을 찾는다 (워크북의 문서_찾기).

    찾는 곳: team/docs/*.md (회의록, 설계, 노션 보드 설계), team/roles/*.md (사람별 역할),
    team/AGENTS.md (조 규칙), team/README.md, team/tasks.csv (할 일).
    결과는 '파일:줄 번호: 내용' 모양으로 최대 30줄. 대소문자는 무시한다.
    예: '화면' 으로 화면 구성 관련 결정 모으기, '타깃' 으로 타깃 찾기, '스탠드업' 으로 규칙 찾기.
    """
    key = keyword.strip().lower()
    if not key:
        return "찾을 키워드를 넣어 주세요."
    hits = []
    for path in knowledge_files():
        name = path.relative_to(TEAM_DIR).as_posix()
        for no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if key in line.lower():
                hits.append(f"{name}:{no}: {line.strip()}")
                if len(hits) >= MAX_DOC_HITS:
                    return "\n".join(hits + [f"(최대 {MAX_DOC_HITS}줄까지만 보여 줘요)"])
    return "\n".join(hits) if hits else f"'{keyword}' 가 들어간 줄이 없어요."


def github_issues() -> list[dict]:
    """우리 조 레포의 이슈와 PR 을 최근 100개까지 읽는다 (GET 만).

    GITHUB_PAT 가 있으면 같이 보내고(비공개 레포, 요청 한도), 없으면 공개 레포로 읽는다.
    토큰 값은 어디에도 출력하지 않는다.
    """
    url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "team-mcp"})
    token = os.environ.get("GITHUB_PAT", "").strip()
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True))
def link_status(assignee: str = "") -> str:
    """할 일(tasks.csv)과 깃허브 이슈, PR 을 할 일 번호로 맞춰 보고 엇갈린 곳을 알려 준다.

    이슈 제목 앞의 [T번호] 로 할 일과 이슈를 잇고, PR 은 본문의 '#이슈번호' 나 제목의 [T번호] 로 잇는다.
    알려 주는 것: 이슈가 없는 할 일, 이슈가 닫혔거나 PR 이 머지됐는데 tasks.csv 가 '완료'가 아닌 할 일,
    tasks.csv 는 '완료'인데 이슈가 열린 할 일, 리뷰를 기다리는 PR.
    assignee 로 한 사람만 볼 수 있다 (깃허브 아이디, 이름, 폴더). 깃허브를 읽지 못하면 이유를 돌려준다.
    """
    tasks = read_csv(TASKS_CSV)
    if assignee.strip():
        m = find_member(assignee)
        login = (m["깃허브"] if m else assignee.strip().lstrip("@")).lower()
        tasks = [t for t in tasks if t.get("담당자", "").lower() == login]
    if not tasks:
        return "맞춰 볼 할 일이 없어요."

    try:
        items = github_issues()
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return f"깃허브({REPO})를 읽지 못했어요: {e}. 인터넷, GITHUB_PAT, 레포 이름(TEAM_REPO)을 확인해 주세요."

    # 이슈와 PR 나누기 (깃허브 API 는 PR 도 이슈 목록에 같이 준다)
    issues = {}  # 할 일 번호 → 이슈
    prs = [i for i in items if "pull_request" in i]
    for i in items:
        tag = TASK_TAG.match(i.get("title", ""))
        if tag and "pull_request" not in i:
            issues.setdefault(tag.group(1), i)

    lines, flags = [], []
    for t in tasks:
        no = t.get("번호", "")
        state = t.get("상태", "")
        issue = issues.get(no)
        related = [
            p for p in prs
            if (issue and re.search(rf"#{issue['number']}\b", p.get("body") or ""))
            or (TASK_TAG.match(p.get("title", "")) and TASK_TAG.match(p["title"]).group(1) == no)
        ]
        merged = [p for p in related if (p.get("pull_request") or {}).get("merged_at")]
        open_prs = [p for p in related if p.get("state") == "open"]

        issue_txt = f"이슈 #{issue['number']} {'열림' if issue['state'] == 'open' else '닫힘'}" if issue else "이슈 없음"
        pr_txt = ", ".join(
            f"PR #{p['number']} {'머지됨' if (p.get('pull_request') or {}).get('merged_at') else ('열림' if p['state'] == 'open' else '닫힘')}"
            for p in related
        ) or "PR 없음"
        lines.append(f"#{no} [{state}] {t.get('할 일')} | @{t.get('담당자')} | {issue_txt} | {pr_txt}")

        # 엇갈린 곳 찾기
        if not issue and state != "완료":
            flags.append(f"#{no}: 이슈가 없어요 (PO 가 [T{no}] 이슈를 만들면 이어져요)")
        if state != "완료" and ((issue and issue["state"] == "closed") or merged):
            flags.append(f"#{no}: 이슈가 닫혔거나 PR 이 머지됐는데 tasks.csv 는 '{state}' (상태를 PR 로 '완료'로)")
        if state == "완료" and issue and issue["state"] == "open":
            flags.append(f"#{no}: tasks.csv 는 '완료'인데 이슈 #{issue['number']} 가 열려 있어요")
        for p in open_prs:
            flags.append(f"#{no}: PR #{p['number']} 리뷰, 머지 대기")

    return "\n".join(
        [f"레포 {REPO} 기준 ({len(tasks)}개 할 일)"] + lines + ["", "엇갈린 곳, 기다리는 것"] + (flags or ["없음"])
    )


# ---------- 명령 틀 (Prompts): team 이 아는 것으로 github, notion 을 같이 쓰는 순서 ----------
# 공통 규칙: 쓰기 전에 먼저 보여 주고 확인받기. 원본은 tasks.csv. 번호로 잇기.
RULES = (
    "지킬 것: 이슈, PR, 댓글, 노션 쓰기는 먼저 표로 보여 주고 내가 확인하면 한다. "
    "원본은 team/tasks.csv 이고 세 곳은 할 일 번호로 잇는다 (이슈 제목 [T번호], 노션 할 일 DB 번호). "
    "도구로 확인 못 한 건 지어내지 않는다."
)


@mcp.prompt()
def next_steps(who: str) -> str:
    """내 진행 현황과 지금 할 일 1~3개 (team + github + notion)."""
    return (
        f"{who} 기준으로 지금 무엇을 하면 되는지 알려 줘. shin-team-orchestrator 에이전트가 있으면 그 에이전트에게 맡기고, "
        f"없으면 직접: team whoami('{who}') → team progress → team link_status('{who}') → "
        "notion '할 일' DB 와 '스탠드업' DB 의 내 최근 줄. "
        "결과: 조 진행 현황 한 줄, 내 지금 할 일 1~3개(왜 지금인지), 엇갈린 곳, 1번을 시작할 프롬프트. " + RULES
    )


@mcp.prompt()
def standup(who: str) -> str:
    """하루 끝 스탠드업 한 줄을 노션 스탠드업 DB 에 (team + github → notion)."""
    return (
        f"{who} 의 오늘 스탠드업을 써 줘. team whoami('{who}') 와 team link_status('{who}') 로 오늘 바뀐 할 일, "
        "github 로 오늘 내가 올리거나 리뷰한 PR, 머지된 PR 을 보고 오늘 한 일, 다음 할 일, 막힌 것을 한 줄씩 정리해서 "
        f"notion '스탠드업' DB 에 내 줄 하나로 넣어 줘 (제목 '오늘날짜 {who}', 날짜 오늘, 사람 {who}). "
        "다른 사람 줄은 건드리지 마. " + RULES
    )


@mcp.prompt()
def sync_board() -> str:
    """tasks.csv 원본에 맞춰 노션 할 일 DB 를 맞추기 (PO 용, team + github → notion)."""
    return (
        "team list_tasks 와 team link_status 로 원본 할 일과 이슈, PR 링크를 모으고, notion '할 일' DB 와 번호로 맞춰 봐. "
        "다른 줄(상태, 담당, 마감, 이슈 링크, PR 링크, 없는 줄)을 표로 보여 주고, 내가 '맞춰' 하면 노션 쪽만 고쳐 줘. "
        "tasks.csv 와 깃허브는 고치지 마. " + RULES
    )


@mcp.prompt()
def meeting_to_issues() -> str:
    """노션 회의록의 할 일을 깃허브 이슈로 (PO 용, notion + team → github)."""
    return (
        "notion '회의록' DB 의 가장 최근 회의와 team list_tasks, team link_status 를 같이 보고, "
        "이슈가 없는 할 일마다 깃허브 이슈 초안을 표로 보여 줘: 제목 '[T번호] 할 일', 본문(완료 기준), "
        "라벨(개발/디자인/PO), 담당자(tasks.csv 의 깃허브 아이디). 회의록에는 있는데 tasks.csv 에 없는 할 일은 따로 알려 줘 "
        "(배정은 PO 가 tasks.csv 에 먼저). 내가 '만들어' 하면 이슈를 만들고, 링크를 notion '할 일' DB 같은 번호 줄의 '이슈' 칸에 적어 줘. "
        + RULES
    )


if __name__ == "__main__":
    mcp.run()  # 기본값 stdio
