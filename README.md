# 📈 모닝 시세 브리핑 봇 (Morning News Briefing Bot)

매일 아침 8시, **삼성전자, SK하이닉스, 비트코인**의 가격 변동에 영향을 미칠 수 있는 최신 뉴스를 수집/분석하여 **카카오톡(나와의 채팅방)**으로 자동 전송하는 프로그램입니다.

---

## 📁 프로젝트 파일 구성

- [main.py](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/main.py) : 뉴스 수집 → AI 시세 분석 요약 → 카카오톡 전송 통합 파이프라인
- [get_kakao_token.py](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/get_kakao_token.py) : 카카오톡 OAuth2 토큰 1회 발급 헬퍼
- [news_collector.py](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/news_collector.py) : 실시간 RSS 기반 종목별 핵심 뉴스 수집기
- [summarizer.py](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/summarizer.py) : 시세 영향도(호재/악재/중립) 및 3줄 요약 생성기
- [kakao_sender.py](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/kakao_sender.py) : 카카오톡 '나에게 보내기' API & 토큰 자동 갱신(Refresh) 모듈
- [schedule_runner.py](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/schedule_runner.py) : 로컬 파이썬 8시 스케줄러 데몬
- [register_windows_task.ps1](file:///C:/Users/dlwod/.gemini/antigravity/scratch/news_briefing_bot/register_windows_task.ps1) : Windows 작업 스케줄러(08:00 AM) 등록 스크립트

---

## 🛠️ 1. 카카오톡 연동 방법 (최초 1회, 약 3분 소요)

### 1단계: 카카오 개발자 센터 설정
1. [카카오 개발자 센터](https://developers.kakao.com/)에 접속하여 로그인합니다.
2. 상단 **[내 애플리케이션]** → **[애플리케이션 추가하기]** 클릭 (앱 이름: `뉴스브리핑봇` 등 자유롭게 입력).
3. 생성된 앱의 **[앱 설정] → [앱 키]**에서 **`REST API 키`**를 복사합니다.
4. 좌측 메뉴 **[제품 설정] → [카카오 로그인]**에서:
   - **활성화 설정 상태**를 `ON`으로 변경합니다.
   - **[Redirect URI 등록]** 버튼을 누르고 `https://localhost:5000` 을 입력 후 저장합니다.
5. 좌측 메뉴 **[제품 설정] → [카카오 로그인] → [동의항목]**에서:
   - **`카카오톡 메시지 전송 (talk_message)`** 항목을 찾아서 **[설정]** 클릭 → `이용 중 동의` 또는 `필수 동의`를 선택하고 목적(예: 뉴스 알림)을 적은 뒤 저장합니다.

### 2단계: 토큰 발급 스크립트 실행
터미널에서 아래 명령어를 실행합니다:
```bash
python get_kakao_token.py
```
1. 복사해둔 **REST API 키**를 붙여넣습니다.
2. 콘솔에 출력되는 **인증 URL**을 브라우저에 붙여넣고 카카오 로그인 & 권한 동의를 완료합니다.
3. 브라우저 주소창의 리다이렉트된 URL(`https://localhost:5000/?code=...`)을 콘솔에 복사/붙여넣기하면 **연동 완료 및 테스트 메시지가 카톡으로 즉시 전송**됩니다!

---

## ⏰ 2. 매일 아침 8시 자동 실행 설정 (선택)

### 방법 A: Windows 작업 스케줄러 등록 (PC 자동 실행)
PowerShell을 열고 프로젝트 경로에서 다음 명령을 실행하면 매일 오전 8시에 자동 실행되도록 등록됩니다:
```powershell
powershell -ExecutionPolicy Bypass -File .\register_windows_task.ps1
```

### 방법 B: 백그라운드 스케줄러 실행
컴퓨터가 켜져 있는 동안 백그라운드에서 매일 8시마다 전송되도록 데몬을 실행할 수 있습니다:
```bash
python schedule_runner.py
```

### 방법 C: GitHub Actions 클라우드 실행 (PC를 꺼두어도 100% 무료 실행)
1. 본 프로젝트 폴더를 본인의 개인 GitHub 레포지토리에 푸시합니다.
2. GitHub 레포지토리 **[Settings] → [Secrets and variables] → [Actions]**에 Secret을 등록합니다:
   - `KAKAO_REST_API_KEY`: 본인의 카카오 REST API 키
   - `KAKAO_TOKEN_JSON`: 생성된 `kakao_token.json` 파일의 전체 내용(텍스트)
3. `.github/workflows/daily_briefing.yml` 워크플로우에 의해 매일 한국시간 오전 8시(UTC 23:00)에 자동으로 카톡이 전송됩니다.

---

## 🧪 3. 즉시 테스트 실행

언제든지 수동으로 뉴스를 수집하고 브리핑을 전송해 보려면 다음 명령어를 실행하세요:
```bash
python main.py
```
