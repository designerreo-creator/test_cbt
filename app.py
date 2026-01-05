import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="사전평가 CBT 종합분석", layout="centered")

st.title("📝 사전역량 진단 CBT (개인·기수 종합분석)")
st.write("본 평가는 개인별 진단 및 기수 전체 운영 분석 자료로 활용됩니다.")

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
# 제출 및 종합 분석
# ─────────────────────
if st.button("📊 제출 및 종합분석"):

    records = []
    score = 0

    for user_ans, (_, _, correct, area) in zip(answers, questions):
        correct_yn = 1 if user_ans == correct else 0
        score += correct_yn
        records.append({"영역": area, "정답여부": correct_yn})

    df_person_detail = pd.DataFrame(records)
    area_rate = (df_person_detail.groupby("영역")["정답여부"].mean() * 100).round(1)

    total_rate = round(score / len(questions) * 100, 1)

    if total_rate < 50:
        level = "집중관리 필요"
    elif total_rate < 80:
        level = "일반 수준"
    else:
        level = "우수 수준"

    strong = area_rate.idxmax()
    weak = area_rate.idxmin()

    personal_analysis = (
        f"{name} 훈련생은 사전평가 결과 전체 정답률 {total_rate}%로 "
        f"'{level}' 수준에 해당합니다. "
        f"영역별 분석 결과 '{strong}' 영역에서 강점을 보이며, "
        f"'{weak}' 영역에서는 보완이 필요한 것으로 분석되었습니다."
    )

    # ───────── 개인 결과 DataFrame
    df_person = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "총점": score,
        "정답률(%)": total_rate,
        "수준": level,
        "강점영역": strong,
        "취약영역": weak,
        "개인분석": personal_analysis
    }])

    # ───────── 누적 저장
    if os.path.exists(DATA_FILE):
        df_all = pd.read_csv(DATA_FILE)
        df_all = pd.concat([df_all, df_person], ignore_index=True)
    else:
        df_all = df_person.copy()

    df_all.to_csv(DATA_FILE, index=False)

    # ───────── 기수 전체 분석
    class_df = df_all[df_all["기수"] == class_no]
    class_avg = round(class_df["정답률(%)"].mean(), 1)
    weak_area_class = class_df["취약영역"].value_counts().idxmax()

    class_analysis = (
        f"본 기수는 평균 정답률 {class_avg}% 수준으로, "
        f"'{weak_area_class}' 영역에서 공통적인 학습 보완 필요성이 확인됨. "
        f"해당 영역에 대한 기초 개념 정리 및 반복 실습 중심의 수업 운영이 요구됨."
    )

    df_class_summary = pd.DataFrame([{
        "기수": class_no,
        "평균정답률(%)": class_avg,
        "공통취약영역": weak_area_class,
        "기수운영분석": class_analysis
    }])

    # ───────── 화면 출력
    st.success("분석 완료! 아래 버튼을 통해 엑셀 파일을 다운로드하세요.")

    # ───────── 엑셀 다중 시트 생성
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_person.to_excel(writer, sheet_name="개인결과", index=False)
        df_class_summary.to_excel(writer, sheet_name="기수요약", index=False)
        class_df.to_excel(writer, sheet_name="기수원자료", index=False)

    excel_buffer.seek(0)

    st.download_button(
        "📥 개인·기수 종합분석 엑셀 다운로드",
        excel_buffer,
        f"{class_no}_사전평가_종합분석.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
