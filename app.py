import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="사전역량 진단 CBT", layout="centered")

DATA_FILE = "results.csv"
RETRY_FILE = "retry_allow.csv"
TEACHER_PASSWORD = "teacher123"

# ==============================
# session_state 초기화
# ==============================
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "retry_user" not in st.session_state:
    st.session_state.retry_user = None

# ==============================
# 파일 초기화
# ==============================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "이름","기수","식별자",
        "총점","정답률","수준","개인분석"
    ]).to_csv(DATA_FILE, index=False)

if not os.path.exists(RETRY_FILE):
    pd.DataFrame(columns=["이름","기수","식별자"]).to_csv(RETRY_FILE, index=False)

# ==============================
# UI
# ==============================
st.title("📝 사전역량 진단 CBT")

name = st.text_input("이름")
class_no = st.text_input("기수 / 반")
uid = st.text_input("휴대폰 번호 뒤 4자리", max_chars=4)

st.divider()

# ==============================
# 문제
# ==============================
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "기초역량"),
    ("전공 기초 개념을 이해하고 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "전공이해"),
]

answers = []
for i, (q, opts, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    answers.append(st.radio("선택", opts, key=f"q{i}"))

# ==============================
# 제출 처리 (🔥 핵심 수정)
# ==============================
if st.button("📊 제출하기") and not st.session_state.submitted:

    df_all = pd.read_csv(DATA_FILE)

    # 🔥 재응시 허용 대상이면 기존 데이터 무조건 삭제
    if st.session_state.retry_user == (name, class_no, uid):
        df_all = df_all[
            ~(
                (df_all["이름"] == name) &
                (df_all["기수"] == class_no) &
                (df_all["식별자"] == uid)
            )
        ]
        st.session_state.retry_user = None

    else:
        # 일반 중복 차단
        if not df_all[
            (df_all["이름"] == name) &
            (df_all["기수"] == class_no) &
            (df_all["식별자"] == uid)
        ].empty:
            st.error("이미 제출한 평가입니다.")
            st.session_state.submitted = True
            st.stop()

    # 채점
    score = sum(
        a == opts[c]
        for a, (q, opts, c, _) in zip(answers, questions)
    )
    rate = round(score / len(questions) * 100, 1)

    save_df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "식별자": uid,
        "총점": score,
        "정답률": rate,
        "수준": "일반",
        "개인분석": f"{name} 훈련생 정답률 {rate}%"
    }])

    df_all = pd.concat([df_all, save_df], ignore_index=True)
    df_all.to_csv(DATA_FILE, index=False)

    st.session_state.submitted = True
    st.success("제출 완료")

# ==============================
# 교사용 재응시 허용 (🔥 상태 기반)
# ==============================
st.divider()
st.subheader("👩‍🏫 교사용 관리")

pw = st.text_input("교사용 비밀번호", type="password")

if pw == TEACHER_PASSWORD:

    df_all = pd.read_csv(DATA_FILE)

    if not df_all.empty:
        target = st.selectbox(
            "재응시 허용 대상",
            df_all[["이름","기수","식별자"]]
            .astype(str)
            .apply(" / ".join, axis=1)
        )

        if st.button("🔓 재응시 허용 (기존 데이터 삭제 예약)"):
            n, c, u = target.split(" / ")

            # 🔥 session_state에만 저장 (즉시 삭제 ❌)
            st.session_state.retry_user = (n, c, u)
            st.session_state.submitted = False

            st.success(
                f"{n} 훈련생 재응시 허용됨\n"
                f"→ 다음 제출 시 기존 결과가 자동 삭제됩니다."
            )
