import os
import requests
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

CLIENT_ID = os.getenv("SEATGEEK_CLIENT_ID")
CLIENT_SECRET = os.getenv("SEATGEEK_CLIENT_SECRET")

EVENT_ID = "18381457"  # San Francisco Giants 경기 ID


def get_event_overview(event_id: str):
    if not CLIENT_ID:
        print("❌ [오류] .env 파일에 SEATGEEK_CLIENT_ID가 설정되지 않았습니다.")
        print("💡 .env 파일을 생성하고 발급받으신 클라이언트 아이디를 입력해 주세요.")
        return None

    url = f"https://api.seatgeek.com/2/events/{event_id}"
    params = {
        "client_id": CLIENT_ID.strip(),
    }

    print(f"📡 SeatGeek 공식 API 호출 중: 이벤트 ID {event_id}...")
    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        print(f"❌ API 호출 실패 (상태코드: {response.status_code})")
        print(response.text)
        return None

    data = response.json()
    title = data.get("title")
    venue = data.get("venue", {}).get("name")
    city = data.get("venue", {}).get("city")
    datetime_local = data.get("datetime_local")
    stats = data.get("stats", {})

    print("\n" + "=" * 60)
    print("🎫 [SeatGeek 공식 API - 이벤트 정보]")
    print(f"• 경기명: {title}")
    print(f"• 장소: {venue} ({city})")
    print(f"• 일시: {datetime_local}")
    print("-" * 60)
    print("📊 [가격 및 티켓 통계]")
    print(f"• 등록된 티켓 수: {stats.get('listing_count')} 개")
    print(f"• 최저 가격: ${stats.get('lowest_price')}")
    print(f"• 평균 가격: ${stats.get('average_price')}")
    print(f"• 최고 가격: ${stats.get('highest_price')}")
    print("=" * 60 + "\n")

    return data


if __name__ == "__main__":
    get_event_overview(EVENT_ID)
