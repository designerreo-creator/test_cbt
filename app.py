import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="사전역량 진단 CBT", layout="centered")

DATA_FILE = "results.csv"
RETRY_FILE = "retry_allow.csv"
TEACHER_PASSWORD = "teacher123"

# ==============================
# 세션 상태 (중복 제출 차단)
# ==============================
if "submitted" not in st.session_state:
    st.session_state.submitted = False

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
# 문제은행
# ==============================
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "기초역량"),
    ("전공 기초 개념을 이해하고 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "전공이해"),
    ("수업에 성실히 참여할 수 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "학습태도"),
    ("취업 목표가 있다", ["없다","모호하다","어느 정도 있다","명확하다"], 3, "취업인식"),
]

answers = []
for i, (q, opts, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    answers.append(st.radio("선택", opts, key=f"q{i}"))

# ==============================
# 제출
# ==============================
if st.button("📊 제출하기") and not st.session_state.submitted:

    df_all = pd.read_csv(DATA_FILE)
    retry_df = pd.read_csv(RETRY_FILE)

    already = df_all[
        (df_all["이름"] == name) &
        (df_all["기수"] == class_no) &
        (df_all["식별자"] == uid)
    ]

    retry_allowed = retry_df[
        (retry_df["이름"] == name) &
        (retry_df["기수"] == class_no) &
        (retry_df["식별자"] == uid)
    ].shape[0] > 0

    if not already.empty and not retry_allowed:
        st.error("이미 제출한 평가입니다.")
        st.session_state.submitted = True
        st.stop()

    score = 0
    weak = []

    for a, (q, opts, c, area) in zip(answers, questions):
        if a == opts[c]:
            score += 1
        else:
            weak.append(area)

    rate = round(score / len(questions) * 100, 1)
    level = "집중관리 필요" if rate < 60 else "일반 수준"

    analysis = f"{name} 훈련생은 정답률 {rate}% ({level}) 수준입니다."

    save_df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "식별자": uid,
        "총점": score,
        "정답률": rate,
        "수준": level,
        "개인분석": analysis
    }])

    df_all = pd.concat([df_all, save_df], ignore_index=True)
    df_all = df_all.drop_duplicates(subset=["이름","기수","식별자"])
    df_all.to_csv(DATA_FILE, index=False)

    st.session_state.submitted = True
    st.success("제출 완료")
    st.info(analysis)

# ==============================
# 교사용 관리 (🔥 재응시 허용 시 기존 데이터 삭제)
# ==============================
st.divider()
st.subheader("👩‍🏫 교사용 관리")

pw = st.text_input("교사용 비밀번호", type="password")

if pw == TEACHER_PASSWORD:

    df_all = pd.read_csv(DATA_FILE)
    retry_df = pd.read_csv(RETRY_FILE)

    if not df_all.empty:
        target = st.selectbox(
            "재응시 허용 대상 선택",
            df_all[["이름","기수","식별자"]]
            .astype(str)
            .apply(" / ".join, axis=1)
        )

        if st.button("🔓 재응시 허용 (기존 결과 삭제)"):
            n, c, u = target.split(" / ")

            # 🔥 기존 결과 즉시 삭제
            df_all = df_all[
                ~(
                    (df_all["이름"] == n) &
                    (df_all["기수"] == c) &
                    (df_all["식별자"] == u)
                )
            ]
            df_all.to_csv(DATA_FILE, index=False)

            # 재응시 허용 등록
            retry_df = pd.concat(
                [retry_df, pd.DataFrame([{"이름": n, "기수": c, "식별자": u}])],
                ignore_index=True
            )
            retry_df.to_csv(RETRY_FILE, index=False)

            st.success(f"{n} 훈련생 재응시 허용 완료 (기존 결과 삭제됨)")

    # 결과 다운로드
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False, sheet_name="전체결과")
    buffer.seek(0)

    st.download_button(
        "📥 전체 결과 엑셀 다운로드",
        buffer,
        "사전평가_전체결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
