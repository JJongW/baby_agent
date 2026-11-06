"""할인 레이더: 조원 5명이 각자 모은 할인 데이터를 한 사이트에서 본다.

sources/<이름>/adapter.py 가 있는 폴더를 자동으로 찾아 사이드바에 올린다.
크롤링(API, requests, Playwright)은 각자 컴퓨터에서 돌려 CSV로 저장하고, 이 앱은 CSV만 읽는다.
그래야 배포된 사이트에 Playwright가 없어도, 수집처가 막혀도 시연이 된다.
"""
import importlib.util
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import folders
import radar

HERE = Path(__file__).parent
ALL = "전체 보기"

st.set_page_config(page_title="할인 레이더", page_icon="📡", layout="wide")
st.markdown(f"<style>{(HERE / 'theme.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data
def load_sources(version: float) -> tuple[dict, list]:  # version: 바뀐 시각. 밑줄로 시작하면 캐시 키에서 빠지니 주의
    """조원 폴더를 읽는다. 한 명이 깨져도 나머지는 뜨도록 오류는 모아서 돌려준다."""
    sources, errors = {}, []
    for adapter in sorted(HERE.glob("sources/*/adapter.py")):
        folder = adapter.parent
        try:
            spec = importlib.util.spec_from_file_location(f"src_{folder.name}", adapter)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            df = radar.normalize(mod.load())
            df["source"] = mod.TITLE
            sources[mod.TITLE] = {
                "df": df,
                "folder": folder.name,
                "where": getattr(mod, "SOURCE", ""),
                "method": getattr(mod, "METHOD", ""),
                "css": (folder / "style.css").read_text(encoding="utf-8") if (folder / "style.css").exists() else "",
            }
        except Exception as e:  # 조원 코드가 어떤 오류를 낼지 몰라 넓게 받는다
            errors.append(f"`{folder.name}`: {e}")
    return sources, errors


def newest_change() -> float:
    """조원 파일이나 공통 계산(radar.py)이 바뀌면 캐시를 새로 만든다."""
    files = [*HERE.glob("sources/**/*"), HERE / "radar.py"]
    return max((f.stat().st_mtime for f in files if f.is_file()), default=0.0)


def won(x: float) -> str:
    return f"{int(x):,}원"


sources, errors = load_sources(newest_change())

# 사이드바: 누구 데이터를 볼지
st.sidebar.title("할인 레이더")
choice = st.sidebar.radio("데이터 고르기", [ALL, *sources.keys()])
for err in errors:
    st.sidebar.warning(f"불러오지 못함 {err}")

if not sources:
    st.title("할인 레이더")
    st.info("아직 올라온 데이터가 없어요. `sources/<이름>/adapter.py`를 넣으면 여기에 나타나요.")
    st.stop()

if choice == ALL:
    df = pd.concat([s["df"] for s in sources.values()], ignore_index=True)
    where = ", ".join(f"{t} ({s['where']})" for t, s in sources.items() if s["where"])
    method = ", ".join(sorted({s["method"] for s in sources.values() if s["method"]}))
else:
    src = sources[choice]
    df = src["df"]
    where, method = src["where"], src["method"]
    if src["css"]:
        st.markdown(f"<style>{src['css']}</style>", unsafe_allow_html=True)

# 머리
st.title("할인 레이더")
st.caption("폴더를 열면 그 조원 데이터로 바뀌어요. 다시 닫으면 전체 보기.")
folders.show(sources, None if choice == ALL else choice, ALL)
st.caption(f"수집처: {where or '-'}  |  수집 방법: {method or '-'}")
c1, c2, c3 = st.columns(3)
c1.metric("상품 수", f"{len(df):,}개")
c2.metric("평균 할인율", f"{df['discount_rate'].mean():.1f}%")
c3.metric("카테고리", f"{df['category'].nunique()}개")

# ① 카테고리별 할인율
st.header("① 어느 카테고리가 할인을 가장 많이 할까")
cats = radar.by_category(df)
best = cats.index[0]
st.subheader(f"정답: **{best}** (평균 {cats.iloc[0]['평균할인율']}% 할인)")
chart = (
    alt.Chart(cats.reset_index())
    .mark_bar(cornerRadiusEnd=6, height=22)
    .encode(
        x=alt.X("평균할인율:Q", title="평균 할인율 (%)"),
        y=alt.Y("category:N", sort="-x", title=None),
        # 1등만 진하게, 나머지는 옅은 회색
        color=alt.condition(alt.datum.category == best, alt.value("#191f28"), alt.value("#b0b8c1")),
        tooltip=["category", "평균할인율", "상품수"],
    )
    .properties(height=48 * len(cats))
    .configure_axis(grid=False, labelColor="#4e5968", titleColor="#8b95a1", domain=False, ticks=False)
    .configure_view(stroke=None)
)
st.altair_chart(chart, use_container_width=True)
with st.expander("카테고리별 숫자 보기"):
    st.dataframe(cats, use_container_width=True)

# ② 예산으로 고르기
st.header("② 예산으로 고르기")
with st.form("budget"):
    a, b, c = st.columns(3)
    budget = a.number_input("예산 (원)", min_value=0, value=int(df["price"].median()), step=10000)
    category = b.selectbox("카테고리", ["상관없음", *sorted(df["category"].unique())])
    min_reviews = c.number_input("리뷰 최소 몇 개", min_value=0, value=0, step=10)
    st.form_submit_button("추천 받기", type="primary")

picks = radar.pick_by_budget(df, budget, None if category == "상관없음" else category, min_reviews)
if picks.empty:
    st.info("조건에 맞는 상품이 없어요. 예산을 늘리거나 조건을 풀어 보세요.")
else:
    for i, (col, (_, row)) in enumerate(zip(st.columns(3), picks.iterrows())):
        with col.container(key=f"pick_{i}"):
            st.markdown(f"**{row['name']}**")
            st.markdown(f"### {won(row['price'])}")
            if row["discount_rate"] > 0:
                st.markdown(f"~~{won(row['original_price'])}~~  **{row['discount_rate']}% 할인**")
            st.caption(f"{row['category']}  |  {row['source']}")
            if row["caution"]:
                st.markdown(f"<span class='chip'>확인 필요: {row['caution']}</span>", unsafe_allow_html=True)
            if row["url"]:
                st.link_button("보러 가기", row["url"])

# ③ 할인 TOP 5
st.header("③ 할인 TOP 5")
st.caption(f"조건이 붙었거나 리뷰가 {radar.REVIEW_MIN}개보다 적으면 ⚠️ 표시를 붙여요.")
top = radar.top5(df).copy()
top.insert(0, "", top["caution"].map(lambda x: "⚠️" if x else ""))
st.dataframe(
    top[["", "name", "category", "price", "original_price", "discount_rate", "caution", "source", "url"]],
    hide_index=True,
    use_container_width=True,
    column_config={
        "name": "상품",
        "category": "카테고리",
        "price": st.column_config.NumberColumn("지금 값(원)", format="localized"),
        "original_price": st.column_config.NumberColumn("기준 값(원)", format="localized"),
        "discount_rate": st.column_config.ProgressColumn("할인율", format="%.1f%%", min_value=0, max_value=100),
        "caution": "확인 필요 이유",
        "source": "누구 데이터",
        "url": st.column_config.LinkColumn("링크", display_text="열기"),
    },
)
