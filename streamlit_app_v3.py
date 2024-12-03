import streamlit as st
import pandas as pd
import os
# import openai

import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

logo = "./asset/logo.png"


st.title("2024연구행정혁신 - AI행정원 Demo")

# 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 인증 페이지
if not st.session_state.authenticated:
    password_input = st.text_input("Please enter the access code:", type="password")
    if st.button("Enter"):
        if password_input == st.secrets["auth"]["password"]:
            st.session_state.authenticated = True
            # 페이지를 다시 로드하지 않고, 현재 상태에서 컨텐츠가 업데이트되도록 설정
            st.rerun()
        else:
            st.error("Access code is incorrect.")

else:
    # Replicate Credentials
    with st.sidebar:
        st.title('AI행정원 @NST')

        if "api" in st.secrets and "openai_api" in st.secrets["api"]:
            st.success('API key already provided!', icon='✅')
            openai_api = st.secrets["api"]["openai_api"]
        else:
            openai_api = st.text_input("Enter OpenAI API Key", type="password")
            if openai_api:
                st.success('API key provided!', icon='✅')

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages     = [{"role": "assistant", "content": "안녕하세요 저는 AI행정원'에디'입니다."}]
        st.session_state.messages.append({"role": "assistant", "content": "만나서 반갑습니다."})  # 역할 이름을 "user"로 변경

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # def clear_chat_history():
    #     st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    # st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

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
        
        # # 파일 내용 읽기 (예: 텍스트 파일의 경우)
        # try:
        #     file_contents = uploaded_file.read().decode("utf-8")
        #     st.text_area("File Content", file_contents)
        # except Exception as e:
        #     st.error("Unable to read file content.")


    # User-provided prompt
    if prompt := st.chat_input(disabled=not openai_api):  # `replicate_api` 대신 `openai_api` 사용
        st.session_state.messages.append({"role": "user", "content": prompt})  # 역할 이름을 "user"로 변경
        with st.chat_message("user"):  # 역할 이름에 맞게 "user"로 수정
            st.write(prompt)


# # Function for generating LLaMA2 response
# def generate_llama2_response(prompt_input):
#     string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
#     for dict_message in st.session_state.messages:
#         if dict_message["role"] == "user":
#             string_dialogue += "User: " + dict_message["content"] + "\n\n"
#         else:
#             string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
#     output = replicate.run(llm, 
#                            input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
#                                   "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
#     return output



# # Generate a new response if last message is not from assistant
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             response = generate_llama2_response(prompt)
#             placeholder = st.empty()
#             full_response = ''
#             for item in response:
#                 full_response += item
#                 placeholder.markdown(full_response)
#             placeholder.markdown(full_response)
#     message = {"role": "assistant", "content": full_response}
#     st.session_state.messages.append(message)