from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

# ✅ 아이디 / 비밀번호 입력
NAVER_ID = ""
NAVER_PW = ""

# ✅ 크롬 드라이버 실행
driver = webdriver.Chrome()
driver.get("https://nid.naver.com/nidlogin.login")
time.sleep(2)  # 페이지 로딩 대기

# ✅ 자바스크립트로 id/pw 입력 (일반 send_keys는 보안 정책에 막힘)
driver.execute_script(f'document.getElementById("id").value = "{NAVER_ID}";')
driver.execute_script(f'document.getElementById("pw").value = "{NAVER_PW}";')

time.sleep(1)

# ✅ 로그인 버튼 클릭
login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
login_btn.click()

# ✅ 로그인 성공 대기 (2단계 인증 or CAPTCHA 있는 경우 멈춤)
time.sleep(10)

# ✅ 로그인 후 쿠키 저장
cookies = driver.get_cookies()
with open("cookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f)

print("✅ 쿠키 저장 완료!")
driver.quit()
