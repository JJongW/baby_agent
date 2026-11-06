"""그릇 수집 공통: 예절 규칙, 카테고리 나누기, CSV 저장."""
import csv
import re
from pathlib import Path

UA = "Mozilla/5.0 (compatible; discount-radar-study/0.1)"  # 봇임을 숨기지 않는다
DELAY = 1.5  # 요청 사이 쉬는 시간(초)
MAX_PAGES = 10  # 한 곳에서 최대 10페이지
DATA = Path(__file__).parent / "data"
FIELDS = ["name", "category", "price", "original_price", "review_count", "url", "note", "shop"]

# 쇼핑몰마다 카테고리 이름이 달라서 상품 이름의 낱말로 나눈다. 위에서부터 먼저 걸리는 것
CATEGORY_WORDS = [
    ("세트", ["홈세트", "세트", "set", "반상기"]),
    ("커트러리", ["커트러리", "수저", "스푼", "spoon", "포크", "나이프", "젓가락", "숟가락"]),
    ("컵/잔", ["머그", "컵", "잔", "텀블러", "글라스", "고블렛", "피처", "저그"]),
    ("볼/공기", ["보울", "볼", "공기", "대접", "면기", "국그릇", "찬기", "종지", "bowl", "우동기", "돈부리",
                "덴다시", "다완", "자무시", "탕기", "그라탕", "그릇"]),
    ("접시", ["접시", "플레이트", "plate", "디쉬", "디시", "dish", "쿠프", "굽부", "트레이", "쟁반"]),
]

# 그릇 쇼핑몰이 같이 파는 생활용품. 그릇 데이터에서 뺀다
NOT_TABLEWARE = ["샤워타월", "타월", "수건", "브러쉬", "화분", "알림판", "숄더백", "백시트", "가방", "매트", "장갑",
                 "팟홀더", "집게", "정리대", "주차", "세차", "슬리퍼", "앞치마"]


def is_tableware(name: str) -> bool:
    return not any(w in name for w in NOT_TABLEWARE)


def categorize(name: str) -> str:
    low = name.lower()
    for cat, words in CATEGORY_WORDS:
        if any(w in low for w in words):
            return cat
    return "기타"


def won(text: str | None) -> int | None:
    """'24,500원' -> 24500. 숫자가 없으면 None."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", str(text))
    return int(digits) if digits else None


def save(rows: list[dict], filename: str) -> Path:
    DATA.mkdir(exist_ok=True)
    path = DATA / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return path
