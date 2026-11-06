"""오늘의 타로: Streamlit에서 prototype.html을 그대로 띄운다.

Streamlit의 HTML 조각(iframe)은 옆 폴더 파일을 읽지 못하므로,
이미지와 폰트를 data URI로 바꿔 한 덩어리 HTML로 넘긴다.
화면을 고칠 때는 prototype.html만 고치면 된다.
"""
import base64
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent
MIME = {".webp": "image/webp", ".png": "image/png", ".woff2": "font/woff2"}
FRAME_HEIGHT = 860  # 높이 값은 필수라 넣지만, 아래 CSS가 창 높이(100dvh)로 덮어쓴다


@st.cache_data
def build_page(version: float) -> str:
    """version: 화면 파일들이 마지막으로 바뀐 시각. 바뀌면 캐시를 새로 만든다.
    인자 이름을 밑줄로 시작하면 Streamlit이 캐시 키에서 빼 버리니 밑줄을 붙이지 않는다."""
    html = (HERE / "prototype.html").read_text(encoding="utf-8")
    # 폰트 미리 불러오기 줄은 iframe 안에서 쓸모가 없어 뺀다
    html = re.sub(r'<link rel="preload"[^>]*>\n?', "", html)

    def inline(match: re.Match) -> str:
        path = HERE / match.group(1)
        data = base64.b64encode(path.read_bytes()).decode()
        return f"data:{MIME[path.suffix]};base64,{data}"

    return re.sub(r'((?:assets/web|fonts)/[\w.-]+\.(?:webp|png|woff2))', inline, html)


st.set_page_config(page_title="오늘의 타로", page_icon="🃏", layout="wide")
st.markdown(
    """<style>
    header, footer, #MainMenu { visibility: hidden; height: 0; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background: #2A040C; }
    iframe { display: block; height: 100dvh !important; }
    </style>""",
    unsafe_allow_html=True,
)
def newest_change() -> float:
    """HTML, 그림, 폰트 중 가장 최근에 바뀐 시각."""
    files = [HERE / "prototype.html", *HERE.glob("assets/web/*"), *HERE.glob("fonts/*")]
    return max(f.stat().st_mtime for f in files)


components.html(build_page(newest_change()), height=FRAME_HEIGHT, scrolling=False)
