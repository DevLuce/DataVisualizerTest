import streamlit as st
# from your_agent import get_ai_agent_response # 실제로는 직접 만드신 AI 에이전트 함수를 가져옵니다.

# --- 더미 함수: 실제 AI 에이전트 로직으로 교체될 부분 ---
def get_ai_agent_response(prompt: str) -> str:
    """사용자의 프롬프트를 받아 AI 에이전트가 답변을 생성하는 함수(예시)"""
    if "가입자" in prompt:
        return "어제 신규 가입자는 총 125명입니다."
    elif "매출" in prompt:
        return "지난 주 총 매출은 1,250만원입니다."
    else:
        return "죄송합니다. 이해할 수 없는 질문입니다. '어제 가입자 수'와 같이 질문해주세요."
# ----------------------------------------------------

# 웹 페이지의 제목 설정
st.title("🤖 New Flower")

# 사용자가 프롬프트를 입력할 수 있는 텍스트 영역 생성
prompt = st.text_input("궁금한 점을 여기에 물어보세요! (예: 어제 신규 가입자는 몇 명이야?)")

# '결과 확인' 버튼 생성
if st.button("결과 확인하기"):
    if prompt:
        # 로딩 중임을 시각적으로 보여줌
        with st.spinner("데이터를 조회하고 답변을 생성하는 중입니다..."):
            # 입력된 프롬프트를 AI 에이전트 함수로 전달하여 결과를 받음
            response = get_ai_agent_response(prompt)
            # 결과 표시
            st.success(response)
    else:
        st.warning("질문을 입력해주세요.")