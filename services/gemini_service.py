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
    
    def get_data_analysis_response(self, prompt: str, context_data: str = None) -> str:
        """데이터 분석 전용 응답 생성
        
        Args:
            prompt: 사용자 질문
            context_data: 추가 컨텍스트 데이터
            
        Returns:
            데이터 분석 결과
        """
        try:
            # 데이터 분석에 특화된 프롬프트 작성
            analysis_prompt = f"""
당신은 데이터 분석 전문가입니다. 다음 데이터를 분석하고 한국어로 명확하고 유용한 인사이트를 제공해주세요.

사용자 질문: {prompt}

추가 컨텍스트 데이터:
{context_data if context_data else '없음'}

다음 가이드라인을 따라 답변해주세요:
1. 데이터를 명확하고 이해하기 쉬운 방식으로 설명
2. 주요 트렌드나 패턴 식별
3. 비즈니스 인사이트나 액션 아이템 제안
4. 숫자는 한국어 단위(만원, 명 등)로 표시
"""
            
            response = self.model.generate_content(analysis_prompt)
            return response.text
            
        except Exception as e:
            return f"데이터 분석 중 오류가 발생했습니다: {str(e)}"
    
    def get_smart_query_response(self, user_question: str) -> str:
        """사용자 질문을 분석하여 자동으로 데이터를 조회하고 답변 생성
        
        Args:
            user_question: 사용자의 질문
            
        Returns:
            데이터 기반 답변
        """
        try:
            # Firebase 서비스 import
            from services.firebase_service import firebase_service
            
            # 데이터베이스 스키마 정보 가져오기
            schema_info = firebase_service.get_database_schema()
            
            # Gemini에게 쿼리 생성 요청
            query_generation_prompt = f"""
당신은 데이터베이스 전문가입니다. 사용자의 질문을 분석하여 적절한 Firestore 쿼리를 생성하고 실행해주세요.

사용자 질문: "{user_question}"

데이터베이스 스키마:
{schema_info}

다음 단계로 진행해주세요:
1. 사용자 질문을 분석하여 필요한 데이터 파악
2. 적절한 쿼리 전략 결정 (조회, 집계, 정렬 등)
3. 쿼리 실행 및 결과 분석
4. 한국어로 자연스럽고 유용한 답변 생성

예시 쿼리 형식:
- 단순 조회: execute_dynamic_query('collection_name', filters, order_by, limit)
- 집계 연산: get_aggregated_data('collection_name', 'sum/count/avg', 'field_name', filters)

지금 실제 쿼리를 실행하고 결과를 분석해주세요.
"""
            
            # 첫 번째 단계: 쿼리 전략 결정
            strategy_response = self.model.generate_content(query_generation_prompt)
            strategy_text = strategy_response.text
            
            # 질문 유형에 따른 데이터 조회 로직
            query_result = self._execute_smart_query(user_question)
            
            # 결과를 바탕으로 최종 답변 생성
            final_prompt = f"""
다음 데이터 조회 결과를 바탕으로 사용자의 질문에 답변해주세요.

사용자 질문: "{user_question}"

데이터 조회 결과:
{query_result}

답변 가이드라인:
1. 숫자는 한국어 단위로 표시 (예: 1,250명, 125만원)
2. 구체적이고 유용한 정보 제공
3. 필요시 추가 인사이트나 추천사항 포함
4. 자연스럽고 친근한 어조
"""
            
            final_response = self.model.generate_content(final_prompt)
            return final_response.text
            
        except Exception as e:
            return f"스마트 쿼리 처리 중 오류가 발생했습니다: {str(e)}"
    
    def _execute_smart_query(self, question: str) -> str:
        """질문 유형에 따른 실제 데이터 조회 실행"""
        try:
            from services.firebase_service import firebase_service
            from datetime import datetime, timedelta
            
            # 오늘 날짜 계산
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            question_lower = question.lower()
            
            # 사용자 수 관련 질문
            if any(word in question for word in ['가입자', '사용자', '회원']):
                if '오늘' in question:
                    result = firebase_service.get_aggregated_data('users', 'count', 
                        filters=[{'field': 'created_at', 'operator': '>=', 'value': today}])
                    return f"오늘 신규 가입자: {result['result']}명"
                elif '이번 주' in question or '주간' in question:
                    result = firebase_service.get_aggregated_data('users', 'count',
                        filters=[{'field': 'created_at', 'operator': '>=', 'value': week_ago}])
                    return f"이번 주 신규 가입자: {result['result']}명"
                else:
                    result = firebase_service.get_aggregated_data('users', 'count')
                    return f"전체 사용자 수: {result['result']}명"
            
            # 매출 관련 질문
            elif any(word in question for word in ['매출', '매상', '수익', '금액']):
                if '오늘' in question:
                    result = firebase_service.get_aggregated_data('orders', 'sum', 'amount',
                        filters=[{'field': 'created_at', 'operator': '>=', 'value': today}])
                    return f"오늘 매출: {result['result']:,.0f}원"
                elif '이번 주' in question or '주간' in question:
                    result = firebase_service.get_aggregated_data('orders', 'sum', 'amount',
                        filters=[{'field': 'created_at', 'operator': '>=', 'value': week_ago}])
                    return f"이번 주 매출: {result['result']:,.0f}원"
                elif '이번 달' in question or '월간' in question:
                    result = firebase_service.get_aggregated_data('orders', 'sum', 'amount',
                        filters=[{'field': 'created_at', 'operator': '>=', 'value': month_ago}])
                    return f"이번 달 매출: {result['result']:,.0f}원"
                else:
                    result = firebase_service.get_aggregated_data('orders', 'sum', 'amount')
                    return f"전체 매출: {result['result']:,.0f}원"
            
            # 상품 관련 질문
            elif any(word in question for word in ['상품', '제품', '인기', '재고']):
                if '인기' in question or '베스트' in question:
                    result = firebase_service.execute_dynamic_query('products', 
                        order_by='-sales_count', limit=5)
                    products = [f"{p['name']} ({p['sales_count']}개 판매)" for p in result]
                    return f"인기 상품 TOP 5: {', '.join(products)}"
                elif '재고' in question and '부족' in question:
                    result = firebase_service.execute_dynamic_query('products',
                        filters=[{'field': 'stock', 'operator': '<', 'value': 10}])
                    products = [f"{p['name']} (재고 {p['stock']}개)" for p in result]
                    return f"재고 부족 상품: {', '.join(products) if products else '없음'}"
                else:
                    result = firebase_service.get_aggregated_data('products', 'count')
                    return f"전체 상품 수: {result['result']}개"
            
            # 기본 대시보드 데이터
            else:
                dashboard_data = firebase_service.get_comprehensive_dashboard_data()
                return str(dashboard_data)
                
        except Exception as e:
            return f"데이터 조회 중 오류: {str(e)}"

# 싱글톤 인스턴스 생성
gemini_service = GeminiService()
