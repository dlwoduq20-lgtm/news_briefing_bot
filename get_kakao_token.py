import os
import sys
import json
import urllib.parse
import webbrowser
import requests
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import BASE_DIR, TOKEN_PATH, ENV_PATH

def setup_kakao_token():
    print("=" * 65)
    print("      [카카오톡 '나에게 보내기' 토큰 발급 도우미]")
    print("=" * 65)

    print("\n💡 KOE010 (Bad client credentials) 에러 원인은 다음 중 하나입니다:")
    print(" 1. 복사한 키가 'REST API 키'가 아닌 'JavaScript 키' 또는 '네이티브 앱 키'인 경우")
    print(" 2. [카카오 로그인] -> [보안] 메뉴에서 'Client Secret(클라이언트 시크릿)'이 활성화되어 있는 경우\n")
    print("-" * 65)

    rest_api_key = input("👉 카카오 [앱 키]의 'REST API 키'를 입력하세요 (기존: 50da1114dbfd4f5da26c6cb092d67b4e / Enter 시 기존값 유지): ").strip()
    if not rest_api_key:
        rest_api_key = "50da1114dbfd4f5da26c6cb092d67b4e"

    client_secret = input("👉 [선택] [카카오 로그인 > 보안]의 'Client Secret' 코드가 있다면 입력하세요 (없으면 그냥 Enter): ").strip()

    redirect_uri = "https://localhost:5000"

    print(f"\n✅ 적용할 REST API 키: {rest_api_key}")
    if client_secret:
        print(f"✅ 적용할 Client Secret: {client_secret[:6]}******")
    print(f"✅ 적용할 Redirect URI: {redirect_uri}")
    print("-" * 65)

    # 인가 코드 요청 URL 생성
    auth_params = {
        "client_id": rest_api_key,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "talk_message"
    }
    auth_url = f"https://kauth.kakao.com/oauth/authorize?{urllib.parse.urlencode(auth_params)}"

    print("\n🌐 잠시 후 카카오 로그인 브라우저 창이 자동으로 열립니다...")
    print(f"  👉 {auth_url}\n")
    
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("=" * 65)
    print("📌 브라우저에서 로그인/동의 후, 주소창의 전체 주소를 복사해 아래에 붙여넣어 주세요.")
    print("=" * 65)

    code_input = input("\n👉 주소창에 표시된 전체 URL(또는 code)을 여기에 붙여넣고 Enter를 누르세요:\n> ").strip()

    if not code_input:
        print("❌ 입력된 내용이 없습니다.")
        return

    # URL에서 code 파라미터 추출
    if "code=" in code_input:
        parsed_url = urllib.parse.urlparse(code_input)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        code = query_params.get("code", [""])[0]
        if not code and "code=" in code_input:
            code = code_input.split("code=")[1].split("&")[0]
    else:
        code = code_input

    code = code.strip()

    if not code:
        print("❌ code 값을 추출할 수 없습니다.")
        return

    print(f"\n🔑 추출된 인가 코드: {code[:10]}... (인증 토큰 발급 요청 중)")
    
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": rest_api_key,
        "redirect_uri": redirect_uri,
        "code": code
    }
    if client_secret:
        token_data["client_secret"] = client_secret

    try:
        resp = requests.post(token_url, data=token_data, timeout=15)
        if resp.status_code == 200:
            token_json = resp.json()
            # 토큰 파일 저장
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                json.dump(token_json, f, ensure_ascii=False, indent=2)
            
            # .env 파일 저장
            env_content = f"KAKAO_REST_API_KEY={rest_api_key}\nKAKAO_CLIENT_SECRET={client_secret}\nKAKAO_REDIRECT_URI={redirect_uri}\nGEMINI_API_KEY=\n"
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.write(env_content)

            print("\n🎉 축하합니다! 카카오 인증 토큰이 성공적으로 발급 및 저장되었습니다.")
            print(f"📁 저장 파일: {TOKEN_PATH}")

            # 연동 테스트 메시지 발송
            print("\n📱 카카오톡 '나와의 채팅방'으로 테스트 메시지를 발송합니다...")
            from kakao_sender import KakaoSender
            sender = KakaoSender(token_file=TOKEN_PATH, rest_api_key=rest_api_key, client_secret=client_secret)
            test_sent = sender.send_text_message("🔔 [뉴스 브리핑 봇] 카카오톡 연동이 성공적으로 완료되었습니다!\n\n내일부터 매일 아침 8시에 삼성전자, SK하이닉스, 비트코인 시세 영향 뉴스 브리핑이 발송됩니다.")
            
            if test_sent:
                print("✅ 카카오톡 테스트 메시지가 정상 전송되었습니다! 지금 카카오톡을 확인해보세요.")
            else:
                print("⚠️ 메시지 전송 중 오류가 발생했습니다. 카카오 로그인 동의항목에서 '카카오톡 메시지 전송'이 동의되었는지 확인해주세요.")

        else:
            print(f"\n❌ 토큰 발급 실패 (상태코드: {resp.status_code})")
            print("응답 내용:", resp.text)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    setup_kakao_token()
