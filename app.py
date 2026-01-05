import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="사전역량 진단", layout="centered")

st.title("📋 훈련생 사전역량 진단")
st.write("본 평가는 훈련생의 현재 수준을 파악하기 위한 사전평가입니다.")

# ─────────────────────
# 인적사항
# ─────────────────────
name = st.text_input("이름")
class_no = st.text_input("기수 / 반")

st.divider()

# ─────────────────────
# 문항 함수 (중복 제거 핵심)
# ─────────────────────
def q(label):
    return st.slider(label, 1, 5, 3)

# ─────────────────────
# 20문항
# ─────────────────────
st.subheader("① 기초역량")
q1 = q("Q1. 컴퓨터 기본 조작이 익숙하다")
q2 = q("Q2. 인터넷 검색을 활용할 수 있다")
q3 = q("Q3. 파일 업로드/다운로드가 가능하다")
q4 = q("Q4. 온라인 강의 수강 경험이 있다")
q5 = q("Q5. 새로운 프로그램 학습에 부담이 적다")

st.subheader("② 전공 이해도")
q6 = q("Q6. 전공 기초 개념을 알고 있다")
q7 = q("Q7. 전공 용어 이해에 어려움이 적다")
q8 = q("Q8. 실습 수업을 따라갈 자신이 있다")
q9 = q("Q9. 전공 학습 속도가 적절하다")
q10 = q("Q10. 전공 내용에 흥미가 있다")

st.subheader("③ 학습 태도")
q11 = q("Q11. 수업에 성실히 참여할 수 있다")
q12 = q("Q12. 과제를 기한 내 수행할 수 있다")
q13 = q("Q13. 어려운 내용은 질문하는 편이다")
q14 = q("Q14. 복습·예습 의지가 있다")
q15 = q("Q15. 수료까지 학습을 유지할 수 있다")

st.subheader("④ 취업·목표 인식")
q16 = q("Q16. 수료 후 진로 목표가 있다")
q17 = q("Q17. 희망 직무를 알고 있다")
q18 = q("Q18. 취업 준비 계획이 있다")
q19 = q("Q19. 관련 자격·역량 향상 의지가 있다")
q20 = q("Q20. 취업을 위해 추가 노력을 할 의향이 있다")

# ─────────────────────
# 제출 및 분석
# ─────────────────────
if st.button("📊 결과 확인"):
    scores = [q1,q2,q3,q4,q5,
              q6,q7,q8,q9,q10,
              q11,q12,q13,q14,q15,
              q16,q17,q18,q19,q20]

    total_avg = round(sum(scores) / 20, 2)

    if total_avg < 2.5:
        level = "집중관리 필요"
    elif total_avg < 3.8:
        level = "일반 수준"
    else:
        level = "우수 수준"

    st.success(f"종합 평균: {total_avg}점")
    st.info(f"수준 분류: {level}")

    # 결과 데이터
    df = pd.DataFrame([{
        "이름": name,
        "기수": class_no,
        "종합평균": total_avg,
        "수준": level
    }])

    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    st.download_button(
         label="📥 결과 엑셀 다운로드",
         data=excel_buffer,
         file_name="사전평가결과.xlsx",
         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)



