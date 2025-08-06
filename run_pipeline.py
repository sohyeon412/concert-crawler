from pathlib import Path
import os

# ✅ 경로 설정
md_path = Path("markdown/concert_post.txt")
title_path = Path("markdown/concert_title.txt")

def cleanup_old_markdown():
    if md_path.exists():
        md_path.unlink()
        print("🧹 이전 concert_post.txt 삭제 완료")
    if title_path.exists():
        title_path.unlink()
        print("🧹 이전 concert_title.txt 삭제 완료")

def run(command):
    print(f"\n▶ 실행 중: {command}")
    os.system(command)

def markdown_exists():
    return md_path.exists() and md_path.stat().st_size > 0

def main():
    # ✅ 1단계: 기존 텍스트 파일 삭제
    cleanup_old_markdown()

    # ✅ 2단계: 콘서트 정보 크롤링
    print("🚀 [1] 콘서트 정보 크롤링")
    run("python crawler/interpark_crawler.py")

    # ✅ 3단계: 기존 데이터와 비교
    print("🔍 [2] 기존 데이터와 비교")
    run("python main_auto_crawl.py")

    # ✅ 4단계: 변경 사항 있을 경우 계속 진행
    if not markdown_exists():
        print("⛔ 변경 없음 → 시스템 종료")
        return

    # ✅ 5단계: 마크다운 자동 생성
    print("📝 [3] 제목/본문 텍스트 생성")
    run("python generate_markdown.py")

    # ✅ 6단계: 쿠키 생성
    print("🔐 [4] 네이버 로그인 쿠키 생성")
    run("python naver/save_naver_cookies.py")

    print("📤 [5] 블로그 자동 업로드")
    run("python naver/upload_to_naver_blog.py")


    print("🎉 전체 파이프라인 완료!")

if __name__ == "__main__":
    main()
