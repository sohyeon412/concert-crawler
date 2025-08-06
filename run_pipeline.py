import os
from pathlib import Path

# 🎯 기존 마크다운 및 타이틀 파일 삭제
md_path = Path("markdown/concert_post.txt")
title_path = Path("markdown/concert_title.txt")

if md_path.exists():
    md_path.unlink()

if title_path.exists():
    title_path.unlink()

# ✅ 크롤링 → Firebase 저장까지
os.system("python crawler/interpark_crawler.py")
os.system("python firebase/uploader.py")

# ✅ 마크다운 생성
os.system("python markdown/generate_markdown.py")

# 🔍 마크다운이 생성되었는지 확인
if md_path.exists() and md_path.stat().st_size > 0:
    print("✅ 마크다운 생성됨. 네이버 자동 업로드 진행.")
    os.system("python naver/save_naver_cookies.py")
    os.system("python naver/upload_to_naver_blog.py")
    print("🎉 전체 파이프라인 완료!")
else:
    print("⛔ 공연 데이터 변경 없음. 블로그 업로드 생략됨.")
