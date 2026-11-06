import os
import csv
import requests
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()

CLIENT_ID = os.getenv("SEATGEEK_CLIENT_ID", "").strip()


def export_giants_vs_dodgers_schedule():
    """
    SeatGeek 공식 API를 통해 로봇 차단 없이
    SF Giants vs LA Dodgers의 예정된 모든 경기(15개) 정보를 수집하여
    한글 깨짐 없는 CSV 파일로 저장합니다.
    """
    if not CLIENT_ID:
        print("❌ [오류] .env 파일에 SEATGEEK_CLIENT_ID가 설정되지 않았습니다.")
        return

    print("=" * 70)
    print("📡 [SeatGeek 공식 API] SF Giants vs LA Dodgers 경기 일정 수집 시작...")
    print("=" * 70)

    url = "https://api.seatgeek.com/2/events"
    params = {
        "client_id": CLIENT_ID,
        "performers.slug": "san-francisco-giants",
        "q": "Dodgers",
        "per_page": 50,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"❌ API 호출 실패 (상태코드: {response.status_code})")
            print(response.text)
            return
        data = response.json()
        events = data.get("events", [])
    except Exception as e:
        print(f"❌ 요청 중 오류 발생: {e}")
        return

    results = []
    game_count = 0

    for e in events:
        title = e.get("title", "")
        # Giants와 Dodgers 맞대결 경기만 선별
        if "Dodgers" in title and "Giants" in title:
            game_count += 1
            venue = e.get("venue", {})
            venue_name = venue.get("name", "경기장 미정")
            city = venue.get("city", "")
            state = venue.get("state", "")
            location = f"{venue_name} ({city}, {state})" if city else venue_name

            datetime_local = e.get("datetime_local", "")
            date_part = datetime_local[:10] if len(datetime_local) >= 10 else "날짜 미정"
            time_part = datetime_local[11:16] if len(datetime_local) >= 16 else "시간 미정"

            # 홈/원정 구분
            if "at San Francisco Giants" in title:
                home_team = "SF 자이언츠 (홈)"
            elif "at Los Angeles Dodgers" in title:
                home_team = "LA 다저스 (홈)"
            else:
                home_team = "중립/스프링캠프"

            # 이벤트 통계 (티켓 가격) 확인
            stats = e.get("stats", {}) or {}
            lowest_price = stats.get("lowest_price")
            highest_price = stats.get("highest_price")

            min_price_str = f"${lowest_price:,}" if lowest_price else "티켓 오픈 대기 중"
            max_price_str = f"${highest_price:,}" if highest_price else "티켓 오픈 대기 중"

            event_url = e.get("url", "") + "?quantity=1"

            results.append({
                "경기 번호": game_count,
                "경기명": title,
                "홈팀": home_team,
                "경기 날짜": date_part,
                "경기 시간": time_part,
                "경기장 위치": location,
                "티켓 최저가(추정)": min_price_str,
                "티켓 최고가(추정)": max_price_str,
                "좌석 및 티켓 확인 링크": event_url,
            })

    # 날짜 및 시간순 정렬
    results.sort(key=lambda x: (x["경기 날짜"], x["경기 시간"]))
    # 정렬 후 번호 재할당
    for idx, item in enumerate(results, 1):
        item["경기 번호"] = idx

    csv_filename = "sf_giants_vs_la_dodgers_schedule.csv"

    # 한글이 엑셀에서 깨지지 않도록 utf-8-sig 인코딩 적용
    fieldnames = [
        "경기 번호",
        "경기명",
        "홈팀",
        "경기 날짜",
        "경기 시간",
        "경기장 위치",
        "티켓 최저가(추정)",
        "티켓 최고가(추정)",
        "좌석 및 티켓 확인 링크"
    ]

    with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n🎉 총 {len(results)}개의 Giants vs Dodgers 예정 경기를 성공적으로 수집했습니다!")
    print(f"📁 CSV 파일 생성 완료: {os.path.abspath(csv_filename)}")
    print("-" * 70)
    for r in results:
        print(f"[{r['경기 번호']:02d}] {r['경기 날짜']} ({r['경기 시간']}) | {r['경기명']} @ {r['경기장 위치']}")
    print("=" * 70)


if __name__ == "__main__":
    export_giants_vs_dodgers_schedule()
