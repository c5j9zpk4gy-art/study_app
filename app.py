import streamlit as st
import time
import math

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 모바일 앱 스타일 UI CSS (이모티콘 완전 제거 / 앱 느낌)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고등 수학 내신 솔루션", layout="centered")

st.markdown("""
    <style>
    /* 앱 전용 배경색 및 기본 폰트 설정 */
    .stApp {
        background-color: #F5F7FA;
    }
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", "Segoe UI", Roboto, sans-serif;
        color: #191F28;
    }

    /* 카드 UI (모던 네이티브 앱 스타일) */
    .app-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E8EB;
        margin-bottom: 16px;
    }

    /* 상단 미니 뱃지 */
    .pill-badge {
        display: inline-block;
        background-color: #E8F3FF;
        color: #1B64DA;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .pill-badge-gray {
        display: inline-block;
        background-color: #F2F4F6;
        color: #4E5968;
        font-size: 11px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
    }

    /* 깔끔한 타이틀 */
    .app-header {
        font-size: 22px;
        font-weight: 700;
        color: #191F28;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    
    .app-subtext {
        font-size: 14px;
        color: #8B95A1;
        margin-bottom: 0px;
    }

    /* 버튼 스타일 (토스/카카오뱅크 느낌) */
    .stButton>button {
        width: 100%;
        background-color: #2D65F2;
        color: #FFFFFF;
        border-radius: 14px;
        padding: 14px 20px;
        font-size: 15px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(45, 101, 242, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1A4FD8;
        color: #FFFFFF;
    }

    /* 스케줄 세부 라인 */
    .schedule-item {
        border-left: 2px solid #2D65F2;
        padding-left: 14px;
        margin-bottom: 16px;
    }
    .schedule-day {
        font-size: 12px;
        font-weight: 700;
        color: #2D65F2;
    }
    .schedule-title {
        font-size: 15px;
        font-weight: 700;
        color: #333D4B;
        margin: 2px 0;
    }
    .schedule-desc {
        font-size: 13px;
        color: #6B7684;
        margin: 0;
        line-height: 1.5;
    }

    /* 기존 스트림릿 헤더 지우기 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
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
# 2. 내신 교재 및 상세 소단원 커리큘럼 DB
# -----------------------------------------------------------------------------
PROBLEM_BOOKS_DB = {
    "수력충전": {"level": 1, "type": "연산기초", "pages": 220},
    "개념원리": {"level": 1, "type": "기본개념", "pages": 310},
    "개념쎈": {"level": 1, "type": "개념강화", "pages": 290},
    "라이트쎈": {"level": 1, "type": "쉬운유형", "pages": 250},
    "쎈 (SSEN)": {"level": 2, "type": "대표유형", "pages": 320},
    "개념원리 RPM": {"level": 2, "type": "표준유형", "pages": 270},
    "마플시너지": {"level": 2, "type": "다량유형", "pages": 460},
    "자이스토리": {"level": 2, "type": "내신기출", "pages": 420},
    "일품": {"level": 3, "type": "준심화", "pages": 210},
    "내신 고쟁이": {"level": 3, "type": "심화유형", "pages": 270},
    "1등급 만들기": {"level": 3, "type": "내신고득점", "pages": 200},
    "블랙라벨": {"level": 4, "type": "최심화", "pages": 170},
    "531 프로젝트 HYPER": {"level": 4, "type": "최심화", "pages": 120}
}

# 단원별 소단원 상세 분할 DB (세밀한 일차별 작성을 위함)
CURRICULUM_DETAILED_DB = {
    "공통수학1": [
        ("다항식의 연산", "다항식의 덧셈·뺄셈·곱셈, 덧셈 공식 및 전개 유형"),
        ("항등식과 미정계수법", "항등식의 성질, 수치대입법 및 계수비교법 유형"),
        ("나머지정리와 인수분해", "나머지정리, 조립제법, 인수분해 공식 변형"),
        ("복소수와 이차방정식", "복소수의 연산, 허수단위 i의 성질, 이차방정식의 판별식"),
        ("이차방정식과 이차함수", "이차함수의 그래프와 직교, 최댓값 및 최솟값 응용"),
        ("여러 가지 방정식 및 부등식", "삼·사차방정식, 연립방정식, 연립이차부등식"),
        ("행렬과 그 연산", "행렬의 정의, 행렬의 덧셈·뺄셈 및 실수배, 곱셈"),
        ("순열과 조합", "합의 법칙·곱의 법칙, 순열 nPr, 조합 nCr 계산 및 실전 응용")
    ],
    "공통수학2": [
        ("평면좌표와 두 점 사이의 거리", "두 점 사이의 거리 공식, 선분의 내분점과 외분점"),
        ("직선의 방정식", "직선의 방정식 구하기, 두 직선의 위치 관계, 점과 직선 사이의 거리"),
        ("원의 방정식", "원의 표준형·일반형, 원과 직선의 위치 관계, 접선의 방정식"),
        ("도형의 이동", "평행이동, 대칭이동(x축, y축, 원점, y=x) 및 활용"),
        ("집합의 뜻과 연산", "집합의 표현, 포함관계, 집합의 연산 법칙, 드모르간 법칙"),
        ("명제와 조건", "명제와 조건, 명제의 역과 대우, 충분조건과 필요조건, 절대부등식"),
        ("함수의 뜻과 합성함수", "함수의 정의, 일대일대응, 합성함수의 성질과 역함수 구하기"),
        ("유리함수와 무리함수", "유리식·무리식 연산, 유리함수와 무리함수의 그래프 해석")
    ],
    "대수": [
        ("지수와 로그", "거듭제곱근, 지수법칙 확장, 로그의 뜻과 성질"),
        ("지수함수와 로그함수", "지수·로그함수의 그래프, 평행이동, 방부등식 응용"),
        ("삼각함수의 뜻과 그래프", "호도법, 삼각함수의 정의, 주기와 최대·최소 해석"),
        ("삼각함수의 활용", "사인법칙, 코사인법칙, 삼각형의 넓이 구하기"),
        ("등차수열과 등비수열", "등차·등비수열의 일반항 및 합의 공식 구조 분석"),
        ("수열의 합과 귀납법", "시그마(∑)의 성질, 여러 가지 수열의 합, 수학적 귀납법")
    ],
    "미적분I": [
        ("수열의 극한과 급수", "수열의 극한값 계산, 등비수열의 극한, 무한급수의 수렴과 발산"),
        ("여러 가지 함수의 미분", "지수·로그·삼각함수의 극한과 미분법"),
        ("여러 가지 미분법", "몫의 미분법, 합성함수·음함수·매개변수 미분법"),
        ("도함수의 활용", "접선의 방정식, 극대·극소, 함수의 그래프 개형, 방정식과 부등식"),
        ("여러 가지 적분법", "치환적분법, 부분적분법, 삼각함수 및 지수함수 적분"),
        ("정적분의 활용", "정적분으로 정의된 함수, 곡선 사이의 넓이, 입체도형의 부피")
    ],
    "확률과 통계": [
        ("여러 가지 순열과 중복조합", "원순열, 중복순열, 같은 것이 있는 순열, 중복조합 nHr"),
        ("이항정리", "이항정리의 전개식, 이항계수의 성질 및 성질 응용"),
        ("확률의 뜻과 조건부확률", "확률의 기본 성질, 조건부확률, 사건의 독립과 종속"),
        ("확률변수와 확률분포", "이산확률변수, 기댓값과 표준편차, 이항분포"),
        ("연속확률변수와 정규분포", "확률밀도함수, 정규분포의 표준화, 정규분포 응용"),
        ("통계적 추정", "모집단과 표본, 표본평균의 분포, 모평균의 신뢰구간 추정")
    ],
    "미적분II": [
        ("지수·로그·삼각함수의 미분", "극한 계산의 부정형 처리, 덧셈정리 및 삼각함수 미분"),
        ("도함수의 활용 및 변곡점", "이계도함수, 변곡점, 오목과 볼록, 그래프의 정밀 스케치"),
        ("여러 가지 정적분", "치환적분과 부분적분을 이용한 정적분 계산"),
        ("정적분의 활용 (넓이·부피·속도)", "평면상의 넓이, 입체 부피, 점이 움직인 거리")
    ]
}


# -----------------------------------------------------------------------------
# 3. 뷰 함수 정의
# -----------------------------------------------------------------------------

def render_home():
    st.markdown("""
        <div class="app-card">
            <div class="pill-badge">ACADEMIC SOLUTION</div>
            <div class="app-header">고등 수학 내신 플래너</div>
            <div class="app-subtext">학군지 수준 분석 및 소단원별 초밀착 스케줄링</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("내신 진단 시작", use_container_width=True):
            st.session_state.page = 'survey'
            st.rerun()
    with col2:
        if st.button("순공 타이머", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()


def render_survey():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 1</div>
            <div class="app-header">학습 상태 입력</div>
            <div class="app-subtext">정확한 분석을 위해 세부 정보를 설정해 주세요.</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("precision_survey_form"):
        # 1. 과목 및 범위
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">과목 및 범위</div>', unsafe_allow_html=True)
        subject = st.selectbox("진단 과목", list(CURRICULUM_DETAILED_DB.keys()))
        exam_type = st.radio(
            "시험 범위 선택",
            ["중간고사 (전반부 범위)", "기말고사 (후반부 범위)", "전범위"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. 학생 수 및 석차 (에러 방지 방어 코드 적용)
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">석차 정보</div>', unsafe_allow_html=True)
        
        total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=800, value=200, step=1)
        
        # 석차가 전체 학생 수를 초과해서 에러가 발생하는 현상 완벽 방지
        current_rank_val = min(71, int(total_students))
        student_rank = st.number_input(
            "현재 수학 전교 석차 (등)", 
            min_value=1, 
            max_value=int(total_students), 
            value=current_rank_val, 
            step=1
        )
            
        target_grade = st.selectbox("목표 내신 등급 (5등급제)", [1, 2, 3, 4, 5], index=0)
        days = st.number_input("시험 대비 남아있는 기간 (일)", min_value=7, max_value=90, value=30, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. 학군지 수준
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">학교 출제 난이도</div>', unsafe_allow_html=True)
        region_level = st.radio(
            "학군지 및 시험 난이도 선택",
            [
                "Level 4 [최상위 학군지]: 강남, 대치, 서초, 목동, 중계, 분당\n- 모의고사 킬러 변형 출제 / 서술형 엄격 / 타임어택 극심",
                "Level 3 [주요 거점 학군지]: 천안, 청주, 전주, 창원, 수성, 해운대\n- 시중 대표유형서 이상 출제 / 준심화 3~5문항으로 변별력 확보",
                "Level 2 [일반계 고교]: 전국 일반계 고등학교 평균\n- 교과서 및 시중 대표 유형서(RPM/쎈) 충실 학습 시 상위권 진입 가능",
                "Level 1 [기본 개념 중심]: 기초 학력 보장 출제 학교\n- 연산 및 기본 개념 위주 출제 / 실수 방지가 최우선"
            ],
            index=1
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. 약점 분석
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">약점 및 학습 패턴</div>', unsafe_allow_html=True)
        weak_point = st.selectbox(
            "가장 흔한 감점 요인",
            [
                "개념 이해 부족 (공식 적용이 서툴고 원리를 잘 모름)",
                "유형 연습 부족 (개념은 아는데 문제를 보면 막힘)",
                "시간 부족 (시험 시간이 항상 모자람)",
                "고난도 킬러 문항 막힘 (상위권 변형 문제 해결력 부족)",
                "계산 실수 및 서술형 감점 (알면서도 과정에서 깎임)"
            ]
        )
        essay_needed = st.checkbox("서술형 풀이 집중 훈련 필요", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("맞춤 플랜 및 스케줄 생성")
        
        if submitted:
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

    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">REPORT</div>
            <div class="app-header">내신 맞춤 솔루션</div>
            <div class="app-subtext">진단 결과와 일차별 초밀착 스케줄입니다.</div>
        </div>
    """, unsafe_allow_html=True)

    # 1. 진단 서머리 카드
    st.markdown(f"""
        <div class="app-card">
            <div class="pill-badge-gray">{ans['subject']} · {ans['exam_type'].split(' ')[0]}</div>
            <div style="font-size: 18px; font-weight: 700; margin-top: 4px;">
                현재 전교 {ans['student_rank']}위 <span style="color: #8B95A1; font-weight: 400;">/ {ans['total_students']}명 (상위 {ans['pct']}%)</span>
            </div>
            <div style="font-size: 14px; color: #4E5968; margin-top: 6px;">
                현재 내신 <b>{ans['calc_grade']}등급</b> ➔ 목표 <b>{ans['target_grade']}등급</b> ({ans['days']}일 남음)
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 교재 추천 매칭
    reg_text = ans['region_level']
    weak = ans['weak_point']
    
    if "Level 4" in reg_text:
        rec_books = ["마플시너지", "내신 고쟁이", "블랙라벨"]
    elif "Level 3" in reg_text:
        if "개념" in weak:
            rec_books = ["개념원리 RPM", "쎈 (SSEN)", "일품"]
        else:
            rec_books = ["쎈 (SSEN)", "일품", "내신 고쟁이"]
    elif "Level 2" in reg_text:
        rec_books = ["개념원리", "쎈 (SSEN)", "1등급 만들기"]
    else:
        rec_books = ["수력충전", "개념원리", "라이트쎈"]

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">RECOMMENDED BOOKS</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header" style="font-size: 16px;">추천 교재 라인업</div>', unsafe_allow_html=True)
    st.write("")
    for idx, b in enumerate(rec_books, 1):
        info = PROBLEM_BOOKS_DB.get(b, {"type": "유형서", "pages": 200})
        st.markdown(f"**{idx}. {b}** ` {info['type']} ` (약 {info['pages']}p)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 소단원 세부 일차별 초밀착 스케줄
    st.markdown("""
        <div style="margin-top: 24px; margin-bottom: 12px;">
            <div class="app-header" style="font-size: 18px;">초밀착 일차별 학습 스케줄</div>
            <div class="app-subtext">단원 내 소단원별로 세밀하게 쪼갠 일일 실행 계획입니다.</div>
        </div>
    """, unsafe_allow_html=True)

    full_units = CURRICULUM_DETAILED_DB.get(ans['subject'], [("전체 단원", "개념 및 유형 학습")])
    
    # 중간/기말 범위 추출
    total_len = len(full_units)
    half_len = math.ceil(total_len / 2)
    
    if "중간고사" in ans['exam_type']:
        target_units = full_units[:half_len]
    elif "기말고사" in ans['exam_type']:
        target_units = full_units[half_len:]
    else:
        target_units = full_units

    # 일수 계산 및 세부 스케줄 생성 (2~3일 단위로 세분화)
    num_sub_units = len(target_units)
    total_days = ans['days']
    
    # 각 소단원당 배정할 일수
    days_per_subunit = max(2, total_days // num_sub_units)
    
    current_day = 1
    
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    for idx, (sub_title, sub_desc) in enumerate(target_units):
        start_d = current_day
        end_d = min(current_day + days_per_subunit - 1, total_days)
        if idx == num_sub_units - 1:
            end_d = total_days  # 마지막 단원에 남은 기간 합산
            
        st.markdown(f"""
            <div class="schedule-item">
                <div class="schedule-day">{start_d}일차 ~ {end_d}일차</div>
                <div class="schedule-title">{idx+1}. {sub_title}</div>
                <div class="schedule-desc">
                    • <b>핵심 개념:</b> {sub_desc}<br>
                    • <b>실행 과제:</b> {rec_books[0]} 개념/대표유형 풀이 ➔ {rec_books[1]} 고난도 문항 & 틀린 문제 오답 정리
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        current_day = end_d + 1
        if current_day > total_days:
            break
            
    # 마무리 총복습 스케줄 추가
    st.markdown(f"""
        <div class="schedule-item" style="border-left-color: #10B981;">
            <div class="schedule-day" style="color: #10B981;">직전 모의고사 & 오답 완성</div>
            <div class="schedule-title">전 단원 총복습 및 서술형 대비</div>
            <div class="schedule-desc">
                • {rec_books[-1]} 킬러 문항 및 누적 오답노트 2회독<br>
                • 학교 기출 족보 서술형 조건 누락 및 계산 실수 최종 점검
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


def render_stopwatch():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">TIMER</div>
            <div class="app-header">순공 타이머</div>
            <div class="app-subtext">오늘의 순수 학습 시간을 측정하세요.</div>
        </div>
    """, unsafe_allow_html=True)

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
        timer_placeholder.markdown(f"<h1 style='text-align: center; color: #2D65F2; font-size: 40px; margin: 20px 0;'>{format_time(st.session_state.sw_elapsed_time)}</h1>", unsafe_allow_html=True)
        time.sleep(0.1)
        st.rerun()
    else:
        timer_placeholder.markdown(f"<h1 style='text-align: center; color: #8B95A1; font-size: 40px; margin: 20px 0;'>{format_time(st.session_state.sw_elapsed_time)}</h1>", unsafe_allow_html=True)

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
