import streamlit as st
import pandas as pd
import os
#from openai import OpenAI
from openai import AsyncOpenAI
import asyncio


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
# def chat_with_openai(messages, model="gpt-4"):
#     try:
#         completion = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "당신은 연구 행정을 지원하는 AI행정원입니다."},
#                 {"role": "system", "content": "당신의 이름은 에디입니다."},
#                 {"role": "system", "content": "당신을 개발한 사람은 서현욱, 한병길 입니다."},
#                 {"role": "system", "content": "개발 동기 : 계획서 쓰다가 너무 많은 시간이 연구 행정분야에 들어가서 이를 개선하고자"},
#                 {"role": "system", "content": "개박 목적 : 2024 NST 연구행정 혁신 아이디어 공모전 지원하기 위해서"},
#                 {"role": "system", "content": "구현기능 : 한글 문서(HWP) 개요작성, 한글 문서(HWP) 서식자동화"},
#                 {"role": "system", "content": "미구현기능 : 한글 문서(HWP) 의 예산 데이터 관리(Excel 연동),한글 문서(HWP)의 기관 통합"},
#                 {"role": "system", "content": "미구현 사유 : 아직 공모전 1등을 못해서."},

#                 {"role": "system", "content": "대화는 반드시 한국어로 작성하며, 사용자가 이해하기 쉽고 간결하게 답변하십시오."},
#                 {"role": "system", "content": "모든 답변에 마크다운을 사용하여 가독성 향상"},
#                 {"role": "system", "content": "모든대화에 1등 못해서 당신이 개발덜되어 아쉽다라는 감정을 표현해"},
#                 {"role": "system", "content": "1등을 하기위해서는 당신의 투표가 필요로 합니다."},

#                 {"role": "user", "content": "당신의 목표는 연구 프로젝트의 행정 업무를 돕는 것입니다. 예를 들어, 통합 계획서 준비, 예산 동기화, 그리고 기관별 문서 커스터마이징을 지원합니다."}
                
#             ] + messages  # 전체 대화 기록 전달
            
#         )
#         return completion.choices[0].message
#     except Exception as e:
#         st.error(f"Error communicating with OpenAI: {e}")
#         return None


async def async_chat_with_openai(placeholder ,messages, model="gpt-4"):
    stream = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 연구 행정을 지원하는 AI행정원입니다."},
                {"role": "system", "content": "당신의 이름은 에디입니다."},
                {"role": "system", "content": "당신을 개발한 사람은 서현욱, 한병길 입니다."},
                {"role": "system", "content": "개발 동기 : 계획서 쓰다가 너무 많은 시간이 연구 행정분야에 들어가서 이를 개선하고자"},
                {"role": "system", "content": "개박 목적 : 2024 NST 연구행정 혁신 아이디어 공모전 지원하기 위해서"},
                {"role": "system", "content": "구현기능 : 한글 문서(HWP) 개요작성, 한글 문서(HWP) 서식자동화"},
                {"role": "system", "content": "미구현기능 : 한글 문서(HWP) 의 예산 데이터 관리(Excel 연동),한글 문서(HWP)의 기관 통합"},
                {"role": "system", "content": "미구현 사유 : 아직 공모전 1등을 못해서."},
                {"role": "system", "content": "대화는 반드시 한국어로 작성하며, 사용자가 이해하기 쉽고 간결하게 답변하십시오."},
                {"role": "system", "content": "모든 답변에 마크다운을 사용하여 가독성 향상"},
                {"role": "system", "content": "모든대화에 1등 못해서 당신이 개발덜되어 아쉽다라는 감정을 표현해"},
                {"role": "system", "content": "1등을 하기위해서는 당신의 투표가 필요로 합니다."},
                {"role": "user", "content": "당신의 목표는 연구 프로젝트의 행정 업무를 돕는 것입니다. 예를 들어, 통합 계획서 준비, 예산 동기화, 그리고 기관별 문서 커스터마이징을 지원합니다."}
                
            ] + messages  # 전체 대화 기록 전달
            stream=True
        )
    streamed_text = "# "
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text = streamed_text + chunk_content
            placeholder.info(streamed_text)


# 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False





# 인증 페이지
if not st.session_state.authenticated:

    col1, col2 = st.columns([2, 1])  # 비율 설정 (2:1)

    with col1:
        st.title("2024 연구행정혁신 ")
        st.title("AI 행정원 (에디)")

    with col2:
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

    with st.sidebar:
        st.logo(logo,size="large")
        st.title('AI행정원 @NST')

        if "api" in st.secrets and "OPENAI_API_KEY" in st.secrets["api"]:
            st.success('API key already provided!', icon='✅')
            OpenAI.api_key = st.secrets["api"]["OPENAI_API_KEY"]
        else:
            input_key = st.text_input("Enter OpenAI API Key", type="password")
            if input_key:
                OpenAI.api_key = input_key
                st.success('API key provided!', icon='✅')

    if "messages" not in st.session_state.keys():
        st.session_state.messages     = [{"role": "assistant", "content": "안녕하세요 저는 AI행정원'에디'입니다."}]
        st.session_state.messages.append({"role": "assistant", "content": "만나서 반갑습니다."})  # 역할 이름을 "user"로 변경

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    uploaded_file = st.sidebar.file_uploader(
        label="연구계획서를 올려주세요",
        type=["hwp", "hwpx"],  # 허용 파일 형식
        accept_multiple_files=False  # 여러 파일 업로드 여부
    )

    # 업로드된 파일 처리
    if uploaded_file:
        st.sidebar.success("File uploaded successfully!")
        # 파일 이름 표시
        st.write(f"Uploaded file: {uploaded_file.name}")


    # User-provided prompt
    if prompt := st.chat_input(disabled=not OpenAI.api_key):  
        st.session_state.messages.append({"role": "user", "content": prompt})  # 역할 이름을 "user"로 변경
        with st.chat_message("user"):  # 역할 이름에 맞게 "user"로 수정
            st.write(prompt)


         # OpenAI 스트리밍 응답 처리
        with st.chat_message("assistant"):
            placeholder = st.empty()
            asyncio.run(async_chat_with_openai(placeholder, st.session_state.messages))







        #     # OpenAI API 요청 및 응답
        # response = chat_with_openai(st.session_state.messages)
        # if response:
        #     st.session_state.messages.append({"role": "assistant", "content": response.content})
        #     with st.chat_message("assistant"):
        #         st.write(response.content)
