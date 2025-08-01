# generate_markdown.py

import json
from datetime import datetime
import os

CONCERT_FILE = os.path.join("crawler", "all_concerts.json")
OUTPUT_FILE = os.path.join("markdown", "concert_post.md")

def generate_markdown():
    if not os.path.exists(CONCERT_FILE):
        print("❗ 콘서트 데이터 파일이 없습니다.")
        return False

    with open(CONCERT_FILE, "r", encoding="utf-8") as f:
        concerts = json.load(f)

    today = datetime.today()
    date_str = today.strftime("%Y년 %m월 %d일")
    month_str = today.strftime("%m월")

    # 공연 있는 그룹만 필터링
    active_groups = [
        group for group, items in concerts.items()
        if any(c['status'] in ["판매중", "오픈예정", "판매예정"] for c in items)
    ]

    title_groups = ", ".join(active_groups)

    lines = []
    lines.append(f"# [{month_str} 최신] 아이돌 콘서트 티켓팅 일정 정리 – 판매중·예정 링크 포함 ({title_groups})\n")
    lines.append("")
    lines.append(f"📅 **{date_str} 기준으로 정리한 아이돌 콘서트 일정입니다.**")
    lines.append("판매중 및 판매예정 공연 위주로 작성되었습니다.")
    lines.append("\n> ⚠️ 일정은 변경될 수 있으니, 반드시 공식 예매처에서 최신 정보를 확인해주세요!")
    lines.append("\n---")

    for group in active_groups:
        lines.append(f"\n## 🎤 {group}")
        for concert in concerts[group]:
            if concert["status"] not in ["판매중", "오픈예정", "판매예정"]:
                continue

            lines.append("\n---")
            lines.append(f"🎫 **{concert['title']}**")
            lines.append(f"📆 {concert['concert_date']}")
            if concert.get("booking_date") and concert["booking_date"] != "-":
                lines.append(f"🗓 예매일: {concert['booking_date']}")
            lines.append(f"📍 {concert['place']}")
            lines.append(f"🛒 {concert['status']}")
            lines.append(f"🔗 [예매 링크 바로가기]({concert['url']})")
            lines.append(f"✍️ 출처: {concert.get('source', '미확인')}")

    lines.append("\n---")
    lines.append("📌 최신 촬영 장비가 필요하다면?")
    lines.append("👉 [모빌렌트 바로가기](https://smartstore.naver.com/movilrent)")
    lines.append("\n#모던빌리지 #최신촬영장비 #홈마카메라 #콘서트캠코더 #카메라렌탈 …")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ 마크다운 생성 완료:", OUTPUT_FILE)
    return True
