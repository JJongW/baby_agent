#!/usr/bin/env bash
# 레포 규칙 검사. PR 올리기 전에 각자 돌리고, 리뷰어도 한 번 돌린다.
# 규칙 설명은 CLAUDE.md "이름 규칙". 사람 목록은 members/ 아래 폴더 이름이다.
# macOS 기본 bash 3.2에서도 돌도록 연관 배열은 쓰지 않는다.
set -u
cd "$(dirname "$0")/.."

errors=0
fail() { echo "✗ $1"; errors=$((errors + 1)); }

members=$(find members -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
is_member() { echo "$members" | grep -qx "$1"; }

# frontmatter(첫 --- 와 다음 --- 사이)에서 key 값을 꺼낸다
# 윈도우에서 만든 파일은 줄 끝에 \r이 붙어 있으므로 먼저 떼고 읽는다
front() { awk -v k="$2" '{sub(/\r$/,"")} NR==1&&$0!="---"{exit} NR>1&&$0=="---"{exit} NR>1&&index($0,k": ")==1{sub(k": *","");print;exit}' "$1"; }

# 1. 폴더, 파일 이름에 한글 등 ASCII 밖 글자 금지 (git이 아는 파일 + 새로 만든 파일)
while IFS= read -r p; do
  [ -n "$p" ] && fail "이름에 영어가 아닌 글자: $p"
done < <(git ls-files -z --cached --others --exclude-standard | tr '\0' '\n' | LC_ALL=C grep '[^ -~]')

# 2. 에이전트: .claude/agents/<사람>/<사람>-<이름>.md
for entry in .claude/agents/*; do
  [ -e "$entry" ] || continue
  owner=$(basename "$entry")
  if [ ! -d "$entry" ]; then fail "에이전트는 사람 폴더 안에: $entry → .claude/agents/<사람>/"; continue; fi
  is_member "$owner" || { fail "members/에 없는 사람 폴더: $entry"; continue; }
  for f in "$entry"/*; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    [ "$base" = ".gitkeep" ] && continue
    case "$base" in *.md) ;; *) fail "에이전트 폴더에 .md가 아닌 파일: $f"; continue ;; esac
    name=${base%.md}
    echo "$name" | grep -Eq "^$owner-[a-z0-9]+(-[a-z0-9]+)*$" || fail "파일 이름은 $owner-<영어 소문자, 숫자, ->.md: $f"
    [ "$(front "$f" name)" = "$name" ] || fail "frontmatter name이 파일 이름($name)과 다름: $f"
    [ -n "$(front "$f" description)" ] || fail "frontmatter description이 없음: $f"
    [ -f "members/$owner/cards/$name.md" ] || fail "소개 카드가 없음: members/$owner/cards/$name.md"
  done
done

# 3. 스킬: .claude/skills/<사람>-<이름>/SKILL.md
for dir in .claude/skills/*; do
  [ -e "$dir" ] || continue
  name=$(basename "$dir")
  [ "$name" = ".gitkeep" ] && continue
  [ -d "$dir" ] || { fail "스킬은 폴더로: $dir → .claude/skills/<사람>-<이름>/SKILL.md"; continue; }
  owner=${name%%-*}
  { is_member "$owner" && echo "$name" | grep -Eq "^$owner-[a-z0-9]+(-[a-z0-9]+)*$"; } || fail "스킬 폴더 이름은 <사람>-<이름>: $dir"
  if [ -f "$dir/SKILL.md" ]; then
    [ "$(front "$dir/SKILL.md" name)" = "$name" ] || fail "SKILL.md name이 폴더 이름($name)과 다름: $dir/SKILL.md"
    [ -n "$(front "$dir/SKILL.md" description)" ] || fail "SKILL.md description이 없음: $dir/SKILL.md"
  else
    fail "SKILL.md가 없음: $dir"
  fi
done

# 4. 사람마다 README.md, CLAUDE.md가 있어야 한다
for m in $members; do
  [ -f "members/$m/README.md" ] || fail "members/$m/README.md 없음"
  [ -f "members/$m/CLAUDE.md" ] || fail "members/$m/CLAUDE.md 없음"
done

if [ "$errors" -eq 0 ]; then
  agents=$(find .claude/agents -name '*.md' | wc -l | tr -d ' ')
  echo "✓ 규칙 통과 (사람 $(echo "$members" | wc -l | tr -d ' ')명, 에이전트 ${agents}개)"
else
  echo "규칙 위반 ${errors}건"
  exit 1
fi
