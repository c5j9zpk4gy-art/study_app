# study_app
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="고교 내신 맞춤형 학습 솔루션", page_icon="🎯", layout="wide")

st.title("🎯 고교 내신 맞춤형 초인쇄 학습 솔루션 (v2.0)")
st.caption("학교알리미 5단계 학군지 분석 + 5대 학습 성향 진단 + 시중 15개 문제집 DB 기반")
st.divider()

# --- 1. DATABASE DEFINITIONS ---
REGION_DB = {
    "최상위 학군지 (강남/서초/송파/수성/분당)": 1.30,
    "상위 학군지 (양천/노원/동안/수지)": 1.20,
    "중상위 학군지 (영통/일산/연수/유성)": 1.10,
    "평이 지역 (천안/청주/전주/창원 등 주요도시)": 1.00,
    "기타 / 지방 소도시 및 읍면지역": 0.90
}

BOOK_DB = [
    {"name": "개념원리", "level": 1, "pages": 220, "type": "개념"},
    {"name": "라이트쎈", "level": 1, "pages": 200, "type": "개념유형"},
    {"name": "개념쎈", "level": 1, "pages": 210, "type": "개념"},
    {"name": "개념원리 RPM", "level": 2, "pages": 280, "type": "유형"},
    {"name": "쎈 (SSEN)", "level": 2, "pages": 320, "type": "대표유형"},
    {"name": "마플시너지", "level": 2, "pages": 380, "type": "유형패키지"},
    {"name": "일품", "level": 3, "pages": 220, "type": "준심화"},
    {"name": "일등급수학", "level": 3, "pages": 200, "type": "준심화"},
    {"name": "자이스토리 내신", "level": 3, "pages": 300, "type": "기출유형"},
    {"name": "블랙라벨", "level": 4, "pages": 180, "type": "심화"},
    {"name": "수학의 신", "level": 4, "pages": 190, "type": "심화"},
    {"name": "531 프로젝트 Hyper", "level": 4, "pages": 150, "type": "단기심화"},
    {"name": "절대등급", "level": 5, "pages": 160, "type": "최상위"},
    {"name": "올림포스 고난도", "level": 5, "pages": 140, "type": "최상위"},
    {"name": "1등급 만들기", "level": 5, "pages": 170, "type": "최상위"}
]

# --- 2. USER INPUT FORM ---
st.header("📋 1. 학생 기본 정보 및 학군지 설정")
c1, c2, c3, c4 = st.columns(4)
with c1:
    curr_grade = st.number_input("현재 내신 등급", 1, 9, 3)
with c2:
    target_grade = st.number_input("목표 내신 등급", 1, 9, 1)
with c3:
    region_choice = st.selectbox("학교 지역 (학군지)", list(REGION_DB.keys()), index=3)
with c4:
    target_days = st.number_input("목표 대비 기간(일)", 10, 180, 30)

st.subheader("📝 2. 5대 학습 습관 및 취약점 진단 설문")
col_a, col_b = st.columns(2)

with col_a:
    q1 = st.radio("Q1. 시험 볼 때 시간 배분은 어떤가요?", 
                  ["시간이 많이 부족해서 뒷문제를 못 푼다", "딱 맞게 풀거나 약간 부족하다", "시간이 남아 검토까지 가능하다"])
    q2 = st.radio("Q2. 계산 실수나 문제 오독으로 감점되는 비율은?", 
                  ["자주 발생한다 (2~3문항 이상)", "가끔 발생한다 (1문항 정도)", "실수가 거의 없다"])
    q3 = st.radio("Q3. 서술형 문항 작성 시 감점 경험은?", 
                  ["풀이과정을 어디서부터 써야할지 모른다", "감점을 자주 당한다", "서술형 작성이 완벽하다"])

with col_b:
    q4 = st.radio("Q4. 오답노트 작성 및 회독 습관은?", 
                  ["틀린 문제를 눈으로만 보고 넘어간다", "답지만 보고 이해되면 넘어간다", "직접 다시 풀고 3회독 이상 반복한다"])
    q5 = st.radio("Q5. 고난도/신유형 문항을 만났을 때 반응은?", 
                  ["바로 포기하고 답지를 본다", "5분 정도 고민하다 답지를 본다", "끝까지 스스로 풀려고 오랫동안 고민한다"])

# --- 3. ALGORITHM & GENERATION ---
if st.button("🚀 초인쇄 맞춤 솔루션 리포트 생성하기", type="primary", use_container_width=True):
    st.divider()
    st.header("📊 3. 개인 맞춤형 학습 솔루션 리포트")
    
    weight = REGION_DB[region_choice]
    gap = curr_grade - target_grade
    
    # 등급 격차 및 학군지 가중치 기반 문제집 로직
    if gap >= 3 or weight >= 1.2:
        rec_books = [BOOK_DB[4], BOOK_DB[6], BOOK_DB[9]]  # 쎈, 일품, 블랙라벨
        sol_type = "A솔루션 (고난도 심화 돌파형)"
    elif gap >= 1 or weight >= 1.0:
        rec_books = [BOOK_DB[3], BOOK_DB[4], BOOK_DB[6]]  # RPM, 쎈, 일품
        sol_type = "B솔루션 (유형 마스터 및 상위권 도약형)"
    else:
        rec_books = [BOOK_DB[0], BOOK_DB[3]]  # 개념원리, RPM
        sol_type = "C솔루션 (개념 확립 및 실수 방지형)"
        
    total_p = sum(b['pages'] for b in rec_books)
    daily_p = round((total_p * weight) / target_days, 1)

    # 지표 출력
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("적용 솔루션 유형", sol_type)
    m2.metric("학군지 난이도 가중치", f"{weight}x")
    m3.metric("추천 문제집 조합", f"{len(rec_books)}권")
    m4.metric("하루 권장 학습량", f"일 {daily_p} 페이지")

    st.subheader("📚 추천 맞춤 문제집 조합 상세")
    for b in rec_books:
        st.write(f"• **{b['name']}** [{b['type']}] | 총 {b['pages']}p (난이도 Lv.{b['level']})")

    st.subheader("💡 1:1 맞춤형 세부 학습 방향 멘토링")
    
    # 5대 설문 결과 기반 세부 멘토링
    if "부족해서" in q1:
        st.error("⏱️ **시간 관리 전략:** 시험 시 '1차 스킵 법칙'을 적용하세요. 1분 이상 막히는 문제는 별표 치고 넘어간 후, 아는 문제를 다 풀고 돌아오는 훈련이 필수적입니다.")
    if "자주 발생" in q2:
        st.warning("✏️ **계산 실수 방지:** '풀이과정 구획화 노트'를 작성하세요. 연습장에 반을 접어 순서대로 풀이과정을 적는 습관을 들이면 오답 검토 시간이 절반으로 줄어듭니다.")
    if "어디서부터" in q3 or "자주 당" in q3:
        st.info("📝 **서술형 감점 방지:** 문제집 해설지의 '채점 기준표(감점 포인트)'를 빨간펜으로 표시하며 출제자의 정답 키워드를 적는 연습을 하세요.")
    if "눈으로만" in q4 or "답지만 보고" in q4:
        st.warning("🔄 **오답 회독 전략:** 틀린 문제는 문제지에 '24시간 후 재풀이', '1주일 후 재풀이' 체크박스를 표시하고 3색 펜 오답노트를 만드세요.")
    if "바로 포기" in q5:
        st.info("🧠 **고난도 문항 접근법:** 고난도 문제는 3단계 쪼개기 분석법(조건 정리 ➔ 사용될 개념 나열 ➔ 식 세우기)을 적용하세요.")

st.divider()
st.header("⏱️ Today 순공시간 측정 스톱워치")
if st.button("⏱️ 스톱워치 시작 / 일시정지"):
    st.info("스톱워치가 동작 중입니다. (학습 기록 자동 저장 연동 가능)")
