import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
TOKEN_PATH = BASE_DIR / "kakao_token.json"

# .env 파일 로드
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# 환경 변수 로드
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "https://localhost:5000")

# GitHub Secrets 등 환경변수에서 KAKAO_TOKEN_JSON이 전달된 경우 파일로 자동 복원
env_token_str = os.getenv("KAKAO_TOKEN_JSON", "")
if env_token_str and not TOKEN_PATH.exists():
    try:
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(env_token_str)
    except Exception:
        pass

# AI 요약 API 키 (선택사항)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 대안 메신저 웹훅 (선택사항)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# 모니터링 대상 종목 및 키워드 설정
TARGET_ASSETS = {
    "samsung": {
        "name": "삼성전자",
        "code": "005930",
        "type": "stock",
        "keywords": ["삼성전자", "반도체", "HBM", "파운드리", "D램", "메모리", "어닝서프라이즈", "목표주가", "외국인 순매수", "실적"],
        "search_queries": [
            "삼성전자 반도체",
            "삼성전자 HBM",
            "삼성전자 실적 주가"
        ]
    },
    "hynix": {
        "name": "SK하이닉스",
        "code": "000660",
        "type": "stock",
        "keywords": ["SK하이닉스", "하이닉스", "HBM3E", "HBM4", "엔비디아", "DRAM", "낸드", "실적", "목표주가", "외인 수급"],
        "search_queries": [
            "SK하이닉스 HBM",
            "SK하이닉스 엔비디아",
            "SK하이닉스 실적 주가"
        ]
    },
    "bitcoin": {
        "name": "비트코인 (BTC)",
        "code": "BTC",
        "type": "crypto",
        "keywords": ["비트코인", "BTC", "가상자산", "암호화폐", "현물 ETF", "연준 금리", "SEC", "반감기", "고래", "온체인"],
        "search_queries": [
            "비트코인 시세 호재 악재",
            "비트코인 ETF 금리",
            "비트코인 암호화폐 전망"
        ]
    }
}
