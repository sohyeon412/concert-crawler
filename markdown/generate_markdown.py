import json
from datetime import datetime
import os

# 📁 파일 경로 설정
CONCERT_FILE = os.path.join( "all_concerts.json")
OUTPUT_FILE = os.path.join("markdown", "concert_post.md")


def generate_markdown():
    if not os.path.exists(CONCERT_FILE):
        print("❗ 콘서트 데이터 파일이 없습니다.")
        return False

    with open(CONCERT_FILE, "r", encoding="utf-8") as f:
        concerts = json.load(f)

    # 📅 오늘 날짜
    today = datetime.today()
    date_str = today.strftime("%Y년 %m월 %d일")
    month_str = today.strftime("%m월")

    # 🎤 공연 있는 그룹만 필터링
    active_groups = [
        group for group, items in concerts.items()
        if any(c['status'] in ["판매중", "오픈예정", "판매예정"] for c in items)
    ]

    title_groups = ", ".join(active_groups)

    # 📝 마크다운 라인 구성
    lines = []

    # 제목 및 설명
    lines.append(f"# [{month_str} 최신] 아이돌 콘서트 티켓팅 일정 정리 – 판매중·예정 링크 포함 ({title_groups})\n")
    lines.append(f"📅 **{date_str} 기준으로 정리한 아이돌 콘서트 일정입니다.**")
    lines.append("판매중 및 판매예정 공연 위주로 작성되었습니다.")
    lines.append("")
    lines.append("> ⚠️ 일정은 변경될 수 있으니, 반드시 공식 예매처에서 최신 정보를 확인해주세요!")
    lines.append("\n---")

    # 그룹별 출력
    for idx, group in enumerate(active_groups):
        if idx > 0:
            lines.append("\n---")  # 그룹 사이에만 구분선

        lines.append(f"\n### 🎤 {group}\n")

        for concert in concerts[group]:
            if concert["status"] not in ["판매중", "오픈예정", "판매예정"]:
                continue

            lines.append(f"**🎫 {concert['title']}**")
            lines.append(f"- 📅 공연일: {concert['concert_date']}")

            if concert.get("booking_date") and concert["booking_date"] != "-":
                lines.append(f"- 🗓 예매일: {concert['booking_date']}")

            lines.append(f"- 📍 장소: {concert['place']}")
            lines.append(f"- 🏷 상태: {concert['status']}")
            lines.append(f"- 🔗 [예매 링크 바로가기]({concert['url']})")
            lines.append(f"- ✍️ 출처: {concert.get('source', '미확인')}")
            lines.append("")  # 각 공연 사이 간단한 줄바꿈

    # 하단 배너 & 해시태그
    lines.append("\n---")
    lines.append("📌 최신 촬영 장비가 필요하다면?")
    lines.append("👉 [모빌렌트 바로가기](https://smartstore.naver.com/movilrent)")
    lines.append("")
    lines.append("#모던빌리지 #최신촬영장비 #최신촬영장비추천 #촬영장비대여 #촬영장비렌탈 #카메라추천 #카메라렌탈 #카메라대여 #카메라렌즈추천 #카메라렌즈대여 #카메라렌즈렌탈 #홈마카메라 #홈마카메라추천 #홈마카메라렌탈 #홈마카메라대여 #콘서트캠코더 #콘서트캠코더추천 #콘서트캠코더대여 #콘서트캠코더렌탈 #카메라뉴스 #카메라소식 #캐논소식 #니콘소식 #소니뉴스 #소니소식 #사진잘찍는법")

    # 저장
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ 마크다운 생성 완료:", OUTPUT_FILE)
    return True
if __name__ == "__main__":
    generate_markdown()
