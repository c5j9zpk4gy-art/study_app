import streamlit as st
import time

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 모범 앱 커스텀 CSS (AI 느낌 제거 / 모바일 카드 UI)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고등 수학 내신 솔루션", page_icon="📱", layout="centered")

# 모바일 앱 스타일 커스텀 CSS (예시 이미지 디자인 반영)
st.markdown("""
    <style>
    /* 기본 배경 및 폰트 설정 */
    .main {
        background-color: #F8FAFC;
    }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 카드형 컨테이너 스타일 */
    .app-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }
    
    /* 뱃지 스타일 */
    .badge-primary {
        background-color: #2563EB;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-secondary {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #BFDBFE;
    }
    
    /* 버튼 스타일 개편 */
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    
    /* Streamlit 기본 헤더 및 텍스트 정제 */
    h1, h2, h3 {
        color: #0F172A;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'sw_running' not in st.session_state:
    st.session_state.sw_running = False
if 'sw_start_time' not in st.session_state:
    st.session_state.sw_start_time = 0
if 'sw_elapsed_time' not in st.session_state:
    st.session_state.sw_elapsed_time = 0


# -----------------------------------------------------------------------------
# 2. 내신 전용 교재 DB (N제 전량 삭제, 내신 명품 교재 40여 권) 및 교육과정 단원 DB
# -----------------------------------------------------------------------------
PROBLEM_BOOKS_DB = {
    # Level 1: 연산 및 기초 개념
    "수력충전": {"level": 1, "type": "연산기초", "pages": 220},
    "개념원리": {"level": 1, "type": "기본개념", "pages": 310},
    "개념쎈": {"level": 1, "type": "개념강화", "pages": 290},
    "라이트쎈": {"level": 1, "type": "쉬운유형", "pages": 250},
    "수학의 바이블": {"level": 1, "type": "기본개념", "pages": 340},
    "올림포스 기본": {"level": 1, "type": "학교부교재", "pages": 170},
    "베이직쎈": {"level": 1, "type": "기초유형", "pages": 230},
    "풍성한 한샘": {"level": 1, "type": "개념서", "pages": 270},
    
    # Level 2: 표준 내신 유형서
    "쎈 (SSEN)": {"level": 2, "type": "대표유형", "pages": 320},
    "개념원리 RPM": {"level": 2, "type": "표준유형", "pages": 270},
    "마플시너지": {"level": 2, "type": "다량유형", "pages": 460},
    "자이스토리 고등수학": {"level": 2, "type": "내신기출", "pages": 420},
    "마더텅 내신기출": {"level": 2, "type": "내신기출", "pages": 410},
    "짱 중요한 유형": {"level": 2, "type": "핵심유형", "pages": 180},
    "우공비 Q+Q 표준": {"level": 2, "type": "표준유형", "pages": 250},
    "유형 해결의 법칙": {"level": 2, "type": "표준유형", "pages": 260},
    "올림포스 평가문항": {"level": 2, "type": "내신유형", "pages": 190},
    
    # Level 3: 내신 준심화 & 고득점
    "일품": {"level": 3, "type": "준심화", "pages": 210},
    "내신 고쟁이": {"level": 3, "type": "심화유형", "pages": 270},
    "1등급 만들기": {"level": 3, "type": "내신고득점", "pages": 200},
    "짱 어려운 유형": {"level": 3, "type": "준심화", "pages": 190},
    "절대등급": {"level": 3, "type": "준심화", "pages": 180},
    "일등급 수학": {"level": 3, "type": "준심화", "pages": 190},
    "우공비 Q+Q 발전": {"level": 3, "type": "준심화", "pages": 220},
    "EBS 올림포스 고난도": {"level": 3, "type": "고난도부교재", "pages": 150},
    
    # Level 4: 내신 최심화 / 킬러
    "블랙라벨": {"level": 4, "type": "최심화", "pages": 170},
    "531 프로젝트 HYPER": {"level": 4, "type": "최심화", "pages": 120},
    "최강 TOT": {"level": 4, "type": "최심화", "pages": 160},
    "하이엔드": {"level": 4, "type": "최심화", "pages": 160},
    "수학의 신": {"level": 4, "type": "최심화", "pages": 180}
}

# 2022 개정 수학 단원 데이터 (내신 전용)
CURRICULUM_DB = {
    "공통수학1": [
        "1. 다항식 (다항식의 연산, 항등식과 인수분해)",
        "2. 방정식과 부등식 (복소수, 이차방정식, 이차함수, 여러 가지 방정식·부등식)",
        "3. 행렬 (행렬과 그 연산)",
        "4. 경우의 수 (순열과 조합)"
    ],
    "공통수학2": [
        "1. 도형의 방정식 (평면좌표, 직선의 방정식, 원의 방정식, 도형의 이동)",
        "2. 집합과 명제 (집합의 연산, 명제와 조건)",
        "3. 함수와 그래프 (함수, 합성함수와 역함수, 유리함수와 무리함수)"
    ],
    "대수": [
        "1. 지수함수와 로그함수 (지수와 로그, 지수함수, 로그함수)",
        "2. 삼각함수 (삼각함수의 뜻과 그래프, 삼각함수의 활용)",
        "3. 수열 (등차수열과 등비수열, 수열의 합, 수학적 귀납법)"
    ],
    "미적분I": [
        "1. 수열의 극한 (수열의 극한, 급수)",
        "2. 미분법 (여러 가지 함수의 미분, 미분법의 활용)",
        "3. 적분법 (여러 가지 적분법, 정적분의 활용)"
    ],
    "확률과 통계": [
        "1. 순열과 조합 (여러 가지 순열, 중복조합과 이항정리)",
        "2. 확률 (확률의 뜻과 활용, 조건부확률)",
        "3. 통계 (확률변수와 확률분포, 통계적 추정)"
    ],
    "미적분II": [
        "1. 지수·로그·삼각함수의 극한과 미분",
        "2. 여러 가지 미분법 및 도함수의 활용",
        "3. 여러 가지 적분법 및 정적분의 활용"
    ]
}


# -----------------------------------------------------------------------------
# 3. 화면별 뷰(View) 구현
# -----------------------------------------------------------------------------

# --- [VIEW 1] 메인 홈 화면 ---
def render_home():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.title("고등 수학 내신 솔루션")
    st.write("2025 개정 내신 5등급제 대비 · 전교 석차 및 학군지 가중치 적용")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("진단 및 맞춤 플랜 생성", use_container_width=True):
            st.session_state.page = 'survey'
            st.rerun()
    with col2:
        if st.button("순공 스톱워치 실행", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()


# --- [VIEW 2] 상세 진단 설문 화면 ---
def render_survey():
    st.markdown('<span class="badge-primary">STEP 1</span> <b>정밀 학습 진단</b>', unsafe_allow_html=True)
    st.write("")
    
    with st.form("detail_survey_form"):
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("1. 과목 및 학교 석차 정보")
        subject = st.selectbox("진단할 수학 과목", list(CURRICULUM_DB.keys()))
        
        c1, c2 = st.columns(2)
        with c1:
            total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=600, value=200)
        with c2:
            student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=total_students, value=30)
            
        target_grade = st.selectbox("목표 내신 등급 (5등급제 기준)", [1, 2, 3, 4, 5], index=0)
        days = st.number_input("시험 대비 목표 기간 (일)", min_value=7, max_value=90, value=30)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("2. 학군지 수준 및 내신 난이도")
        region_level = st.radio(
            "학교의 내신 출제 난이도 및 학군지 선택",
            [
                "Level 4: 최상위 학군지 (강남, 대치, 서초, 목동, 중계, 분당 등 / 변형 심화 출제)",
                "Level 3: 주요 도시 거점 학군지 (천안, 청주, 전주, 창원, 대구 수성, 부산 해운대 등)",
                "Level 2: 일반 평이 학군지 (전국 일반계 고교 평균 수준 출제)",
                "Level 1: 기본 개념 위주 출제 학교 (기초 문항 비중이 높음)"
            ]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("3. 취약 오답 유형 분석")
        weak_point = st.radio(
            "가장 주된 감점 요인",
            ["기본 개념 미숙 및 공식 이해 부족", "대표 유형 적용 능력 부족", "내신 킬러/변형 문항 해결력 부족", "시간 부족 및 서술형 감점"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("맞춤 커리큘럼 분석 결과 보기")
        
        if submitted:
            # 백분위 및 등급 계산 (2025 5등급제: 1등급 10%, 2등급 34%, 3등급 66%, 4등급 90%)
            pct = (student_rank / total_students) * 100
            
            if pct <= 10.0:
                calc_grade = 1
            elif pct <= 34.0:
                calc_grade = 2
            elif pct <= 66.0:
                calc_grade = 3
            elif pct <= 90.0:
                calc_grade = 4
            else:
                calc_grade = 5
                
            if calc_grade <= target_grade and calc_grade != 1:
                st.error("목표 등급은 현재 내신 등급보다 높아야 합니다.")
            else:
                st.session_state.answers = {
                    "subject": subject, "total_students": total_students, "student_rank": student_rank,
                    "pct": round(pct, 2), "calc_grade": calc_grade, "target_grade": target_grade,
                    "days": days, "region_level": region_level, "weak_point": weak_point
                }
                st.session_state.page = 'result'
                st.rerun()

    if st.button("메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


# --- [VIEW 3] 정밀 결과 리포트 및 커리큘럼 캘린더 ---
def render_result():
    ans = st.session_state.answers
    if not ans:
        st.session_state.page = 'survey'
        st.rerun()
        return

    st.markdown('<span class="badge-secondary">ANALYSIS REPORT</span>', unsafe_allow_html=True)
    st.title("내신 맞춤 솔루션 리포트")
    st.markdown('---')

    # 백분위 정보 출력
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.write(f"**선택 과목:** {ans['subject']} | **대비 기간:** {ans['days']}일")
    st.write(f"**현재 석차:** 전교 {ans['student_rank']}위 / {ans['total_students']}명 (상위 {ans['pct']}%)")
    st.write(f"**진단 등급:** 현재 내신 {ans['calc_grade']}등급 ➔ **목표 {ans['target_grade']}등급**")
    st.markdown('</div>', unsafe_allow_html=True)

    # [가중치 부여 로직] 학군지 난이도 보정값 계산
    reg_text = ans['region_level']
    if "Level 4" in reg_text:
        region_weight = 2.0  # 학군지 가중치 높음
    elif "Level 3" in reg_text:
        region_weight = 1.0
    elif "Level 2" in reg_text:
        region_weight = 0.0
    else:
        region_weight = -0.5

    # 가중치가 반영된 실질 타겟 난이도 점수
    target_score = (6 - ans['target_grade']) + region_weight + (1.0 if ans['pct'] <= 15.0 else 0.0)

    # 문제집 매칭
    recommended_books = []
    if target_score >= 5.5: # 최상위 학군지 1~2등급 목표
        recommended_books = ["마플시너지", "내신 고쟁이", "블랙라벨"]
    elif target_score >= 4.0: # 주요 학군지 2등급 / 최상위 학군지 3등급
        recommended_books = ["쎈 (SSEN)", "일품", "내신 고쟁이"]
    elif target_score >= 2.5: # 일반 학군지 2~3등급
        recommended_books = ["개념원리 RPM", "쎈 (SSEN)", "1등급 만들기"]
    else: # 기초/유형 보강
        recommended_books = ["개념원리", "라이트쎈", "짱 중요한 유형"]

    # 하루 권장 분량
    total_pages = sum([PROBLEM_BOOKS_DB.get(b, {"pages": 200})["pages"] for b in recommended_books])
    daily_page = round(total_pages / ans['days'])
    daily_time_min = round(daily_page * 4.5)

    # 추천 교재 출력
    st.markdown('### 📚 추천 내신 교재 라인업')
    for idx, b in enumerate(recommended_books, 1):
        info = PROBLEM_BOOKS_DB.get(b, {"type": "내신유형", "pages": 200})
        st.markdown(f"**{idx}. {b}** `<span class='badge-secondary'>{info['type']}</span>` (약 {info['pages']}p)", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('### ⏱️ 권장 일일 학습 목표')
    st.info(f"매일 **최소 {daily_time_min}분 이상** 집중 투자하여 하루 **약 {daily_page} Page** 진도를 권장합니다.")

    # [과목별 대단원 캘린더 커리큘럼 생성 Engine]
    st.markdown("---")
    st.markdown(f"### 🗓️ {ans['subject']} {ans['days']}일 달성 캘린더 커리큘럼")
    
    units = CURRICULUM_DB.get(ans['subject'], ["전범위 기본 개념 및 유형 학습"])
    num_units = len(units)
    days_per_unit = max(1, ans['days'] // num_units)

    for i, unit in enumerate(units):
        start_day = i * days_per_unit + 1
        end_day = (i + 1) * days_per_unit if i < num_units - 1 else ans['days']
        
        st.markdown(f"""
        <div class="app-card">
            <span class="badge-primary">{start_day}일차 ~ {end_day}일차</span>
            <h4 style="margin-top: 8px;">{unit}</h4>
            <p style="color: #475569; font-size: 14px;">
            <b>주요 과제:</b> {recommended_books[0]} 개념/유형 완성 ➔ {recommended_books[-1]} 심화 문항 기출 분석
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


# --- [VIEW 4] 스톱워치 화면 ---
def render_stopwatch():
    st.markdown('<span class="badge-primary">TIMER</span>', unsafe_allow_html=True)
    st.title("순공 스톱워치")
    st.write("학습 몰입 시간을 측정합니다.")
    st.markdown('---')

    timer_placeholder = st.empty()
    
    def format_time(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("시작"):
            if not st.session_state.sw_running:
                st.session_state.sw_running = True
                st.session_state.sw_start_time = time.time() - st.session_state.sw_elapsed_time
    with col2:
        if st.button("일시정지"):
            if st.session_state.sw_running:
                st.session_state.sw_running = False
                st.session_state.sw_elapsed_time = time.time() - st.session_state.sw_start_time
    with col3:
        if st.button("리셋"):
            st.session_state.sw_running = False
            st.session_state.sw_start_time = 0
            st.session_state.sw_elapsed_time = 0

    if st.session_state.sw_running:
        st.session_state.sw_elapsed_time = time.time() - st.session_state.sw_start_time
        timer_placeholder.markdown(f"<h1 style='text-align: center; color: #2563EB;'>{format_time(st.session_state.sw_elapsed_time)}</h1>", unsafe_allow_html=True)
        time.sleep(0.1)
        st.rerun()
    else:
        timer_placeholder.markdown(f"<h1 style='text-align: center; color: #64748B;'>{format_time(st.session_state.sw_elapsed_time)}</h1>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("메인으로 돌아가기"):
        st.session_state.sw_running = False
        st.session_state.page = 'home'
        st.rerun()


# -----------------------------------------------------------------------------
# 4. 앱 라우터
# -----------------------------------------------------------------------------
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'survey':
    render_survey()
elif st.session_state.page == 'result':
    render_result()
elif st.session_state.page == 'stopwatch':
    render_stopwatch()
