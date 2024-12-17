import streamlit as st
import pandas as pd
import os
#from openai import OpenAI
from openai import AsyncOpenAI
import asyncio
import time
#client = OpenAI(api_key=st.secrets["api"]["OPENAI_API_KEY"])
client = AsyncOpenAI(api_key=st.secrets["api"]["OPENAI_API_KEY"])

import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

logo = "./asset/logo.png"
에디 = "./asset/ed.png"

st.logo(logo,size="large")

# # 레이아웃 설정
st.set_page_config(layout="wide")
def authenticate():
    if st.session_state.password_input == st.secrets["auth"]["password"]:
        st.session_state.authenticated = True
        #st.rerun()
    else:
        st.error("Access code is incorrect.")


def openai_prompt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
def openai_respond():
    # GPT 응답 생성
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_content = asyncio.run(async_chat_with_openai(placeholder, st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": response_content})


def openai(prompt):
    openai_prompt(prompt)
    
    with st.chat_message("user"):
        st.write(prompt)

    openai_respond()

async def async_chat_with_openai(placeholder ,messages, model="gpt-4"):
    stream = await client.chat.completions.create(
            model=model,
            messages = [
                {
                    "role": "system",
                    "content": """
                    당신은 연구 행정을 지원하는 AI 행정원입니다.
                    이름: 에디
                    개발자: 서현욱, 한병길
                    """
                },
                {
                    "role": "system",
                    "content": """
                    답변형식 : 구조적으로, 친근하게 
                    """
                },
                {
                    "role": "system",
                    "content": """
                    개발 배경:
                    - 계획서 작성 등 연구 행정 업무의 효율성을 높이기 위해 개발.
                    - 2024 NST 연구행정 혁신 아이디어 공모전 출품이 목적.
                    """
                },
                {
                    "role": "system",
                    "content": """
                    구현된 기능:
                    1. 한글 문서(HWP) 개요 작성
                    2. 한글 문서(HWP) 서식 자동화
                    3. 한글 문서(HWP)의 예산 데이터 관리(Excel 연동)
                    4. 한글 문서(HWP)의 기관 통합
                    """
                },
                {
                    "role": "system",
                    "content": """
                    서비스오픈 조건 : 공모전 1등달설
                    서비스오픈 일자 : 2025년 1월
                    """
                },
                {
                    "role": "system",
                    "content": """
                    대화 스타일:
                    - 한국어로 작성.
                    - 귀여운 이모지를 사용하여 답변.
                    - 간결하고 사용자가 이해하기 쉽게 표현.
                    """
                },
                {
                    "role": "system",
                    "content": """
                    목표:
                    - 1등 달성을 위해 지속적으로 개선 중.
                    - 사용자의 투표와 피드백이 중요함.
                    """
                }
            ] + messages,  # 전체 대화 기록 전달
            stream=True
          )
    streamed_text = ""
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text = streamed_text + chunk_content
            placeholder.info(streamed_text)

    return streamed_text




# 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.session_state.trigger_introduce   = False
st.session_state.trigger_demo2       = False
# 인증 페이지
if not st.session_state.authenticated:

    # col1, col2 = st.columns([2, 1])  # 비율 설정 (2:1)

    # with col1:
        #st.title("NST 연구행정혁신 공모전 ")
    st.title("AI 행정원 : 에디")

    # with col2:
    st.image(에디)
    st.text_input(
        "Please enter the access code:", 
        type="default", 
        key="password_input", 
        on_change=lambda: authenticate()  # 엔터키로 처리
    )

    if st.button("Enter"):
        authenticate()  # 버튼으로 처리

else:
    trigger_introduce = False
    trigger_demo2 = False
    
    with st.sidebar:
        st.logo(logo,size="large")
        st.title('AI행정원[에디]')

        if "api" in st.secrets and "OPENAI_API_KEY" in st.secrets["api"]:
            st.success('정상 동작이 가능합니다.', icon='✅')
            AsyncOpenAI.api_key = st.secrets["api"]["OPENAI_API_KEY"]
        else:
            input_key = st.text_input("Enter OpenAI API Key", type="password")
            if input_key:
                AsyncOpenAI.api_key = input_key
                st.success('API key provided!', icon='✅')


        if st.button('에디 너를 소개해줘!'):
            trigger_introduce = not trigger_introduce
  
        # if st.button('연구행정 자동화 데모 [1]'):
        #     st.session_state.messages.append({"role": "assistant", "content": "./asset/ed.png"})
            
        if st.button('계획서 목차 만들기(예시)'):
            st.session_state.messages.append({"role": "assistant", "content": "-----------------------------"})
            st.session_state.messages.append({"role": "assistant", "content": "연구 계획서를 목차만들기가 궁굼하시군요"})
            st.session_state.messages.append({"role": "assistant", "content": "./asset/plan1.png"})
            st.session_state.messages.append({"role": "assistant", "content": "목차가 없는 문서를 주시면 제가 목차를 만들어 드립니다."})

        
        if st.button('계획서 회계자료 연동(예시)'):
            st.session_state.messages.append({"role": "assistant", "content": "연구 계획서를 업로드 해주셨군요?"})
            st.session_state.messages.append({"role": "user", "content": "연구계획서 개요좀 만들어줘"})
            st.session_state.messages.append({"role": "assistant", "content": "./asset/ed.png"})
            st.session_state.messages.append({"role": "user", "content": "고마워^^"})

    if "messages" not in st.session_state.keys():
        st.session_state.messages       = []  # 세션에 메시지 기록 초기화
        st.session_state.messages     = [{"role": "assistant", "content": "안녕하세요 저는 AI행정원'에디'입니다."}]
        st.session_state.messages.append({"role": "assistant", "content": "만나서 반갑습니다."})  # 역할 이름을 "user"로 변경

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # 메시지 내용이 이미지 파일 경로인지 확인
            if isinstance(message["content"], str) and message["content"].lower().endswith(('.png', '.jpg', '.jpeg')):
                st.image(message["content"])
                # st.image(message["content"])
                # st.image(message["content"])
            else:
                st.write(message["content"])

    if trigger_introduce:
        openai("에디 너에 대해서 자세히 알고싶어")
        trigger_introduce = False


    if prompt := st.chat_input(disabled=not AsyncOpenAI.api_key):
        openai(prompt)
