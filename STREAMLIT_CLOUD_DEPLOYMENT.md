# ☁️ Streamlit Cloud 배포 가이드

이 가이드는 New Flower 애플리케이션을 Streamlit Cloud에 배포하는 방법을 설명합니다.

## 🚀 배포 단계

### 1. GitHub 저장소 준비

```bash
# 프로젝트를 GitHub에 푸시 (보안 파일은 제외됨)
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

**중요**: `.env` 파일과 `firebase-credentials.json` 파일은 자동으로 제외됩니다.

### 2. Streamlit Cloud 배포

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `your-username/DataVisualizerTest`
5. Branch: `main`
6. Main file path: `app.py`
7. "Deploy!" 클릭

### 3. 🔐 Secrets 설정 (중요!)

배포 후 앱 대시보드에서:

1. **Settings** → **Secrets** 클릭
2. 다음 내용을 입력:

#### 기본 환경변수:
```toml
GEMINI_API_KEY = "your_actual_gemini_api_key"
FIREBASE_PROJECT_ID = "macc-qed"
FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"
```

#### Firebase 자격 증명 (선택사항):
```toml
[firebase_credentials]
type = "service_account"
project_id = "macc-qed"
private_key_id = "your_private_key_id_here"
private_key = """-----BEGIN PRIVATE KEY-----
your_private_key_content_here
-----END PRIVATE KEY-----"""
client_email = "your-service-account@macc-qed.iam.gserviceaccount.com"
client_id = "your_client_id_here"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs/your-service-account%40macc-qed.iam.gserviceaccount.com"
```

3. **Save** 클릭

### 4. 🔧 Firebase 자격 증명 정보 찾기

`config/firebase-credentials.json` 파일을 열어서 각 값을 복사:

```json
{
  "type": "service_account",
  "project_id": "macc-qed",
  "private_key_id": "복사할 값",
  "private_key": "-----BEGIN PRIVATE KEY-----\n복사할 값\n-----END PRIVATE KEY-----\n",
  "client_email": "복사할 값",
  "client_id": "복사할 값",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "복사할 값"
}
```

## ✅ 배포 확인

1. 앱이 성공적으로 시작되는지 확인
2. Gemini API 연결 상태 확인 (✅ 표시)
3. Firebase 연결 상태 확인 (✅ 또는 ⚠️ 표시)
4. 질문을 입력해서 AI 응답이 정상적으로 작동하는지 테스트

## 🐛 문제 해결

### 앱이 시작되지 않는 경우
1. **Logs** 탭에서 오류 메시지 확인
2. `requirements.txt`에 모든 필요한 패키지가 있는지 확인
3. Secrets가 올바르게 설정되었는지 확인

### Gemini API 오류
- `GEMINI_API_KEY`가 Secrets에 올바르게 설정되었는지 확인
- API 키가 유효한지 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 확인

### Firebase 연결 오류
- `firebase_credentials` 섹션이 Secrets에 올바르게 설정되었는지 확인
- `private_key` 값에 따옴표가 올바르게 처리되었는지 확인
- Firebase 프로젝트 ID가 정확한지 확인

### Private Key 형식 주의사항
```toml
# 올바른 형식 (멀티라인 문자열)
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"""

# 또는 이스케이프 문자 사용
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
```

## 🔄 업데이트 배포

코드를 수정한 후:

```bash
git add .
git commit -m "Update: 변경사항 설명"
git push origin main
```

Streamlit Cloud가 자동으로 새 버전을 배포합니다.

## 📊 모니터링

- **Analytics**: 앱 사용량 통계 확인
- **Logs**: 실시간 로그 모니터링
- **Settings**: 앱 설정 및 Secrets 관리

## 💡 팁

1. **Firebase 없이 배포**: Firebase 설정을 생략하면 질문 저장 기능 없이 Gemini AI만 사용 가능
2. **Secrets 테스트**: 로컬에서 `st.secrets` 대신 환경변수로 테스트
3. **로그 확인**: 배포 후 반드시 Logs 탭에서 초기화 메시지 확인

---

**🎉 배포 완료 후 앱 URL을 공유하여 다른 사람들과 함께 사용하세요!**
