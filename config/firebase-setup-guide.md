# Firebase 설정 가이드

## 1. Firebase 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: `datavisualizer-test`)
4. Google Analytics 설정 (선택사항)
5. 프로젝트 생성 완료

## 2. Firestore 데이터베이스 설정
1. Firebase 콘솔에서 "Firestore Database" 선택
2. "데이터베이스 만들기" 클릭
3. 보안 규칙 모드 선택:
   - 테스트 모드: 개발 중 사용 (30일 후 자동 만료)
   - 프로덕션 모드: 보안 규칙 직접 설정
4. 위치 선택 (asia-northeast3 - 서울 권장)

## 3. 서비스 계정 키 생성
1. Firebase 콘솔에서 "프로젝트 설정" (톱니바퀴 아이콘)
2. "서비스 계정" 탭 선택
3. "새 비공개 키 생성" 클릭
4. JSON 파일 다운로드
5. 다운로드한 파일을 `config/firebase-credentials.json`으로 저장

## 4. 환경변수 설정
`.env` 파일에서 다음 값들을 설정:

```bash
# Firebase 프로젝트 ID (Firebase 콘솔에서 확인)
FIREBASE_PROJECT_ID=your-firebase-project-id

# Firebase 서비스 계정 키 파일 경로
FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
```

## 5. Firestore 보안 규칙 (선택사항)
개발 단계에서는 테스트 모드로 시작하되, 프로덕션에서는 다음과 같은 규칙을 설정:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 질문 컬렉션
    match /user_queries/{document} {
      allow read, write: if request.auth != null;
    }
    
    // 비즈니스 데이터 컬렉션
    match /business_data/{document} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 6. 테스트
애플리케이션을 실행하고 Firebase 연결 상태를 확인:
- ✅ Firebase 연결됨: 정상 설정
- ⚠️ Firebase 연결 안됨: 설정 재확인 필요

## 주의사항
- `firebase-credentials.json` 파일은 절대 Git에 커밋하지 마세요
- `.gitignore`에 `config/firebase-credentials.json` 추가 권장
- 프로덕션 환경에서는 환경변수로 인증 정보 관리 권장
