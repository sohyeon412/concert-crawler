
import streamlit as st
import subprocess
import os
from datetime import datetime
import tempfile

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# 🎫 페이지 설정
st.set_page_config(page_title="아이돌 콘서트 일정 자동 수집기", page_icon="🎫")
st.title("🎫 아이돌 콘서트 일정 자동 수집기")

# ✅ Firebase 초기화
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
        except:
            cred = credentials.Certificate("firebase/idol-ticket-firebase-adminsdk.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

# ✅ 콘서트 데이터 불러오기
@st.cache_data(ttl=300)
def load_concert_data():
    db = init_firebase()
    concerts_ref = db.collection("concerts").stream()
    concert_data = {}
    for doc in concerts_ref:
        artist = doc.id
        concert_list = doc.to_dict().get("concert_list", [])
        concert_data[artist] = concert_list
    return concert_data

@st.cache_data(ttl=300)
def get_artist_list_from_firebase():
    db = init_firebase()
    docs = db.collection("concerts").stream()
    return sorted([doc.id for doc in docs])

@st.cache_data(ttl=60)
def get_last_crawl_time():
    db = init_firebase()
    doc = db.collection("metadata").document("last_updated").get()
    if doc.exists:
        return doc.to_dict().get("timestamp", "기록 없음")
    return "기록 없음"

def filter_by_status(concerts, status_filter):
    if not status_filter or status_filter == "전체":
        return concerts
    return {
        artist: [e for e in events if e["status"] == status_filter]
        for artist, events in concerts.items()
        if any(e["status"] == status_filter for e in events)
    }

# ✅ 크롤러 실행 함수
def run_crawler(selected_artists):
    try:
        result = subprocess.run(
            ["python", "-X", "utf8", "crawler/interpark_crawler.py", "--artists", *selected_artists],
            capture_output=True,
            env={**os.environ, "PYTHONUTF8": "1"}
        )
        out = result.stdout.decode("utf-8", errors="replace")
        err = result.stderr.decode("utf-8", errors="replace")

        db = init_firebase()
        db.collection("metadata").document("last_updated").set({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        load_concert_data.clear()
        get_last_crawl_time.clear()

        return out, err
    except Exception as e:
        return "", str(e)

# ✅ 마크다운 생성기 실행 함수
def run_blog_generator():
    try:
        result = subprocess.run(
            ["python", "-X", "utf8", "markdown/generate_markdown.py"],
            capture_output=True,
            env={**os.environ, "PYTHONUTF8": "1"}
        )
        out = result.stdout.decode("utf-8", errors="replace")
        err = result.stderr.decode("utf-8", errors="replace")
        return out, err
    except Exception as e:
        return "", str(e)

# ✅ 배너 이미지 업로드 함수
def upload_banner_image(file):
    try:
        storage_client = storage.Client.from_service_account_json("firebase/idol-ticket-firebase-adminsdk.json")

        # ❗ 올바른 버킷 이름으로 수정
        bucket = storage_client.bucket("fanclub-schedule.firebasestorage.app")


        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        blob = bucket.blob(f"banner/{file.name}")
        blob.upload_from_filename(tmp_path, content_type=file.type)
        blob.make_public()

        public_url = blob.public_url
        db = init_firebase()
        db.collection("metadata").document("banner").set({"url": public_url})
        return public_url
    except Exception as e:
        return str(e)

# ✅ 콘서트 데이터 로드
concert_data = load_concert_data()
artist_list = sorted(concert_data.keys()) if concert_data else []
last_updated = get_last_crawl_time()

# ✅ 크롤링 시간 표시
st.markdown(f"🕒 **마지막 크롤링 시간:** `{last_updated}`")

# ✅ 사이드바: 크롤링할 아이돌 선택
st.sidebar.markdown("### 🎤 크롤링할 아이돌 선택")
firebase_artists = get_artist_list_from_firebase()

if "selected_artists" not in st.session_state:
    st.session_state.selected_artists = sorted(firebase_artists)

custom_input = st.sidebar.text_input("➕ 추가 아이돌 입력 (쉼표로 구분)", "")
if custom_input.strip():
    custom_artists = [a.strip() for a in custom_input.split(",") if a.strip()]
    st.session_state.selected_artists = sorted(set(st.session_state.selected_artists + custom_artists))

selected_artists = st.sidebar.multiselect(
    "아이돌 목록 선택",
    options=st.session_state.selected_artists,
    default=st.session_state.selected_artists
)

final_artist_list = sorted(set(selected_artists))

# ✅ 배너 이미지 업로드
st.sidebar.markdown("### 🖼️ 배너 이미지 업로드")
uploaded_banner = st.sidebar.file_uploader("📤 이미지 업로드 (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_banner:
    with st.spinner("이미지 업로드 중..."):
        result = upload_banner_image(uploaded_banner)
        if result.startswith("http"):
            st.sidebar.success("✅ 업로드 완료!")
            st.sidebar.image(result, caption="배너 미리보기", use_column_width=True)
        else:
            st.sidebar.error(f"❌ 실패: {result}")

# ✅ 크롤링 실행
if st.button("📄 선택한 아이돌로 크롤링"):
    if not final_artist_list:
        st.warning("⚠️ 크롤링할 아이돌을 선택하세요.")
    else:
        with st.spinner("크롤링 중..."):
            out, err = run_crawler(final_artist_list)
        st.subheader("📋 콘솔 출력 로그")
        if err:
            st.error(f"❗ 오류 발생:\n```\n{err}\n```")
        else:
            st.success("✅ 크롤링 완료!")
            st.code(out)

# ✅ 콘서트 목록 보기
st.sidebar.markdown("### 🎛️ 콘서트 보기 필터")
selected_view_artist = st.sidebar.selectbox("아티돌 선택", ["전체"] + artist_list)
status_option = st.sidebar.selectbox("상태", ["전체", "판매중", "예정", "판매종료"])

if st.button("📂 콘서트 목록 보기"):
    filtered_data = concert_data
    if selected_view_artist != "전체":
        filtered_data = {selected_view_artist: concert_data.get(selected_view_artist, [])}
    filtered_data = filter_by_status(filtered_data, status_option)

    if not filtered_data or all(len(events) == 0 for events in filtered_data.values()):
        st.warning("⚠️ 조건에 맞는 콘서트가 없습니다.")
    else:
        for artist, events in filtered_data.items():
            st.markdown(f"### 🎤 {artist}")
            for e in events:
                date = e.get("concert_date", "날짜 정보 없음")
                place = e.get("place", "장소 정보 없음")
                status = e.get("status", "상태 정보 없음")
                st.write(f"- 📅 {date} | 📍 {place} | 🏷️ {status}")

# ✅ 블로그 생성
MARKDOWN_PATH = "markdown/concert_post.md"
if st.button("📝 블로그 글 생성하기"):
    with st.spinner("생성 중..."):
        out, err = run_blog_generator()
    if err:
        st.error(f"❗ 오류 발생:\n```\n{err}\n```")
    else:
        st.success("✅ 마크다운 생성 완료!")
        if os.path.exists(MARKDOWN_PATH):
            with open(MARKDOWN_PATH, "r", encoding="utf-8") as f:
                md = f.read()
            st.markdown("### 📄 생성된 블로그 글")
            st.markdown(md, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 마크다운 파일이 없습니다.")

