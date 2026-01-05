import streamlit as st
import pandas as pd
import os
import io

# ==============================
# 기본 설정
# ==============================
st.set_page_config(page_title="사전역량 진단 CBT", layout="centered")

DATA_FILE = "results.csv"
RETRY_FILE = "retry_allow.csv"
TEACHER_PASSWORD = "teacher123"

# ==============================
# 세션 상태 초기화 (🔥 중복 제출 핵심)
# ==============================
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ==============================
# 파일 초기화 (EmptyDataError 방지)
# ==============================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "이름","기수","식별자",
        "총점","정답률","수준","개인분석"
    ]).to_csv(DATA_FILE, index=False)

if not os.path.exists(RETRY_FILE):
    pd.DataFrame(columns=["이름","기수","식별자"]).to_csv(RETRY_FILE, index=False)

# ==============================
# UI 안내
# ==============================
st.title("📝 훈련생 사전역량 진단 CBT")
st.write("본 평가는 훈련생의 현재 수준을 파악하기 위한 사전평가입니다.")

# ==============================
# 인적사항
# ==============================
st.subheader("📌 인적사항")

name = st.text_input("이름")
class_no = st.text_input("기수 / 반")
uid = st.text_input("휴대폰 번호 뒤 4자리", max_chars=4)

if uid and (not uid.isdigit() or len(uid) != 4):
    st.error("휴대폰 번호 뒤 4자리는 숫자 4자리만 입력하세요.")

st.divider()

# ==============================
# 문제은행 (4지선다)
# ==============================
questions = [
    ("컴퓨터 기본 조작이 가능하다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "기초역량"),
    ("인터넷 검색을 활용할 수 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "기초역량"),
    ("파일 업로드/다운로드가 가능하다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "기초역량"),

    ("전공 기초 개념을 이해하고 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "전공이해"),
    ("전공 용어 이해에 어려움이 없다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "전공이해"),
    ("실습 수업을 따라갈 수 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "전공이해"),

    ("수업에 성실히 참여할 수 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "학습태도"),
    ("과제를 기한 내 수행할 수 있다", ["전혀 아니다","아니다","보통이다","그렇다"], 3, "학습태도"),

    ("수료 후 진로 목표가 있다", ["없다","모호하다","어느 정도 있다","명확하다"], 3, "취업인식"),
    ("취업 준비 계획이 있다", ["없다","모호하다","어느 정도 있다","명확하다"], 3, "취업인식"),
]

user_answers = []
for i, (q, options, _, _) in enumerate(questions):
    st.subheader(f"Q{i+1}. {q}")
    user_answers.append(st.radio("선택", options, key=f"q{i}"))

# ==============================
# 제출 처리 (🔥 완전 차단 로직)
# ==============================
if st.button("📊 제출하기") and not st.session_state.submitted:

    if not name or not class_no or not uid:
        st.warning("이름, 기수, 휴대폰 번호 뒤 4자리를 모두 입력하세요.")
        st.stop()

    if not uid.isdigit() or len(uid) != 4:
        st.warning("휴대폰 번호 뒤 4자리는 숫자 4자리여야 합니다.")
        st.stop()

    df_all = pd.read_csv(DATA_FILE)
    retry_df = pd.read_csv(RETRY_FILE)

    # 기존 제출 여부
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
        st.error("이미 제출한 평가입니다. 재응시는 교사 승인 후 가능합니다.")
        st.session_state.submitted = True
        st.stop()

    # 재응시 허용 → 기존 데이터 삭제
    if not already.empty and retry_allowed:
        df_all = df_all.drop(already.index)
        retry_df = retry_df.drop(
            retry_df[
                (retry_df["이름"] == name) &
                (retry_df["기수"] == class_no) &
                (retry_df["식별자"] == uid)
            ].index
        )
        retry_df.to_csv(RETRY_FILE, index=False)

    # 채점
    score = 0
    weak_areas = []

    for ans, (q, opts, correct, area) in zip(user_answers, questions):
        if ans == opts[correct]:
            score += 1
        else:
            weak_areas.append(area)

    rate = round(score / len(questions) * 100, 1)
    level = "집중관리 필요" if rate < 50 else "일반 수준" if rate < 80 else "우수 수준"

    guides = {
        "기초역량": "컴퓨터 기초 및 온라인 학습 환경 적응이 필요합니다.",
        "전공이해": "전공 기초 개념과 용어 중심의 반복 학습이 필요합니다.",
        "학습태도": "출결 및 과제 관리 중심의 학습 태도 개선이 필요합니다.",
        "취업인식": "진로 탐색 및 취업 목표 설정 활동이 필요합니다."
    }

    guide_text = "전반적으로 안정적인 수준입니다."
    if weak_areas:
        guide_text = "\n".join([f"- {a}: {guides[a]}" for a in set(weak_areas)])

    analysis = (
        f"{name} 훈련생은 정답률 {rate}%로 '{level}' 수준입니다.\n\n"
        f"[맞춤 학습 가이드]\n{guide_text}"
    )

    save_df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "식별자": uid,
        "총점": score,
        "정답률": rate,
        "수준": level,
        "개인분석": analysis
    }])

    # 저장 + 최종 중복 제거
    df_all = pd.concat([df_all, save_df], ignore_index=True)
    df_all = df_all.drop_duplicates(
        subset=["이름","기수","식별자"],
        keep="first"
    )
    df_all.to_csv(DATA_FILE, index=False)

    # 🔒 세션 잠금 (결정타)
    st.session_state.submitted = True

    st.success("제출이 완료되었습니다.")
    st.info(analysis)

# ==============================
# 교사용 관리
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

        if st.button("🔓 재응시 허용"):
            n, c, u = target.split(" / ")
            retry_df = pd.read_csv(RETRY_FILE)
            retry_df = pd.concat(
                [retry_df, pd.DataFrame([{"이름": n, "기수": c, "식별자": u}])],
                ignore_index=True
            )
            retry_df.to_csv(RETRY_FILE, index=False)
            st.success(f"{n} 훈련생 재응시 허용 완료")

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
