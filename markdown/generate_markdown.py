# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# 🔐 Firebase 초기화
cred_path = "C:/Users/user/idol-ticket-blog-generator/firebase/idol-ticket-firebase-adminsdk.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 📄 출력 마크다운 & 제목 파일 경로
OUTPUT_FILE = os.path.join("markdown", "concert_post.txt")
TITLE_FILE = os.path.join("markdown", "concert_title.txt")

def generate_markdown_from_firestore():
    concerts_ref = db.collection("concerts")
    docs = concerts_ref.stream()

    today = datetime.today()
    date_str = today.strftime("%Y년 %m월 %d일")
    month_str = today.strftime("%m월")

    active_groups = []
    group_data = {}

    for doc in docs:
        artist = doc.id
        data = doc.to_dict()
        concert_list = data.get("concert_list", [])

        active_concerts = [c for c in concert_list if c.get("status") in ["판매중", "오픈예정", "판매예정"]]
        if active_concerts:
            active_groups.append(artist)
            group_data[artist] = active_concerts

    # ✅ 제목은 최대 3개까지만
    title_groups_full = ", ".join(active_groups)
    title_groups_short = ", ".join(active_groups[:3]) + " 등"


    # 📝 제목 저장
    title_text = f"[{month_str} 최신] 아이돌 콘서트 티켓팅 일정 정리 - 판매중·예정링크 포함({title_groups_short})"
    with open(TITLE_FILE, "w", encoding="utf-8") as f:
        f.write(title_text)

    # 📝 본문 마크다운 구성
    lines = []
    lines.append(f"[{month_str} 최신] 아이돌 콘서트 티켓팅 일정 정리 🎫")
    lines.append(f"📅{date_str} 기준으로 정리한 아이돌 콘서트 일정입니다.**")
    lines.append("판매중 및 판매예정 공연 위주로 정리했어요.\n")
    lines.append("> ⚠️ 일정은 변경될 수 있으니, 반드시 공식 예매처에서 확인하세요.\n")
    lines.append(f"🎤 이번 달 활동 아이돌: {title_groups_full}")
    lines.append("")

    for group in active_groups:
        lines.append("\n---\n")
        lines.append(f"[🎤 {group}]")
        for concert in group_data[group]:
            lines.append("")
            lines.append(f"📌 {concert.get('title', '제목 없음')}")
            lines.append(f"📅 공연일: {concert.get('concert_date', '정보 없음')}")
            if concert.get("booking_date") and concert["booking_date"] != "-":
                lines.append(f"🗓 예매일: {concert['booking_date']}")
            lines.append(f"📍 장소: {concert.get('place', '정보 없음')}")
            lines.append(f"🏷 상태: {concert.get('status')}")
            lines.append(f"🔗 [예매 링크 바로가기] {concert.get('url', '#')}")
            lines.append(f"✍️ 출처: {concert.get('source', '미확인')}")
            lines.append("")

    # 📣 광고 영역
    lines.append("\n---\n")
    lines.append("📸 최신 촬영 장비가 필요하다면?")
    lines.append("👉 [모빌렌트 바로가기] https://smartstore.naver.com/movilrent \n")

    # 💾 마크다운 저장
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ Firebase에서 마크다운 & 제목 생성 완료:")
    print(f"   - 본문: {OUTPUT_FILE}")
    print(f"   - 제목: {TITLE_FILE}")

# ▶️ 실행 시작
if __name__ == "__main__":
    generate_markdown_from_firestore()
