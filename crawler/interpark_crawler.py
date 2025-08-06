import sys
sys.stdout.reconfigure(encoding='utf-8')

import unicodedata
import argparse
import firebase_admin
from firebase_admin import credentials, firestore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timezone
import json
import os

# ✅ 제목 정규화 함수
def normalize_title(title):
    return unicodedata.normalize("NFKC", title)

# ✅ 날짜 지난 공연 필터 함수
def is_past(concert_date_str):
    try:
        first_date = concert_date_str.split("~")[0].strip()
        concert_date = datetime.strptime(first_date.replace(".", "-"), "%Y-%m-%d").date()
        return concert_date < datetime.today().date()
    except:
        return False

# ✅ 인자 파싱
parser = argparse.ArgumentParser()
parser.add_argument('--artists', nargs='*', help='크롤링할 아이돌 리스트')
args = parser.parse_args()

default_artists = [
    "하츠투하츠", "키키", "뉴비트", "코스모시", "스트레이 키즈"
"아이브", "보이넥스트도어", "플레이브", "라이즈", "엔믹스"
"데이식스", "리센느", "뉴진스", "블랙핑크", "방탄소년단"
"세븐틴", "엔시티", "에스파", "르세라핌", "투모로우바이투게더"
"아이유", "비투비", "더보이즈", "몬스타엑스", "트와이스"
"김세정", "김재환", "골든차일드", "뉴이스트", "영파씨"
"베이비몬스터", "아이들", "엔하이픈", "드림캐쳐", "라잇썸"
"샤이니", "레드벨벳", "블락비", "비비지", "브브걸"
"빌리", "에이티즈", "소녀시대", "있지", "스테이씨"
"슈퍼주니어", "온앤오프", "아스트로", "아이즈원", "투어스"
"트리플에스", "박지훈", "빅톤", "아이콘", "악뮤"
"에스에프나인", "에이티투메이저", "에이비식스", "에이핑크", "엑소"
"마마무", "엔플라잉", "여자친구", "오마이걸", "키스오브라이프"
"강다니엘", "원어스", "원호", "위너", "위아이"
"위클리", "이달의 소녀", "이승윤", "전소미", "정세운"
"갓세븐", "조유리", "최예나", "케플러", "크래비티"
"클라씨", "츄", "투피엠", "트레저", "티엔엑스"
"퍼플키스", "펜타곤", "프로미스나인", "하성운", "하이라이트"
"우주소녀", "김우석", "임영웅", "베리베리", "엑스디너리 히어로즈"
"싸이커스", "제로베이스원", "하이키", "루시", "이펙스"
"이븐", "미야오", "이즈나", "아홉", "올데이 프로젝트"
"아일릿", "킥플립", "캣츠아이", "에잇턴", "앤팀"
"카드", "Hearts2Hearts", "KiiiKiii", "cosmosy", "NCT 127"
"NCT DREAM", "i-dle", "CLASS:y", "Chuu", "Xdinary Heroes"
"xikers", "H1-KEY", "MEOVV", "izna", "AHOF"
"ALLDAY PROJECT", "ILLIT", "KickFlip", "KATSEYE", "8TURN"

]
artists = args.artists if args.artists else default_artists

# ✅ Firebase 초기화
cred = credentials.Certificate("firebase/idol-ticket-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

today = datetime.now().strftime("%Y-%m-%d")

# ✅ 기존 데이터 불러오기
def get_existing_data():
    all_concerts = {}
    excluded_keys = {}

    for doc in db.collection("concerts").stream():
        artist = doc.id
        concerts = doc.to_dict().get("concert_list", [])
        all_concerts[artist] = concerts

    for doc in db.collection("excluded").stream():
        artist = doc.id
        excluded_list = doc.to_dict().get("excluded_list", [])
        excluded_keys[artist] = {
            (normalize_title(item["title"]), item["concert_date"])
            for item in excluded_list
            if isinstance(item, dict) and "title" in item and "concert_date" in item
        }

    existing_dict = {
        artist: {
            (normalize_title(item["title"]), item["concert_date"]): item
            for item in concerts
        }
        for artist, concerts in all_concerts.items()
    }

    return all_concerts, excluded_keys, existing_dict

all_concerts, excluded_keys, existing_dict = get_existing_data()

# ✅ 크롬 드라이버 설정
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

for artist in artists:
    url = f"https://tickets.interpark.com/contents/search?keyword=\"{artist}\""
    driver.get(url)
    time.sleep(2)

    try:
        while True:
            try:
                more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="티켓 더보기"]')))
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(2)
            except:
                break

        try:
            group = driver.find_element(By.CSS_SELECTOR, ".search-artist_name__LgP3C").text.strip()
            group = group.replace("가수", "").replace("\n", "").strip()
        except:
            group = artist

        if group not in all_concerts:
            all_concerts[group] = []
        if group not in excluded_keys:
            excluded_keys[group] = set()
        if group not in existing_dict:
            existing_dict[group] = {}

        new_concerts = []
        new_excluded = []

        new_concerts_set = set()

        ticket_items = driver.find_elements(By.CSS_SELECTOR, 'a[class^="TicketItem_ticketItem__"]')
        for item in ticket_items:
            try:
                prd_no = item.get_attribute("data-prd-no")
                href = f"https://tickets.interpark.com/goods/{prd_no}" if prd_no else "-"
                title = item.find_element(By.CSS_SELECTOR, "li[class*=TicketItem_goodsName]").text.strip()
                normalized_title = normalize_title(title)
                concert_date = item.find_element(By.CSS_SELECTOR, "li[class*=TicketItem_playDate]").text.strip()
                key = (normalized_title, concert_date)

                if is_past(concert_date):
                    continue

                place = item.find_element(By.CSS_SELECTOR, "li[class*=TicketItem_placeName]").text.strip()
                booking_date = "-"
                status = "판매중"

                if "판매종료" in item.text:
                    status = "판매종료"
                elif "판매예정" in item.text:
                    status = "판매예정"
                elif "오픈예정" in item.text:
                    status = "오픈예정"

                if status == "판매종료":
                    continue

                if key in existing_dict[group]:
                    existing = existing_dict[group][key]
                       # 기존 정보랑 비교해서 완전히 같으면 넘어감
                    if (
                      concert_date == existing["concert_date"] and
                      status == existing["status"] and
                      place == existing["place"] and
                      booking_date == existing.get("booking_date", "-") and
                       href == existing.get("url", "-")
                 ):
                      continue  # 변화 없음 → 저장 안 함
                      # 그 외에는 업데이트로 간주해서 아래로 진행 (덮어쓰기)

                allow = False
                if href != "-":
                    try:
                        driver.execute_script("window.open(arguments[0]);", href)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)

                        banned = ["뮤지컬", "스포츠", "전시/행사", "클래식/무용", "아동/가족", "연극", "레저/캠핑", "토핑", "MD shop", "오페라", "클레식", "무용", "레저", "무용/전통예술", "전통예술", "아동", "가족"]
                        tags = driver.find_elements(By.CSS_SELECTOR, "div.tagText span")
                        tag_texts = [tag.text.strip() for tag in tags]
                        allow = "콘서트" in tag_texts


                        if not allow:
                            excluded_keys[group].add(key)
                            new_excluded.append({"title": title, "concert_date": concert_date})
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            continue

                        if status in ["오픈예정", "판매예정"]:
                            titles = driver.find_elements(By.CSS_SELECTOR, "p.openGuideTitle")
                            times = driver.find_elements(By.CSS_SELECTOR, "p.openGuideTime")
                            for t, d in zip(titles, times):
                                if "티켓오픈" in t.text:
                                    booking_date = d.text.strip()
                                    break

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except:
                        try:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                        continue

                concert = {
                    "title": title,
                    "concert_date": concert_date,
                    "booking_date": booking_date,
                    "place": place,
                    "status": status,
                    "url": href,
                    "source": "인터파크" if "interpark.com" in href else "기타",
                    "saved_at": today
                }

                # ✅ 중복 콘서트 방지
                if any(
                    normalize_title(c.get("title", "")) == normalized_title and c.get("concert_date", "") == concert_date
                    for c in all_concerts[group]
                ):
                    continue


                new_concerts.append(concert)
                all_concerts[group].append(concert)
                existing_dict[group][key] = concert

            except Exception as e:
                print("❗ 항목 오류:", e)
                continue

        if new_concerts:
            db.collection("concerts").document(group).set({"concert_list": all_concerts[group]})
            print(f"🆕 {group}: {len(new_concerts)}개 새로 저장 또는 갱신됨")
        else:
            print(f"✅ {group}: 새 항목 또는 변경 사항 없음")

        # ✅ excluded 저장 (지난 공연 제외)
        existing_doc = db.collection("excluded").document(group).get()
        existing_excluded = set()
        if existing_doc.exists:
            raw_list = existing_doc.to_dict().get("excluded_list", [])
            for item in raw_list:
                if isinstance(item, dict) and "title" in item and "concert_date" in item:
                    if not is_past(item["concert_date"]):
                        normalized = normalize_title(item["title"])
                        existing_excluded.add((normalized, item["concert_date"]))

        merged_excluded = existing_excluded.union({
            (normalize_title(t), d) for (t, d) in excluded_keys[group] if not is_past(d)
        })

        db.collection("excluded").document(group).set({
            "excluded_list": [{"title": t, "concert_date": d} for (t, d) in merged_excluded]
        })
        print(f"📁 excluded 저장됨 → {group}: {len(merged_excluded)}개 (지나간 공연 제외됨)")

    except Exception as e:
        print(f"❗ {artist} 오류:", e)

print("🎉 Firebase 기준 크롤링 완료!")
driver.quit()

# ✅ 마지막 크롤링 시간 저장
now_str = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
db.collection("metadata").document("last_updated").set({"timestamp": now_str})
print(f"🕒 마지막 크롤링 시간 기록됨 (KST): {now_str}")

# ✅ 로컬 JSON 파일로 저장
with open("all_concerts.json", "w", encoding="utf-8") as f:
    json.dump(all_concerts, f, ensure_ascii=False, indent=2)

print("💾 all_concerts.json 저장 완료!")
