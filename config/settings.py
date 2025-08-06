"""
애플리케이션 설정 관리 모듈
"""
import os
import streamlit as st

# 환경 변수 로드 (로컬 환경에서만)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Streamlit Cloud에서는 dotenv가 필요하지 않음
    pass

def get_env_var(key: str, default: str = None):
    """환경변수 또는 Streamlit secrets에서 값 가져오기"""
    # 먼저 환경변수에서 확인 (로컬 환경 우선)
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value
    
    # 환경변수가 없으면 Streamlit secrets 확인 (Streamlit Cloud용)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        # secrets 파일이 없거나 오류가 발생하면 무시
        pass
    
    # 둘 다 없으면 기본값 반환
    return default

class Config:
    """애플리케이션 설정 클래스"""
    
    # Gemini API 설정
    GEMINI_API_KEY = get_env_var("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.0-flash"
    
    # Firebase 설정
    FIREBASE_CREDENTIALS_PATH = get_env_var("FIREBASE_CREDENTIALS_PATH", "config/firebase-credentials.json")
    FIREBASE_PROJECT_ID = get_env_var("FIREBASE_PROJECT_ID")
    
    # Streamlit 설정
    APP_TITLE = "🤖 New Flower"
    
    @classmethod
    def validate_config(cls):
        """필수 설정값들이 있는지 확인"""
        missing_configs = []
        
        if not cls.GEMINI_API_KEY:
            missing_configs.append("GEMINI_API_KEY")
        
        if not cls.FIREBASE_PROJECT_ID:
            missing_configs.append("FIREBASE_PROJECT_ID")
            
        return missing_configs
