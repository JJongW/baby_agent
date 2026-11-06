"""조원 데이터를 유리 폴더 카드로 보여 준다.

components/glass_folder/glass-folder-cards.tsx 는 받은 React 컴포넌트 그대로다.
이 앱은 Streamlit(파이썬)이라 빌드 도구가 없으므로, 페이지 안에서 CDN의 React와 Babel로
TSX를 바로 돌린다. 폴더 = 조원 데이터 한 묶음, 폴더 속 종이 = 할인 큰 상품.

폴더를 열면 사이드바의 같은 이름 항목을 대신 눌러 화면 전체가 그 데이터로 바뀐다.
(components.html 은 값을 돌려주지 못해서 같은 출처인 부모 문서의 라디오를 누르는 방식)
바꿀 시점: 이 방식이 Streamlit 버전에서 막히면 declare_component 로 양방향 컴포넌트를 만든다.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit.components.v1 as components

TSX = (Path(__file__).parent / "components" / "glass_folder" / "glass-folder-cards.tsx").read_text(encoding="utf-8")
CARD_W = 240
PER_ROW = 3
ROW_H = 300  # 폴더 높이 + 열었을 때 종이가 위로 올라오는 자리

# 무채색 그림: 토스 회색 단계를 대리석처럼 섞는다. 폴더마다 seed만 다르다
GREY_ART = {
    "style": "marble",
    "colors": ["#191f28", "#333d4b", "#6b7684", "#b0b8c1", "#e5e8eb", "#f9fafb"],
    "scale": 0.7,
    "warp": 3.2,
    "angle": 0.6,
    "gloss": 0.45,
    "veins": 0.35,
}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
  body { margin: 0; background: transparent; }
  #root { display: flex; flex-wrap: wrap; gap: 24px; padding: 48px 4px 8px; }
  .gf-root { font-family: "Pretendard Variable", Pretendard, -apple-system, sans-serif !important; }
  .gf-sheet:focus-visible, .gf-key:focus-visible { outline-color: #191f28 !important; }
</style>
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.7/babel.min.js"></script>
</head><body><div id="root"></div>
<script id="tsx" type="text/plain">__TSX__</script>
<script>
const DATA = __DATA__;
const out = Babel.transform(document.getElementById("tsx").textContent, {
  filename: "glass-folder-cards.tsx",
  presets: ["typescript", "react"],
  plugins: ["transform-modules-commonjs"],
}).code;
const mod = { exports: {} };
new Function("require", "module", "exports", out)(() => React, mod, mod.exports);
const GlassFolder = mod.exports.default;

// 사이드바에서 같은 이름의 라디오를 찾아 누른다
function pick(title) {
  try {
    const labels = window.parent.document.querySelectorAll('[data-testid="stSidebar"] [role="radiogroup"] label');
    for (const l of labels) if (l.innerText.trim() === title) { l.click(); return; }
  } catch (e) { /* 부모 문서를 못 읽으면 사이드바로 고르면 된다 */ }
}

const h = React.createElement;
ReactDOM.createRoot(document.getElementById("root")).render(
  h(React.Fragment, null, DATA.folders.map((f, i) => h(GlassFolder, {
    key: f.label,
    label: f.label,
    meta: f.meta,
    art: DATA.art,
    seed: i * 7 + 3,
    files: f.files,
    action: "none",
    width: DATA.width,
    tone: f.selected ? "dark" : "light",
    defaultOpen: f.selected,
    appear: !DATA.selected,
    appearDelay: i * 120,
    onOpenChange: (open) => pick(open ? f.label : DATA.all),
    onFileSelect: (file) => { if (file.url) window.open(file.url, "_blank", "noopener"); },
  })))
);
</script></body></html>"""


def show(sources: dict, selected: str | None, all_label: str) -> None:
    folders = []
    for title, src in sources.items():
        df = src["df"]
        top = df[df["discount_rate"] > 0].sort_values("discount_rate", ascending=False).head(4)
        folders.append({
            "label": title,
            "meta": f"{len(df)}개 상품" + (f", 평균 {avg:.0f}%" if pd.notna(avg := df["discount_rate"].mean()) else ""),
            "selected": title == selected,
            # 가장 큰 할인이 맨 앞(유리 쪽)에 오도록 거꾸로 넣는다
            "files": [
                {"name": r["name"], "meta": f"{r['discount_rate']:.0f}%", "url": r["url"]}
                for _, r in top.iloc[::-1].iterrows()
            ],
        })
    data = {"folders": folders, "art": GREY_ART, "width": CARD_W, "selected": selected, "all": all_label}
    html = PAGE.replace("__TSX__", TSX).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    rows = -(-len(folders) // PER_ROW)
    components.html(html, height=rows * ROW_H + 24, scrolling=False)
