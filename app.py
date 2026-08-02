import streamlit as st
import time
import math

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 모바일 커스텀 CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고등 수학 내신 솔루션", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .app-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
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
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    .report-box {
        background-color: #F1F5F9;
        border-left: 4px solid #2563EB;
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 15px;
        line-height: 1.6;
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
# 2. 내신 교재 및 단원 DB
# -----------------------------------------------------------------------------
PROBLEM_BOOKS_DB = {
    # 연산 / 개념
    "수력충전": {"level": 1, "type": "연산기초", "pages": 220},
    "개념원리": {"level": 1, "type": "기본개념", "pages": 310},
    "개념쎈": {"level": 1, "type": "개념강화", "pages": 290},
    "라이트쎈": {"level": 1, "type": "쉬운유형", "pages": 250},
    "수학의 바이블": {"level": 1, "type": "기본개념", "pages": 340},
    "올림포스 기본": {"level": 1, "type": "학교부교재", "pages": 170},
    "베이직쎈": {"level": 1, "type": "기초유형", "pages": 230},
    "풍성한 한샘": {"level": 1, "type": "개념서", "pages": 270},
    
    # 유형 / 내신기출
    "쎈 (SSEN)": {"level": 2, "type": "대표유형", "pages": 320},
    "개념원리 RPM": {"level": 2, "type": "표준유형", "pages": 270},
    "마플시너지": {"level": 2, "type": "다량유형", "pages": 460},
    "자이스토리": {"level": 2, "type": "내신기출", "pages": 420},
    "마더텅 내신기출": {"level": 2, "type": "내신기출", "pages": 410},
    "짱 중요한 유형": {"level": 2, "type": "핵심유형", "pages": 180},
    "우공비 Q+Q 표준": {"level": 2, "type": "표준유형", "pages": 250},
    "유형 해결의 법칙": {"level": 2, "type": "표준유형", "pages": 260},
    "올림포스 평가문항": {"level": 2, "type": "내신유형", "pages": 190},
    
    # 준심화
    "일품": {"level": 3, "type": "준심화", "pages": 210},
    "내신 고쟁이": {"level": 3, "type": "심화유형", "pages": 270},
    "1등급 만들기": {"level": 3, "type": "내신고득점", "pages": 200},
    "짱 어려운 유형": {"level": 3, "type": "준심화", "pages": 190},
    "절대등급": {"level": 3, "type": "준심화", "pages": 180},
    "일등급 수학": {"level": 3, "type": "준심화", "pages": 190},
    "우공비 Q+Q 발전": {"level": 3, "type": "준심화", "pages": 220},
    "EBS 올림포스 고난도": {"level": 3, "type": "고난도부교재", "pages": 150},
    
    # 최심화 / 킬러
    "블랙라벨": {"level": 4, "type": "최심화", "pages": 170},
    "531 프로젝트 HYPER": {"level": 4, "type": "최심화", "pages": 120},
    "최강 TOT": {"level": 4, "type": "최심화", "pages": 160},
    "하이엔드": {"level": 4, "type": "최심화", "pages": 160},
    "수학의 신": {"level": 4, "type": "최심화", "pages": 180}
}

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
# 3. 뷰 함수 정의
# -----------------------------------------------------------------------------

def render_home():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.title("고등 수학 내신 솔루션")
    st.write("2025 개정 내신 5등급제 대비 · 정밀 학군지 가중치 및 시험 범위 분석")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("정밀 학습 진단 시작", use_container_width=True):
            st.session_state.page = 'survey'
            st.rerun()
    with col2:
        if st.button("순공 스톱워치 실행", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()


def render_survey():
    st.markdown('<span class="badge-primary">STEP 1</span> <b>상세 학습 정밀 진단</b>', unsafe_allow_html=True)
    st.write("학생 개개인의 현재 상태와 학군지 환경을 미세 분석하여 최적의 커리큘럼을 생성합니다.")
    st.write("")
    
    # 폼 생성
    with st.form("precision_survey_form"):
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("1. 과목 및 시험 범위 선택")
        subject = st.selectbox("진단할 수학 과목", list(CURRICULUM_DB.keys()))
        exam_type = st.radio(
            "대비할 시험 범위",
            ["중간고사 (과목 전반부 50% 범위)", "기말고사 (과목 후반부 50% 범위)", "전범위 (한 번에 전체 범위)"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("2. 성적 및 석차 정보 입력")
        c1, c2 = st.columns(2)
        with c1:
            total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=800, value=200, step=1)
        with c2:
            student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=total_students, value=71, step=1)
            
        target_grade = st.selectbox("목표 내신 등급 (5등급제 기준)", [1, 2, 3, 4, 5], index=0)
        days = st.number_input("시험 대비 남아있는 목표 기간 (일)", min_value=7, max_value=120, value=30, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("3. 학군지 수준 및 학교 시험 출제 난이도")
        region_level = st.radio(
            "학교의 내신 출제 난이도 및 학군지 선택",
            [
                "Level 4 [최상위 학군지]: 강남, 대치, 서초, 목동, 중계, 분당 등\n→ 모의고사 4점 킬러 변형 문항이 다수 출제되며, 서술형 감점이 매우 엄격하고 시간이 극도로 부족한 시험 스타일.",
                "Level 3 [주요 도시 거점 학군지]: 천안, 청주, 전주, 창원, 대구 수성, 부산 해운대 등\n→ 대표 유형서(쎈/마플)를 뛰어넘어 교육청 기출 고난도 및 준심화서(일품/고쟁이) 수준의 변형 문제가 3~5문항 변별력으로 출제되는 스타일.",
                "Level 2 [일반 평이 학군지]: 전국 일반계 고등학교 평균 수준\n→ 교과서 및 시중 대표 유형서(RPM/쎈)를 충실히 학습하면 상위권 진입이 가능하고, 변별력 문항도 시중 기출 수준에서 출제되는 스타일.",
                "Level 1 [기본 개념 중심 학교]: 기초 학력 보장 위주 출제 학교\n→ 연산 및 기본 개념, 교과서 예제/유형 위주로 출제되어 실수 줄이기와 확실한 개념 완성이 핵심인 시험 스타일."
            ],
            index=1
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("4. 약점 세부 진단 및 학습 습관")
        weak_point = st.selectbox(
            "가장 감점이 많이 발생하는 주원인",
            [
                "개념 이해 부족 (공식 적용이 서툴고 원리를 잘 모름)",
                "유형 연습 부족 (개념은 아는데 문제를 보면 어떻게 풀지 모름)",
                "시간 부족 및 타임어택 (시험 시간이 항상 모자라 뒤쪽 문제 못  get)",
                "고난도 킬러 문항 막힘 (상위권 문항이나 변형 문제에서 막힘)",
                "계산 실수 및 서술형 조건 누락 (알면서도 풀이 과정이나 계산에서 깎임)"
            ]
        )
        
        study_hours = st.slider("주당 순수 수학 공부 투자 시간 (시간)", min_value=2, max_value=30, value=12)
        essay_needed = st.checkbox("우리 학교는 서술형 감점 요소가 매우 크다 (서술형 집중 풀이 훈련 필요)", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("🔥 정밀 분석 리포트 & 맞춤 커리큘럼 생성")
        
        if submitted:
            # 석차 기반 정확한 백분위 계산
            pct = (student_rank / total_students) * 100
            
            # 2025 개정 5등급제 비율: 1등급(10%), 2등급(34%), 3등급(66%), 4등급(90%), 5등급(100%)
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
                
            # 세션에 정확히 데이터 저장
            st.session_state.answers = {
                "subject": subject,
                "exam_type": exam_type,
                "total_students": total_students,
                "student_rank": student_rank,
                "pct": round(pct, 2),
                "calc_grade": calc_grade,
                "target_grade": target_grade,
                "days": days,
                "region_level": region_level,
                "weak_point": weak_point,
                "study_hours": study_hours,
                "essay_needed": essay_needed
            }
            st.session_state.page = 'result'
            st.rerun()

    if st.button("메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


def render_result():
    ans = st.session_state.answers
    if not ans:
        st.session_state.page = 'survey'
        st.rerun()
        return

    st.markdown('<span class="badge-secondary">DETAILED SOLUTION REPORT</span>', unsafe_allow_html=True)
    st.title("내신 맞춤 솔루션 정밀 리포트")
    st.markdown('---')

    # 1. 입력 상태 정확한 출력
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("📌 진단 대상 및 성적 분석")
    st.write(f"• **선택 과목 & 범위:** {ans['subject']} ({ans['exam_type'].split(' ')[0]})")
    st.write(f"• **전교 석차:** **전교 {ans['student_rank']}위** / {ans['total_students']}명 (상위 **{ans['pct']}%**)")
    st.write(f"• **내신 등급 진단:** 현재 내신 **{ans['calc_grade']}등급** ➔ 목표 **{ans['target_grade']}등급**")
    st.write(f"• **대비 기간 & 주당 공부량:** {ans['days']}일 남음 (주당 {ans['study_hours']}시간 수학 투자)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. 다양성을 위한 교재 추천 매칭 세부 로직
    reg_text = ans['region_level']
    weak = ans['weak_point']
    
    # 학군지 가중치 계산
    if "Level 4" in reg_text:
        reg_score = 4
    elif "Level 3" in reg_text:
        reg_score = 3
    elif "Level 2" in reg_text:
        reg_score = 2
    else:
        reg_score = 1

    # 조건 조합별 다채로운 3권 교재 라인업 생성
    if reg_score == 4: # 최상위 학군지
        if "개념" in weak or ans['calc_grade'] >= 3:
            rec_books = ["개념원리 RPM", "내신 고쟁이", "블랙라벨"]
        elif "타임어택" in weak or "계산" in weak:
            rec_books = ["마플시너지", "일품", "531 프로젝트 HYPER"]
        else:
            rec_books = ["쎈 (SSEN)", "내신 고쟁이", "블랙라벨"]
            
    elif reg_score == 3: # 주요 거점 학군지
        if "개념" in weak:
            rec_books = ["개념쎈", "쎈 (SSEN)", "1등급 만들기"]
        elif "고난도" in weak or ans['target_grade'] == 1:
            rec_books = ["마플시너지", "내신 고쟁이", "최강 TOT"]
        elif "타임어택" in weak:
            rec_books = ["자이스토리", "짱 어려운 유형", "일품"]
        else:
            rec_books = ["쎈 (SSEN)", "일품", "내신 고쟁이"]
            
    elif reg_score == 2: # 일반 학군지
        if "개념" in weak:
            rec_books = ["개념원리", "라이트쎈", "쎈 (SSEN)"]
        elif "고난도" in weak or ans['target_grade'] <= 2:
            rec_books = ["개념원리 RPM", "쎈 (SSEN)", "1등급 만들기"]
        else:
            rec_books = ["라이트쎈", "쎈 (SSEN)", "자이스토리"]
            
    else: # 기본 개념 중심 학교
        if "개념" in weak:
            rec_books = ["수력충전", "개념원리", "라이트쎈"]
        else:
            rec_books = ["개념원리", "라이트쎈", "짱 중요한 유형"]

    # 하루 권장 분량 계산
    total_pages = sum([PROBLEM_BOOKS_DB.get(b, {"pages": 220})["pages"] for b in rec_books])
    daily_page = math.ceil(total_pages / ans['days'])
    daily_time_min = math.ceil(daily_page * 4.8)

    # 교재 라인업 출력
    st.markdown('### 📚 1:1 맞춤 추천 교재 라인업')
    for idx, b in enumerate(rec_books, 1):
        info = PROBLEM_BOOKS_DB.get(b, {"type": "내신유형", "pages": 200})
        st.markdown(f"**{idx}. {b}** `<span class='badge-secondary'>{info['type']}</span>` (전체 약 {info['pages']}p)", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('### ⏱️ 일일 권장 학습 목표')
    st.info(f"선택하신 {ans['days']}일 동안 하루 **약 {daily_page} Page** 진도를 권장하며, 하루 **최소 {daily_time_min}분 이상** 집중 수학 공부가 필요합니다.")

    # 3. 상세 진단 종합 장문 정성 리포트
    st.markdown("---")
    st.markdown("### 📝 약점 극복 & 내신 등급 수직상승 장문 솔루션")
    
    st.markdown(f"""
    <div class="report-box">
        <h4>🔍 1. 현재 학군지 및 전교 석차({ans['student_rank']}위/상위 {ans['pct']}%) 상세 종합 진단</h4>
        <p>현재 학생의 위치는 상위 <b>{ans['pct']}%</b> 영역에 위치해 있습니다. 선택하신 학교 난이도(<b>{reg_text.split(':')[0]}</b>) 특성상 단순 문제 풀이 양치기만으로는 목표 등급({ans['target_grade']}등급) 진입 시 고난도 변형 문제에서 감점될 위험이 높습니다.</p>
        <p>특히 <b>'{weak}'</b>을 주요 약점으로 꼽으셨는데, 이는 문제 풀이 시 조건 해석 단계에서 시간을 많이 소비하거나, 개념을 실전 유형으로 연결하는 다리 역할(Bridge)이 부족하기 때문에 발생하는 전형적인 현상입니다.</p>
    </div>
    
    <div class="report-box">
        <h4>🎯 2. 단계별 맞춤 전략 솔루션</h4>
        <ul>
            <li><b>STEP 1 - [{rec_books[0]} 기반 빈틈 메우기]:</b> 1회독 시 맞힌 문제도 풀이 과정의 정확성을 점검하세요. 특히 서술형 감점을 방지하기 위해 풀이 과정을 생략하지 않고 정석대로 적는 습관이 필요합니다.</li>
            <li><b>STEP 2 - [{rec_books[1]} 실전 유형 및 타임어택 훈련]:</b> 시험 시간 부족 문제를 해결하기 위해 한 문제당 2.5분 제한 시간을 두고 푸는 연습을 하세요. 3분이 넘어가도록 아이디어가 안 떠오르면 별표를 치고 넘어가는 '스킵 연섭'이 필수적입니다.</li>
            <li><b>STEP 3 - [{rec_books[2]} 심화 킬러 및 변형 대비]:</b> 목표 등급을 가르는 상위 10% 변별력 문항입니다. 답지를 바로 보지 말고 최소 10분 이상 고민한 뒤, 조건 1개를 놓친 이유를 오답노트에 적으세요.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if ans['essay_needed']:
        st.warning("✍️ **서술형 감점 방지 꿀팁:** 계산 과정을 생략하는 암산 습관을 버리고, 등호(=) 연결과 조건 범위(예: x > 0)를 정확히 명시하는 연습을 매일 2문항씩 제출용으로 작성해 보세요.")

    # 4. 범위를 반영한 시험 범위 분할 커리큘럼 캘린더 Engine
    st.markdown("---")
    full_units = CURRICULUM_DB.get(ans['subject'], ["전범위 기본 개념 및 유형 학습"])
    
    # 범위 나누기 (중간고사: 앞쪽 절반 / 기말고사: 뒤쪽 절반)
    total_u_count = len(full_units)
    half_idx = math.ceil(total_u_count / 2)
    
    if "중간고사" in ans['exam_type']:
        target_units = full_units[:half_idx]
        range_title = "중간고사 (전반부 범위)"
    elif "기말고사" in ans['exam_type']:
        target_units = full_units[half_idx:]
        range_title = "기말고사 (후반부 범위)"
    else:
        target_units = full_units
        range_title = "전범위"

    st.markdown(f"### 🗓️ [{ans['subject']} - {range_title}] {ans['days']}일 달성 스케줄표")
    
    num_units = len(target_units)
    days_per_unit = max(1, ans['days'] // num_units)

    for i, unit in enumerate(target_units):
        start_day = i * days_per_unit + 1
        end_day = (i + 1) * days_per_unit if i < num_units - 1 else ans['days']
        
        st.markdown(f"""
        <div class="app-card">
            <span class="badge-primary">{start_day}일차 ~ {end_day}일차</span>
            <h4 style="margin-top: 8px;">{unit}</h4>
            <p style="color: #334155; font-size: 14px; margin-bottom: 4px;">
            <b>• 1단계 (개념/유형):</b> {rec_books[0]} 로 해당 단원 핵심 공식 및 대표 유형 Master
            </p>
            <p style="color: #334155; font-size: 14px; margin-bottom: 4px;">
            <b>• 2단계 (심화/기출):</b> {rec_books[1]} 및 {rec_books[2]} 고난도 문항 실전 풀이 및 오답 정독
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


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
# 4. 앱 라우팅
# -----------------------------------------------------------------------------
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'survey':
    render_survey()
elif st.session_state.page == 'result':
    render_result()
elif st.session_state.page == 'stopwatch':
    render_stopwatch()
