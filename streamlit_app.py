import streamlit as st
import subprocess
import json
import os

# 🎫 제목 설정
st.set_page_config(page_title="아이돌 콘서트 일정 자동 수집기", page_icon="🎫")
st.title("🎫 아이돌 콘서트 일정 자동 수집기")

# 📁 경로
ALL_CONCERTS_PATH = "all_concerts.json"
MARKDOWN_PATH     = "markdown/concert_post.md"

# ✅ 크롤러 실행 함수
def run_crawler():
    try:
        result = subprocess.run(
            ["python", "-X", "utf8", "crawler/interpark_crawler.py"],
            capture_output=True,
            env={**os.environ, "PYTHONUTF8": "1"}
        )
        out = result.stdout.decode("utf-8", errors="replace")
        err = result.stderr.decode("utf-8", errors="replace")
        return out, err
    except Exception as e:
        return "", str(e)

# ✅ 마크다운 생성 함수
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

# ✅ 콘서트 JSON 불러오기
def load_concert_data():
    if os.path.exists(ALL_CONCERTS_PATH):
        with open(ALL_CONCERTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ✅ 상태 필터링
def filter_by_status(concerts, status_filter):
    if not status_filter or status_filter == "전체":
        return concerts
    return {
        artist: [e for e in events if e["status"] == status_filter]
        for artist, events in concerts.items()
        if any(e["status"] == status_filter for e in events)
    }

concert_data = load_concert_data()
artist_list  = sorted(concert_data.keys()) if concert_data else []

# 사이드바
st.sidebar.markdown("### 🎛️ 필터")
selected_artist = st.sidebar.selectbox("🎤 아티돌 선택", ["전체"] + artist_list)
status_option   = st.sidebar.selectbox("🎟️ 상태", ["전체", "판매중", "예정", "판매종료"])

# 크롤링 버튼
if st.button("📄 최신 콘서트 정보 크롤링"):
    with st.spinner("크롤링 중입니다..."):
        out, err = run_crawler()
    st.subheader("📋 콘솔 출력 로그")
    if err:
        st.error(f"❗ 오류 발생:\n```\n{err}\n```")
    else:
        st.success("✅ 크롤링 완료!")
        st.code(out)

# 콘서트 목록 보기
if st.button("📂 저장된 콘서트 목록 보기"):
    filtered_data = concert_data
    if selected_artist != "전체":
        filtered_data = {selected_artist: concert_data.get(selected_artist, [])}
    filtered_data = filter_by_status(filtered_data, status_option)

    if not filtered_data or all(len(events) == 0 for events in filtered_data.values()):
        st.warning("⚠️ 조건에 맞는 콘서트가 없습니다.")
    else:
        for artist, events in filtered_data.items():
            st.markdown(f"### 🎤 {artist}")
            for e in events:
                date  = e.get("concert_date", "날짜 정보 없음")
                place = e.get("place", "장소 정보 없음")
                status= e.get("status", "상태 정보 없음")
                st.write(f"- 📅 {date} | 📍 {place} | 🏷️ {status}")

# 블로그 글 생성 및 미리보기
if st.button("📝 블로그 글 생성하기"):
    with st.spinner("블로그 글을 생성 중입니다..."):
        out, err = run_blog_generator()

    if err:
        st.error(f"❗ 오류 발생:\n```\n{err}\n```")
    else:
        st.success("✅ 마크다운 파일 생성 완료!")
        if os.path.exists(MARKDOWN_PATH):
            with open(MARKDOWN_PATH, "r", encoding="utf-8") as f:
                md = f.read()
            st.markdown("### ✏️ 생성된 블로그 글 미리보기")
            st.markdown(md, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 마크다운 파일을 찾을 수 없습니다.")
