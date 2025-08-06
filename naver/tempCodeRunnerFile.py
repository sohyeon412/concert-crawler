from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import pyautogui
import pyperclip

# ✅ 입력할 제목
with open("markdown/concert_title.txt", "r", encoding="utf-8") as f:
    title = f.read().strip()

# ✅ 본문 내용을 markdown 파일에서 읽기
with open("markdown/concert_post.md", "r", encoding="utf-8") as f:
    body = f.read()

# ✅ 해시태그 (원한다면 여기에 추가)
hashtags = "#모던빌리지 #최신촬영장비 #최신촬영장비추천 #촬영장비대여 #촬영장비렌탈 #카메라추천 #카메라렌탈 #카메라대여 #카메라렌즈추천 #카메라렌즈대여 #카메라렌즈렌탈 #홈마카메라 #홈마카메라추천 #홈마카메라렌탈 #홈마카메라대여 #콘서트캠코더 #콘서트캠코더추천 #콘서트캠코더대여 #콘서트캠코더렌탈 #카메라뉴스 #카메라소식 #캐논소식 #니콘소식 #소니뉴스 #소니소식 #사진잘찍는법"


# ✅ 크롬 드라이버 실행
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

# ✅ 네이버 접속 및 쿠키 로그인
driver.get("https://www.naver.com")
time.sleep(2)

with open("cookies.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)
for cookie in cookies:
    if "domain" not in cookie:
        cookie["domain"] = ".naver.com"
    try:
        driver.add_cookie(cookie)
    except:
        pass

# ✅ 블로그 글쓰기 진입
driver.get("https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0")
time.sleep(3)

try:
    write_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'글쓰기') and contains(@href, 'GoBlogWrite')]"))
    )
    write_button.click()
    print("📝 글쓰기 버튼 클릭 완료")
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[-1])
    print("✅ 새 창으로 전환 완료")
except Exception as e:
    print("❌ 글쓰기 버튼 실패:", e)
    driver.quit()
    exit()

# ✅ iframe 진입
try:
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame")))
    print("✅ mainFrame iframe 진입 성공")
except Exception as e:
    print("❌ iframe 진입 실패:", e)
    driver.quit()
    exit()

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".se-toolbar"))
    )
    print("✅ 에디터 로드 완료")
except Exception as e:
    print("❌ 에디터 로드 실패 (팝업 닫기 생략):", e)

# ✅ 팝업 닫기
try:
    cancel_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div[3]/button[1]'))
    )
    cancel_button.click()
    print("✅ 임시저장 팝업 닫기 완료")
except:
    print("ℹ️ 임시저장 팝업 없음")

try:
    close_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/article/div/header/button'))
    )
    close_button.click()
    print("✅ 우측 팝업 닫기 완료")
except:
    print("ℹ️ 우측 팝업 없음")

# ✅ 제목 입력
try:
    title_xpath = '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span[2]'
    title_field = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, title_xpath)))
    pyperclip.copy(title)
    title_field.click()
    pyautogui.hotkey('ctrl', 'v')
    print("✅ 제목 입력 완료")
except Exception as e:
    print("❌ 제목 입력 실패:", e)

# ✅ 1) 본문 입력
try:
    content_xpath = '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p'
    content_field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, content_xpath))
    )
    pyperclip.copy(body)
    content_field.click()
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'v')
    print("✅ 본문 입력 완료")
except Exception as e:
    print("❌ 본문 입력 실패:", e)

# ✅ 2) 링크 카드 삽입
try:
    link_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "se-oglink-toolbar-button"))
    )
    link_button.click()
    print("✅ 링크 버튼 클릭 완료")
    time.sleep(1)

    link_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.se-popup-oglink-input"))
    )
    link_input.clear()
    link_input.send_keys("https://smartstore.naver.com/movilrent")
    link_input.send_keys('\n')
    print("✅ 링크 입력 및 엔터 완료")
    time.sleep(2.5)

    confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.se-popup-button-confirm"))
    )
    confirm_button.click()
    print("✅ 링크 카드 삽입 완료")
except Exception as e:
    print("❌ 링크 카드 삽입 실패:", e)

# ✅ 3) 해시태그 입력
try:
    # 링크 카드 아래로 커서 이동
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyperclip.copy(hashtags)
    pyautogui.hotkey('ctrl', 'v')
    print("✅ 해시태그 입력 완료")
except Exception as e:
    print("❌ 해시태그 입력 실패:", e)

# ✅ 4) 썸네일(대표 이미지) 업로드
 # ✅ 이미지 업로드
try:
    photo_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='사진']]"))
    )
    photo_button.click()
    time.sleep(2)

    # 파일 input에 경로 직접 전달하여 자동 업로드 (파일 탐색기 창 없이 실행됨)
    upload_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    image_path = "C:/Users/user/thum.png"  # ← 여기서 카카오톡 받은 이미지 말고 샘플 이미지 사용
    upload_input.send_keys(image_path)
    print("✅ 이미지 업로드 완료")
    time.sleep(3)

    # ✅ 이미지 업로드 완료 후 커서를 다시 본문으로 이동시킴
    content_xpath = '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p'
    content_field = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, content_xpath)))
    content_field.click()
    time.sleep(0.3)
except Exception as e:
    print("❌ 썸네일 업로드 실패:", e)



# ✅ 발행 팝업 열기
try:
    publish_layer_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='발행']/ancestor::button"))
    )
    publish_layer_button.click()
    print("✅ 발행 팝업 열기 완료")
except Exception as e:
    print("❌ 발행 팝업 열기 실패:", e)



# ✅ 카테고리 선택 (일기)
try:
    category_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.selectbox_button__jb1Dt"))
    )
    category_button.click()
    time.sleep(0.5)

    category_labels = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "label.radio_label__mB6ia"))
    )
    for label in category_labels:
        if "일기" in label.text:
            label.click()
            print("✅ 카테고리 '일기' 선택 완료")
            break
    else:
        print("⚠️ '일기' 카테고리를 찾지 못했습니다.")
except Exception as e:
    print("❌ 카테고리 선택 실패:", e)

# ✅ 최종 발행
try:
    confirm_publish_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.confirm_btn__WEaBq[data-testid='seOnePublishBtn']"))
    )
    confirm_publish_button.click()
    print("🎉 블로그 발행 완료")
except Exception as e:
    print("❌ 최종 발행 실패:", e)

# ✅ 종료
time.sleep(5)
driver.quit()
