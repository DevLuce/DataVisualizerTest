"""
Gemini AI 연동 서비스 모듈
"""
import google.generativeai as genai
import streamlit as st
from config.settings import Config

class GeminiService:
    """Gemini AI 연동을 위한 서비스 클래스"""
    
    def __init__(self):
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Gemini API 초기화"""
        try:
            if Config.GEMINI_API_KEY:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            else:
                st.error("⚠️ GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
                self.model = None
        except Exception as e:
            st.error(f"❌ Gemini API 초기화 중 오류: {str(e)}")
            self.model = None
    
    def is_connected(self) -> bool:
        """Gemini API 연결 상태 확인"""
        return self.model is not None
    
    def generate_response(self, prompt: str, context: str = None) -> str:
        """사용자 프롬프트에 대한 AI 응답 생성"""
        if not self.is_connected():
            return "❌ Gemini API가 설정되지 않았습니다. API 키를 확인해주세요."
        
        try:
            # 기본 시스템 프롬프트
            system_prompt = """
당신은 데이터 분석 전문가입니다. 사용자의 질문에 대해 친근하고 정확한 답변을 제공해주세요.
특히 비즈니스 데이터 관련 질문(가입자 수, 매출, 성과 등)에 대해 전문적인 분석을 제공합니다.
답변은 한국어로 해주세요.
            """
            
            # 컨텍스트가 있다면 추가
            if context:
                system_prompt += f"\n\n참고 데이터:\n{context}"
            
            full_prompt = f"{system_prompt}\n\n사용자 질문: {prompt}"
            
            # Gemini API 호출
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"❌ AI 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def generate_data_analysis(self, data: dict, question: str) -> str:
        """데이터 분석 전용 응답 생성"""
        if not self.is_connected():
            return "❌ Gemini API가 설정되지 않았습니다."
        
        try:
            analysis_prompt = f"""
데이터 분석 전문가로서 다음 데이터를 분석하고 질문에 답변해주세요.

데이터: {data}
질문: {question}

분석 결과를 다음 형식으로 제공해주세요:
1. 핵심 인사이트
2. 구체적인 수치 분석
3. 추천사항 (있다면)

답변은 한국어로 해주세요.
            """
            
            response = self.model.generate_content(analysis_prompt)
            return response.text
            
        except Exception as e:
            return f"❌ 데이터 분석 중 오류가 발생했습니다: {str(e)}"

# 싱글톤 인스턴스 생성
gemini_service = GeminiService()
