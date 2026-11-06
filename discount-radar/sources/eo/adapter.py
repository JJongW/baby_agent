"""어: 야구 티켓 (SeatGeek 공식 API). 어가 만든 members/eo/eo_crawling_1106/ 의 원화 환산 CSV를 그대로 읽는다.

할인 데이터가 아니다: 경기마다 티켓 최저가와 최고가만 있고, 둘은 좌석이 달라 정가와 할인가로 볼 수 없다.
그래서 할인 비교 대신 어의 기획안(ticket_dashboard_prd.md)대로 만든 전용 화면 show()를 앱이 부른다.
가격은 모두 원화와 달러를 같이 적는다. 환율은 어가 CSV를 만들 때 쓴 값(아래 RATE)이다.
어 폴더는 고치지 않는다. 다시 받으려면 그 폴더에서 export_giants_dodgers_schedule.py 를 돌린다(.env에 키 필요).
"""
from pathlib import Path

import pandas as pd

TITLE = "야구 티켓"
SOURCE = "SeatGeek API"
METHOD = "API"

CSV = Path(__file__).parents[3] / "members" / "eo" / "eo_crawling_1106" / "sf_giants_vs_la_dodgers_schedule_ko.csv"
RATE = "1달러 = 1,355.10원 (2026-11-06 17:48 매매기준율, 어 기획안)"
# 어 기획안이 "가격 상승 주의"로 꼽은 경기: 5월, 7월, 8월의 주말 경기. 지난 시즌 기사에 기댄 추정이지 이 데이터로 나온 값이 아니다
WATCH_MONTHS = {5, 7, 8}


def number(col: pd.Series) -> pd.Series:
    """"$1,234", "135,510원" → 숫자."""
    return pd.to_numeric(col.astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce")


def games() -> pd.DataFrame:
    raw = pd.read_csv(CSV, encoding="utf-8-sig")
    df = pd.DataFrame({
        "경기": raw["경기 구분"],
        "홈팀": raw["홈팀"],
        "날짜": pd.to_datetime(raw["경기 일자"].str[:10]),
        "요일": raw["경기 일자"].str.extract(r"\((.)요일\)")[0],
        "주말": raw["주말 여부"] == "주말",
        "경기장": raw["경기장 위치"],
        "최저가_원": number(raw["티켓 최저가 (원화 환산)"]),
        "최저가_달러": number(raw["티켓 최저가 (USD)"]),
        "최고가_원": number(raw["티켓 최고가 (원화 환산)"]),
        "최고가_달러": number(raw["티켓 최고가 (USD)"]),
        "링크": raw["예매 바로가기 링크"],
    })
    df["상승 주의"] = df["주말"] & df["날짜"].dt.month.isin(WATCH_MONTHS)
    return df


def load() -> pd.DataFrame:
    """공통 앱 표준 열. 정가가 없어 할인율은 '모름'이 되고, 전체 보기 합계에서 빠진다."""
    df = games()
    return pd.DataFrame({
        "name": df["경기"] + " " + df["날짜"].dt.strftime("%Y-%m-%d"),
        "category": df["홈팀"],
        "price": df["최저가_원"],
        "url": df["링크"],
    })


def both(won: float, usd: float) -> str:
    """원화와 달러를 같이: 128,734원 ($95)"""
    return f"{int(won):,}원 (${int(usd):,})"


def day(row) -> str:
    return f"{row['날짜']:%Y-%m-%d} ({row['요일']})"


def show(st) -> None:
    """야구 티켓 전용 화면. 기획안 기능 4개: 최저가와 최고가 경기, 주말 TOP 3, 원화와 달러 동시 표기, 필터와 상승 주의 표시."""
    df = games()
    st.caption(f"할인 정보가 없는 데이터라 할인 비교 대신 티켓 값을 비교해요. 환율: {RATE}")

    # 기능 1. 시즌 최저가, 최고가 경기
    low = df[df["최저가_달러"] == df["최저가_달러"].min()]
    high = df[df["최고가_달러"] == df["최고가_달러"].max()]
    c1, c2 = st.columns(2)
    c1.metric("시즌 최저가", both(low.iloc[0]["최저가_원"], low.iloc[0]["최저가_달러"]))
    c1.caption(", ".join(low.apply(day, axis=1)) + f"  |  {low.iloc[0]['경기장']}")
    c2.metric("시즌 최고가", both(high.iloc[0]["최고가_원"], high.iloc[0]["최고가_달러"]))
    c2.caption(", ".join(high.apply(day, axis=1)))

    # 기능 2. 주말 경기 중 최고가가 가장 싼 3경기 (좋은 자리를 가장 싸게)
    st.header("주말에 좋은 자리를 가장 싸게")
    st.caption("토요일, 일요일 경기 중 최고가(좋은 자리)가 낮은 순이에요. 같으면 날짜가 빠른 순.")
    top = df[df["주말"]].sort_values(["최고가_달러", "날짜"]).head(3)
    for i, (col, (_, r)) in enumerate(zip(st.columns(3), top.iterrows())):
        with col.container(key=f"pick_{i}"):
            st.markdown(f"**{i + 1}위  {day(r)}**")
            st.markdown(f"### {both(r['최고가_원'], r['최고가_달러'])}")
            st.caption(f"{r['경기']}  |  {r['경기장']}")
            st.caption(f"최저가 {both(r['최저가_원'], r['최저가_달러'])}")
            st.link_button("좌석 보기", r["링크"])

    # 기능 3, 4. 전체 경기 표: 필터, 정렬, 원화와 달러 같이, 상승 주의 표시
    st.header(f"전체 {len(df)}경기")
    a, b, c = st.columns(3)
    home = a.selectbox("홈팀", ["전체", *sorted(df["홈팀"].unique())])
    when = b.selectbox("요일", ["전체", "주말", "주중"])
    order = c.selectbox("정렬", ["날짜순", "최저가 낮은 순", "최고가 낮은 순"])
    view = df
    if home != "전체":
        view = view[view["홈팀"] == home]
    if when != "전체":
        view = view[view["주말"] == (when == "주말")]
    view = view.sort_values({"날짜순": "날짜", "최저가 낮은 순": "최저가_달러", "최고가 낮은 순": "최고가_달러"}[order])
    table = pd.DataFrame({
        "": view["상승 주의"].map(lambda x: "🔥" if x else ""),
        "날짜": view.apply(day, axis=1),
        "경기": view["경기"],
        "홈팀": view["홈팀"],
        "경기장": view["경기장"],
        "최저가": [both(w, u) for w, u in zip(view["최저가_원"], view["최저가_달러"])],
        "최고가": [both(w, u) for w, u in zip(view["최고가_원"], view["최고가_달러"])],
        "링크": view["링크"],
    })
    st.dataframe(table, hide_index=True, use_container_width=True,
                 column_config={"링크": st.column_config.LinkColumn("링크", display_text="열기")})
    st.caption("🔥 가격 상승 주의: 5월, 7월, 8월 주말 경기. 지난 시즌 기사를 바탕으로 한 어 기획안의 추정이에요. "
               "이 데이터로 확인한 값은 아니에요.")
    st.caption("경기 시간은 원본에 시간대 오류(정규시즌이 현지 새벽 3시 30분)가 있어 어가 고칠 때까지 뺐어요.")
