import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from config import TOKEN_PATH, KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class KakaoSender:
    """
    카카오톡 REST API를 사용하여 '나와의 채팅방'으로 메시지를 전송하고 토큰을 관리합니다.
    """
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    SEND_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    def __init__(self, token_file: Path = TOKEN_PATH, rest_api_key: str = KAKAO_REST_API_KEY, client_secret: str = KAKAO_CLIENT_SECRET):
        self.token_file = Path(token_file)
        self.rest_api_key = rest_api_key or os.getenv("KAKAO_REST_API_KEY", "")
        self.client_secret = client_secret or os.getenv("KAKAO_CLIENT_SECRET", "")
        self.tokens: Dict[str, Any] = {}
        self._load_tokens()

    def _load_tokens(self) -> bool:
        # 1. 단일 문자열 KAKAO_REFRESH_TOKEN 환경변수 우선 확인
        refresh_token_env = os.getenv("KAKAO_REFRESH_TOKEN", "").strip()
        if refresh_token_env:
            self.tokens = {"refresh_token": refresh_token_env}
            logging.info("환경변수 KAKAO_REFRESH_TOKEN 로드 완료")
            return True

        # 2. KAKAO_TOKEN_JSON 환경변수 확인
        env_token_str = os.getenv("KAKAO_TOKEN_JSON", "").strip()
        if env_token_str:
            try:
                self.tokens = json.loads(env_token_str)
                logging.info("환경변수 KAKAO_TOKEN_JSON 로드 완료")
                return True
            except Exception as e:
                logging.warning(f"KAKAO_TOKEN_JSON 파싱 경고: {e}")

        # 3. 로컬 파일에서 로드
        if self.token_file.exists():
            try:
                with open(self.token_file, "r", encoding="utf-8") as f:
                    self.tokens = json.load(f)
                return True
            except Exception as e:
                logging.error(f"토큰 파일 로드 실패: {e}")
        
        return bool(self.tokens)

    def refresh_access_token(self) -> bool:
        """
        Refresh Token을 사용하여 새로운 Access Token을 발급받습니다.
        """
        refresh_token = self.tokens.get("refresh_token") or os.getenv("KAKAO_REFRESH_TOKEN", "").strip()
        if not refresh_token:
            logging.error("Refresh token이 존재하지 않습니다.")
            return False

        if not self.rest_api_key:
            logging.error("KAKAO_REST_API_KEY가 설정되지 않았습니다.")
            return False

        payload = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": refresh_token
        }
        if self.client_secret:
            payload["client_secret"] = self.client_secret

        try:
            response = requests.post(self.TOKEN_URL, data=payload, timeout=10)
            if response.status_code == 200:
                new_token_data = response.json()
                self.tokens["access_token"] = new_token_data["access_token"]
                if "refresh_token" in new_token_data:
                    self.tokens["refresh_token"] = new_token_data["refresh_token"]
                
                # 파일 저장 시도
                try:
                    with open(self.token_file, "w", encoding="utf-8") as f:
                        json.dump(self.tokens, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

                logging.info("카카오톡 Access Token이 성공적으로 발급/갱신되었습니다.")
                return True
            else:
                logging.error(f"토큰 갱신 실패 (HTTP {response.status_code}): {response.text}")
                return False
        except Exception as e:
            logging.error(f"토큰 갱신 요청 중 예외: {e}")
            return False

    def send_text_message(self, message_text: str, web_url: str = "https://m.naver.com") -> bool:
        """
        카카오톡 '나와의 채팅방'으로 메시지를 전송합니다.
        """
        # access_token이 없으면 refresh_token으로 먼저 발급
        if not self.tokens.get("access_token"):
            if not self.refresh_access_token():
                logging.error("Access Token을 발급받지 못했습니다.")
                return False

        max_len = 950
        chunks = [message_text[i:i + max_len] for i in range(0, len(message_text), max_len)]

        for chunk in chunks:
            success = self._send_single_chunk(chunk, web_url)
            if not success:
                logging.info("토큰 만료 감지, 재발급 후 재전송 시도...")
                if self.refresh_access_token():
                    if not self._send_single_chunk(chunk, web_url):
                        return False
                else:
                    return False
        return True

    def _send_single_chunk(self, text_chunk: str, web_url: str) -> bool:
        headers = {
            "Authorization": f"Bearer {self.tokens.get('access_token')}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template_object = {
            "object_type": "text",
            "text": text_chunk,
            "link": {
                "web_url": web_url,
                "mobile_web_url": web_url
            },
            "button_title": "자세히 보기"
        }
        
        payload = {
            "template_object": json.dumps(template_object, ensure_ascii=False)
        }

        try:
            resp = requests.post(self.SEND_MEMO_URL, headers=headers, data=payload, timeout=10)
            if resp.status_code == 200:
                logging.info("카카오톡 메시지 전송 성공!")
                return True
            elif resp.status_code == 401:
                logging.warning(f"인증 만료(401): {resp.text}")
                return False
            else:
                logging.error(f"카카오톡 전송 실패 ({resp.status_code}): {resp.text}")
                return False
        except Exception as e:
            logging.error(f"카카오톡 전송 중 오류: {e}")
            return False

if __name__ == "__main__":
    sender = KakaoSender()
    sender.send_text_message("테스트 메시지입니다.")
