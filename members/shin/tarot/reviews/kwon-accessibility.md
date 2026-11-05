> kwon-accessibility-checker 결과 그대로 (2026-11-05, 반영 전 prototype.html 기준)

# `members/shin/tarot/prototype.html` 접근성 점검 결과

**범위와 한계**
- 코드만 읽고 점검했습니다. 브라우저 렌더링, 스크린 리더, 실제 키보드 조작은 실행하지 않았으므로 모든 시뮬레이션은 예상 흐름입니다.
- 대비는 CSS 값으로 계산했습니다. 배경이 그라디언트와 노이즈이므로, 배경이 걸린 값은 노이즈를 뺀 "추정"입니다.
- 파일은 고치지 않았습니다. 아래 코드는 모두 제안이며, `.sr-only` 클래스는 새로 추가해야 합니다.

## 우선순위 한눈에 보기

| 우선순위 | 문제 | WCAG 기준 | 등급 |
| --- | --- | --- | --- |
| 🔴 | 장면이 바뀔 때 포커스가 사라지고 안내가 없음 | 2.4.3, 4.1.3 | A, AA |
| 🔴 | 뒤집기 전에 보이지 않는 체크박스가 조작되어 단계를 건너뜀 | 2.4.7, 2.4.3 | AA, A |
| 🟡 | 체크박스를 누르면 예고 없이 화면이 바뀜 | 3.2.2 | A |
| 🟡 | 뒤집은 뒤 카드 버튼의 이름과 동작이 맞지 않음 | 4.1.2, 2.5.3 | A |
| 🟡 | 계속 움직이는 요소를 멈출 수 없음 | 2.2.2 | A |
| 🟡 | 결과 화면에 제목 구조가 없음 | 1.3.1, 2.4.6 | A, AA |
| 🟡 | 확대하거나 낮은 화면에서 위쪽 내용에 닿을 수 없음 | 1.4.10, 1.4.4 | AA |
| 🟡 | 이름 입력의 힌트와 테두리 대비가 낮고, 보이는 라벨이 없음 | 1.4.3, 1.4.11, 3.3.2 | AA, AA, A |
| 🟡 | 탭 힌트가 깜빡일 때 대비가 기준 아래로 떨어짐 | 1.4.3 | AA |
| 🟡 | 영어 문구에 언어 표시가 없음 | 3.1.2 | AA |
| 🟢 | 진행 표시가 시각 전용이고 대비가 낮음 | 1.3.1, 1.4.11 | A, AA |
| 🟢 | `처음부터` 버튼이 작고 내용과 겹칠 수 있음 | 1.4.3, 2.5.5(AAA 권고) | AA |
| 🟢 | 12~13px 글자가 많음 | 기준 없음(권고) | 없음 |

---

## 🔴 문제 1. 장면이 바뀔 때 포커스가 사라지고 안내가 없음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| 전환 후 포커스 이동(346~350행) | Fail | Level A | 2.4.3 Focus Order |
| 새 장면과 대기 상태 안내 | Fail | Level AA | 4.1.3 Status Messages |

### 2. 원인 및 맥락 분석
`go()`는 클래스만 바꿉니다. `입장하기`를 누르면 버튼이 있던 장면이 `display:none`이 되어 포커스를 잃습니다. `이 카드로 할게요`도 `visibility:hidden`이 되어 같은 일이 생깁니다.

키보드 사용자는 다음 Tab의 위치를 예측하기 어렵습니다. 스크린 리더 사용자는 화면이 바뀐 사실도, 약 1.4초의 대기도 듣지 못합니다.

### 3. 개선안
- **디자인/컬러**: 변경 없음
- **코드(HTML/ARIA)**:

```js
// Before
$(['s1','s2','s3','s3','s5'][n - 1]).classList.add('on');
```
```js
// After: 첫 로드에는 호출하지 않고, 사용자 조작 후 전환에서만 호출
function focusFirst(id) { $(id).focus(); }
// s1, s2, s5의 h1에 id와 tabindex="-1"을 추가
// 입장: go(2); focusFirst('s2Title');
// 카드 등장: go(3); focusFirst('flip');
// 지킴: go(5); focusFirst('s5Title');
// 처음부터: start(); focusFirst('s1Title');
```
```html
<p class="sr-only" role="status" id="status"></p>
<!-- 고른 직후 $('status').textContent = '카드를 고르고 있어요' -->
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. `입장하기`를 누른다.
2. "마음이 가는 순간에 멈추세요, 제목 1"
3. Tab: "이 카드로 할게요, 버튼"
4. 누른다: "카드를 고르고 있어요"
5. 잠시 후: "카드를 눌러 뒤집기, 버튼"

---

## 🔴 문제 2. 뒤집기 전에 보이지 않는 체크박스가 조작되어 단계를 건너뜀

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| 투명한 체크박스의 포커스 표시(144, 314행) | Fail | Level AA | 2.4.7 Focus Visible |
| 카드 공개 전 포커스 진입 | Fail | Level A | 2.4.3 Focus Order |

### 2. 원인 및 맥락 분석
`.reveal`은 `opacity:0`일 뿐이라 `#kept`가 계속 활성 상태입니다. 키보드 사용자는 Tab 위치를 볼 수 없습니다.

Space를 누르면 카드를 보지 않고 완료 화면으로 넘어갑니다. 미션 내용을 듣지 못한 스크린 리더 사용자가 "지켰어요"만 듣고 체크할 수도 있습니다. 투명한 라벨은 마우스나 터치로도 눌립니다.

### 3. 개선안
- **디자인/컬러**: 변경 없음
- **코드(HTML/ARIA)**:

```css
/* Before */
.reveal { opacity: 0; }
```
```css
/* After: 미션이 나타나기 전에는 포커스와 클릭이 닿지 않음 */
.reveal { opacity: 0; }
.r-mission.reveal { visibility: hidden; }
@keyframes magic {
  0%   { visibility: visible; opacity: 0; transform: translateY(-10px); filter: blur(8px); letter-spacing: .08em; }
  60%  { opacity: 1; filter: blur(0); }
  100% { visibility: visible; opacity: 1; transform: none; filter: blur(0); letter-spacing: normal; }
}
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 뒤집기 전 Tab 순서: 카드 버튼 → `처음부터`
2. 미션이 나타난 뒤 Tab 순서: 카드 버튼 → 미션 조작 요소 → `처음부터`
3. 뒤집기 전에는 "지켰어요"가 읽히지 않습니다.

---

## 🟡 문제 3. 체크박스를 누르면 예고 없이 화면이 바뀜

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| 체크 즉시 장면 전환(422~426행) | Fail | Level A | 3.2.2 On Input |

### 2. 원인 및 맥락 분석
체크박스는 상태만 바꾸는 요소로 인식됩니다. 그런데 체크하면 0.4초 뒤 다른 장면으로 넘어가고, 되돌아갈 수단은 `처음부터`뿐입니다.

운동 조절이 어려운 사용자나 스크린 리더 사용자는 실수로 체크한 뒤 맥락을 잃기 쉽습니다.

### 3. 개선안
- **디자인/컬러**: 기존 `.btn`을 재사용합니다. 글자 `#C8102E`, 배경 `#FBF7F2`로 5.5:1입니다.
- **코드(HTML/ARIA)**:

```html
<!-- Before -->
<label><input type="checkbox" id="kept"> 지켰어요</label>
```
```html
<!-- After: 버튼으로 바꾸고 미션 내용을 연결. 스크립트는 onchange에서 onclick으로 변경 -->
<button class="btn" id="kept" type="button" aria-describedby="rMission">지켰어요</button>
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. Tab: "지켰어요, 버튼, 오늘 처음 만나는 사람에게 먼저 인사하기"
2. Enter: "오늘의 운을 지켰어요, 제목 1"

---

## 🟡 문제 4. 뒤집은 뒤 카드 버튼의 이름과 동작이 맞지 않음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| 뒤집은 뒤에도 남는 이름과 상태(295, 408행) | Fail | Level A | 4.1.2 Name, Role, Value |
| 보이는 `THE SUN`이 이름에 없음 | Fail | Level A | 2.5.3 Label in Name |
| `button` 안의 `div`(296~304행) | Warning | Level A | 4.1.1 Parsing |

### 2. 원인 및 맥락 분석
뒤집은 뒤에도 버튼은 "카드를 눌러 뒤집기"로 읽히지만, 눌러도 아무 일이 일어나지 않습니다. 스크린 리더 사용자는 고장으로 오해할 수 있습니다.

음성 입력 사용자가 화면에 보이는 "THE SUN"을 말해도 이 버튼과 연결되지 않습니다.

### 3. 개선안
- **디자인/컬러**: 변경 없음
- **코드(HTML/ARIA)**:

```js
// Before
$('flip').classList.add('open');
```
```js
// After
const flip = $('flip');
flip.classList.add('open');
flip.setAttribute('aria-label', `${card.num} ${card.name} 카드, 공개됨`);
flip.disabled = true;
$('rHead').focus(); // 문제 6의 h2로 이동
```

`.flip-inner`, `.face`, `.num`, `.art`, `.name`의 `div`는 `span`으로 바꾸는 것을 권합니다. 현재 CSS가 `position`과 `display`를 지정하지 않은 요소는 `display:block`도 함께 줍니다. `start()`에서는 `disabled`와 `aria-label`을 원래대로 되돌려야 합니다.

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 뒤집기 전: "카드를 눌러 뒤집기, 버튼"
2. Enter: "먼저 웃는 쪽이 하루를 가져가요, 제목 2"
3. 이후 카드는 Tab 순서에서 빠집니다. 가상 커서로는 "XIX THE SUN 카드, 공개됨, 흐리게 표시된 버튼"처럼 읽힙니다.

---

## 🟡 문제 5. 계속 움직이는 요소를 멈출 수 없음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| 별, 동물, 덱, 탭 힌트의 무한 애니메이션(24, 27, 96, 139행) | Fail | Level A | 2.2.2 Pause, Stop, Hide |

### 2. 원인 및 맥락 분석
장식이 5초 넘게 내용 옆에서 계속 움직입니다. 주의력 장애나 전정 장애가 있는 사용자는 글에 집중하기 어렵습니다.

`prefers-reduced-motion` 처리는 좋지만 OS 설정을 켠 사람에게만 적용됩니다. 화면 안에서 멈추는 수단도 있어야 합니다.

### 3. 개선안
- **디자인/컬러**: 새 버튼은 글자 `#D8B6BA`, 배경 `#2A040C`로 약 10.1:1입니다.
- **코드(HTML/ARIA)**:

```html
<!-- Before: 멈춤 수단 없음 -->
```
```html
<!-- After: main 앞에 배치 -->
<button id="motion" type="button" aria-pressed="false">움직임 멈추기</button>
```
```css
.paused .gstar, .paused .pet, .paused .shuffling .tcard, .paused .tap-hint {
  animation-play-state: paused;
}
```

스크립트에서 `body`의 `.paused`와 `aria-pressed`를 함께 토글합니다.

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 첫 Tab: "움직임 멈추기, 전환 버튼, 누르지 않음"
2. Space: "눌림". 장식과 덱이 멈춥니다.
3. 다음 Tab: 이름 입력

---

## 🟡 문제 6. 결과 화면에 제목 구조가 없음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| `#s3`에 제목 없음, `#rHead`는 `div`(309행) | Fail | Level A | 1.3.1 Info and Relationships |
| 미션 제목이 `b`(312행) | Warning | Level AA | 2.4.6 Headings and Labels |

### 2. 원인 및 맥락 분석
가장 중요한 결과 화면에 제목이 하나도 없습니다. 스크린 리더 사용자는 제목 단위로 이동해 결과와 미션을 찾을 수 없습니다.

### 3. 개선안
- **디자인/컬러**: 변경 없음. 기존 클래스로 모양을 유지합니다. 다만 전역 `h1` 여백이 있어 `.sr-only`가 이를 덮어야 합니다.
- **코드(HTML/ARIA)**:

```html
<!-- Before -->
<div class="reveal r-head" style="--i:1" id="rHead"></div>
<b>이 운을 지키려면</b>
```
```html
<!-- After -->
<h1 class="sr-only">오늘의 카드</h1>
<h2 class="reveal r-head" style="--i:1" id="rHead" tabindex="-1"></h2>
<h3 class="r-mission-title">이 운을 지키려면</h3>
```

`.r-mission b`의 스타일은 `.r-mission-title`로 옮기고, `font-weight`도 지정합니다.

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 제목 탐색: "오늘의 카드, 제목 1"
2. "먼저 웃는 쪽이 하루를 가져가요, 제목 2"
3. "이 운을 지키려면, 제목 3"

---

## 🟡 문제 7. 확대하거나 낮은 화면에서 위쪽 내용에 닿을 수 없음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| `.scene`의 중앙 정렬과 내부 스크롤(45행) | Fail(코드 판단, 실측은 구현에서 확인 필요) | Level AA | 1.4.10 Reflow |
| 같은 원인의 200% 확대 | Warning(구현에서 확인 필요) | Level AA | 1.4.4 Resize Text |

### 2. 원인 및 맥락 분석
세로 flex 컨테이너에 `justify-content:center`와 `overflow-y:auto`를 함께 쓰면, 넘친 내용의 위쪽은 스크롤로도 닿지 않습니다. `body`도 `overflow:hidden`입니다.

코드 기준으로 `#s3`는 내용 높이가 약 650px로 추정됩니다. 400% 확대(약 320×256)에서 카드와 결과 제목이 잘릴 가능성이 큽니다. 저시력 사용자는 내용이 있다는 사실조차 모르고 지나칠 수 있습니다.

### 3. 개선안
- **디자인/컬러**: 변경 없음
- **코드(HTML/ARIA)**:

```css
/* Before */
.scene { justify-content: center; overflow-y: auto; }
```
```css
/* After: 넘치지 않을 때만 중앙에 놓임 */
.scene { justify-content: flex-start; overflow-y: auto; }
.scene > :first-child { margin-top: auto; }
.scene > :last-child { margin-bottom: auto; }
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 400% 확대에서 뒤집은 뒤, 포커스가 결과 제목으로 이동하면 해당 위치로 스크롤됩니다.
2. 위로 스크롤하면 카드까지 닿습니다.
3. Tab으로 미션 조작 요소까지 이동합니다. 실제 동작은 구현에서 확인이 필요합니다.

---

## 🟡 문제 8. 이름 입력의 힌트와 테두리 대비가 낮고, 보이는 라벨이 없음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| placeholder 대비(`::placeholder` 지정 없음) | Fail(추정, Chrome 기본값 기준) | Level AA | 1.4.3 Contrast (Minimum) |
| 입력 칸 테두리 대비(58행) | Fail(추정) | Level AA | 1.4.11 Non-text Contrast |
| placeholder가 유일한 보이는 라벨, 선택 입력 표시 없음 | Warning | Level A | 3.3.2 Labels or Instructions |

`aria-label`이 있어 입력 칸의 이름 자체는 있습니다(4.1.2 Pass).

### 2. 원인 및 맥락 분석
저시력 사용자는 입력 칸의 경계와 힌트를 찾기 어렵습니다. 글자를 입력하면 힌트가 사라져, 인지 장애가 있는 사용자는 무엇을 쓰는 칸인지 잊을 수 있습니다. 입력이 선택 사항이라는 점도 보이지 않습니다.

### 3. 개선안
- **디자인/컬러**:

| 요소 | Before | After |
| --- | --- | --- |
| placeholder | `#757575` 가정, 약 2.3~2.9:1(추정) | `#D8B6BA`, 최저 약 5.6:1(추정) |
| 테두리 | `rgba(251,247,242,.25)`, 바깥 배경 대비 약 2.3~2.5:1, 안쪽 대비 약 1.9:1(추정) | `#D8B6BA`, 바깥 약 6.7:1, 안쪽 약 5.6:1(추정) |

- **코드(HTML/ARIA)**:

```html
<!-- Before -->
<input class="field" id="name" placeholder="이름 또는 별명" aria-label="이름 또는 별명" maxlength="12">
```
```html
<!-- After -->
<label class="field-label" for="name">이름 또는 별명 (선택)</label>
<input class="field" id="name" autocomplete="nickname" maxlength="12" aria-describedby="nameHint">
<p class="muted" id="nameHint">12자까지 쓸 수 있어요</p>
```
```css
.field { border-color: var(--on-dark-muted); }
.field::placeholder { color: var(--on-dark-muted); opacity: 1; }
```

`.shimmer`의 애니메이션 순서는 자식이 5개일 때까지만 지정되어 있어, 요소를 늘리면 `nth-child` 규칙도 함께 늘려야 합니다.

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. Tab: "이름 또는 별명 (선택), 편집창, 12자까지 쓸 수 있어요"
2. Tab: "입장하기, 버튼"

---

## 🟡 문제 9. 탭 힌트가 깜빡일 때 대비가 기준 아래로 떨어짐

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| `.tap-hint`의 `opacity:.4`(139~140행) | Fail(추정) | Level AA | 1.4.3 Contrast (Minimum) |

### 2. 원인 및 맥락 분석
14px 안내 문구가 2초 주기로 흐려집니다. 저시력 사용자는 다음 행동을 알려 주는 유일한 문구를 읽기 어렵습니다.

### 3. 개선안
- **디자인/컬러**: 글자색 `#D8B6BA`의 불투명도만 조정합니다.

| Before | After |
| --- | --- |
| `opacity:.4`, 최저 약 2.1~2.4:1(추정) | `opacity:.8`, 가장 밝은 배경 `#6A0D1E`에서 약 4.7:1(추정) |

- **코드(HTML/ARIA)**:

```css
/* Before */
@keyframes breathe { 50% { opacity: .4; } }
/* After */
@keyframes breathe { 50% { opacity: .8; } }
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
음성 흐름은 바뀌지 않습니다.
1. 포커스가 카드로 이동: "카드를 눌러 뒤집기, 버튼"
2. 가상 커서로 다음 항목: "카드를 눌러 뒤집어 보세요"

---

## 🟡 문제 10. 영어 문구에 언어 표시가 없음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| `TODAY'S TAROT`, `SHUFFLING`, `LUCK KEPT`, 카드 이름 | Fail | Level AA | 3.1.2 Language of Parts |
| 문서 언어 `lang="ko"` | Pass | Level A | 3.1.1 Language of Page |

### 2. 원인 및 맥락 분석
페이지 전체가 한국어로 지정되어 있어, 영어 문구가 한국어 음성으로 어색하게 읽히거나 철자 단위로 읽힐 수 있습니다. `XIX` 같은 로마 숫자도 의미가 전달되기 어렵습니다.

### 3. 개선안
- **디자인/컬러**: 변경 없음
- **코드(HTML/ARIA)**:

```html
<!-- Before -->
<span class="eyebrow">TODAY'S TAROT</span>
<div class="reveal r-title" style="--i:0" id="rTitle"></div>
```
```html
<!-- After -->
<span class="eyebrow" lang="en">TODAY'S TAROT</span>
<div class="reveal r-title" style="--i:0" id="rTitle" lang="en"></div>
```

`SHUFFLING`, `.stamp`, `#cNum`, `#cName`에도 `lang="en"`을 답니다. `rTitle`은 로마 숫자를 `aria-hidden`으로 숨기고 `.sr-only`로 "19번"을 넣는 구조를 권합니다. 이때 "19번"에는 `lang="ko"`를 답니다.

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. `s1`: "Today's Tarot"(영어 음성)
2. "오늘의 카드가 당신을 기다려요, 제목 1"
3. 결과: "19번"(한국어 음성), "The Sun"(영어 음성)

---

## 🟢 문제 11. 진행 표시가 시각 전용이고 대비가 낮음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| `aria-hidden`이고 텍스트 없음(269행) | Warning | Level A | 1.3.1 Info and Relationships |
| 비활성 막대 대비 약 1.7:1(추정) | Warning | Level AA | 1.4.11 Non-text Contrast |

### 2. 원인 및 맥락 분석
3px 막대라 저시력 사용자에게 잘 보이지 않고, 스크린 리더 사용자는 진행 단계를 알 수 없습니다. 흐름을 이해하는 데 꼭 필요한 정보는 아니어서 Warning으로 봤습니다.

### 3. 개선안
- **디자인/컬러**: 막대는 장식으로 두고 `#D8B6BA` 글자를 더합니다. 배경 대비는 약 8.5:1 이상입니다(추정).
- **코드(HTML/ARIA)**:

```html
<!-- Before: 막대만 있음 -->
<div class="progress" aria-hidden="true">...</div>
```
```html
<!-- After: go()에서 글자도 갱신 -->
<div class="progress" aria-hidden="true">...</div>
<p class="progress-text" id="stepText">5단계 중 2단계</p>
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 가상 커서로 첫 항목을 읽으면 "5단계 중 2단계"로 들립니다.
2. 포커스 요소가 아니므로 Tab 순서는 바뀌지 않습니다.

---

## 🟢 문제 12. `처음부터` 버튼이 작고 내용과 겹칠 수 있음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| 미션 패널과 겹칠 때 대비 약 1.7:1 | Warning(구현에서 확인 필요) | Level AA | 1.4.3 Contrast (Minimum) |
| 패딩 없는 13px, 높이 약 16~18px(추정) | Warning(AAA 권고) | AAA 참고 | 2.5.5 Target Size |

### 2. 원인 및 맥락 분석
손 떨림이 있는 사용자는 작은 버튼을 누르기 어렵습니다. 이 버튼은 화면에 고정되어 있어 작은 화면에서 밝은 미션 패널 위에 올라올 수 있습니다. 그러면 저시력 사용자가 글자를 읽기 어렵습니다.

### 3. 개선안
- **디자인/컬러**: 배경을 깔아 겹침과 관계없이 대비를 유지합니다.

| Before | After |
| --- | --- |
| `#D8B6BA` on `#FBF7F2`, 약 1.7:1(겹칠 때) | `#D8B6BA` on `#2A040C`, 약 10.1:1 |

- **코드(HTML/ARIA)**:

```css
/* Before */
.restart { background: none; }
```
```css
/* After */
.restart { background: var(--night); min-height: 44px; padding: 0 16px; border-radius: 999px; }
```

`.scene`의 아래쪽 여백도 버튼 높이만큼 늘려야 겹침이 줄어듭니다.

### 4. 스크린 리더/키보드 가상 시뮬레이션
1. 항상 마지막 Tab: "처음부터, 버튼"
2. Enter: "오늘의 카드가 당신을 기다려요, 제목 1"(문제 1 적용 시)

---

## 🟢 문제 13. 12~13px 글자가 많음

### 1. 진단 요약 표
| 항목 | 준수 여부 | 적용 등급 | WCAG 성공 기준 |
| --- | --- | --- | --- |
| `.eyebrow`, `.num`, `.r-mission b`(12px), `.name`, `.r-title`, `.restart`(13px) | Warning(권고) | 기준 없음 | 글자 크기 자체의 A·AA 기준은 없음 |

### 2. 원인 및 맥락 분석
작은 글자에 넓은 자간까지 더해져, 저시력 사용자나 고령 사용자가 읽기 어렵습니다. 특히 `이 운을 지키려면`은 장식이 아니라 실제 내용입니다.

### 3. 개선안
- **디자인/컬러**: 색 변경은 필요 없습니다. 현재 색은 모두 4.5:1 이상입니다.
- **코드(HTML/ARIA)**:

```css
/* Before */
.r-mission b { font-size: 12px; letter-spacing: .1em; }
.r-title { font-size: 13px; }
```
```css
/* After */
.r-mission-title { font-size: 14px; letter-spacing: .02em; }
.r-title { font-size: 14px; }
```

### 4. 스크린 리더/키보드 가상 시뮬레이션
음성 안내와 Tab 순서는 바뀌지 않습니다.

---

## 구현에서 확인 필요

통과로 판단하지 않은 항목입니다.

- **기본 포커스 링**: `.flip`, `.restart`, `#kept`는 포커스 스타일을 지정하지 않아 브라우저 기본값을 씁니다. 뒤집히는 카드에서 잘 보이는지 확인이 필요합니다.
- **`aria-live`**: `#reading`에 내용 4개가 연달아 들어갈 때 읽기가 끊기는지 확인이 필요합니다. 문제 4처럼 포커스를 옮기면 `aria-live`는 빼는 편이 중복 낭독을 막습니다.
- **장식 위 글자**: 601~800px 폭이나 낮은 화면에서 밝은 강아지(`#F3E6D8`)와 토끼(`#FBF0EE`) 위에 글자가 겹치면 대비가 크게 떨어집니다.
- **장식 노출**: `#sparks`와 `#deck` 안의 SVG에 `aria-hidden`이 없어 보조 기술에 노출되는지 확인이 필요합니다.
- **글자 간격(1.4.12)**: 크기가 고정된 카드 앞면과 스탬프에서 글자가 잘리는지 확인이 필요합니다.
- **고대비 모드**: `.glint`의 `color: transparent`가 Windows 고대비 모드에서 보이는지 확인이 필요합니다.
- **타이머 충돌**: 카드를 고른 뒤 1.4초 안에 `처음부터`를 누르면, 남은 타이머가 `s3`로 다시 이동시킬 것으로 보입니다. `clearTimeout`이 필요합니다.
- **페이지 제목(2.4.2)**: 단계가 바뀌어도 제목이 그대로입니다. 포커스 이동을 고친 뒤 추가할지 판단하면 됩니다.

## 기준을 충족한 대비

| 조합 | 대비 | 결과 |
| --- | --- | --- |
| `.btn`, 카드 글자, 미션 제목 `#C8102E` on `#FBF7F2` | 5.5:1 | Pass |
| 미션 본문 `#2A1A1C` on `#FBF7F2` | 15.6:1 | Pass |
| 본문 `#FBF0EE` on 배경 | 최저 약 11.1:1(추정) | Pass |
| 보조 글자 `#D8B6BA` on 배경 | 최저 약 6.7:1(추정) | Pass |
| 금색 글자와 포커스 링 `#E2C07A` on 배경 | 최저 약 7.1:1(추정) | Pass |

**한 줄 요약**: 색과 조작 요소의 기반은 좋지만, 장면 전환 시 포커스 관리와 뒤집기 전 숨은 체크박스를 먼저 고쳐야 키보드와 스크린 리더로 흐름을 제대로 따라갈 수 있습니다.

**잘 된 점**
- `button`, `input`, `label` 같은 기본 요소를 써서 조작 요소가 키보드로 닿는 구조이고, 확대를 막는 viewport 설정도 없습니다.
- `prefers-reduced-motion` 처리와 장식의 `aria-hidden`이 이미 적용되어 있고, 미션 라벨 영역은 최소 높이 44px를 확보했습니다.

**점검 파일**: `members/shin/tarot/prototype.html`

