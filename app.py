import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="사전평가 CBT", layout="centered")

DATA_FILE = "results.csv"
TEACHER_PASSWORD = "teacher123"

st.title("📝 사전역량 진단 CBT")
st.write("제출 후 본인 결과와 분석 내용을 확인할 수 있습니다.")

# ─────────────────────
# 인적사항
# ─────────────────────
name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

st.divider()

# ─────────────────────
# 문제은행 (문항, 보기, 정답, 영역)
# ─────────────────────
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),
    ("인터넷 검색을 활용할 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),
    ("파일 업로드/다운로드가 가능하다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),
    ("온라인 강의 수강 경험이 있다", ["없다","조금","보통","많다"], 2, "기초역량"),
    ("새로운 프로그램 학습이 부담되지 않는다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),

    ("전공 기초 개념을 알고 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
    ("전공 용어 이해가 가능하다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
    ("실습 수업을 따라갈 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
    ("전공 학습 속도가 적절하다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
    ("전공 내용에 흥미가 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),

    ("수업에 성실히 참여할 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),
    ("과제를 기한 내 수행한다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),
    ("질문을 하는 편이다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),
    ("복습/예습 의지가 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),
    ("수료까지 학습을 유지할 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),

    ("수료 후 진로 목표가 있다", ["없다","모호","어느 정도","명확"], 3, "취업인식"),
    ("희망 직무를 알고 있다", ["전혀","조금","어느 정도","명확"], 3, "취업인식"),
    ("취업 준비 계획이 있다", ["없다","모호","어느 정도","명확"], 3, "취업인식"),
    ("취업을 위해 노력할 의지가 있다", ["전혀","조금","보통","높다"], 3, "취업인식"),
    ("추가 역량 향상 의지가 있다", ["전혀","조금","보통","높다"], 3, "취업인식"),
]

# ─────────────────────
# 문항 출력
# ─────────────────────
answers = []
for i, (q, options, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    choice = st.radio("", options, key=f"q{i}")
    answers.append(options.index(choice))

st.divider()

# ─────────────────────
# 제출
# ─────────────────────
if st.button("📊 제출하기"):

    score = 0
    records = []

    for ans, (_, _, correct, area) in zip(answers, questions):
        correct_yn = 1 if ans == correct else 0
        score += correct_yn
        records.append({"영역": area, "정답": correct_yn})

    df_area = pd.DataFrame(records)
    area_rate = (df_area.groupby("영역")["정답"].mean() * 100).round(1)

    total_rate = round(score / 20 * 100, 1)

    level = "집중관리 필요" if total_rate < 50 else "일반 수준" if total_rate < 80 else "우수 수준"

    strong = area_rate.idxmax()
    weak = area_rate.idxmin()

    analysis_text = (
        f"{name} 훈련생은 정답률 {total_rate}%로 '{level}' 수준입니다. "
        f"'{strong}' 영역에서 강점을 보이며, "
        f"'{weak}' 영역에 대한 보완 학습이 필요합니다."
    )

    # 🔹 훈련생 화면 출력
    st.success(f"총점: {score} / 20점")
    st.info(analysis_text)

    # 🔹 데이터 저장
    df_save = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "총점": score,
        "정답률": total_rate,
        "수준": level,
        "강점영역": strong,
        "취약영역": weak,
        "개인분석": analysis_text
    }])

    if os.path.exists(DATA_FILE):
        df_all = pd.read_csv(DATA_FILE)
        df_all = pd.concat([df_all, df_save], ignore_index=True)
    else:
        df_all = df_save.copy()

    df_all.to_csv(DATA_FILE, index=False)

    # ─────────────────────
    # 👩‍🏫 교사용 영역
    # ─────────────────────
    st.divider()
    st.subheader("👩‍🏫 교사용 다운로드")

    password = st.text_input("교사용 비밀번호 입력", type="password")

    if password == TEACHER_PASSWORD:
        class_df = df_all[df_all["기수"] == class_no]

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            class_df.to_excel(writer, sheet_name="기수전체결과", index=False)

        excel_buffer.seek(0)

        st.download_button(
            "📥 기수별 전체 결과 엑셀 다운로드",
            excel_buffer,
            f"{class_no}_사전평가_결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
