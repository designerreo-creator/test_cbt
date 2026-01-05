import streamlit as st

st.title("사전평가 예시")

name = st.text_input("이름을 입력하세요")

score = st.slider("컴퓨터 활용 수준", 1, 5)

if st.button("제출"):
    st.write(f"{name}님의 점수는 {score}점입니다.")