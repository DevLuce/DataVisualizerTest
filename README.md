# 🤖 New Flower - AI 기반 데이터 분석 도우미

Gemini AI와 Firebase Firestore를 활용한 한국어 데이터 분석 질의응답 시스템입니다.

## ✨ 주요 기능

- 🧠 **Gemini AI 연동**: 최신 Gemini 2.0 Flash 모델을 활용한 한국어 데이터 분석
- 💾 **Firebase Firestore**: 사용자 질문과 응답 히스토리 저장
- 📊 **실시간 상태 모니터링**: API 연결 상태 실시간 확인
- 🔄 **컨텍스트 기반 대화**: 이전 대화 맥락을 고려한 AI 응답
- 🎨 **직관적인 UI**: Streamlit 기반의 사용자 친화적 인터페이스

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <your-repository-url>
cd DataVisualizerTest
```

### 2. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.template .env
```

### 3. API 키 설정

`.env` 파일을 열고 Gemini API 키를 설정:

```bash
GEMINI_API_KEY=your_actual_gemini_api_key
```

[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받을 수 있습니다.

### 4. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8502`로 접속하여 사용할 수 있습니다.

## 📁 프로젝트 구조

```
DataVisualizerTest/
├── config/
│   ├── settings.py              # 중앙화된 설정 관리
│   └── firebase-credentials.json # Firebase 인증 파일 (생성 필요)
├── services/
│   ├── gemini_service.py        # Gemini AI 서비스 모듈
│   └── firebase_service.py      # Firebase Firestore 서비스 모듈
├── app.py                       # 메인 Streamlit 애플리케이션
├── requirements.txt             # Python 의존성 목록
├── .env.template               # 환경변수 템플릿
└── SETUP.md                    # 상세 설정 가이드
```

## 🔧 고급 설정

### Firebase 연동 (선택사항)

Firebase를 사용하면 질문 히스토리 저장, 사용자 통계 등의 기능을 사용할 수 있습니다:

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. Firestore Database 활성화
3. 서비스 계정 키 다운로드 → `config/firebase-credentials.json`에 저장
4. `.env` 파일에서 `FIREBASE_PROJECT_ID` 설정

자세한 설정 방법은 [SETUP.md](SETUP.md)를 참고하세요.

## 🛡️ 보안

- `.env` 파일과 `firebase-credentials.json` 파일은 Git에 커밋되지 않습니다
- API 키와 인증 정보는 환경변수로 안전하게 관리됩니다
- Firebase 없이도 애플리케이션은 정상 작동합니다

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

---

**Made with ❤️ using Gemini AI and Firebase**
