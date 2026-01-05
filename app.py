import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="사전평가 CBT 개인분석", layout="centered")

st.title("📝 사전역량 진단 CBT (개인분석 포함)")
st.write("본 평가는 훈련생의 현재 수준을 진단하고, 개인별 학습 지원을 위해 활용됩니다.")

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

    ("Q11. 수료에 가장 중요한 요소는?",
     ["재능", "성실한 참여", "운", "도움"], 1, "학습태도"),
    ("Q12. 과제가 어려울 때 행동은?",
     ["미제출", "복사", "질문", "포기"], 2, "학습태도"),
    ("Q13. 복습 시점으로 적절한 것은?",
     ["한 달 후", "수업 직후", "시험 전", "생각날 때"], 1, "학습태도"),
    ("Q14. 집중이 안 될 때 대처는?",
     ["폰", "잠", "휴식 후 집중", "포기"], 2, "학습태도"),
    ("Q15. 동기 유지에 도움이 되는 것은?",
     ["목표 없음", "수업만", "목표 설정", "비교"], 2, "학습태도"),

    ("Q16. 훈련 수강의 바람직한 목적은?",
     ["시간", "자격증", "취업·역량", "권유"], 2, "취업인식"),
    ("Q17. 취업 목표 설정 시 우선 요소는?",
     ["연봉", "필요 역량", "거리", "평가"], 1, "취업인식"),
    ("Q18. 취업 준비의 핵심은?",
     ["운", "준비 과정", "나이", "학력"], 1, "취업인식"),
    ("Q19. 취업 가능성 향상 방법은?",
     ["잊기", "결과물 정리", "출석", "자격증"], 1, "취업인식"),
    ("Q20. 취업을 위한 태도는?",
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
# 채점 + 개인분석
# ─────────────────────
if st.button("📊 제출 및 개인분석 확인"):

    records = []
    score = 0

    for user_ans, (q, opts, correct, area) in zip(answers, questions):
        correct_yn = 1 if user_ans == correct else 0
        score += correct_yn
        records.append({"영역": area, "정답여부": correct_yn})

    df = pd.DataFrame(records)
    area_score = df.groupby("영역")["정답여부"].mean() * 100
    area_score = area_score.round(1)

    total_rate = round(score / len(questions) * 100, 1)

    if total_rate < 50:
        level = "집중관리 필요"
    elif total_rate < 80:
        level = "일반 수준"
    else:
        level = "우수 수준"

    strong = area_score.idxmax()
    weak = area_score.idxmin()

    # ───────── 개인 분석 문장 생성 ─────────
    personal_analysis = (
        f"{name} 훈련생은 사전평가 결과 전체 정답률 {total_rate}%로 "
        f"현재 수준은 '{level}'에 해당합니다. "
        f"영역별 분석 결과, '{strong}' 영역에서 상대적으로 강점을 보이며 "
        f"'{weak}' 영역에서는 보완이 필요한 것으로 나타났습니다. "
        f"향후 학습 과정에서는 '{weak}' 영역에 대한 기초 개념 정리 및 "
        f"반복 실습을 중심으로 학습을 진행하고, "
        f"강점 영역인 '{strong}'은 심화 학습을 통해 역량을 확장하는 것이 바람직합니다."
    )

    # ───────── 화면 출력 ─────────
    st.success(f"총점: {score}/20점 | 정답률: {total_rate}% | 수준: {level}")

    st.subheader("📊 영역별 점수")
    st.dataframe(area_score.reset_index().rename(
        columns={"영역": "영역", "정답여부": "점수(%)"}
    ), use_container_width=True)

    st.subheader("🧾 개인 분석 결과")
    st.write(personal_analysis)

    # ───────── 엑셀 저장 ─────────
    result_df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "총점": score,
        "정답률(%)": total_rate,
        "수준": level,
        "강점영역": strong,
        "취약영역": weak,
        "개인분석": personal_analysis
    }])

    excel_buffer = io.BytesIO()
    result_df.to_excel(excel_buffer, index=False, engine="xlsxwriter")
    excel_buffer.seek(0)

    st.download_button(
        "📥 개인분석 결과 엑셀 다운로드",
        excel_buffer,
        "사전평가_개인분석결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
