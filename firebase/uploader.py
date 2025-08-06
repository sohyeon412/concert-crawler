# firebase/uploader.py
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# ✅ Firebase 초기화
cred = credentials.Certificate("C:/Users/user/idol-ticket-blog-generator/firebase/idol-ticket-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ all_concerts.json 업로드
if os.path.exists("all_concerts.json"):
    with open("all_concerts.json", "r", encoding="utf-8") as f:
        all_concerts = json.load(f)

    for artist, concerts in all_concerts.items():
        artist = artist.strip()
        if not artist:
            print("⚠️ 공백 아티스트 이름 건너뜀")
            continue

        try:
            db.collection("concerts").document(artist).set({
                "concert_list": concerts
            })
            print(f"✅ 공연 저장 완료: {artist}")
        except Exception as e:
            print(f"❗ 공연 업로드 오류 ({artist}):", e)

# ✅ excluded_concerts.json 업로드
if os.path.exists("excluded_concerts.json"):
    with open("excluded_concerts.json", "r", encoding="utf-8") as f:
        excluded = json.load(f)

    for artist, excluded_list in excluded.items():
        artist = artist.strip()
        if not artist:
            print("⚠️ 공백 아티스트 이름 건너뜀")
            continue

        # 🔧 각 항목을 {"title": ..., "concert_date": ...}로 변환
        flat_objects = []
        for item in excluded_list:
            if isinstance(item, list) and len(item) == 2:
                flat_objects.append({
                    "title": item[0],
                    "concert_date": item[1]
                })
            elif isinstance(item, dict) and "title" in item and "concert_date" in item:
                flat_objects.append(item)

        try:
            db.collection("excluded").document(artist).set({
                "excluded_list": flat_objects
            })
            print(f"✅ 제외 목록 저장 완료: {artist}")
        except Exception as e:
            print(f"❗ 제외 목록 업로드 오류 ({artist}):", e)

print("🎉 Firebase 초기 업로드 전체 완료")
