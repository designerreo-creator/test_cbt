import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="사전역량 진단 CBT", layout="centered")

# ==============================
# 기본 설정
# ==============================
DATA_FILE = "results.csv"
RETRY_FILE = "retry_allow.csv"
TEACHER_PASSWORD = "teacher123"

# ==============================
# 파일 초기화
# ==============================
if not os.path.exists(DATA_FILE):
    pd.DataFrame().to_csv(DATA_FILE, index=False)

if not os.path.exists(RETRY_FILE):
    pd.DataFrame(columns=["이름","기수","식별자"]).to_csv(RETRY_FILE, index=False)

st.title("📝 사전역량 진단 CBT")
st.write("본 평가는 훈련생의 현재 역량을 진단하기 위한 사전평가입니다.")

# ==============================
# 학습 가이드
# ==============================
learning_guides = {
    "기초역량": "컴퓨터 기본 조작 및 온라인 학습 환경 활용 능력 보완이 필요합니다.",
    "전공이해": "전공 기초 개념과 핵심 용어 위주의 단계적 학습을 권장합니다.",
    "학습태도": "출결·과제 관리 등 학습 태도 개선이 필요합니다.",
    "취업인식": "직무 탐색 및 취업 목표 설정 활동이 필요합니다."
}

# ==============================
# 인적사항
# ==============================
st.subheader("📌 인적사항 입력")

name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

uid = st.text_input(
    "휴대폰 번호 뒤 4자리",
    max_chars=4,
    help="동명이인 구분을 위해 숫자 4자리만 입력"
)

if uid and (not uid.isdigit() or len(uid) != 4):
    st.error("휴대폰 뒤 4자리는 숫자 4자리만 입력해야 합니다.")

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

user_answers = []
for i, (q, options, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    user_answers.append(st.radio("", options, key=f"q{i}"))

# ==============================
# 제출 처리
# ==============================
if st.button("📊 제출하기"):

    if not name or not class_no or not uid:
        st.warning("이름, 기수, 휴대폰 뒤 4자리를 모두 입력해주세요.")
        st.stop()

    if not uid.isdigit() or len(uid) != 4:
        st.warning("휴대폰 뒤 4자리는 숫자 4자리여야 합니다.")
        st.stop()

    df_all = pd.read_csv(DATA_FILE)
    retry_df = pd.read_csv(RETRY_FILE)

    submitted = (
        (df_all.get("이름") == name) &
        (df_all.get("기수") == class_no) &
        (df_all.get("식별자") == uid)
    ) if not df_all.empty else False

    retry_allowed = (
        (retry_df["이름"] == name) &
        (retry_df["기수"] == class_no) &
        (retry_df["식별자"] == uid)
    ).any()

    if submitted.any() and not retry_allowed:
        st.error("이미 제출한 평가입니다. 재응시는 교사 승인 후 가능합니다.")
        st.stop()

    # 재응시 허용 시 기존 결과 삭제
    if submitted.any() and retry_allowed:
        df_all = df_all[~submitted]
        retry_df = retry_df[~(
            (retry_df["이름"] == name) &
            (retry_df["기수"] == class_no) &
            (retry_df["식별자"] == uid)
        )]
        retry_df.to_csv(RETRY_FILE, index=False)

    # 채점
    wrong = []
    score = 0
    for i, (ua, (q, opts, ans, area)) in enumerate(zip(user_answers, questions)):
        if ua == opts[ans]:
            score += 1
        else:
            wrong.append((i+1, area))

    total_rate = round(score / len(questions) * 100, 1)
    level = "집중관리 필요" if total_rate < 50 else "일반 수준" if total_rate < 80 else "우수 수준"

    wrong_df = pd.DataFrame(wrong, columns=["문항번호","영역"])

    guide = "모든 영역에서 안정적인 수준입니다." if wrong_df.empty else \
        "\n".join([f"▶ {a}: {learning_guides[a]}" for a in wrong_df["영역"].unique()])

    analysis = f"{name} 훈련생은 정답률 {total_rate}%로 '{level}' 수준입니다.\n\n{guide}"

    save_df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "식별자": uid,
        "총점": score,
        "정답률": total_rate,
        "수준": level,
        "개인분석": analysis
    }])

    df_all = pd.concat([df_all, save_df], ignore_index=True)
    df_all.to_csv(DATA_FILE, index=False)

    st.success("제출 완료! 아래에서 결과를 확인하세요.")
    st.info(analysis)

# ==============================
# 교사용 재응시 승인
# ==============================
st.divider()
st.subheader("👩‍🏫 교사용 관리")

password = st.text_input("교사용 비밀번호", type="password")

if password == TEACHER_PASSWORD:
    df_all = pd.read_csv(DATA_FILE)

    if not df_all.empty:
        target = st.selectbox(
            "재응시 허용 대상 선택",
            df_all[["이름","기수","식별자"]].astype(str).apply(" / ".join, axis=1)
        )

        if st.button("🔓 재응시 허용"):
            n, c, u = target.split(" / ")
            retry_df = pd.read_csv(RETRY_FILE)
            retry_df = pd.concat([retry_df, pd.DataFrame([{
                "이름": n, "기수": c, "식별자": u
            }])], ignore_index=True)
            retry_df.to_csv(RETRY_FILE, index=False)
            st.success(f"{n} 훈련생 재응시가 허용되었습니다.")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False)
    buffer.seek(0)

    st.download_button(
        "📥 전체 결과 엑셀 다운로드",
        buffer,
        "사전평가_전체결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
