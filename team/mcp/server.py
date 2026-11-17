"""7조 team MCP 서버 (읽기 전용).

조원 모두가 같은 질문에 같은 답을 받게 하는 우리 조 전용 도구 상자이자, github 와 notion 을 잇는 허브다.

도구 (Tools)
- whoami        : 지금 세션의 사람이 누구인지 찾고, 그 사람의 역할과 할 일을 돌려준다
- list_tasks    : 할 일을 담당자, 상태로 거른다 (워크북의 할일_보기)
- progress      : 직군별, 사람별 진행률 (워크북의 진행률)
- search_docs   : 조 지식(docs, roles, AGENTS.md, README, tasks.csv)에서 키워드 줄을 찾는다 (워크북의 문서_찾기)
- link_status   : 깃허브 이슈, PR 을 직접 읽어 할 일 번호와 맞춰 보고 엇갈린 곳을 알려 준다
- notion_board  : 노션 할 일 DB 를 읽어 "담당자가 내 줄에서 고칠 것", "PO 가 맞출 것"을 만든다
- search_notion : 조 노션 페이지에서 키워드 줄을 찾는다 (노션까지 포함한 문서 찾기)
- report        : 진행률 + 할 일마다 노션 상태, 이슈, PR 을 한 번에 읽은 보고

명령 틀 (Prompts, Claude Code 에서 /mcp__team__이름 으로 부른다)
- next_steps, finish, my_board, standup, sync_board, meeting_to_issues
  finish: 일을 끝내면 github(PR) → notion(내 줄) → team report 보고를 한 번 확인하고 이어서
  team 이 읽은 것으로 github, notion MCP 를 어떻게 쓸지 순서를 만들어 준다.

어디가 원본인가
- 배정(번호, 할 일, 직군, 담당자, 마감): team/tasks.csv. PO 만 PR 로 고친다
- 상태(할 일, 진행 중, 완료): 노션 할 일 DB. 각자 Claude(notion MCP)로 내 줄만 고친다
  team 은 노션을 읽어 상태를 덮어 보여 주고, 노션을 못 읽으면 tasks.csv 의 처음 값을 쓴다
- 세 곳을 잇는 열쇠는 할 일 번호: tasks.csv 번호 = 이슈 제목 앞 [T번호] = 노션 할 일 DB 번호

읽기만 한다. 파일을 쓰거나 지우는 코드, 깃허브와 노션에 쓰는 요청은 일부러 없다.
노션 쓰기는 각자 로그인한 notion MCP 로, 사용자가 확인한 뒤에 한다.

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
# 조 노션 허브 페이지 ID (링크 끝의 32자리). 페이지 ID 는 비밀이 아니다: 통합이 연결된 사람만 읽을 수 있다
NOTION_PAGE = os.environ.get("TEAM_NOTION_PAGE", "41bb2cc357758002932be070588ca6ec")
# 노션 API 버전. 2022-06-28 은 DB 를 바로 query 할 수 있어 단순하다
NOTION_VERSION = "2022-06-28"
TODO_DB_NAME = "할 일"  # 노션 허브 아래 할 일 DB 이름에 들어가는 글자
MAX_NOTION_PAGES = 8  # search_notion 이 본문까지 읽는 페이지 수 (느려지지 않게)
# 이슈 제목 앞의 할 일 번호 표시: "[T3] 할 일 이름"
TASK_TAG = re.compile(r"^\s*\[T(\d+)\]")
# PR 본문에서 이슈를 닫는 말 (깃허브와 같은 규칙): Closes #3, fixes #3, Resolved #3
CLOSING = r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)"
# 인터넷 문제(연결, 시간 초과, 401/404)와 응답 해석 문제는 멈추지 않고 이유를 돌려준다
NET_ERRORS = (OSError, ValueError)

# 파일만 읽는 도구에 붙이는 표시: 읽기만 하고, 같은 입력이면 같은 결과
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
# 깃허브, 노션을 읽는 도구에 붙이는 표시: 읽기만 하지만 바깥(인터넷)을 본다
READ_ONLY_WEB = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)

mcp = Server(
    "team",
    instructions=(
        "7조 조 과제용 읽기 전용 도구. 세션을 시작하면 whoami 로 사람을 확정하고, "
        "그 사람의 역할과 할 일을 기준으로 일한다. 노션 할 일 DB 의 내 줄(상태, 이슈, PR)은 "
        "notion_board 로 고칠 것을 찾고, 사용자가 확인하면 notion MCP 로 고친다. "
        "이 도구로 확인할 수 없는 내용은 지어내지 않는다."
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


def for_assignee(tasks: list[dict], assignee: str) -> list[dict]:
    """한 사람의 할 일만 남긴다 (담당자 = 깃허브 아이디). assignee 가 비면 그대로."""
    if not assignee.strip():
        return tasks
    m = find_member(assignee)
    login = (m["깃허브"] if m else assignee.strip().lstrip("@")).lower()
    return [t for t in tasks if t.get("담당자", "").lower() == login]


def rank(status: str) -> int:
    """상태의 순서: 할 일 0, 진행 중 1, 완료 2. 모르는 값은 0."""
    return STATUSES.index(status) if status in STATUSES else 0


@mcp.tool(annotations=READ_ONLY_WEB)
def whoami(who: str = "") -> str:
    """7조 조원 한 명의 정보, 오늘 역할, 맡은 할 일, 역할 안내문을 돌려준다.

    세션을 시작할 때 가장 먼저 쓴다. who 에는 이름(예: 신), 폴더(예: shin),
    깃허브 아이디(예: JJongW) 중 아무거나 넣는다.
    who 를 비우면 조원 전체 명단을 돌려준다 (누구인지 물어볼 때 보기로 쓴다).
    명단에 없는 사람이면 그렇다고 알려 준다. 할 일 상태는 노션의 지금 값을 쓴다 (못 읽으면 tasks.csv).
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

    tasks, note = live_tasks()
    mine = for_assignee(tasks, m["깃허브"])
    todo = [t for t in mine if t.get("상태") != "완료"]

    out = [
        f"{m['이름']} ({m['폴더']}, {m['직군']}, @{m['깃허브']})",
        f"조 과제 역할: {m['조과제역할']}",
        f"브랜치 이름: {m['폴더']}/<종류>-<주제>",
        "",
        f"맡은 할 일 {len(mine)}개 중 남은 것 {len(todo)}개 {note}:",
    ]
    out += [f"- {task_line(t)}" for t in mine] or ["- (없음)"]

    # 역할 안내문: 폴더 이름이 영어 소문자일 때만 파일을 연다 (엉뚱한 경로를 막는다)
    folder = m["폴더"]
    role_file = ROLES_DIR / f"{folder}.md"
    if re.fullmatch(r"[a-z0-9-]+", folder) and role_file.exists():
        out += ["", "---- 역할 안내문 (team/roles/" + folder + ".md) ----", role_file.read_text(encoding="utf-8")]
    return "\n".join(out)


@mcp.tool(annotations=READ_ONLY_WEB)
def list_tasks(assignee: str = "", status: str = "") -> str:
    """할 일을 담당자와 상태로 걸러 보여 준다 (워크북의 할일_보기).

    assignee: 담당자. 깃허브 아이디, 이름(신), 폴더(shin) 모두 된다. 비우면 전체.
    status: '할 일', '진행 중', '완료' 중 하나. 비우면 전체.
    배정은 team/tasks.csv, 상태는 노션 할 일 DB 의 지금 값 (노션을 못 읽으면 tasks.csv 의 처음 값).
    없는 담당자를 넣으면 빈 결과를 돌려준다 (에러로 멈추지 않는다).
    """
    tasks, note = live_tasks()
    tasks = for_assignee(tasks, assignee)
    if status.strip():
        tasks = [t for t in tasks if t.get("상태") == status.strip()]
    if not tasks:
        return f"조건에 맞는 할 일이 없어요. {note}"
    return "\n".join([task_line(t) for t in tasks] + [note])


@mcp.tool(annotations=READ_ONLY_WEB)
def progress() -> str:
    """직군별, 사람별 완료/전체 개수와 전체 진행률(%)을 보여 준다 (워크북의 진행률).

    스탠드업, 주간 진행 보고, 백로그 우선순위를 정할 때 쓴다. 상태는 노션의 지금 값 (못 읽으면 tasks.csv).
    """
    return progress_text()


def progress_text() -> str:
    tasks, note = live_tasks()
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
        [f"전체 진행률 {percent}% ({done_all}/{len(tasks)}) | {counts}", note, "", "직군별"]
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
    노션에 있는 회의록, 스탠드업은 search_notion 으로 찾는다.
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


# ---------- 깃허브 읽기 (GET 만) ----------

def github_issues() -> list[dict]:
    """우리 조 레포의 이슈와 PR 을 최근 100개까지 읽는다 (GET 만, 새것부터).

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


def github_links() -> dict[str, dict]:
    """깃허브 이슈와 PR 을 할 일 번호로 묶는다: 번호 → {'issue': 이슈 또는 None, 'prs': [PR, 새것부터]}.

    이슈는 제목 앞 [T번호] 로, PR 은 본문의 'Closes #이슈번호'(Fixes, Resolves 도) 나 제목의 [T번호] 로 잇는다.
    본문에 이슈 번호가 그냥 적혀 있는 것(예: '이슈 #75 확인')은 잇지 않는다. 깃허브가 이슈를 닫는 규칙과 같다.
    """
    items = github_issues()
    links: dict[str, dict] = {}
    for i in items:
        tag = TASK_TAG.match(i.get("title", ""))
        if tag and "pull_request" not in i and tag.group(1) not in links:
            links[tag.group(1)] = {"issue": i, "prs": []}
    for p in (i for i in items if "pull_request" in i):
        body = p.get("body") or ""
        nos = {no for no, link in links.items()
               if link["issue"] and re.search(rf"{CLOSING}\s*:?\s+#{link['issue']['number']}\b", body, re.IGNORECASE)}
        tag = TASK_TAG.match(p.get("title", ""))
        if tag:
            nos.add(tag.group(1))
        for no in nos:
            links.setdefault(no, {"issue": None, "prs": []})["prs"].append(p)
    return links


def is_merged(pr: dict) -> bool:
    return bool((pr.get("pull_request") or {}).get("merged_at"))


def evidence(link: dict | None) -> tuple[str, str]:
    """깃허브가 보여 주는 상태와 근거. 머지된 PR, 끝난 이슈 → 완료. 열린 PR → 진행 중. 근거가 없으면 ('', '')."""
    if not link:
        return "", ""
    merged = [p for p in link["prs"] if is_merged(p)]
    if merged:
        return "완료", f"PR #{merged[0]['number']} 머지됨"
    issue = link["issue"]
    if issue and issue.get("state") == "closed" and issue.get("state_reason") != "not_planned":
        return "완료", f"이슈 #{issue['number']} 닫힘"
    opened = [p for p in link["prs"] if p.get("state") == "open"]
    if opened:
        return "진행 중", f"PR #{opened[0]['number']} 열림"
    return "", ""


@mcp.tool(annotations=READ_ONLY_WEB)
def link_status(assignee: str = "") -> str:
    """할 일과 깃허브 이슈, PR 을 할 일 번호로 맞춰 보고 엇갈린 곳을 알려 준다.

    이슈 제목 앞의 [T번호] 로 할 일과 이슈를 잇고, PR 은 본문의 'Closes #이슈번호' 나 제목의 [T번호] 로 잇는다.
    알려 주는 것: 이슈가 없는 할 일, PR 이 머지됐거나 이슈가 닫혔는데 상태가 '완료'가 아닌 할 일,
    PR 이 열렸는데 상태가 '할 일'인 할 일, '완료'인데 이슈가 열린 할 일, 리뷰를 기다리는 PR.
    assignee 로 한 사람만 볼 수 있다 (깃허브 아이디, 이름, 폴더). 깃허브를 읽지 못하면 이유를 돌려준다.
    """
    return link_text(assignee)


def link_text(assignee: str = "") -> str:
    tasks, note = live_tasks()
    tasks = for_assignee(tasks, assignee)
    if not tasks:
        return "맞춰 볼 할 일이 없어요."

    try:
        links = github_links()
    except NET_ERRORS as e:
        return f"깃허브({REPO})를 읽지 못했어요: {e}. 인터넷, GITHUB_PAT, 레포 이름(TEAM_REPO)을 확인해 주세요."

    lines, flags = [], []
    for t in tasks:
        no, state = t.get("번호", ""), t.get("상태", "")
        link = links.get(no) or {"issue": None, "prs": []}
        issue = link["issue"]
        issue_txt = f"이슈 #{issue['number']} {'열림' if issue['state'] == 'open' else '닫힘'}" if issue else "이슈 없음"
        pr_txt = ", ".join(
            f"PR #{p['number']} {'머지됨' if is_merged(p) else ('열림' if p['state'] == 'open' else '닫힘')}"
            for p in link["prs"]
        ) or "PR 없음"
        lines.append(f"#{no} [{state}] {t.get('할 일')} | @{t.get('담당자')} | {issue_txt} | {pr_txt}")

        # 엇갈린 곳 찾기
        ev, why = evidence(link)
        if not issue and state != "완료":
            flags.append(f"#{no}: 이슈가 없어요 (PO 가 [T{no}] 이슈를 만들면 이어져요)")
        if ev and rank(ev) > rank(state):
            flags.append(f"#{no}: 깃허브는 '{ev}'({why})인데 상태는 '{state}' (담당자가 노션 내 줄을 '{ev}'로: /mcp__team__my_board)")
        if state == "완료" and issue and issue["state"] == "open":
            flags.append(f"#{no}: 상태는 '완료'인데 이슈 #{issue['number']} 가 열려 있어요")
        for p in link["prs"]:
            if p.get("state") == "open":
                flags.append(f"#{no}: PR #{p['number']} 리뷰, 머지 대기")

    return "\n".join(
        [f"레포 {REPO} 기준 ({len(tasks)}개 할 일) {note}"] + lines + ["", "엇갈린 곳, 기다리는 것"] + (flags or ["없음"])
    )


@mcp.tool(annotations=READ_ONLY_WEB)
def report(assignee: str = "") -> str:
    """세 곳(team 할 일, 노션 상태, 깃허브 이슈와 PR)을 한 번에 읽어 진행 보고를 만든다.

    일을 끝내고 PR 과 노션 기록을 마친 직후, 스탠드업과 주간 진행을 쓰기 전, "지금 조 어디까지 왔어?"에 쓴다.
    위: 조 전체 진행률(직군별, 사람별). 아래: assignee 의 할 일마다 상태, 이슈, PR 과 엇갈린 곳
    (assignee 를 비우면 조 전체 할 일). 읽기만 한다.
    """
    return "\n".join(["## 조 진행률", progress_text(), "", "## 할 일과 깃허브", link_text(assignee)])


# ---------- 노션 읽기 (통합 토큰 NOTION_TOKEN, 노션 쪽 권한은 "Read content" 만) ----------
# 보내는 요청: GET(블록), POST /search, POST /databases/{id}/query. 모두 노션 API 의 "읽기" 요청이다.
# 페이지를 만들거나 고치는 요청(PATCH, POST /pages)은 일부러 없다. 고치기는 각자의 notion MCP 로.

class NotionMissing(Exception):
    """NOTION_TOKEN 이 없을 때."""


NOTION_HELP = (
    "team 이 노션을 읽으려면 환경변수 NOTION_TOKEN 이 필요해요 (team/docs/tokens.md). "
    "토큰이 있는데도 안 되면 노션 조 페이지의 ••• → 연결(Connections)에 우리 통합이 있는지 확인해 주세요. "
    "그동안은 notion MCP 로 '할 일' DB 를 직접 읽어 같은 비교를 하면 돼요."
)


def notion_call(path: str, body: dict | None = None) -> dict:
    """노션 API 를 읽기 요청으로 부른다. 토큰이 없으면 NotionMissing 을 던진다. 토큰 값은 출력하지 않는다."""
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        raise NotionMissing()
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"https://api.notion.com/v1/{path}",
        data=data,
        method="POST" if body is not None else "GET",
        headers={"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))


def plain(rich: list) -> str:
    """노션 rich_text 배열을 그냥 글자로."""
    return "".join(r.get("plain_text", "") for r in rich or [])


def prop_text(p: dict) -> str:
    """노션 속성 하나를 사람이 읽는 글자로. 모르는 종류는 빈 글자."""
    kind = p.get("type")
    v = p.get(kind)
    if kind in ("title", "rich_text"):
        return plain(v)
    if kind in ("select", "status"):
        return (v or {}).get("name", "")
    if kind == "multi_select":
        return ", ".join(x.get("name", "") for x in v or [])
    if kind == "number":
        return "" if v is None else (str(int(v)) if float(v).is_integer() else str(v))
    if kind == "date":
        return (v or {}).get("start", "") or ""
    if kind in ("url", "email", "phone_number"):
        return v or ""
    if kind == "people":
        return ", ".join(x.get("name", "") for x in v or [])
    if kind == "checkbox":
        return "예" if v else "아니오"
    return ""


def page_title(page: dict) -> str:
    """페이지나 DB 줄의 제목."""
    for p in (page.get("properties") or {}).values():
        if p.get("type") == "title":
            return plain(p.get("title"))
    return plain(page.get("title", [])) or "(제목 없음)"


def block_lines(block_id: str) -> list[str]:
    """페이지 본문(첫 100블록)을 줄 목록으로. 표, 이미지 같은 건 건너뛴다."""
    lines = []
    for b in notion_call(f"blocks/{block_id}/children?page_size=100").get("results", []):
        kind = b.get("type")
        text = plain((b.get(kind) or {}).get("rich_text"))
        if kind == "child_database":
            text = f"[DB] {(b.get(kind) or {}).get('title', '')}"
        elif kind == "child_page":
            text = f"[페이지] {(b.get(kind) or {}).get('title', '')}"
        if text.strip():
            lines.append(text.strip())
    return lines


def find_todo_db() -> str | None:
    """할 일 DB 의 ID. 허브 페이지 바로 아래를 먼저 보고, 없으면 통합이 볼 수 있는 DB 를 이름으로 찾는다.

    통합은 연결된 조 페이지(와 그 아래)만 볼 수 있어서, 이름으로 찾아도 다른 페이지의 DB 는 나오지 않는다.
    """
    for b in notion_call(f"blocks/{NOTION_PAGE}/children?page_size=100").get("results", []):
        if b.get("type") == "child_database" and TODO_DB_NAME in (b["child_database"].get("title") or ""):
            return b["id"]
    found = notion_call("search", {"query": TODO_DB_NAME, "filter": {"property": "object", "value": "database"}})
    for d in found.get("results", []):
        if TODO_DB_NAME in plain(d.get("title")):
            return d["id"]
    return None


def notion_rows() -> dict[str, dict] | None:
    """노션 할 일 DB 를 번호 → {칸 이름: 글자, 'url': 줄 링크} 로 읽는다. DB 가 없으면 None."""
    db = find_todo_db()
    if db is None:
        return None
    rows = notion_call(f"databases/{db}/query", {"page_size": 100}).get("results", [])
    board = {}
    for r in rows:
        props = {k: prop_text(v) for k, v in (r.get("properties") or {}).items()}
        if props.get("번호"):
            board[props["번호"]] = {**props, "url": r.get("url", "")}
    return board


def live_tasks() -> tuple[list[dict], str]:
    """tasks.csv 의 할 일에 노션 할 일 DB 의 지금 상태를 덮어 돌려준다. 두 번째 값은 상태를 어디서 읽었는지."""
    tasks = read_csv(TASKS_CSV)
    try:
        board = notion_rows()
    except NotionMissing:
        return tasks, "(상태: tasks.csv 처음 값. NOTION_TOKEN 이 없어 노션의 지금 상태를 못 읽었어요)"
    except NET_ERRORS as e:
        return tasks, f"(상태: tasks.csv 처음 값. 노션을 못 읽었어요: {e})"
    if board is None:
        return tasks, "(상태: tasks.csv 처음 값. 노션에 할 일 DB 가 아직 없어요)"
    for t in tasks:
        now = (board.get(t.get("번호", "")) or {}).get("상태", "")
        if now in STATUSES:
            t["상태"] = now
    return tasks, "(상태: 노션 할 일 DB 의 지금 값)"


def due_tail(due: str) -> str:
    """tasks.csv 마감 '11/7' → '-11-07'. 노션 날짜 '2026-11-07' 의 끝과 비교한다. 모양이 다르면 빈 글자."""
    m = re.fullmatch(r"\s*(\d{1,2})/(\d{1,2})\s*", due or "")
    return f"-{int(m.group(1)):02d}-{int(m.group(2)):02d}" if m else ""


@mcp.tool(annotations=READ_ONLY_WEB)
def notion_board(assignee: str = "") -> str:
    """노션 할 일 DB 를 읽어, 노션에서 고칠 것을 두 묶음으로 알려 준다. 노션은 읽기만 한다.

    1) 담당자가 노션 내 줄에서 고칠 것: 깃허브 근거(머지된 PR, 닫힌 이슈 → 완료, 열린 PR → 진행 중)보다
       늦은 상태, 비어 있거나 다른 이슈, PR 링크. 각 줄에 노션 링크를 붙인다 (그 링크의 그 칸만 고치면 된다)
    2) PO 가 맞출 것: tasks.csv(배정 원본)에 있는데 노션에 없는 줄, 담당, 마감이 다른 줄, tasks.csv 에 없는 노션 줄
    assignee 로 한 사람만 볼 수 있다 (이름, 폴더, 깃허브 아이디). 실제 고치기는 사용자가 확인한 뒤 notion MCP 로 한다.
    NOTION_TOKEN 이 없거나 노션 페이지에 통합이 연결되지 않았으면 방법을 알려 준다.
    """
    all_tasks = read_csv(TASKS_CSV)
    tasks = for_assignee(all_tasks, assignee)
    login_to_name = {m["깃허브"].lower(): m["이름"] for m in read_csv(MEMBERS_CSV)}

    try:
        board = notion_rows()
    except NotionMissing:
        return NOTION_HELP
    except NET_ERRORS as e:
        return f"노션을 읽지 못했어요: {e}. " + NOTION_HELP
    if board is None:
        return "노션 조 페이지에서 할 일 DB 를 못 찾았어요. PO 가 team/docs/notion-board.md 대로 보드를 먼저 만들어 주세요."

    try:
        links, gh_note = github_links(), ""
    except NET_ERRORS as e:
        links, gh_note = {}, f" (깃허브를 못 읽어 깃허브 근거는 빼고 봤어요: {e})"

    lines = [f"노션 할 일 DB {len(board)}줄 | 이번에 본 할 일 {len(tasks)}개{gh_note}"]
    mine, po = [], []
    for t in tasks:
        no = t.get("번호", "")
        n = board.get(no)
        who = login_to_name.get(t.get("담당자", "").lower(), t.get("담당자", ""))
        if not n:
            po.append(f"#{no}: 노션에 줄이 없어요 ({t.get('할 일')}, 담당 {who})")
            continue
        now = n.get("상태", "")
        lines.append(f"#{no} [{now}] {n.get('할 일', '')} | {n.get('담당', '')} | 마감 {n.get('마감', '')} | {n['url']}")

        link = links.get(no)
        ev, why = evidence(link)
        if ev and rank(ev) > rank(now):
            mine.append(f"#{no} 상태: '{now}' → '{ev}' (근거: {why}) | {n['url']}")
        if link and link["issue"]:
            issue = link["issue"]
            if now == "완료" and issue.get("state") == "open":
                mine.append(f"#{no} 상태는 '완료'인데 이슈 #{issue['number']} 가 열려 있어요 (맞는지 확인) | {n['url']}")
            if n.get("이슈", "") != issue.get("html_url", ""):
                mine.append(f"#{no} 이슈 칸: '{n.get('이슈') or '비어 있음'}' → {issue.get('html_url')} | {n['url']}")
        if link and link["prs"] and n.get("PR", "") != link["prs"][0].get("html_url", ""):
            mine.append(f"#{no} PR 칸: '{n.get('PR') or '비어 있음'}' → {link['prs'][0].get('html_url')} | {n['url']}")

        if n.get("담당", "") != who:
            po.append(f"#{no}: 담당이 달라요 (tasks.csv '{who}', 노션 '{n.get('담당') or '비어 있음'}')")
        tail = due_tail(t.get("마감", ""))
        if tail and not (n.get("마감") or "").endswith(tail):
            po.append(f"#{no}: 마감이 달라요 (tasks.csv '{t.get('마감')}', 노션 '{n.get('마감') or '비어 있음'}')")

    if not assignee.strip():
        known = {t.get("번호") for t in all_tasks}
        po += [f"노션 #{no}: tasks.csv 에 없는 줄이에요 ({board[no].get('할 일', '')})" for no in board if no not in known]

    return "\n".join(
        lines
        + ["", "담당자가 노션 내 줄에서 고칠 것 (각자 Claude 로 내 줄만: /mcp__team__my_board)"] + (mine or ["없음"])
        + ["", "PO 가 맞출 것 (배정: 줄 추가, 담당, 마감: /mcp__team__sync_board)"] + (po or ["없음"])
    )


@mcp.tool(annotations=READ_ONLY_WEB)
def search_notion(keyword: str) -> str:
    """조 노션(통합이 연결된 페이지)에서 키워드로 페이지를 찾고, 속성과 본문에서 키워드가 들어간 줄을 돌려준다.

    회의록의 결정, 스탠드업에서 누가 막혔는지, 직군 문서 내용 등을 근거 줄과 함께 찾을 때 쓴다 (노션까지 포함한 문서 찾기).
    제목이나 본문에 키워드가 있는 페이지를 최대 8개까지 읽고, 줄은 최대 30개. 노션은 읽기만 한다.
    """
    key = keyword.strip()
    if not key:
        return "찾을 키워드를 넣어 주세요."
    try:
        pages = notion_call("search", {"query": key, "page_size": MAX_NOTION_PAGES,
                                       "filter": {"property": "object", "value": "page"}}).get("results", [])
        hits, shown = [], 0
        for p in pages[:MAX_NOTION_PAGES]:
            title = page_title(p)
            props = [f"{k}: {prop_text(v)}" for k, v in (p.get("properties") or {}).items()
                     if v.get("type") != "title" and prop_text(v)]
            body = block_lines(p["id"])
            matched = [x for x in props + body if key.lower() in x.lower()] or (props[:3] if key.lower() in title.lower() else [])
            hits.append(f"■ {title} ({p.get('url', '')})")
            hits += [f"  - {x}" for x in matched[:6]]
            shown += len(matched[:6])
            if shown >= MAX_DOC_HITS:
                break
    except NotionMissing:
        return NOTION_HELP
    except NET_ERRORS as e:
        return f"노션을 읽지 못했어요: {e}. " + NOTION_HELP
    return "\n".join(hits) if hits else f"노션에서 '{keyword}' 가 들어간 페이지를 못 찾았어요."


# ---------- 명령 틀 (Prompts): team 이 읽은 것으로 github, notion 을 같이 쓰는 순서 ----------
# 공통 규칙: 쓰기 전에 먼저 보여 주고 확인받기. 배정은 tasks.csv, 상태는 노션. 번호로 잇기.
RULES = (
    "지킬 것: 이슈, PR, 댓글, 노션 쓰기는 먼저 표로 보여 주고 내가 확인하면 한다. "
    "배정(번호, 할 일, 담당, 마감)의 원본은 team/tasks.csv, 상태의 지금 값은 노션 할 일 DB 이고, "
    "세 곳은 할 일 번호로 잇는다 (이슈 제목 [T번호], 노션 할 일 DB 번호). "
    "노션 할 일 DB 는 내 줄의 상태, 이슈, PR 칸만 고친다 (줄 추가, 담당, 마감은 PO). "
    "도구로 확인 못 한 건 지어내지 않는다."
)


@mcp.prompt()
def next_steps(who: str) -> str:
    """내 진행 현황과 지금 할 일 1~3개 (team + github + notion)."""
    return (
        f"{who} 기준으로 지금 무엇을 하면 되는지 알려 줘. shin-team-orchestrator 에이전트가 있으면 그 에이전트에게 맡기고, "
        f"없으면 직접: team whoami('{who}') → team progress → team link_status('{who}') → team notion_board('{who}') "
        "→ notion '스탠드업' DB 의 내 최근 줄. "
        "결과: 조 진행 현황 한 줄, 내 지금 할 일 1~3개(왜 지금인지), 엇갈린 곳, 노션 내 줄에서 고칠 것, 1번을 시작할 프롬프트. " + RULES
    )


@mcp.prompt()
def my_board(who: str) -> str:
    """노션 할 일 DB 의 내 줄을 지금 상태로 맞추기 (team + github → notion, 각자)."""
    return (
        f"{who} 의 노션 할 일 줄을 최신으로 맞춰 줘. team notion_board('{who}') 의 '담당자가 노션 내 줄에서 고칠 것'과 "
        "이번 대화에서 내가 말한 변화(예: '9번 시작했어' → 진행 중, '10번 끝났어' → 완료)를 합쳐 "
        "바꿀 줄을 표로 보여 줘 (번호, 칸, 지금 값 → 바꿀 값, 근거). "
        "내가 확인하면 notion 으로 그 줄의 그 칸만 고쳐 줘. 다른 사람 줄, 담당, 마감, 할 일 이름, 새 줄 만들기는 하지 마. "
        "고친 뒤 team notion_board 를 한 번 더 불러 '없음'이 되었는지 보여 줘. "
        "NOTION_TOKEN 이 없어서 notion_board 가 안 되면 notion 으로 '할 일' DB 를 직접 읽어 같은 비교를 해. " + RULES
    )


@mcp.prompt()
def finish(who: str, task: str) -> str:
    """일을 끝냈을 때: 깃허브에 PR 올리기 → 노션 내 줄 기록 → team 으로 보고 (한 번 확인하고 이어서)."""
    return (
        f"{who} 가 할 일 #{task} 을 끝냈어. 아래 1~3을 먼저 한 표로 보여 주고(무엇을, 어디에, 어떤 값으로), "
        "내가 '응' 하면 1~3을 멈추지 말고 이어서 해 줘.\n"
        "1) github: 지금 브랜치와 바뀐 파일 확인 (main 이면 브랜치 <폴더>/<종류>-<주제> 부터) → bash scripts/check.sh 통과 → "
        f"커밋 '<종류>(<폴더>): 한 줄 요약' → push → PR (레포 PR 템플릿, 본문에 'Closes #이슈번호'. 이슈는 제목이 [T{task}] 인 것, "
        "team link_status 로 찾는다. 이슈가 없으면 멈추고 PO 에게 알리라고 말해). 머지와 이슈 닫기는 하지 않는다\n"
        f"2) notion: '할 일' DB 의 번호 {task} 줄(내 줄)의 상태를 '진행 중'(PR 리뷰 대기)으로, PR 칸에 PR 링크, 이슈 칸이 비었으면 이슈 링크. "
        "PR 이 이미 머지됐으면 상태는 '완료'. 다른 칸, 다른 줄은 건드리지 않는다\n"
        f"3) team report('{who}') 를 불러 세 줄로 보고: 올린 것(PR 링크), 노션에서 바뀐 것, 조 진행률과 내 다음 할 일 1개.\n"
        "check.sh 가 실패하거나 도구가 실패하면 거기서 멈추고 이유를 보여 줘. " + RULES
    )


@mcp.prompt()
def standup(who: str) -> str:
    """하루 끝 스탠드업 한 줄을 노션 스탠드업 DB 에 (team + github → notion)."""
    return (
        f"{who} 의 오늘 스탠드업을 써 줘. team whoami('{who}') 와 team link_status('{who}') 로 오늘 바뀐 할 일, "
        "github 로 오늘 내가 올리거나 리뷰한 PR, 머지된 PR 을 보고 오늘 한 일, 다음 할 일, 막힌 것을 한 줄씩 정리해서 "
        f"notion '스탠드업' DB 에 내 줄 하나로 넣어 줘 (제목 '오늘날짜 {who}', 날짜 오늘, 사람 {who}). "
        f"team notion_board('{who}') 에 내 줄에서 고칠 것이 있으면 같이 보여 줘. 다른 사람 줄은 건드리지 마. " + RULES
    )


@mcp.prompt()
def sync_board() -> str:
    """tasks.csv 배정에 맞춰 노션 할 일 DB 를 맞추기 (PO 용, team + github → notion)."""
    return (
        "team notion_board() 의 'PO 가 맞출 것'을 표로 보여 줘 (노션에 없는 줄, 담당, 마감이 다른 줄, tasks.csv 에 없는 노션 줄). "
        "새 줄은 tasks.csv 의 번호, 할 일, 직군, 담당(이름), 마감(올해 날짜), 상태(tasks.csv 처음 값)로, "
        "이슈, PR 링크는 team link_status 에서 가져온다. 이미 있는 줄의 상태는 담당자 몫이라 고치지 않는다. "
        "내가 '맞춰' 하면 노션 쪽만 고쳐 줘. tasks.csv 와 깃허브는 고치지 마. " + RULES
    )


@mcp.prompt()
def meeting_to_issues() -> str:
    """노션 회의록의 할 일을 깃허브 이슈로 (PO 용, notion + team → github)."""
    return (
        "notion '회의록' DB 의 가장 최근 회의(team search_notion 으로 찾아도 된다)와 team list_tasks, team link_status 를 같이 보고, "
        "이슈가 없는 할 일마다 깃허브 이슈 초안을 표로 보여 줘: 제목 '[T번호] 할 일', 본문(완료 기준), "
        "라벨(개발/디자인/PO), 담당자(tasks.csv 의 깃허브 아이디). 회의록에는 있는데 tasks.csv 에 없는 할 일은 따로 알려 줘 "
        "(배정은 PO 가 tasks.csv 에 먼저). 내가 '만들어' 하면 이슈를 만들고, 링크를 notion '할 일' DB 같은 번호 줄의 '이슈' 칸에 적어 줘. "
        + RULES
    )


if __name__ == "__main__":
    mcp.run()  # 기본값 stdio
