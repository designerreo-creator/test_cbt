import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="사전평가 CBT", layout="centered")

st.title("📝 사전역량 진단 CBT (4지선다형)")
st.write("본 평가는 훈련생의 현재 수준을 진단하기 위한 사전평가입니다.")

# ─────────────────────
# 인적사항
# ─────────────────────
name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

st.divider()

# ─────────────────────
# 문제은행 (문항, 보기, 정답)
# ─────────────────────
questions = [
    ("Q1. 컴퓨터를 켜고 인터넷 브라우저를 실행하는 방법은?",
     ["전원을 끈다", "전원 버튼 후 브라우저 클릭", "키보드 연결", "모니터 설정"], 1),

    ("Q2. 인터넷에서 정보를 찾는 일반적인 방법은?",
     ["메모장 실행", "검색엔진 키워드 입력", "파일 탐색기 실행", "제어판 실행"], 1),

    ("Q3. 이메일 첨부파일을 저장하려면?",
     ["삭제", "클릭하여 저장", "인쇄", "전달"], 1),

    ("Q4. 온라인 강의 수강에 필요한 것은?",
     ["프린터", "인터넷 연결", "USB", "외장하드"], 1),

    ("Q5. 새로운 프로그램 사용 시 바람직한 태도는?",
     ["포기", "무작정 클릭", "설명 확인", "대신 사용"], 2),

    ("Q6. 전공 실습의 목적은?",
     ["이론 암기", "시간 보내기", "실무 능력 향상", "시험 대비"], 2),

    ("Q7. 이해 안 되는 용어가 나오면?",
     ["무시", "기다림", "질문·검색", "대신 요청"], 2),

    ("Q8. 전공 실습 시 중요한 자세는?",
     ["속도", "결과만", "과정 이해", "따라 하기"], 2),

    ("Q9. 효율적인 전공 학습 방법은?",
     ["수업만", "복습", "몰아서", "메모 안 함"], 1),

    ("Q10. 실습 중 실패에 대한 올바른 인식은?",
     ["나쁘다", "학습 과정", "포기", "강사 책임"], 1),

    ("Q11. 수료에 가장 중요한 요소는?",
     ["재능", "성실한 참여", "운", "도움"], 1),

    ("Q12. 과제가 어려울 때 바람직한 행동은?",
     ["미제출", "복사", "질문", "포기"], 2),

    ("Q13. 복습 시점으로 적절한 것은?",
     ["한 달 후", "수업 직후", "시험 전", "생각날 때"], 1),

    ("Q14. 집중이 안 될 때 대처법은?",
     ["폰 보기", "잠", "휴식 후 집중", "포기"], 2),

    ("Q15. 학습 동기 유지에 도움이 되는 것은?",
     ["목표 없음", "수업만", "목표 설정", "비교"], 2),

    ("Q16. 훈련 수강의 바람직한 목적은?",
     ["시간 활용", "자격증", "취업·역량", "권유"], 2),

    ("Q17. 취업 목표 설정 시 먼저 고려할 것은?",
     ["연봉", "필요 역량", "거리", "평가"], 1),

    ("Q18. 취업 준비에서 중요한 요소는?",
     ["운", "준비 과정", "나이", "학력"], 1),

    ("Q19. 취업 가능성을 높이는 방법은?",
     ["잊기", "결과물 정리", "출석", "자격증"], 1),

    ("Q20. 취업을 위한 바람직한 태도는?",
     ["회피", "최소 노력", "지속 노력", "맡김"], 2),
]

# ─────────────────────
# 문항 출력
# ─────────────────────
answers = []

for idx, (q, options, _) in enumerate(questions):
    st.subheader(q)
    choice = st.radio(
        label="",
        options=options,
        key=f"q{idx}"
    )
    answers.append(options.index(choice))

st.divider()

# ─────────────────────
# 채점 및 결과
# ─────────────────────
if st.button("📊 제출 및 결과 확인"):

    score = 0
    for user, (_, _, correct) in zip(answers, questions):
        if user == correct:
            score += 1

    percent = round((score / len(questions)) * 100, 1)

    st.success(f"총점: {score} / 20점")
    st.info(f"정답률: {percent}%")

    # 결과 저장
    df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "총점": score,
        "정답률(%)": percent
    }])

    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="xlsxwriter")
    excel_buffer.seek(0)

    st.download_button(
        label="📥 결과 엑셀 다운로드",
        data=excel_buffer,
        file_name="사전평가_CBT_결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
