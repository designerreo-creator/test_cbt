import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="사전평가 CBT", layout="centered")

DATA_FILE = "results.csv"
TEACHER_PASSWORD = "teacher123"

st.title("📝 사전역량 진단 CBT")

# ─────────────────────
# 세션 초기화
# ─────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "df_all" not in st.session_state:
    st.session_state.df_all = None
if "class_no" not in st.session_state:
    st.session_state.class_no = None

# ─────────────────────
# 인적사항
# ─────────────────────
name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

st.divider()

# ─────────────────────
# 문제은행 (축약 예시 – 기존 문항 그대로 사용 가능)
# ─────────────────────
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),
    ("전공 기초 개념을 알고 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
]

answers = []
for i, (q, options, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    answers.append(st.radio("", options, key=f"q{i}"))

# ─────────────────────
# 제출 버튼
# ─────────────────────
if st.button("📊 제출하기"):
    score = 0
    records = []

    for ans, (_, options, correct, area) in zip(answers, questions):
        correct_yn = 1 if options.index(ans) == correct else 0
        score += correct_yn
        records.append({"영역": area, "정답": correct_yn})

    df_area = pd.DataFrame(records)
    area_rate = df_area.groupby("영역")["정답"].mean() * 100

    total_rate = round(score / len(questions) * 100, 1)
    strong = area_rate.idxmax()
    weak = area_rate.idxmin()

    analysis = f"{name} 훈련생은 정답률 {total_rate}%이며, {strong} 영역이 강점, {weak} 영역이 보완 필요합니다."

    df_save = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "점수": score,
        "정답률": total_rate,
        "강점영역": strong,
        "취약영역": weak,
        "개인분석": analysis
    }])

    if os.path.exists(DATA_FILE):
        df_all = pd.read_csv(DATA_FILE)
        df_all = pd.concat([df_all, df_save], ignore_index=True)
    else:
        df_all = df_save.copy()

    df_all.to_csv(DATA_FILE, index=False)

    # 🔑 세션 저장 (핵심)
    st.session_state.submitted = True
    st.session_state.df_all = df_all
    st.session_state.class_no = class_no
    st.session_state.analysis = analysis
    st.session_state.score = score
    st.session_state.total_rate = total_rate

# ─────────────────────
# 훈련생 결과 화면 (제출 후 유지)
# ─────────────────────
if st.session_state.submitted:
    st.success(f"총점: {st.session_state.score}")
    st.info(st.session_state.analysis)

    st.divider()
    st.subheader("👩‍🏫 교사용 다운로드")

    password = st.text_input("교사용 비밀번호", type="password")

    if password == TEACHER_PASSWORD:
        class_df = st.session_state.df_all[
            st.session_state.df_all["기수"] == st.session_state.class_no
        ]

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            class_df.to_excel(writer, index=False, sheet_name="기수결과")

        excel_buffer.seek(0)

        st.download_button(
            "📥 기수별 결과 엑셀 다운로드",
            excel_buffer,
            f"{class_no}_사전평가.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
