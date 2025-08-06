# 🚀 New Flower - 설정 가이드

AI 기반 데이터 분석 도우미 애플리케이션 설정 방법입니다.

## 📋 필수 요구사항

- Python 3.8+
- pip
- Git

## 🔧 설치 및 설정

### 1. 프로젝트 클론

```bash
git clone <your-repository-url>
cd DataVisualizerTest
```

### 2. 가상환경 설정

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
# .env.template을 복사하여 .env 파일 생성
cp .env.template .env
```

`.env` 파일을 열고 다음 값들을 설정:

```bash
# Gemini API 키 (필수)
GEMINI_API_KEY=your_actual_gemini_api_key

# Firebase 설정 (선택사항)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
```

### 5. Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에 접속
2. "Create API Key" 클릭
3. 생성된 API 키를 `.env` 파일의 `GEMINI_API_KEY`에 입력

### 6. Firebase 설정 (선택사항)

Firebase를 사용하려면:

1. [Firebase Console](https://console.firebase.google.com/)에서 새 프로젝트 생성
2. Firestore Database 활성화 (테스트 모드로 시작)
3. 프로젝트 설정 → 서비스 계정 → "새 비공개 키 생성"
4. 다운로드한 JSON 파일을 `config/firebase-credentials.json`으로 저장
5. `.env` 파일에서 `FIREBASE_PROJECT_ID`를 실제 프로젝트 ID로 변경

**주의**: Firebase 없이도 애플리케이션은 정상 작동합니다. 질문 저장 기능만 비활성화됩니다.

## 🚀 실행

```bash
source venv/bin/activate
streamlit run app.py
```

브라우저에서 `http://localhost:8502`로 접속하여 애플리케이션을 사용할 수 있습니다.

## 📁 프로젝트 구조

```
DataVisualizerTest/
├── config/
│   ├── settings.py              # 설정 관리
│   └── firebase-credentials.json # Firebase 인증 파일 (생성 필요)
├── services/
│   ├── gemini_service.py        # Gemini AI 서비스
│   └── firebase_service.py      # Firebase Firestore 서비스
├── app.py                       # 메인 애플리케이션
├── requirements.txt             # Python 의존성
├── .env.template               # 환경변수 템플릿
├── .env                        # 실제 환경변수 (생성 필요)
└── README.md
```

## 🔐 보안 주의사항

- `.env` 파일과 `firebase-credentials.json` 파일은 Git에 커밋하지 마세요
- API 키는 절대 공개 저장소에 업로드하지 마세요
- 프로덕션 환경에서는 환경변수로 관리하세요

## 🐛 문제 해결

### Gemini API 오류
- API 키가 올바른지 확인
- [Google AI Studio](https://aistudio.google.com/app/apikey)에서 키 상태 확인

### Firebase 연결 오류
- 프로젝트 ID가 정확한지 확인
- Firestore 데이터베이스가 활성화되었는지 확인
- 서비스 계정 키 파일 경로가 올바른지 확인

### Import 오류
- 가상환경이 활성화되었는지 확인
- `pip install -r requirements.txt` 재실행

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.
