import streamlit as st
import subprocess
import os
from markdown.generate_markdown import generate_markdown

# 페이지 설정
st.set_page_config(page_title="아이돌 콘서트 크롤러", layout="wide")
st.title("🎫 아이돌 콘서트 일정 갱신기")

# ✅ 콘서트 크롤링 버튼
if st.button("📥 최신 콘서트 데이터 크롤링"):
    with st.spinner("크롤링 중입니다... 잠시만 기다려주세요!"):
        result = subprocess.run(["python", "crawler/interpark_crawler.py"])
    if result.returncode == 0:
        st.success("✅ 콘서트 크롤링이 완료되었습니다!")
    else:
        st.error("❗ 크롤링 중 오류가 발생했습니다.")

# ✅ 마크다운 글 생성 버튼
if st.button("📝 블로그 글 자동 생성"):
    with st.spinner("마크다운 파일 생성 중입니다..."):
        success = generate_markdown()
        if success:
            try:
                with open("markdown/concert_post.md", "r", encoding="utf-8") as f:
                    st.markdown(f.read(), unsafe_allow_html=True)
                st.success("🎉 블로그 글 생성이 완료되었습니다!")
            except Exception as e:
                st.error(f"❗ 마크다운 파일 읽기 오류: {e}")
        else:
            st.error("❗ 공연 정보가 없어 마크다운을 생성할 수 없습니다.")
