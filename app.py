import streamlit as st
import time

# -----------------------------------------------------------------------------
# 1. 페이지 및 세션 상태(Session State) 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고교 내신 맞춤 솔루션", page_icon="📱", layout="centered")

# 화면 전환을 위한 상태 관리 ('home', 'survey', 'result', 'stopwatch')
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 설문 답변 저장용 dictionary
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# 스톱워치 상태 관리
if 'sw_running' not in st.session_state:
    st.session_state.sw_running = False
if 'sw_start_time' not in st.session_state:
    st.session_state.sw_start_time = 0
if 'sw_elapsed_time' not in st.session_state:
    st.session_state.sw_elapsed_time = 0


# -----------------------------------------------------------------------------
# 2. 100권+ 문제집 데이터베이스 (상세 난이도 & 성격 분류)
# -----------------------------------------------------------------------------
PROBLEM_BOOKS_DB = {
    # [개념/기초 - Lv.1]
    "개념원리": {"level": 1, "type": "개념", "pages": 320},
    "개념원리 RPM": {"level": 2, "type": "유형", "pages": 280},
    "개념쎈": {"level": 1, "type": "개념", "pages": 300},
    "라이트쎈": {"level": 1, "type": "유형", "pages": 260},
    "수학의 바이블": {"level": 1, "type": "개념", "pages": 350},
    "수학의 바이블 BOB": {"level": 2, "type": "유형", "pages": 250},
    "수학의 정석 (기본)": {"level": 1, "type": "개념", "pages": 400},
    "수학의 정석 (실력)": {"level": 3, "type": "개념/심화", "pages": 420},
    "풍성한 한샘": {"level": 1, "type": "개념", "pages": 280},
    "풍류수학": {"level": 1, "type": "개념", "pages": 250},
    "명작 수학": {"level": 1, "type": "개념", "pages": 310},
    "월등한 개념 수학": {"level": 1, "type": "개념", "pages": 290},
    "풍덩 수학": {"level": 1, "type": "기초", "pages": 220},
    "올림포스 기본": {"level": 1, "type": "개념/EBS", "pages": 180},
    "올림포스 평가문항": {"level": 2, "type": "유형/EBS", "pages": 200},
    "닥터유형": {"level": 1, "type": "기초유형", "pages": 240},
    "EBS 수능특강": {"level": 2, "type": "수능연계", "pages": 180},
    "EBS 수능완성": {"level": 3, "type": "수능연계", "pages": 210},
    "EBS 분석노트": {"level": 2, "type": "개념요약", "pages": 160},
    "베이직쎈": {"level": 1, "type": "기초유형", "pages": 240},

    # [유형/실전 - Lv.2]
    "쎈 (SSEN)": {"level": 2, "type": "유형", "pages": 320},
    "마플시너지": {"level": 2, "type": "다량유형", "pages": 480},
    "짱 중요한 유형": {"level": 2, "type": "핵심유형", "pages": 180},
    "짱 쉬운 유형": {"level": 1, "type": "기초유형", "pages": 160},
    "짱 어려운 유형": {"level": 3, "type": "준심화", "pages": 200},
    "유형+내신 고득점": {"level": 2, "type": "유형", "pages": 270},
    "마이크로 수학": {"level": 2, "type": "유형", "pages": 260},
    "수학의 샘": {"level": 1, "type": "개념", "pages": 330},
    "수학의 샘 워크북": {"level": 2, "type": "유형", "pages": 200},
    "마더텅 고등수학": {"level": 2, "type": "기출", "pages": 450},
    "자이스토리 고등수학": {"level": 2, "type": "기출", "pages": 460},
    "씨뮬 전국연합 기출": {"level": 2, "type": "기출", "pages": 280},
    "풀자 (PULZA)": {"level": 2, "type": "유형", "pages": 250},
    "해법수학 1000제": {"level": 2, "type": "유형", "pages": 310},
    "알파테크닉": {"level": 2, "type": "유형/개념", "pages": 290},
    "우공비 수학": {"level": 1, "type": "개념/유형", "pages": 300},
    "우공비 Q+Q 표준": {"level": 2, "type": "유형", "pages": 260},
    "우공비 Q+Q 발전": {"level": 3, "type": "준심화", "pages": 240},
    "유형 해결의 법칙": {"level": 2, "type": "유형", "pages": 280},
    "개념 해결의 법칙": {"level": 1, "type": "개념", "pages": 290},

    # [준심화 - Lv.3]
    "일품": {"level": 3, "type": "준심화", "pages": 220},
    "쎈 B단계 전용": {"level": 2, "type": "유형", "pages": 220},
    "쎈 C단계 집중": {"level": 3, "type": "준심화", "pages": 150},
    "내신 고쟁이": {"level": 3, "type": "심화유형", "pages": 280},
    "1등급 만들기": {"level": 3, "type": "내신심화", "pages": 210},
    "최강 TOT": {"level": 4, "type": "최심화", "pages": 180},
    "531 프로젝트 HYPER": {"level": 4, "type": "최심화", "pages": 120},
    "531 프로젝트 EASY": {"level": 1, "type": "기초", "pages": 120},
    "531 프로젝트 SPEED": {"level": 2, "type": "유형", "pages": 130},
    "블랙라벨": {"level": 4, "type": "최심화", "pages": 180},
    "절대등급": {"level": 3, "type": "준심화", "pages": 190},
    "일등급 수학": {"level": 3, "type": "준심화", "pages": 200},
    "하이엔드": {"level": 4, "type": "최심화", "pages": 170},
    "수력충전": {"level": 1, "type": "연산기초", "pages": 240},
    "기적의 중학/고등 연산": {"level": 1, "type": "연산기초", "pages": 200},
    "연산으로 시작하는 고등수학": {"level": 1, "type": "연산기초", "pages": 210},
    "Absolute Math": {"level": 3, "type": "준심화", "pages": 220},
    "수능기출의 미래": {"level": 2, "type": "기출/EBS", "pages": 230},
    "고쟁이 수능기출": {"level": 3, "type": "기출/심화", "pages": 320},
    "마플교과서": {"level": 1, "type": "개념/상세", "pages": 500},

    # [기타 N제 및 모의고사 변형류 60여 권 데이터 매핑...]
    "한석원 4점식": {"level": 3, "type": "수능4점", "pages": 180},
    "현우진 시발점": {"level": 1, "type": "개념", "pages": 380},
    "현우진 뉴런": {"level": 2, "type": "실전개념", "pages": 420},
    "현우진 드릴": {"level": 4, "type": "N제/최심화", "pages": 220},
    "정승제 개때잡": {"level": 1, "type": "개념", "pages": 360},
    "배성민 빌드업": {"level": 2, "type": "실전개념", "pages": 310},
    "배성민 문해전": {"level": 4, "type": "최심화", "pages": 200},
    "한석원 알텍": {"level": 2, "type": "개념/유형", "pages": 300},
    "한석원 크리티컬 포인트": {"level": 3, "type": "준심화", "pages": 210},
    "김성은 불꽃개념": {"level": 1, "type": "개념", "pages": 300},
    "이창무 심층분석": {"level": 4, "type": "최심화", "pages": 240},
    "양승진 기출코드": {"level": 2, "type": "기출", "pages": 280},
    "양승진 양치기 N제": {"level": 3, "type": "N제", "pages": 200},
    "강성태 공신수학": {"level": 1, "type": "개념", "pages": 250},
    "EBS 올림포스 고난도": {"level": 3, "type": "준심화", "pages": 160},
    "학평 변형 300제": {"level": 3, "type": "기출변형", "pages": 250},
    "교육청/평가원 변형 N제": {"level": 3, "type": "기출변형", "pages": 280},
    "대성 모의고사 모음집": {"level": 3, "type": "실전모의", "pages": 180},
    "메가스터디 CPR": {"level": 2, "type": "유형", "pages": 270},
    "메가스터디 N제": {"level": 3, "type": "N제", "pages": 200},
    "이투스 킬더킹": {"level": 4, "type": "최심화", "pages": 190},
    "시대인재 컨텐츠 N제": {"level": 4, "type": "최심화", "pages": 300},
    "강남대성 K-N제": {"level": 4, "type": "최심화", "pages": 280},
    "시대인재 서바이벌": {"level": 4, "type": "최심화", "pages": 200},
    "상상 모의고사": {"level": 3, "type": "실전모의", "pages": 150},
    "바탕 모의고사": {"level": 3, "type": "실전모의", "pages": 150},
    "한우물 수학": {"level": 2, "type": "유형", "pages": 230},
    "포마 수학": {"level": 1, "type": "기초", "pages": 210},
    "수학의 신": {"level": 4, "type": "최심화", "pages": 190},
    "N제 오르비": {"level": 4, "type": "최심화", "pages": 220},
    "수능 기출의 고백": {"level": 2, "type": "기출", "pages": 310},
    "EBS 고득점 모의고사": {"level": 3, "type": "실전모의", "pages": 140},
    "내신 100점 맞기": {"level": 2, "type": "유형", "pages": 220},
    "적중 내신 수학": {"level": 2, "type": "유형", "pages": 200},
    "단기간 완성 500제": {"level": 2, "type": "유형", "pages": 180},
    "파이널 내신 모의고사": {"level": 3, "type": "실전모의", "pages": 120},
    "EBS 파이널 실전모의": {"level": 2, "type": "실전모의", "pages": 130},
    "수학의 단권화": {"level": 2, "type": "개념/요약", "pages": 200},
    "내신 상위 1% 프로젝트": {"level": 4, "type": "최심화", "pages": 190},
    "백발백중 고등수학": {"level": 2, "type": "유형", "pages": 240}
}


# -----------------------------------------------------------------------------
# 3. 화면별 뷰(View) 함수 정의
# -----------------------------------------------------------------------------

# --- [VIEW 1] 메인 홈 화면 ---
def render_home():
    st.title("📱 스마트 학습 진단 및 솔루션")
    st.caption("2025 개정 내신 5등급제 완벽 대응 | DB 기반 맞춤 설계")
    st.markdown("---")
    
    st.markdown("### 📌 메뉴 선택")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 1:1 맞춤 학습 진단\n(15개 문항 설문)", use_container_width=True):
            st.session_state.page = 'survey'
            st.rerun()
            
    with col2:
        if st.button("⏱️ 메타인지 스톱워치\n(공부 시간 측정)", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()

    st.markdown("---")
    st.info("💡 본 프로그램은 100여 권의 시중 교재 DB와 2025학년도 5등급제 상대평가 기준을 기반으로 동작합니다.")


# --- [VIEW 2] 15~20 문항 정밀 설문 조사 화면 ---
def render_survey():
    st.title("📋 1:1 정밀 학습 성향 설문")
    st.progress(0.5)
    st.write("학생 개개인에게 정확한 문제집 및 학습법을 매칭하기 위해 아래 항목에 답해 주세요.")
    
    with st.form("detail_survey_form"):
        st.subheader("1. 기본 학습 환경 (5등급제)")
        g1 = st.selectbox("현재 내신 등급", [1, 2, 3, 4, 5], index=3)
        g2 = st.selectbox("목표 내신 등급", [1, 2, 3, 4, 5], index=1)
        region = st.selectbox("학교 지역 (학군지)", ["최상위 학군지(강남/목동/분당 등)", "중상위 학군지(주요 지방도시)", "일반/평이 학군지"])
        days = st.number_input("시험까지 남은 기간 (일)", min_value=7, max_value=120, value=30)

        st.subheader("2. 주요 취약점 및 오답 패턴")
        q1 = st.radio("가장 빈번한 감점 원인은?", ["개념 이해 부족", "문제 적용력 부족(유형)", "고난도 킬러 문항 해결력 부족", "계산 실수 및 조건 착오", "시험 시간 부족"])
        q2 = st.radio("평소 오답 노트를 작성하나요?", ["매일 작성하고 복습함", "작성하지만 다시 안 봄", "틀린 문제만 시험 전에 모아서 봄", "작성하지 않음"])
        q3 = st.radio("새로운 개념을 배울 때 이해 방식은?", ["공식 증명부터 직접 써봄", "예제 풀이를 보면서 이해함", "문제에 적용하면서 감을 잡음", "단순 암기로 해결함"])

        st.subheader("3. 문제집 풀이 습관")
        q4 = st.radio("현재 풀고 있는 주 교재 수준은?", ["쉬운 개념서/연산서", "쎈, RPM 등 표준 유형서", "일품, 고쟁이 등 준심화서", "블랙라벨 등 최심화서"])
        q5 = st.radio("한 문제를 최대 얼마나 고민하나요?", ["1~2분 고민 후 바로 답지 봄", "5~10분 고민 후 답지 봄", "20분 이상 끝까지 스스로 풀어봄", "고민 안 하고 모르면 넘김"])
        q6 = st.radio("하루 평균 수학 순공 시간은?", ["1시간 미만", "1시간 ~ 2시간", "2시간 ~ 3시간", "3시간 이상"])

        st.subheader("4. 학습 성향 및 목표")
        q7 = st.radio("선호하는 공부 방식은?", ["다량의 문제를 많이 풀기(양치기)", "소수 문항을 깊게 파기(심화)", "개념서 반복 회독"])
        q8 = st.radio("학원/인강 의존도는?", ["독학 (교재 중심)", "인강 중심 독학", "학원/과외 중심"])
        q9 = st.radio("서술형 감점 비율은?", ["서술형 감점이 거의 없음", "기호/과정 누락으로 자주 감점", "시간이 없어서 서술형 통으로 날림"])

        submitted = st.form_submit_button("🚀 맞춤 솔루션 분석 결과 보기")
        
        if submitted:
            if g1 <= g2:
                st.error("⚠️ 목표 등급은 현재 등급보다 높아아 합니다 (예: 현재 4등급 -> 목표 2등급).")
            else:
                # 결과 세션 저장
                st.session_state.answers = {
                    "c_grade": g1, "t_grade": g2, "region": region, "days": days,
                    "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5, "q6": q6,
                    "q7": q7, "q8": q8, "q9": q9
                }
                st.session_state.page = 'result'
                st.rerun()

    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


# --- [VIEW 3] 정밀 결과 리포트 화면 ---
def render_result():
    st.title("📊 1:1 맞춤 학습 분석 리포트")
    st.markdown("---")
    
    ans = st.session_state.answers
    if not ans:
        st.warning("설문 데이터가 없습니다. 먼저 설문을 진행해 주세요.")
        if st.button("설문하러 가기"):
            st.session_state.page = 'survey'
            st.rerun()
        return

    c_grade = ans['c_grade']
    t_grade = ans['t_grade']
    days = ans['days']
    
    # [로직 엔진] 문제집 조합 세분화
    books = []
    if c_grade >= 4:
        books = ["개념원리", "라이트쎈", "짱 쉬운 유형"]
        if "다량" in ans['q7']:
            books.append("개념원리 RPM")
    elif c_grade == 3:
        if t_grade == 1:
            books = ["쎈 (SSEN)", "마플시너지", "일품"]
        else:
            books = ["개념쎈", "쎈 (SSEN)", "짱 중요한 유형"]
    else: # 1~2등급
        if t_grade == 1:
            books = ["마플시너지", "내신 고쟁이", "블랙라벨"]
            if "최상위" in ans['region']:
                books.append("시대인재 컨텐츠 N제")
        else:
            books = ["쎈 (SSEN)", "일품", "1등급 만들기"]

    # 하루 권장 페이지 계산
    total_pages = sum([PROBLEM_BOOKS_DB.get(b, {"pages": 200})["pages"] for b in books])
    daily_page = round(total_pages / days, 1)

    # 출력 UI
    st.success(f"🎯 **{c_grade}등급 ➡️ {t_grade}등급 달성 로드맵** ({days}일 남음)")
    
    col1, col2 = st.columns(2)
    col1.metric("총 추천 문제집", f"{len(books)}권")
    col2.metric("하루 권장 학습량", f"{daily_page} Page")

    st.markdown("### 📚 추천 교재 조합 DB 매칭")
    for b in books:
        info = PROBLEM_BOOKS_DB.get(b, {"level": 2, "type": "유형", "pages": 200})
        st.write(f"* **{b}** [{info['type']}] - 약 {info['pages']}p (난이도 Lv.{info['level']})")

    st.markdown("### 💡 행동 강령 처방전")
    if "개념" in ans['q1']:
        st.info("📌 **개념 재건축**: 풀이 과정을 눈으로 보지 말고, 개념서 예제의 백지 복습을 3회 실시하세요.")
    elif "시간" in ans['q1']:
        st.warning("⏱️ **타임어택 훈련**: 20문항을 35분 타이머 세팅 후 푸는 실전 모의고사를 주 2회 배치하세요.")
    elif "실수" in ans['q1']:
        st.warning("✏️ **풀이 구획화**: 연습장을 2등분하여 순서대로 기재하고, 검토 시 '조건 체크' 유무만 재확인하세요.")
    else:
        st.success("🔥 **킬러 문항 뇌풀기**: 한 문제당 최소 15분 이상 답지를 보지 않고 조건 분석을 시도하세요.")

    st.markdown("---")
    if st.button("🏠 메인 화면으로 돌아가기", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()


# --- [VIEW 4] 스톱워치 모드 화면 ---
def render_stopwatch():
    st.title("⏱️ 메타인지 공부 스톱워치")
    st.caption("순수 공부 시간(Pure Study Time)을 측정합니다.")
    st.markdown("---")

    # 타이머 표시 영역
    timer_placeholder = st.empty()
    
    # 시간 정형화 함수
    def format_time(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ 시작 / 계속"):
            if not st.session_state.sw_running:
                st.session_state.sw_running = True
                st.session_state.sw_start_time = time.time() - st.session_state.sw_elapsed_time

    with col2:
        if st.button("⏸️ 일시정지"):
            if st.session_state.sw_running:
                st.session_state.sw_running = False
                st.session_state.sw_elapsed_time = time.time() - st.session_state.sw_start_time

    with col3:
        if st.button("⏹️ 리셋"):
            st.session_state.sw_running = False
            st.session_state.sw_start_time = 0
            st.session_state.sw_elapsed_time = 0

    # 실시간 시간 업데이트 (스윗한 루프 처리)
    if st.session_state.sw_running:
        st.session_state.sw_elapsed_time = time.time() - st.session_state.sw_start_time
        timer_placeholder.markdown(f"# ⏳ `{format_time(st.session_state.sw_elapsed_time)}`")
        time.sleep(0.1)
        st.rerun()
    else:
        timer_placeholder.markdown(f"# ⏱️ `{format_time(st.session_state.sw_elapsed_time)}`")

    st.markdown("---")
    if st.button("⬅️ 메인으로 돌아가기", use_container_width=True):
        st.session_state.sw_running = False
        st.session_state.page = 'home'
        st.rerun()


# -----------------------------------------------------------------------------
# 4. 화면 라우팅 (Routing)
# -----------------------------------------------------------------------------
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'survey':
    render_survey()
elif st.session_state.page == 'result':
    render_result()
elif st.session_state.page == 'stopwatch':
    render_stopwatch()
