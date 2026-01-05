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
# 인적사항 (🔑 휴대폰 4자리 추가)
# ==============================
st.subheader("📌 인적사항 입력")

name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

uid = st.text_input(
    "휴대폰 번호 뒤 4자리",
    max_chars=4,
    help="동명이인 구분을 위해 숫자 4자리만 입력해주세요"
)

if uid and (not uid.isdigit() or len(uid) != 4):
    st.error("휴대폰 번호 뒤 4자리는 숫자 4자리만 입력해야 합니다.")

st.caption("※ 입력한 휴대폰 번호 뒤 4자리는 식별 용도로만 사용됩니다.")

st.divider()

# ==============================
# 문제은행 (10문항 예시)
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
# 제출
# ==============================
if st.button("📊 제출하기"):

    # 필수 입력 검증
    if not name or not class_no or not uid:
        st.warning("이름, 기수, 휴대폰 번호 뒤 4자리를 모두 입력해주세요.")
        st.stop()

    if not uid.isdigit() or len(uid) != 4:
        st.warning("휴대폰 번호 뒤 4자리는 숫자 4자리여야 합니다.")
        st.stop()

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

    if not wrong_df.empty:
        guide_text = "\n".join(
            [f"▶ {a}: {learning_guides[a]}" for a in wrong_df["영역"].unique()]
        )
    else:
        guide_text = "모든 영역에서 안정적인 수준을 보이고 있습니다."

    analysis = (
        f"{name} 훈련생은 정답률 {total_rate}%로 '{level}' 수준입니다.\n\n"
        f"📘 맞춤 학습 가이드:\n{guide_text}"
    )

    df_save = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "식별자(휴대폰4자리)": uid,
        "총점": score,
        "정답률": total_rate,
        "수준": level,
        "틀린문항수": len(wrong_df),
        "틀린문항번호": ", ".join(wrong_df["문항번호"].astype(str)) if not wrong_df.empty else "없음",
        "개인분석": analysis,
        "자동학습가이드": guide_text
    }])

    already_submitted = False
    if os.path.exists(DATA_FILE):
        df_all = pd.read_csv(DATA_FILE)
        if (
            (df_all["이름"] == name) &
            (df_all["기수"] == class_no) &
            (df_all["식별자(휴대폰4자리)"] == uid)
        ).any():
            already_submitted = True
    else:
        df_all = pd.DataFrame()

    if not already_submitted:
        df_all = pd.concat([df_all, df_save], ignore_index=True)
        df_all.to_csv(DATA_FILE, index=False)
        save_message = "📌 최초 제출 결과가 저장되었습니다."
    else:
        save_message = "⚠️ 이미 제출 이력이 있어 추가 저장은 되지 않습니다."

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
# 결과 출력
# ==============================
if st.session_state.submitted:
    st.success(f"총점: {st.session_state.score}점")
    st.info(st.session_state.analysis)
    st.warning(st.session_state.save_message)

    if not st.session_state.wrong_df.empty:
        st.subheader("❌ 틀린 문항")
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

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            class_df.to_excel(writer, index=False, sheet_name="기수전체결과")
        buffer.seek(0)

        st.download_button(
            "📥 기수별 전체 결과 엑셀 다운로드",
            buffer,
            f"{st.session_state.class_no}_사전평가결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
