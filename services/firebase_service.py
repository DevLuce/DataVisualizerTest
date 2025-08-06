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
        """스트림릿 클라우드에서 실행 중인지 확인"""
        try:
            import streamlit as st
            return hasattr(st, 'secrets') and 'firebase_credentials' in st.secrets
        except Exception:
            # secrets 파일이 없거나 오류가 발생하면 로컬 환경으로 간주
            return False
    
    def _get_firebase_credentials_from_secrets(self) -> dict:
        """Streamlit secrets에서 Firebase 자격 증명 가져오기"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'firebase_credentials' in st.secrets:
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
    
    # === 비즈니스 데이터 스키마 및 조회 함수 ===
    
    def get_user_count_data(self) -> Dict[str, Any]:
        """사용자 수 관련 데이터 조회
        
        Returns:
            {
                'total_users': int,      # 전체 사용자 수
                'new_users_today': int,  # 오늘 신규 가입자
                'new_users_week': int,   # 이번 주 신규 가입자
                'active_users': int,     # 활성 사용자 수
                'last_updated': str      # 마지막 업데이트 시간
            }
        """
        if not self.is_connected():
            return self._get_mock_user_data()
        
        try:
            # users 컬렉션에서 데이터 조회
            users_ref = self.db.collection('users')
            
            # 전체 사용자 수
            total_users = len(list(users_ref.stream()))
            
            # 오늘 신규 가입자 (예시)
            from datetime import datetime, timedelta
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            new_today_query = users_ref.where('created_at', '>=', today)
            new_users_today = len(list(new_today_query.stream()))
            
            # 이번 주 신규 가입자
            week_ago = today - timedelta(days=7)
            new_week_query = users_ref.where('created_at', '>=', week_ago)
            new_users_week = len(list(new_week_query.stream()))
            
            # 활성 사용자 (최근 7일 내 활동)
            active_query = users_ref.where('last_active', '>=', week_ago)
            active_users = len(list(active_query.stream()))
            
            return {
                'total_users': total_users,
                'new_users_today': new_users_today,
                'new_users_week': new_users_week,
                'active_users': active_users,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"사용자 데이터 조회 중 오류: {str(e)}")
            return self._get_mock_user_data()
    
    def get_sales_data(self) -> Dict[str, Any]:
        """매출 관련 데이터 조회
        
        Returns:
            {
                'total_sales': float,        # 총 매출
                'sales_today': float,        # 오늘 매출
                'sales_this_week': float,    # 이번 주 매출
                'sales_this_month': float,   # 이번 달 매출
                'avg_order_value': float,    # 평균 주문 금액
                'order_count': int,          # 총 주문 수
                'currency': str,             # 통화 단위
                'last_updated': str          # 마지막 업데이트 시간
            }
        """
        if not self.is_connected():
            return self._get_mock_sales_data()
        
        try:
            # orders 컬렉션에서 데이터 조회
            orders_ref = self.db.collection('orders')
            
            # 전체 주문 조회
            orders = list(orders_ref.stream())
            total_sales = sum(order.to_dict().get('amount', 0) for order in orders)
            order_count = len(orders)
            
            # 시간별 필터링
            from datetime import datetime, timedelta
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # 오늘 매출
            today_orders = orders_ref.where('created_at', '>=', today)
            sales_today = sum(order.to_dict().get('amount', 0) for order in today_orders.stream())
            
            # 이번 주 매출
            week_orders = orders_ref.where('created_at', '>=', week_ago)
            sales_this_week = sum(order.to_dict().get('amount', 0) for order in week_orders.stream())
            
            # 이번 달 매출
            month_orders = orders_ref.where('created_at', '>=', month_ago)
            sales_this_month = sum(order.to_dict().get('amount', 0) for order in month_orders.stream())
            
            # 평균 주문 금액
            avg_order_value = total_sales / order_count if order_count > 0 else 0
            
            return {
                'total_sales': total_sales,
                'sales_today': sales_today,
                'sales_this_week': sales_this_week,
                'sales_this_month': sales_this_month,
                'avg_order_value': avg_order_value,
                'order_count': order_count,
                'currency': 'KRW',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"매출 데이터 조회 중 오류: {str(e)}")
            return self._get_mock_sales_data()
    
    def get_product_analytics(self) -> Dict[str, Any]:
        """상품 분석 데이터 조회
        
        Returns:
            {
                'total_products': int,           # 전체 상품 수
                'popular_products': List[Dict],  # 인기 상품 목록
                'low_stock_products': List[Dict], # 재고 부족 상품
                'categories': List[str],         # 상품 카테고리 목록
                'last_updated': str              # 마지막 업데이트 시간
            }
        """
        if not self.is_connected():
            return self._get_mock_product_data()
        
        try:
            # products 컬렉션에서 데이터 조회
            products_ref = self.db.collection('products')
            products = list(products_ref.stream())
            
            total_products = len(products)
            
            # 인기 상품 (판매량 기준 상위 5개)
            popular_products = []
            for product in products:
                data = product.to_dict()
                popular_products.append({
                    'name': data.get('name', ''),
                    'sales_count': data.get('sales_count', 0),
                    'price': data.get('price', 0)
                })
            
            popular_products = sorted(popular_products, key=lambda x: x['sales_count'], reverse=True)[:5]
            
            # 재고 부족 상품 (재고 10개 미만)
            low_stock_products = []
            for product in products:
                data = product.to_dict()
                if data.get('stock', 0) < 10:
                    low_stock_products.append({
                        'name': data.get('name', ''),
                        'stock': data.get('stock', 0),
                        'price': data.get('price', 0)
                    })
            
            # 카테고리 목록
            categories = list(set(product.to_dict().get('category', '') for product in products))
            categories = [cat for cat in categories if cat]  # 빈 문자열 제거
            
            return {
                'total_products': total_products,
                'popular_products': popular_products,
                'low_stock_products': low_stock_products,
                'categories': categories,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"상품 분석 데이터 조회 중 오류: {str(e)}")
            return self._get_mock_product_data()
    
    def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """대시보드용 종합 데이터 조회 (Gemini AI가 분석하기 좋은 형태)
        
        Returns:
            모든 비즈니스 데이터를 포함한 종합 딕셔너리
        """
        return {
            'users': self.get_user_count_data(),
            'sales': self.get_sales_data(),
            'products': self.get_product_analytics(),
            'summary': {
                'data_source': 'Firebase Firestore',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'connected' if self.is_connected() else 'mock_data'
            }
        }
    
    # === Mock 데이터 함수들 (Firebase 연결이 없을 때 사용) ===
    
    def _get_mock_user_data(self) -> Dict[str, Any]:
        """Mock 사용자 데이터 (테스트용)"""
        from datetime import datetime
        return {
            'total_users': 1250,
            'new_users_today': 125,
            'new_users_week': 890,
            'active_users': 750,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_mock_sales_data(self) -> Dict[str, Any]:
        """Mock 매출 데이터 (테스트용)"""
        from datetime import datetime
        return {
            'total_sales': 125000000.0,  # 1억 2천 5백만원
            'sales_today': 2500000.0,    # 250만원
            'sales_this_week': 12500000.0, # 1천 2백 50만원
            'sales_this_month': 45000000.0, # 4천 5백만원
            'avg_order_value': 85000.0,   # 8만 5천원
            'order_count': 1470,
            'currency': 'KRW',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_mock_product_data(self) -> Dict[str, Any]:
        """Mock 상품 데이터 (테스트용)"""
        from datetime import datetime
        return {
            'total_products': 245,
            'popular_products': [
                {'name': '프리미엄 노트북', 'sales_count': 156, 'price': 1200000},
                {'name': '무선 이어폰', 'sales_count': 134, 'price': 150000},
                {'name': '스마트워치', 'sales_count': 98, 'price': 300000},
                {'name': '태블릿', 'sales_count': 87, 'price': 800000},
                {'name': '키보드', 'sales_count': 76, 'price': 120000}
            ],
            'low_stock_products': [
                {'name': '프리미엄 노트북', 'stock': 5, 'price': 1200000},
                {'name': '게이밍 마우스', 'stock': 8, 'price': 80000},
                {'name': '모니터', 'stock': 3, 'price': 400000}
            ],
            'categories': ['전자제품', '컴퓨터', '액세서리', '스마트기기', '게이밍'],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # === 동적 쿼리 생성 및 실행 함수 (Gemini AI용) ===
    
    def execute_dynamic_query(self, collection_name: str, filters: List[Dict] = None, 
                            order_by: str = None, limit: int = None) -> List[Dict]:
        """동적으로 Firestore 쿼리를 생성하고 실행
        
        Args:
            collection_name: 컬렉션 이름 (예: 'users', 'orders', 'products')
            filters: 필터 조건 리스트 [{'field': 'status', 'operator': '==', 'value': 'active'}]
            order_by: 정렬 필드 (예: 'created_at')
            limit: 결과 제한 수
            
        Returns:
            쿼리 결과 리스트
        """
        if not self.is_connected():
            return self._get_mock_query_result(collection_name)
        
        try:
            # 기본 쿼리 시작
            query_ref = self.db.collection(collection_name)
            
            # 필터 조건 적용
            if filters:
                for filter_condition in filters:
                    field = filter_condition.get('field')
                    operator = filter_condition.get('operator', '==')
                    value = filter_condition.get('value')
                    
                    if field and value is not None:
                        query_ref = query_ref.where(field, operator, value)
            
            # 정렬 조건 적용
            if order_by:
                direction = firestore.Query.DESCENDING  # 기본값
                if order_by.startswith('-'):
                    order_by = order_by[1:]  # '-' 제거
                    direction = firestore.Query.DESCENDING
                elif order_by.startswith('+'):
                    order_by = order_by[1:]  # '+' 제거
                    direction = firestore.Query.ASCENDING
                
                query_ref = query_ref.order_by(order_by, direction=direction)
            
            # 결과 제한
            if limit:
                query_ref = query_ref.limit(limit)
            
            # 쿼리 실행
            docs = query_ref.stream()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id  # 문서 ID 추가
                results.append(data)
            
            return results
            
        except Exception as e:
            print(f"동적 쿼리 실행 중 오류: {str(e)}")
            return self._get_mock_query_result(collection_name)
    
    def get_aggregated_data(self, collection_name: str, aggregation_type: str, 
                          field: str = None, filters: List[Dict] = None) -> Dict[str, Any]:
        """집계 데이터 조회 (COUNT, SUM, AVG 등)
        
        Args:
            collection_name: 컬렉션 이름
            aggregation_type: 'count', 'sum', 'avg', 'max', 'min'
            field: 집계할 필드 (count가 아닌 경우 필수)
            filters: 필터 조건
            
        Returns:
            집계 결과
        """
        if not self.is_connected():
            return {'result': 100, 'type': aggregation_type}
        
        try:
            # 데이터 조회
            data = self.execute_dynamic_query(collection_name, filters)
            
            if aggregation_type.lower() == 'count':
                return {'result': len(data), 'type': 'count'}
            
            if not field:
                raise ValueError(f"{aggregation_type}에는 field 파라미터가 필요합니다")
            
            # 숫자 값만 추출
            values = []
            for item in data:
                if field in item and isinstance(item[field], (int, float)):
                    values.append(item[field])
            
            if not values:
                return {'result': 0, 'type': aggregation_type}
            
            # 집계 계산
            if aggregation_type.lower() == 'sum':
                result = sum(values)
            elif aggregation_type.lower() == 'avg':
                result = sum(values) / len(values)
            elif aggregation_type.lower() == 'max':
                result = max(values)
            elif aggregation_type.lower() == 'min':
                result = min(values)
            else:
                result = 0
            
            return {
                'result': result,
                'type': aggregation_type,
                'count': len(values)
            }
            
        except Exception as e:
            print(f"집계 데이터 조회 중 오류: {str(e)}")
            return {'result': 0, 'type': aggregation_type, 'error': str(e)}
    
    def get_database_schema(self) -> Dict[str, Any]:
        """데이터베이스 스키마 정보 반환 (Gemini AI가 쿼리 생성 시 참고용)
        
        Returns:
            JSON 파일에서 로드한 상세한 스키마 정보
        """
        try:
            import json
            import os
            
            # 스키마 파일 경로
            schema_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'firebase-schema.json')
            
            # JSON 파일 로드
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                return schema_data
            else:
                print(f"스키마 파일을 찾을 수 없습니다: {schema_path}")
                return self._get_fallback_schema()
                
        except Exception as e:
            print(f"스키마 로드 중 오류: {str(e)}")
            return self._get_fallback_schema()
    
    def _get_fallback_schema(self) -> Dict[str, Any]:
        """스키마 파일 로드 실패 시 기본 스키마 반환"""
        return {
            'collections': {
                'users': {
                    'description': '사용자 정보',
                    'fields': {
                        'id': 'string (자동생성)',
                        'name': 'string (사용자 이름)',
                        'email': 'string (이메일)',
                        'created_at': 'timestamp (가입일)',
                        'last_active': 'timestamp (마지막 활동일)',
                        'status': 'string (active, inactive)',
                        'age': 'number (나이)',
                        'location': 'string (지역)'
                    }
                },
                'orders': {
                    'description': '주문 정보',
                    'fields': {
                        'id': 'string (자동생성)',
                        'user_id': 'string (사용자 ID)',
                        'amount': 'number (주문 금액)',
                        'status': 'string (pending, completed, cancelled)',
                        'created_at': 'timestamp (주문일)',
                        'product_ids': 'array (상품 ID 목록)',
                        'payment_method': 'string (결제 방법)'
                    }
                },
                'products': {
                    'description': '상품 정보',
                    'fields': {
                        'id': 'string (자동생성)',
                        'name': 'string (상품명)',
                        'price': 'number (가격)',
                        'stock': 'number (재고)',
                        'category': 'string (카테고리)',
                        'sales_count': 'number (판매 수량)',
                        'created_at': 'timestamp (등록일)',
                        'rating': 'number (평점)'
                    }
                }
            },
            'operators': ['==', '!=', '<', '<=', '>', '>=', 'in', 'not-in', 'array-contains'],
            'aggregations': ['count', 'sum', 'avg', 'max', 'min']
        }
    
    def _get_mock_query_result(self, collection_name: str) -> List[Dict]:
        """Mock 쿼리 결과 (테스트용)"""
        mock_data = {
            'users': [
                {'id': 'user1', 'name': '김철수', 'email': 'kim@example.com', 'created_at': '2025-08-06', 'status': 'active'},
                {'id': 'user2', 'name': '이영희', 'email': 'lee@example.com', 'created_at': '2025-08-05', 'status': 'active'}
            ],
            'orders': [
                {'id': 'order1', 'user_id': 'user1', 'amount': 50000, 'status': 'completed', 'created_at': '2025-08-06'},
                {'id': 'order2', 'user_id': 'user2', 'amount': 75000, 'status': 'completed', 'created_at': '2025-08-05'}
            ],
            'products': [
                {'id': 'prod1', 'name': '노트북', 'price': 1200000, 'stock': 5, 'category': '전자제품', 'sales_count': 156},
                {'id': 'prod2', 'name': '마우스', 'price': 50000, 'stock': 20, 'category': '액세서리', 'sales_count': 89}
            ]
        }
        return mock_data.get(collection_name, [])
    
    # === 통계 및 분석 함수 ===
    
    def get_query_statistics(self) -> Dict[str, int]:
        """전체 질문 통계 조회"""
        if not self.is_connected():
            return {
                'total_queries': 1250,
                'today_queries': 45
            }
        
        try:
            # 전체 질문 수
            total_queries = len(list(self.db.collection('user_queries').stream()))
            
            # 오늘 질문 수
            from datetime import datetime
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_query_ref = self.db.collection('user_queries').where('timestamp', '>=', today)
            today_queries = len(list(today_query_ref.stream()))
            
            return {
                'total_queries': total_queries,
                'today_queries': today_queries
            }
        except Exception as e:
            st.error(f"❌ 통계 조회 중 오류: {str(e)}")
            return {
                'total_queries': 0,
                'today_queries': 0
            }

# 싱글톤 인스턴스 생성
firebase_service = FirebaseService()
