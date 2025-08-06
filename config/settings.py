"""
애플리케이션 설정 관리 모듈
"""
import os
from dotenv import load_dotenv
import streamlit as st

# 환경 변수 로드
load_dotenv()

def get_env_var(key: str, default: str = None):
    """환경변수 또는 Streamlit secrets에서 값 가져오기"""
    # Streamlit Cloud에서 실행 중인 경우 secrets 사용
    if hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    # 로컬 환경에서는 환경변수 사용
    return os.getenv(key, default)

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
