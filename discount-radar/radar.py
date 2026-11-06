"""할인 레이더 공통 기능 3개. 조원 데이터가 어디서 왔든 표 모양만 같으면 똑같이 돈다.

표준 열 (adapter.py의 load()가 이 열을 돌려준다)
- name            상품 이름
- category        카테고리
- price           지금 파는 값 (원)
- original_price  할인 기준 값 (원). 정가가 없으면 조원이 정한 기준값(예: 같은 검색 결과 중간값), 그것도 없으면 빈칸
- review_count    리뷰 수. 모르면 비워 둔다
- url             상품 링크
- note            조건 (예: "카드 결제 시", "쿠폰 적용가"). 없으면 비워 둔다
"""
import pandas as pd

COLUMNS = ["name", "category", "price", "original_price", "review_count", "url", "note"]
REVIEW_MIN = 10  # 리뷰가 이보다 적으면 "확인 필요"로 표시한다
CATEGORY_MIN = 10  # 할인율을 아는 상품이 이보다 적은 카테고리는 평균이 흔들려 정답 후보에서 뺀다


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """빠진 열을 채우고, 숫자를 숫자로 바꾸고, 할인율과 확인 필요 표시를 붙인다."""
    df = df.copy()
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    for col in ["price", "original_price", "review_count"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce"
        )
    for col in ["name", "url", "note"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    df["category"] = df["category"].fillna("기타").astype(str).str.strip()
    df = df.dropna(subset=["price"])

    # 기준 값이 없으면 할인율을 "모름"(빈칸)으로 둔다. 0%(할인 안 함)와 다르다. 평균에서도 빠진다
    df["discount_rate"] = (
        ((df["original_price"] - df["price"]) / df["original_price"] * 100).clip(lower=0).round(1)
    )

    reasons = []
    for note, reviews in zip(df["note"], df["review_count"]):
        why = []
        if note:
            why.append(f"조건: {note}")
        if pd.notna(reviews) and reviews < REVIEW_MIN:
            why.append(f"리뷰 {int(reviews)}개")
        reasons.append(", ".join(why))
    df["caution"] = reasons
    return df


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    """① 카테고리별 평균 할인율. 할인율 높은 순."""
    cats = (
        df.dropna(subset=["discount_rate"])
        .groupby("category")
        .agg(평균할인율=("discount_rate", "mean"), 상품수=("name", "count"))
        .round(1)
        .sort_values("평균할인율", ascending=False)
    )
    enough = cats[cats["상품수"] >= CATEGORY_MIN]
    return enough if not enough.empty else cats  # 데이터가 적은 조원은 전부 보여 준다


def pick_by_budget(df: pd.DataFrame, budget: int, category: str | None, min_reviews: int) -> pd.DataFrame:
    """② 예산 안에서 할인율 높은 순 3개. 같으면 싼 것부터."""
    pool = df[df["price"] <= budget]
    if category:
        pool = pool[pool["category"] == category]
    if min_reviews:
        pool = pool[pool["review_count"].fillna(0) >= min_reviews]
    return pool.sort_values(["discount_rate", "price"], ascending=[False, True]).head(3)


def top5(df: pd.DataFrame) -> pd.DataFrame:
    """③ 할인율 큰 순 5개. caution 열에 너무 좋은 할인의 이유가 들어 있다."""
    return df[df["discount_rate"] > 0].sort_values("discount_rate", ascending=False).head(5)
