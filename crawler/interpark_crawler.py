import sys
sys.stdout.reconfigure(encoding='utf-8')  # ✅ 콘솔 출력을 UTF-8로 재설정

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from datetime import datetime
import os


# ✅ 아이돌 리스트
artists = [
    "방탄소년단", "블랙핑크", "뉴진스", "아이브", "르세라핌",
    "엔하이픈", "투모로우바이투게더", "세븐틴", "스트레이 키즈", "에스파",
    "있지", "트와이스", "레드벨벳", "샤이니", "NCT 127",
    "NCT DREAM", "보이넥스트도어", "제로베이스원", "에이티즈", "(여자)아이들", "플레이브"
]

SAVE_PATH = "all_concerts.json"
EXCLUDED_PATH = "excluded_concerts.json"
today = datetime.now().strftime("%Y-%m-%d")

# ✅ 기존 데이터 불러오기
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        all_concerts = json.load(f)
else:
    all_concerts = {}

# ✅ 제외된 항목 불러오기
if os.path.exists(EXCLUDED_PATH):
    with open(EXCLUDED_PATH, "r", encoding="utf-8") as f:
        excluded_concerts = json.load(f)
        excluded_keys = {artist: {tuple(item) for item in items} for artist, items in excluded_concerts.items()}
else:
    excluded_concerts = {}
    excluded_keys = {artist: set() for artist in artists}

# ✅ 기존 콘서트 중복 확인용 세트
existing_keys = {
    artist: {(item["title"], item["concert_date"]) for item in concerts}
    for artist, concerts in all_concerts.items()
}

# ✅ 크롬 드라이버 설정
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

for artist in artists:
    url = f"https://tickets.interpark.com/contents/search?keyword={artist}"
    driver.get(url)
    time.sleep(2)

    try:
        # 판매종료 보기 버튼 클릭
        try:
            close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"판매종료 공연 보기")]')))
            driver.execute_script("arguments[0].click();", close_btn)
            time.sleep(2)
        except:
            pass

        # 티켓 더보기 반복 클릭
        while True:
            try:
                more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="티켓 더보기"]')))
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(2)
            except:
                break

        # 그룹 이름 파싱
        try:
            group = driver.find_element(By.CSS_SELECTOR, ".search-artist_name__LgP3C").text.strip()
            group = group.replace("가수", "").replace("\n", "").strip()
        except:
            group = artist

        if group not in all_concerts:
            all_concerts[group] = []
            existing_keys[group] = set()
        if group not in excluded_keys:
            excluded_keys[group] = set()

        new_count = 0

        # ✅ 공연 항목 리스트
        ticket_items = driver.find_elements(By.CSS_SELECTOR, 'a[class^="TicketItem_ticketItem__"]')
        for item in ticket_items:
            try:
                prd_no = item.get_attribute("data-prd-no")
                href = f"https://tickets.interpark.com/goods/{prd_no}" if prd_no else "-"
                title = item.find_element(By.CSS_SELECTOR, "li[class*=TicketItem_goodsName]").text.strip()
                concert_date = item.find_element(By.CSS_SELECTOR, "li[class*=TicketItem_playDate]").text.strip()
                key = (title, concert_date)

                # ✅ 중복 또는 제외된 항목이면 건너뜀
                if key in existing_keys[group] or key in excluded_keys[group]:
                    continue

                place = item.find_element(By.CSS_SELECTOR, "li[class*=TicketItem_placeName]").text.strip()
                booking_date = "-"  # 기본값
                status = "판매중"

                if "판매종료" in item.text:
                    status = "판매종료"
                elif "판매예정" in item.text:
                    status = "판매예정"
                elif "오픈예정" in item.text:
                    status = "오픈예정"

                # ✅ 상세 페이지 진입
                if href != "-":
                    try:
                        driver.execute_script("window.open(arguments[0]);", href)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)

                        # ✅ 콘서트 필터링
                        allow = False
                        banned = ["뮤지컬", "스포츠", "전시/행사", "클래식/무용", "아동/가족", "연극", "레저/캠핑", "토핑", "MD shop", "오페라", "클레식", "무용"]
                        tags = driver.find_elements(By.CSS_SELECTOR, "div.tagText span")
                        if not tags:
                            allow = True
                        else:
                            tag_texts = [tag.text.strip() for tag in tags]
                            if "콘서트" in tag_texts or not any(tag in banned for tag in tag_texts):
                                allow = True

                        if not allow:
                            print(f"🚫 제외됨: {title} - {concert_date}")
                            excluded_keys[group].add(key)
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            continue

                        # ✅ 예매일 추출 (예정된 경우)
                        if status in ["오픈예정", "판매예정"]:
                            titles = driver.find_elements(By.CSS_SELECTOR, "p.openGuideTitle")
                            times = driver.find_elements(By.CSS_SELECTOR, "p.openGuideTime")
                            for t, d in zip(titles, times):
                                if "티켓오픈" in t.text:
                                    booking_date = d.text.strip()
                                    break

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    except Exception as e:
                        print(f"❗ 상세 페이지 오류: {e}")
                        try:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                        continue

                # ✅ 저장
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
                all_concerts[group].append(concert)
                existing_keys[group].add(key)
                new_count += 1

            except Exception as e:
                print("❗ 항목 오류:", e)
                continue

        if new_count:
            print(f"🆕 {group}: {new_count}개 추가됨")
        else:
            print(f"✅ {group}: 새 항목 없음")

    except Exception as e:
        print(f"❗ {artist} 오류:", e)

# ✅ 콘서트 저장
with open(SAVE_PATH, "w", encoding="utf-8") as f:
    json.dump(all_concerts, f, ensure_ascii=False, indent=2)

# ✅ 제외된 항목 저장
excluded_concerts = {k: list(v) for k, v in excluded_keys.items() if v}
with open(EXCLUDED_PATH, "w", encoding="utf-8") as f:
    json.dump(excluded_concerts, f, ensure_ascii=False, indent=2)

print("🎉 전체 완료!")
driver.quit()
