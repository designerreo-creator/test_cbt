import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="사전평가 CBT 기수분석", layout="centered")

st.title("📝 사전역량 진단 CBT (기수 전체 분석 포함)")
st.write("본 평가는 개인 진단 및 기수 전체 학습 수준 분석을 위한 자료로 활용됩니다.")

DATA_FILE = "results.csv"

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
    ("Q1. 컴퓨터를 켜고 인터넷 브라우저를 실행하는 방법은?",
     ["전원을 끈다", "전원 버튼 후 브라우저 클릭", "키보드 연결", "모니터 설정"], 1, "기초역량"),
    ("Q2. 인터넷에서 정보를 찾는 일반적인 방법은?",
     ["메모장", "검색엔진 키워드 입력", "파일 탐색기", "제어판"], 1, "기초역량"),
    ("Q3. 이메일 첨부파일 저장 방법은?",
     ["삭제", "클릭하여 저장", "인쇄", "전달"], 1, "기초역량"),
    ("Q4. 온라인 강의에 필요한 것은?",
     ["프린터", "인터넷 연결", "USB", "외장하드"], 1, "기초역량"),
    ("Q5. 새로운 프로그램 사용 시 바람직한 태도는?",
     ["포기", "무작정 클릭", "설명 확인", "대신 사용"], 2, "기초역량"),

    ("Q6. 전공 실습의 목적은?",
     ["암기", "시간", "실무 능력 향상", "시험"], 2, "전공이해"),
    ("Q7. 이해 안 되는 용어가 나오면?",
     ["무시", "기다림", "질문·검색", "대신 요청"], 2, "전공이해"),
    ("Q8. 실습 시 중요한 자세는?",
     ["속도", "결과", "과정 이해", "따라 하기"], 2, "전공이해"),
    ("Q9. 효율적인 전공 학습 방법은?",
     ["수업만", "복습", "몰아서", "메모 안 함"], 1, "전공이해"),
    ("Q10. 실습 중 실패에 대한 인식은?",
     ["나쁘다", "학습 과정", "포기", "강사 책임"], 1, "전공이해"),

    ("Q11. 수료에 중요한 요소는?",
     ["재능", "성실한 참여", "운", "도움"], 1, "학습태도"),
    ("Q12. 과제가 어려울 때 행동은?",
     ["미제출", "복사", "질문", "포기"], 2, "학습태도"),
    ("Q13. 복습 시점은?",
     ["한 달 후", "수업 직후", "시험 전", "생각날 때"], 1, "학습태도"),
    ("Q14. 집중 안 될 때 대처는?",
     ["폰", "잠", "휴식 후 집중", "포기"], 2, "학습태도"),
    ("Q15. 동기 유지에 도움 되는 것은?",
     ["목표 없음", "수업만", "목표 설정", "비교"], 2, "학습태도"),

    ("Q16. 훈련 수강 목적은?",
     ["시간", "자격증", "취업·역량", "권유"], 2, "취업인식"),
    ("Q17. 취업 목표 설정 시 우선 요소는?",
     ["연봉", "필요 역량", "거리", "평가"], 1, "취업인식"),
    ("Q18. 취업 준비 핵심은?",
     ["운", "준비 과정", "나이", "학력"], 1, "취업인식"),
    ("Q19. 취업 가능성 향상 방법은?",
     ["잊기", "결과물 정리", "출석", "자격증"], 1, "취업인식"),
    ("Q20. 취업 태도는?",
     ["회피", "최소 노력", "지속 노력", "맡김"], 2, "취업인식"),
]

# ─────────────────────
# 문항 출력
# ─────────────────────
answers = []

for i, (q, options, _, _) in enumerate(questions):
    st.subheader(q)
    choice = st.radio("", options, key=f"q{i}")
    answers.append(options.index(choice))

st.divider()

# ─────────────────────
# 제출 및 분석
# ─────────────────────
if st.button("📊 제출 및 결과 확인"):

    records = []
    score = 0

    for user_ans, (_, _, correct, area) in zip(answers, questions):
        correct_yn = 1 if user_ans == correct else 0
        score += correct_yn
        records.append({"영역": area, "정답여부": correct_yn})

    df_person = pd.DataFrame(records)
    area_rate = (df_person.groupby("영역")["정답여부"].mean() * 100).round(1)

    total_rate = round(score / len(questions) * 100, 1)

    if total_rate < 50:
        level = "집중관리 필요"
    elif total_rate < 80:
        level = "일반 수준"
    else:
        level = "우수 수준"

    strong = area_rate.idxmax()
    weak = area_rate.idxmin()

    # ───────── 개인 결과 출력 ─────────
    st.success(f"총점: {score}/20점 | 정답률: {total_rate}% | 수준: {level}")

    st.subheader("🧾 개인 분석")
    st.write(
        f"{name} 훈련생은 전체 정답률 {total_rate}%로 '{level}' 수준이며, "
        f"'{strong}' 영역에서 강점을 보이고 '{weak}' 영역에서 보완이 필요합니다."
    )

    # ───────── 결과 누적 저장 ─────────
    row = {
        "이름": name,
        "기수": class_no,
        "총점": score,
        "정답률": total_rate,
        "수준": level,
        "강점영역": strong,
        "취약영역": weak
    }

    if os.path.exists(DATA_FILE):
        df_all = pd.read_csv(DATA_FILE)
        df_all = pd.concat([df_all, pd.DataFrame([row])], ignore_index=True)
    else:
        df_all = pd.DataFrame([row])

    df_all.to_csv(DATA_FILE, index=False)

    # ───────── 기수 전체 분석 ─────────
    st.divider()
    st.subheader("📊 기수 전체 분석")

    class_df = df_all[df_all["기수"] == class_no]

    class_avg = round(class_df["정답률"].mean(), 1)
    weak_area_class = class_df["취약영역"].value_counts().idxmax()

    st.write(f"- 기수 평균 정답률: **{class_avg}%**")
    st.write(f"- 기수 공통 취약 영역: **{weak_area_class}**")

    st.subheader("🧾 기수 운영 분석 요약")
    st.write(
        f"본 기수는 평균 정답률 {class_avg}% 수준으로, "
        f"훈련생 다수가 '{weak_area_class}' 영역에서 어려움을 보이고 있음. "
        f"해당 영역에 대한 기초 보강 및 반복 실습 중심의 수업 운영이 필요함."
    )

    # ───────── 엑셀 다운로드 ─────────
    excel_buffer = io.BytesIO()
    class_df.to_excel(excel_buffer, index=False, engine="xlsxwriter")
    excel_buffer.seek(0)

    st.download_button(
        "📥 기수 전체 결과 엑셀 다운로드",
        excel_buffer,
        f"{class_no}_기수_사전평가_결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
