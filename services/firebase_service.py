"""
Firebase Firestore 연동 서비스 모듈
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional, Any
import streamlit as st
from config.settings import Config

class FirebaseService:
    """Firebase Firestore 연동을 위한 서비스 클래스"""
    
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Firebase 초기화"""
        try:
            # Firebase 설정이 있는지 확인
            if not Config.FIREBASE_PROJECT_ID:
                print("Firebase 설정이 없습니다. Firebase 기능은 비활성화됩니다.")
                self.db = None
                return
            
            # Firebase가 이미 초기화되었는지 확인
            if not firebase_admin._apps:
                # Streamlit Cloud에서 실행 중인지 확인
                if self._is_streamlit_cloud():
                    # Streamlit secrets에서 자격 증명 정보 가져오기
                    cred_dict = self._get_firebase_credentials_from_secrets()
                    if cred_dict:
                        cred = credentials.Certificate(cred_dict)
                    else:
                        print("Streamlit secrets에서 Firebase 자격 증명을 찾을 수 없습니다.")
                        self.db = None
                        return
                else:
                    # 로컬 환경에서는 파일 사용
                    import os
                    if not os.path.exists(Config.FIREBASE_CREDENTIALS_PATH):
                        print(f"Firebase 자격 증명 파일을 찾을 수 없습니다: {Config.FIREBASE_CREDENTIALS_PATH}")
                        self.db = None
                        return
                    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                
                firebase_admin.initialize_app(cred, {
                    'projectId': Config.FIREBASE_PROJECT_ID
                })
            
            # Firestore 클라이언트 생성
            self.db = firestore.client()
            print("Firebase 초기화 완료")
            
        except Exception as e:
            print(f"Firebase 초기화 중 오류가 발생했습니다: {str(e)}")
            print("Firebase 기능은 비활성화됩니다.")
            self.db = None
    
    def _is_streamlit_cloud(self) -> bool:
        """Streamlit Cloud에서 실행 중인지 확인"""
        import streamlit as st
        return hasattr(st, 'secrets') and 'firebase_credentials' in st.secrets
    
    def _get_firebase_credentials_from_secrets(self) -> dict:
        """Streamlit secrets에서 Firebase 자격 증명 가져오기"""
        try:
            import streamlit as st
            if 'firebase_credentials' in st.secrets:
                return dict(st.secrets['firebase_credentials'])
        except Exception as e:
            print(f"Streamlit secrets에서 Firebase 자격 증명 로드 중 오류: {str(e)}")
        return None
    
    def is_connected(self) -> bool:
        """Firebase 연결 상태 확인"""
        return self.db is not None
    
    # === 사용자 데이터 관련 함수 ===
    
    def save_user_query(self, user_id: str, query: str, response: str) -> bool:
        """사용자 질문과 응답을 저장"""
        if not self.is_connected():
            return False
        
        try:
            doc_ref = self.db.collection('user_queries').document()
            doc_ref.set({
                'user_id': user_id,
                'query': query,
                'response': response,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            st.error(f"❌ 질문 저장 중 오류: {str(e)}")
            return False
    
    def get_user_queries(self, user_id: str, limit: int = 10) -> List[Dict]:
        """사용자의 최근 질문들을 가져오기"""
        if not self.is_connected():
            return []
        
        try:
            query_ref = (self.db.collection('user_queries')
                        .where('user_id', '==', user_id)
                        .order_by('timestamp', direction=firestore.Query.DESCENDING)
                        .limit(limit))
            
            docs = query_ref.stream()
            queries = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                queries.append(data)
            
            return queries
        except Exception as e:
            st.error(f"❌ 질문 조회 중 오류: {str(e)}")
            return []
    
    # === 비즈니스 데이터 관련 함수 ===
    
    def save_business_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        """비즈니스 데이터 저장 (가입자 수, 매출 등)"""
        if not self.is_connected():
            return False
        
        try:
            doc_ref = self.db.collection('business_data').document()
            doc_ref.set({
                'data_type': data_type,
                'data': data,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            st.error(f"❌ 비즈니스 데이터 저장 중 오류: {str(e)}")
            return False
    
    def get_business_data(self, data_type: str, limit: int = 10) -> List[Dict]:
        """특정 타입의 비즈니스 데이터 조회"""
        if not self.is_connected():
            return []
        
        try:
            query_ref = (self.db.collection('business_data')
                        .where('data_type', '==', data_type)
                        .order_by('timestamp', direction=firestore.Query.DESCENDING)
                        .limit(limit))
            
            docs = query_ref.stream()
            business_data = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                business_data.append(data)
            
            return business_data
        except Exception as e:
            st.error(f"❌ 비즈니스 데이터 조회 중 오류: {str(e)}")
            return []
    
    # === 통계 및 분석 함수 ===
    
    def get_query_statistics(self) -> Dict[str, int]:
        """전체 질문 통계 조회"""
        if not self.is_connected():
            return {}
        
        try:
            # 전체 질문 수
            total_queries = len(list(self.db.collection('user_queries').stream()))
            
            # 오늘 질문 수 (간단한 예시)
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            # 실제로는 더 정교한 날짜 필터링이 필요합니다
            today_queries = 0  # 구현 필요
            
            return {
                'total_queries': total_queries,
                'today_queries': today_queries
            }
        except Exception as e:
            st.error(f"❌ 통계 조회 중 오류: {str(e)}")
            return {}

# 싱글톤 인스턴스 생성
firebase_service = FirebaseService()
