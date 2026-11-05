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
FRAME_HEIGHT = 860  # iframe은 높이를 정해야 한다. 노트북 화면 한 장 기준


@st.cache_data
def build_page() -> str:
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
    iframe { display: block; }
    </style>""",
    unsafe_allow_html=True,
)
components.html(build_page(), height=FRAME_HEIGHT, scrolling=False)
