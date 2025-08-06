import streamlit as st
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from services.gemini_service import gemini_service
from services.firebase_service import firebase_service
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="New Flower",
    page_icon="🤖",
    layout="wide"
)

def initialize_services():
    """서비스 초기화 및 설정 검증"""
    missing_configs = Config.validate_config()
    
    if missing_configs:
        st.error(f"⚠️ 다음 설정이 누락되었습니다: {', '.join(missing_configs)}")
        st.info("📝 .env 파일을 확인하고 필요한 API 키와 설정을 추가해주세요.")
        return False
    
    # 서비스 연결 상태 확인
    gemini_connected = gemini_service.is_connected()
    firebase_connected = firebase_service.is_connected()
    
    if not gemini_connected:
        st.warning("⚠️ Gemini API 연결에 문제가 있습니다.")
    
    if not firebase_connected:
        st.warning("⚠️ Firebase 연결에 문제가 있습니다. (선택사항)")
    
    return gemini_connected

def save_query_to_firebase(user_id: str, query: str, response: str):
    """Firebase에 질문과 응답 저장"""
    if firebase_service.is_connected():
        success = firebase_service.save_user_query(user_id, query, response)
        if success:
            st.success("💾 질문이 저장되었습니다!")
    else:
        st.info("📝 Firebase가 연결되지 않아 질문이 저장되지 않았습니다.")

def display_recent_queries(user_id: str):
    """최근 질문들 표시"""
    if firebase_service.is_connected():
        recent_queries = firebase_service.get_user_queries(user_id, limit=5)
        
        if recent_queries:
            st.sidebar.subheader("📋 최근 질문들")
            for i, query_data in enumerate(recent_queries):
                with st.sidebar.expander(f"질문 {i+1}: {query_data['query'][:30]}..."):
                    st.write(f"**질문:** {query_data['query']}")
                    st.write(f"**답변:** {query_data['response'][:100]}...")
                    if 'timestamp' in query_data and query_data['timestamp']:
                        st.write(f"**시간:** {query_data['timestamp']}")

def main():
    """메인 애플리케이션 함수"""
    # 서비스 초기화
    services_ready = initialize_services()
    
    # 메인 타이틀
    st.title(Config.APP_TITLE)
    st.markdown("---")
    
    # 사용자 ID 생성 (세션 기반)
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 사이드바에 최근 질문들 표시
    display_recent_queries(st.session_state.user_id)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 질문하기")
        prompt = st.text_input(
            "궁금한 점을 여기에 물어보세요!", 
            placeholder="예: 어제 신규 가입자는 몇 명이야?"
        )
        
        # 고급 옵션
        with st.expander("🔧 고급 옵션"):
            save_to_firebase = st.checkbox("Firebase에 질문 저장", value=True)
            include_context = st.checkbox("이전 대화 맥락 포함", value=False)
    
    with col2:
        st.subheader("📊 상태")
        if services_ready:
            st.success("✅ Gemini API 연결됨")
        else:
            st.error("❌ Gemini API 연결 안됨")
        
        if firebase_service.is_connected():
            st.success("✅ Firebase 연결됨")
        else:
            st.warning("⚠️ Firebase 연결 안됨")
    
    # 결과 확인 버튼
    if st.button("🔍 결과 확인하기", type="primary"):
        if not prompt:
            st.warning("질문을 입력해주세요.")
            return
        
        if not services_ready:
            st.error("서비스가 준비되지 않았습니다. 설정을 확인해주세요.")
            return
        
        # 로딩 스피너와 함께 AI 응답 생성
        with st.spinner("🤖 AI가 답변을 생성하는 중입니다..."):
            # 컨텍스트 준비 (옵션)
            context = None
            if include_context and firebase_service.is_connected():
                recent_queries = firebase_service.get_user_queries(st.session_state.user_id, limit=3)
                if recent_queries:
                    context = "\n".join([f"Q: {q['query']} A: {q['response']}" for q in recent_queries])
            
            # AI 응답 생성
            response = gemini_service.generate_response(prompt, context)
            
            # 결과 표시
            st.markdown("### 🎯 답변")
            st.success(response)
            
            # Firebase에 저장 (옵션)
            if save_to_firebase:
                save_query_to_firebase(st.session_state.user_id, prompt, response)
    
    # 푸터
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"  
        "🤖 New Flower - AI 기반 데이터 분석 도우미"  
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()