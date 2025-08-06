import json
import hashlib
import os
import subprocess
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Firebase 초기화
def init_firebase():
    cred_path = os.path.join("firebase", "idol-ticket-firebase-adminsdk.json")
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# ✅ 크롤링 결과 불러오기
def load_crawled_concerts():
    path = "all_concerts.json"
    if not os.path.exists(path):
        print("❌ 크롤링 결과 파일이 존재하지 않습니다.")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ concert_list 정렬 함수
def sort_concert_list(clist):
    if isinstance(clist, list):
        return sorted(clist, key=lambda x: json.dumps(x, sort_keys=True))
    return clist

# ✅ 해시 계산
def compute_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

# ✅ 이전 해시 불러오기
def load_previous_hash():
    path = "concert_hash.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ✅ 해시 저장
def save_current_hash(hash_dict):
    with open("concert_hash.json", "w", encoding="utf-8") as f:
        json.dump(hash_dict, f, ensure_ascii=False, indent=2)

# ✅ 마크다운 생성
def run_markdown_script():
    try:
        print("📄 마크다운 생성 중...")
        subprocess.run(["python", os.path.join("markdown", "generate_markdown.py")], check=True)
        print("✅ 마크다운 생성 완료!")
    except subprocess.CalledProcessError as e:
        print("❌ 마크다운 생성 실패:", e)

# ✅ 유효한 콘서트가 있는지 확인
def has_valid_concert(concerts):
    for concert_list in concerts.values():
        if concert_list:  # 하나라도 콘서트 있으면 True
            return True
    return False

# ✅ 메인 실행
def main():
    concerts = load_crawled_concerts()
    if not concerts:
        return

    old_hashes = load_previous_hash()
    new_hashes = {}
    changed = False

    for artist, concert_list in concerts.items():
       sorted_list = sort_concert_list(concert_list)

      # + saved_at 제거
    cleaned_list = [
           {k: v for k, v in item.items() if k != "saved_at"}
            for item in sorted_list
        ]

         # + 변경: 정제된 리스트로 해시 계산
    hash_val = compute_hash(cleaned_list)
       
          # 해시 저장용 딕셔너리에 기록
    new_hashes[artist] = hash_val


    if old_hashes.get(artist) != hash_val:
            print(f"✨ {artist} 변경 감지됨 → Firebase 저장")
            db.collection("concerts").document(artist).set({"concert_list": sorted_list})
            changed = True
    else:
            print(f"😴 {artist} 변경 없음")

    if changed and has_valid_concert(concerts):
        save_current_hash(new_hashes)
        run_markdown_script()
    elif changed:
        save_current_hash(new_hashes)
        print("😶 콘서트는 없지만 아티스트 정보 변경됨 → 마크다운은 생략")
    else:
        print("🛌 전체적으로 변경 없음 → 마크다운 생략")

if __name__ == "__main__":
    main()
