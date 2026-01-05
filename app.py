import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="사전역량 진단 CBT", layout="centered")

DATA_FILE = "results.csv"
TEACHER_PASSWORD = "teacher123"

# ==============================
# session_state
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
        "총점","정답률","수준",
        "취약영역","개인분석"
    ]).to_csv(DATA_FILE, index=False)

# ==============================
# 문제은행
# ==============================
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "기초역량"),
    ("전공 기초 개념을 이해하고 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "전공이해"),
    ("수업에 성실히 참여할 수 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "학습태도"),
    ("취업 목표가 명확하다", ["없다","모호","어느 정도","명확"], 3, "취업인식"),
]

guides = {
    "기초역량": "컴퓨터 기초 및 온라인 학습 환경 적응 훈련이 필요합니다.",
    "전공이해": "전공 기초 개념 및 핵심 용어 위주의 반복 학습이 필요합니다.",
    "학습태도": "출결·과제·학습 루틴 관리 중심의 학습 상담이 필요합니다.",
    "취업인식": "진로 탐색 및 직무 목표 설정 활동이 필요합니다."
}

# ==============================
# UI – 인적사항
# ==============================
st.title("📝 사전역량 진단 CBT")

name = st.text_input("이름")
class_no = st.text_input("기수 / 반")
uid = st.text_input("휴대폰 번호 뒤 4자리", max_chars=4)

st.divider()

# ==============================
# 문항
# ==============================
answers = []
for i, (q, opts, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    answers.append(st.radio("선택", opts, key=f"q{i}"))

# ==============================
# 제출
# ==============================
if st.button("📊 제출하기") and not st.session_state.submitted:

    df = pd.read_csv(DATA_FILE)

    # 재응시 대상 → 기존 데이터 삭제
    if st.session_state.retry_user == (name, class_no, uid):
        df = df[~(
            (df["이름"] == name) &
            (df["기수"] == class_no) &
            (df["식별자"] == uid)
        )]
        st.session_state.retry_user = None

    else:
        if not df[
            (df["이름"] == name) &
            (df["기수"] == class_no) &
            (df["식별자"] == uid)
        ].empty:
            st.error("이미 제출한 평가입니다.")
            st.stop()

    # 채점
    score = 0
    weak = []

    for a, (q, opts, c, area) in zip(answers, questions):
        if a == opts[c]:
            score += 1
        else:
            weak.append(area)

    rate = round(score / len(questions) * 100, 1)
    level = "집중관리 필요" if rate < 60 else "일반 수준" if rate < 85 else "우수"

    weak_summary = ", ".join(set(weak)) if weak else "없음"

    guide_text = (
        "전반적으로 안정적인 수준입니다."
        if not weak else
        "\n".join([f"- {a}: {guides[a]}" for a in set(weak)])
    )

    analysis = (
        f"{name} 훈련생은 정답률 {rate}%로 '{level}' 수준입니다.\n\n"
        f"[취약 영역]\n{weak_summary}\n\n"
        f"[맞춤 학습 가이드]\n{guide_text}"
    )

    save = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "식별자": uid,
        "총점": score,
        "정답률": rate,
        "수준": level,
        "취약영역": weak_summary,
        "개인분석": analysis
    }])

    df = pd.concat([df, save], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    st.session_state.submitted = True

    # 🔥 훈련생 화면 분석 요약
    st.success("제출 완료")
    st.info(analysis)

# ==============================
# 교사용 분석 + 다운로드
# ==============================
st.divider()
st.subheader("👩‍🏫 교사용 관리")

pw = st.text_input("교사용 비밀번호", type="password")

if pw == TEACHER_PASSWORD:

    df = pd.read_csv(DATA_FILE)

    if not df.empty:

        st.markdown("### 📊 기수 전체 요약")
        st.write(df.groupby("기수")[["정답률"]].mean().round(1))

        st.markdown("### 👥 개인별 결과")
        st.dataframe(df)

        # 엑셀 다운로드
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="개인별결과")
            summary = df.groupby("기수").agg(
                평균정답률=("정답률","mean"),
                응시인원=("이름","count")
            ).reset_index()
            summary.to_excel(writer, index=False, sheet_name="기수요약")

        buffer.seek(0)

        st.download_button(
            "📥 분석 결과 엑셀 다운로드",
            buffer,
            "사전평가_분석결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # 재응시 허용
        target = st.selectbox(
            "재응시 허용 대상",
            df[["이름","기수","식별자"]].astype(str).apply(" / ".join, axis=1)
        )

        if st.button("🔓 재응시 허용 (기존 결과 삭제)"):
            n, c, u = target.split(" / ")
            st.session_state.retry_user = (n, c, u)
            st.session_state.submitted = False
            st.success("재응시 허용 완료 (다음 제출 시 기존 결과 삭제)")
