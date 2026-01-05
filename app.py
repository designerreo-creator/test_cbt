import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="사전역량 진단 CBT", layout="centered")

# ==============================
# 기본 설정
# ==============================
DATA_FILE = "results.csv"
TEACHER_PASSWORD = "teacher123"

st.title("📝 사전역량 진단 CBT")
st.write("제출 후 본인 점수, 오답, 맞춤 학습 가이드를 확인할 수 있습니다.")

# ==============================
# 영역별 자동 학습 가이드
# ==============================
learning_guides = {
    "기초역량": "컴퓨터 기본 조작, 파일 관리, 온라인 학습 도구 활용에 대한 기초 보완 학습이 필요합니다.",
    "전공이해": "전공 핵심 개념과 용어 이해를 중심으로 단계별 실습 학습을 권장합니다.",
    "학습태도": "출결 관리 및 과제 수행을 중심으로 학습 태도 개선이 필요합니다.",
    "취업인식": "직무 탐색 및 진로 목표 설정 활동이 필요합니다."
}

# ==============================
# 세션 초기화
# ==============================
for key in [
    "submitted", "wrong_df", "analysis", "score",
    "total_rate", "df_all", "class_no", "guide_text", "save_message"
]:
    if key not in st.session_state:
        st.session_state[key] = None

# ==============================
# 인적사항
# ==============================
name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

st.divider()

# ==============================
# 문제은행 (예시 10문항 / 필요 시 20문항 확장)
# ==============================
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),
    ("인터넷 검색을 활용할 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),
    ("파일 업로드/다운로드가 가능하다", ["매우 아니다","아니다","보통","그렇다"], 3, "기초역량"),

    ("전공 기초 개념을 알고 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
    ("전공 용어 이해에 어려움이 없다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),
    ("실습 수업을 따라갈 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "전공이해"),

    ("수업에 성실히 참여할 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),
    ("과제를 기한 내 수행할 수 있다", ["매우 아니다","아니다","보통","그렇다"], 3, "학습태도"),

    ("수료 후 진로 목표가 있다", ["없다","모호","어느 정도","명확"], 3, "취업인식"),
    ("취업 준비 계획이 있다", ["없다","모호","어느 정도","명확"], 3, "취업인식"),
]

# ==============================
# 문항 출력
# ==============================
user_answers = []

for i, (q, options, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    user_answers.append(st.radio("", options, key=f"q{i}"))

# ==============================
# 제출 버튼
# ==============================
if st.button("📊 제출하기"):

    wrong_records = []
    score = 0

    for i, (user_ans, (q, options, correct, area)) in enumerate(zip(user_answers, questions)):
        correct_answer = options[correct]

        if user_ans == correct_answer:
            score += 1
        else:
            wrong_records.append({
                "문항번호": i + 1,
                "영역": area,
                "문항내용": q,
                "선택답": user_ans,
                "정답": correct_answer
            })

    wrong_df = pd.DataFrame(wrong_records)
    total_rate = round(score / len(questions) * 100, 1)

    level = (
        "집중관리 필요" if total_rate < 50
        else "일반 수준" if total_rate < 80
        else "우수 수준"
    )

    # ==============================
    # 자동 학습 가이드 생성
    # ==============================
    if not wrong_df.empty:
        wrong_areas = wrong_df["영역"].unique().tolist()
        guide_list = [f"▶ {area}: {learning_guides[area]}" for area in wrong_areas]
        guide_text = "\n".join(guide_list)
    else:
        guide_text = "모든 영역에서 안정적인 수준을 보이고 있습니다."

    analysis = (
        f"{name} 훈련생은 정답률 {total_rate}%로 '{level}' 수준입니다.\n\n"
        f"📘 맞춤 학습 가이드:\n{guide_text}"
    )

    # ==============================
    # 개인 결과 DataFrame
    # ==============================
    df_save = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "총점": score,
        "정답률": total_rate,
        "수준": level,
        "틀린문항수": len(wrong_df),
        "틀린문항번호": ", ".join(wrong_df["문항번호"].astype(str)) if not wrong_df.empty else "없음",
        "개인분석": analysis,
        "자동학습가이드": guide_text
    }])

    # ==============================
    # 🔒 최초 1회만 저장 로직
    # ==============================
    already_submitted = False

    if os.path.exists(DATA_FILE):
        existing_df = pd.read_csv(DATA_FILE)
        if ((existing_df["이름"] == name) &
            (existing_df["기수"] == class_no)).any():
            already_submitted = True

    if not already_submitted:
        if os.path.exists(DATA_FILE):
            df_all = pd.read_csv(DATA_FILE)
            df_all = pd.concat([df_all, df_save], ignore_index=True)
        else:
            df_all = df_save.copy()

        df_all.to_csv(DATA_FILE, index=False)
        save_message = "📌 최초 제출 결과가 정상적으로 저장되었습니다."
    else:
        df_all = pd.read_csv(DATA_FILE)
        save_message = "⚠️ 이미 제출 이력이 있어 추가 저장은 되지 않습니다."

    # ==============================
    # 세션 저장
    # ==============================
    st.session_state.submitted = True
    st.session_state.wrong_df = wrong_df
    st.session_state.analysis = analysis
    st.session_state.score = score
    st.session_state.total_rate = total_rate
    st.session_state.df_all = df_all
    st.session_state.class_no = class_no
    st.session_state.guide_text = guide_text
    st.session_state.save_message = save_message

# ==============================
# 결과 화면
# ==============================
if st.session_state.submitted:

    st.success(f"총점: {st.session_state.score}점")
    st.info(st.session_state.analysis)
    st.warning(st.session_state.save_message)

    if not st.session_state.wrong_df.empty:
        st.subheader("❌ 내가 틀린 문항")
        st.dataframe(st.session_state.wrong_df, use_container_width=True)

    st.subheader("📘 개인 맞춤 학습 가이드")
    st.info(st.session_state.guide_text)

    # ==============================
    # 교사용 다운로드
    # ==============================
    st.divider()
    st.subheader("👩‍🏫 교사용 다운로드")

    password = st.text_input("교사용 비밀번호", type="password")

    if password == TEACHER_PASSWORD:
        class_df = st.session_state.df_all[
            st.session_state.df_all["기수"] == st.session_state.class_no
        ]

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            class_df.to_excel(writer, index=False, sheet_name="기수전체결과")

        excel_buffer.seek(0)

        st.download_button(
            "📥 기수별 전체 결과 엑셀 다운로드",
            excel_buffer,
            f"{class_no}_사전평가_결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
