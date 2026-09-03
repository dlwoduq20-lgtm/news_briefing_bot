import time
import schedule
import logging
from datetime import datetime
from main import run_daily_briefing

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def job():
    logging.info("⏰ 정기 스케줄 트리거: 아침 8시 브리핑을 실행합니다.")
    try:
        run_daily_briefing()
    except Exception as e:
        logging.error(f"브리핑 실행 중 예외 발생: {e}")

def main():
    print("=" * 60)
    print("🤖 [모닝 뉴스 브리핑 봇 - 스케줄 데몬 실행 중]")
    print(" 매일 아침 08:00 에 자동으로 브리핑이 실행되어 카톡으로 전송됩니다.")
    print(" (종료하려면 Ctrl + C 를 누르세요)")
    print("=" * 60)

    # 매일 아침 08:00 실행
    schedule.every().day.at("08:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
