import os
import sys
import logging
from datetime import datetime

# 윈도우 콘솔 UTF-8 및 이모지 출력 인코딩 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import TARGET_ASSETS, TOKEN_PATH, GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK_URL
from news_collector import NewsCollector
from summarizer import NewsSummarizer
from kakao_sender import KakaoSender
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def send_telegram(message_text: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text}
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                logging.info("텔레그램 메시지 전송 성공!")
        except Exception as e:
            logging.error(f"텔레그램 전송 오류: {e}")

def send_discord(message_text: str):
    if DISCORD_WEBHOOK_URL:
        try:
            payload = {"content": message_text}
            resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            if resp.status_code in (200, 204):
                logging.info("디스코드 메시지 전송 성공!")
        except Exception as e:
            logging.error(f"디스코드 전송 오류: {e}")

def run_daily_briefing():
    print("\n" + "=" * 60)
    print(f"🚀 [모닝 시세 심층 브리핑 시작] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 글로벌 거시 + 종목별 뉴스 수집
    logging.info("글로벌 거시(미 증시/금리/엔비디아) 및 삼성/SK하이닉스/비트코인 뉴스 수집 중...")
    collector = NewsCollector()
    collected_data = collector.collect_all_with_macro(TARGET_ASSETS)

    # 2. 주가/시세 영향도 심층 분석 및 브리핑 생성
    logging.info("가격 변동 영향 요인(금리/빅테크 실적/HBM/ETF 등) 심층 분석 중...")
    summarizer = NewsSummarizer(api_key=GEMINI_API_KEY)
    briefing_message = summarizer.generate_full_briefing(collected_data, TARGET_ASSETS)

    print("\n" + "-" * 50)
    print("📋 [생성된 심층 브리핑 내용]")
    print("-" * 50)
    print(briefing_message)
    print("-" * 50 + "\n")

    # 3. 카카오톡 발송
    if TOKEN_PATH.exists():
        logging.info("카카오톡 '나와의 채팅방'으로 브리핑 전송 중...")
        kakao = KakaoSender(token_file=TOKEN_PATH)
        sent = kakao.send_text_message(briefing_message)
        if sent:
            logging.info("✅ 카카오톡 브리핑 전송이 완료되었습니다.")
        else:
            logging.warning("⚠️ 카카오톡 전송 실패. 토큰 만료 또는 설정을 확인하세요.")
    else:
        logging.warning("⚠️ kakao_token.json 파일이 없습니다. get_kakao_token.py를 먼저 실행하여 카톡을 연동해주세요.")

    # 4. 기타 메신저 발송 (설정된 경우)
    send_telegram(briefing_message)
    send_discord(briefing_message)

    print("🎉 브리핑 작업 완료!\n")

if __name__ == "__main__":
    run_daily_briefing()
