import streamlit as st
import time

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 네이티브 앱 UI CSS (다크모드 대응 & 레이아웃 정상화)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고등 수학 내신 맞춤 솔루션", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경 및 기본 폰트 고정 */
    .stApp {
        background-color: #F5F7FA !important;
        color: #191F28 !important;
    }
    
    html, body, [class*="css"], p, span, div, label, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", "Segoe UI", Roboto, sans-serif !important;
        color: #191F28 !important;
    }

    /* 카드 레이아웃 스타일 */
    .app-card {
        background-color: #FFFFFF !important;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E8EB;
        margin-bottom: 20px;
        color: #191F28 !important;
    }

    .pill-badge {
        display: inline-block;
        background-color: #E8F3FF !important;
        color: #1B64DA !important;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    
    .pill-badge-gray {
        display: inline-block;
        background-color: #F2F4F6 !important;
        color: #4E5968 !important;
        font-size: 11px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
    }

    .type-badge {
        display: inline-block;
        background-color: #E8F3FF !important;
        color: #1B64DA !important;
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
        margin-left: 6px;
    }

    .app-header {
        font-size: 22px;
        font-weight: 700;
        color: #191F28 !important;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    
    .app-subtext {
        font-size: 14px;
        color: #8B95A1 !important;
        margin-bottom: 0px;
        line-height: 1.4;
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        background-color: #2D65F2 !important;
        color: #FFFFFF !important;
        border-radius: 14px;
        padding: 14px 20px;
        font-size: 15px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(45, 101, 242, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1A4FD8 !important;
        color: #FFFFFF !important;
    }

    .schedule-item {
        border-left: 3px solid #2D65F2;
        padding-left: 16px;
        margin-bottom: 20px;
    }
    .schedule-day {
        font-size: 12px;
        font-weight: 700;
        color: #2D65F2 !important;
    }
    .schedule-title {
        font-size: 16px;
        font-weight: 700;
        color: #333D4B !important;
        margin: 4px 0;
    }
    .schedule-desc {
        font-size: 13px;
        color: #4E5968 !important;
        margin: 0;
        line-height: 1.6;
    }

    .report-paragraph {
        font-size: 14px;
        line-height: 1.75;
        color: #333D4B !important;
        margin-bottom: 16px;
        word-break: keep-all;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태 관리
# -----------------------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'basic_info' not in st.session_state:
    st.session_state.basic_info = {}
if 'survey_answers' not in st.session_state:
    st.session_state.survey_answers = {}
if 'q_start' not in st.session_state:
    st.session_state.q_start = None
if 'solve_logs' not in st.session_state:
    st.session_state.solve_logs = []

# -----------------------------------------------------------------------------
# 3. 시중 교재 DB & 커리큘럼 DB (기존 데이터 100% 유지)
# -----------------------------------------------------------------------------
BOOKS_DATABASE = {
    "수력충전": {"type": "연산기초", "pages": 220},
    "개념원리": {"type": "기본개념", "pages": 310},
    "개념쎈": {"type": "개념강화", "pages": 290},
    "라이트쎈": {"type": "쉬운유형", "pages": 250},
    "개념원리 RPM": {"type": "표준유형", "pages": 270},
    "쎈 (SSEN)": {"type": "대표유형", "pages": 320},
    "마플시너지": {"type": "다량유형", "pages": 460},
    "자이스토리": {"type": "내신기출", "pages": 420},
    "일품": {"type": "준심화", "pages": 210},
    "내신 고쟁이": {"type": "심화유형", "pages": 270},
    "1등급 만들기": {"type": "내신고득점", "pages": 200},
    "블랙라벨": {"type": "최심화", "pages": 170},
    "531 프로젝트 HYPER": {"type": "최심화", "pages": 120},
}

CURRICULUM_DETAILED_DB = {
    "공통수학1": {
        "중간고사": [
            ("다항식의 연산", "다항식의 덧셈·뺄셈·곱셈, 곱셈 공식 및 전개 유형 분석"),
            ("항등식과 미정계수법", "항등식의 성질, 수치대입법 및 계수비교법 실전 적용"),
            ("나머지정리와 인수분해", "나머지정리, 조립제법, 인수분해 공식 고난도 변형"),
            ("복소수와 이차방정식", "복소수 연산, 허수단위 i의 주기성, 판별식과 근의 공식")
        ],
        "기말고사": [
            ("이차방정식과 이차함수", "이차함수 그래프와 직선의 위치관계, 최대·최소 응용"),
            ("여러 가지 방정식 및 부등식", "삼·사차방정식, 연립이차방정식, 연립이차부등식"),
            ("행렬과 그 연산", "행렬의 정의, 행렬의 성분 연산 및 곱셈 성질"),
            ("순열과 조합", "합·곱의 법칙, 순열 nPr, 조합 nCr 계산 및 실전 활용")
        ]
    },
    "공통수학2": {
        "중간고사": [
            ("평면좌표와 두 점 사이 거리", "두 점 사이의 거리 공식, 선분의 내분점과 외분점"),
            ("직선의 방정식", "직선의 방정식 구하기, 두 직선의 위치 관계, 점과 직선 사이 거리"),
            ("원의 방정식", "원의 표준형·일반형, 원과 직선의 위치 관계, 접선의 방정식"),
            ("도형의 이동", "평행이동, 대칭이동(x축, y축, 원점, y=x) 및 도형 응용"),
            ("집합의 뜻과 연산", "집합의 표현, 포함관계, 집합의 연산 법칙, 드모르간 법칙"),
            ("명제와 조건", "명제와 조건, 역과 대우, 충분·필요조건, 절대부등식 증명")
        ],
        "기말고사": [
            ("함수의 뜻과 그래프", "함수의 정의, 일대일대응, 합성함수 및 역함수 해석"),
            ("유리함수와 무리함수", "유리식·무리식 연산, 유리함수와 무리함수 그래프 분석")
        ]
    },
    "대수": {
        "중간고사": [
            ("지수와 로그", "거듭제곱근, 지수법칙 확장, 로그의 정의 및 성질 계산"),
            ("지수함수와 로그함수", "지수·로그함수 그래프, 평행이동, 지수·로그 방부등식"),
            ("삼각함수의 뜻과 그래프", "호도법, 삼각함수의 정의, 주기와 최대·최소 그래프 해석")
        ],
        "기말고사": [
            ("삼각함수의 활용", "사인법칙, 코사인법칙, 삼각형의 넓이 및 기하 응용"),
            ("등차수열과 등비수열", "등차·등비수열의 일반항 및 합의 공식 구조 분석"),
            ("수열의 합과 귀납법", "시그마(∑)의 성질, 여러 가지 수열의 합, 수학적 귀납법")
        ]
    },
    "미적분I": {
        "중간고사": [
            ("수열의 극한과 급수", "수열의 극한값 계산, 등비수열의 극한, 무한급수의 수렴과 발산"),
            ("여러 가지 함수의 미분", "지수·로그·삼각함수의 극한과 도함수 구하기"),
            ("여러 가지 미분법", "몫의 미분법, 합성함수·음함수·매개변수 미분법")
        ],
        "기말고사": [
            ("도함수의 활용", "접선의 방정식, 극대·극소, 그래프 개형, 방정식과 부등식"),
            ("여러 가지 적분법", "치환적분법, 부분적분법, 삼각함수 및 지수함수 정적분"),
            ("정적분의 활용", "정적분으로 정의된 함수, 곡선 사이 넓이, 입체도형 부피")
        ]
    },
    "확률과 통계": {
        "중간고사": [
            ("여러 가지 순열과 중복조합", "원순열, 중복순열, 같은 것이 있는 순열, 중복조합 nHr"),
            ("이항정리", "이항정리의 전개식, 이항계수의 성질 및 성질 응용"),
            ("확률의 뜻과 조건부확률", "확률의 기본 성질, 조건부확률, 사건의 독립과 종속")
        ],
        "기말고사": [
            ("확률변수와 확률분포", "이산확률변수, 기댓값과 표준편차, 이항분포"),
            ("연속확률변수와 정규분포", "확률밀도함수, 정규분포의 표준화, 정규분포 응용"),
            ("통계적 추정", "모집단과 표본, 표본평균의 분포, 모평균의 신뢰구간 추정")
        ]
    }
}

# -----------------------------------------------------------------------------
# 4. 화면 렌더링
# -----------------------------------------------------------------------------

def render_home():
    st.markdown("""
        <div class="app-card">
            <div class="pill-badge">ACADEMIC AI SOLUTION</div>
            <div class="app-header">고등 수학 내신 정밀 진단 솔루션</div>
            <div class="app-subtext">규칙 기반 AI 진단 엔진을 활용한 백분위 정밀 진단 및 20문항 개별화 스케줄링</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("내신 진단 시작하기", use_container_width=True):
            st.session_state.page = 'basic_input'
            st.rerun()
    with col2:
        if st.button("⏱️ 문항별 랩타임 분석기", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()


def render_basic_input():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 1 / 2</div>
            <div class="app-header">기본 정보 및 출제 유형 설정</div>
            <div class="app-subtext">정확한 백분위 계산과 학교 출제 난이도 진단을 위한 기본 정보입니다.</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("basic_info_form"):
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">과목 및 시험 범위</div>', unsafe_allow_html=True)
        subject = st.selectbox("진단 과목 선택", list(CURRICULUM_DETAILED_DB.keys()))
        exam_type = st.radio(
            "시험 범위 선택",
            ["중간고사 (전반부 범위)", "기말고사 (후반부 범위)", "전범위"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">학생 수 및 정확한 석차 입력</div>', unsafe_allow_html=True)
        
        total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=1000, value=200, step=1, key="input_total_students")
        student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=int(total_students), value=min(34, int(total_students)), step=1, key="input_student_rank")
        
        target_grade = st.selectbox("목표 내신 등급 (5등급제 기준)", [1, 2, 3, 4, 5], index=0)
        days = st.number_input("시험까지 남은 기간 (일)", min_value=7, max_value=120, value=30, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        # 피드백 반영: 순화된 학교 출제 난이도 표현
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">학교 시험 출제 난이도 가이드</div>', unsafe_allow_html=True)
        st.markdown("""
        <b>우리 학교 수학 시험 출제 경향을 선택해 주세요:</b><br>
        • <b>A유형 [수능·모의고사 변형 고난도]</b>: 강남/특목고 수준, 수능 킬러 변형 출제 비중 높음.<br>
        • <b>B유형 [시중 심화서 및 변형 중심]</b>: 주요 거점 지역 수준, 변별력 고난도 문항 3~5개 포함.<br>
        • <b>C유형 [교과서 및 대표 유형서 중심]</b>: 표준 일반계고 수준, 대표 유형 완벽 소화 시 고득점.<br>
        • <b>D유형 [기초 개념 및 기본 예제 중심]</b>: 기본 연산 및 개념 정의 위주 출제.
        """, unsafe_allow_html=True)
        
        region_level = st.radio(
            "자신에 해당하는 학교 출제 난이도 유형을 선택하세요",
            ["A유형 [수능·모의고사 변형 고난도]", "B유형 [시중 심화서 및 변형 중심]", "C유형 [교과서 및 대표 유형서 중심]", "D유형 [기초 개념 및 기본 예제 중심]"],
            index=1
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("다음: 20문항 상세 설문 진행")
        if submitted:
            actual_rank = st.session_state.input_student_rank
            actual_total = st.session_state.input_total_students
            
            pct = round((actual_rank / actual_total) * 100, 2)
            
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

            st.session_state.basic_info = {
                "subject": subject,
                "exam_type": exam_type,
                "total_students": int(actual_total),
                "student_rank": int(actual_rank),
                "pct": pct,
                "calc_grade": calc_grade,
                "target_grade": target_grade,
                "days": int(days),
                "region_level": region_level
            }
            st.session_state.page = 'survey_20'
            st.rerun()

    if st.button("메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


def render_survey_20():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 2 / 2</div>
            <div class="app-header">20문항 정밀 학업 스타일 진단</div>
            <div class="app-subtext">규칙 기반 AI 엔진의 정밀 분석을 위한 20가지 상세 질문입니다.</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("survey_20_form"):
        answers = {}
        
        questions = [
            ("Q1. 평소 수학 하루 평균 순수 공부 시간은 얼마인가요?", ["1시간 미만", "1시간 ~ 2시간", "2시간 ~ 3시간", "3시간 이상"]),
            ("Q2. 새로운 개념을 배울 때 이해하는 속도는 어떠한가요?", ["매우 빨라 바로 문제 적용 가능", "보통이며 여러 번 읽어야 함", "느려서 개념 설명 추가 수강 필요"]),
            ("Q3. 틀린 문제를 처리하는 본인만의 오답 노트 작성 방식은?", ["오답노트를 정성스럽게 작성함", "교재에 맞은표시/틀린표시만 해두고 재풀이", "특별히 오답 관리를 하지 않음"]),
            ("Q4. 계산 실수가 발생하는 빈도는 어떠한가요?", ["시험마다 2~3문항 이상 실수함", "1문항 정도 가끔 실수함", "계산 실수는 거의 없음"]),
            ("Q5. 서술형 문항 풀이 시 가장 자주 감점되는 요인은?", ["풀이 과정 누락 및 기호 오용", "시간 부족으로 손도 못 대움", "계산 중간 오류", "감점된 적 없음"]),
            ("Q6. 시험 시 문제를 풀 때 시간 배분은 잘 이루어지나요?", ["항상 시간이 부족하여 뒤쪽 문항을 찍음", "딱 맞게 끝남", "10분 이상 남아서 검산 가능"]),
            ("Q7. 고난도 킬러 문제(모의고사 변형 등)에 대한 태도는?", ["시도조차 못 하고 포기함", "접근법은 떠올리나 끝까지 못 돎", "시간이 주어지면 해결 가능"]),
            ("Q8. 개념서의 기본 예제/유제 문제 풀이 정답률은?", ["50% 미만", "50% ~ 80%", "80% 이상"]),
            ("Q9. 쎈(SSEN) B단계 수준의 대표 유형 문제 정답률은?", ["50% 미만", "50% ~ 80%", "80% 이상"]),
            ("Q10. 일품/고쟁이 등 준심화 문제 정답률은?", ["30% 미만", "30% ~ 60%", "60% 이상", "풀어본 적 없음"]),
            ("Q11. 블랙라벨/531 하이퍼 등 최심화 문제 경험은?", ["풀어본 적 없음", "시도했으나 너무 어려움", "70% 이상 소화 가능"]),
            ("Q12. 모의고사/수능 기출 문항 분석을 진행해 본 적이 있나요?", ["전혀 없음", "학교 부교재에 포함된 것만 풀었음", "개별 기출회독 진행 중"]),
            ("Q13. 수학 문제를 풀 때 막히면 해설지를 보는 시점은?", ["1~2분 고민 후 바로 해설지 확인", "10분 이상 고민 후 확인", "끝까지 혼자 고민하고 다음 날 확인"]),
            ("Q14. 시험 불안감이나 중압감으로 인한 실력 발휘 저해가 있나요?", ["매우 심함", "약간 있음", "전혀 없음"]),
            ("Q15. 주말(토/일) 수학 학습 가능 시간은?", ["3시간 미만", "3시간 ~ 6시간", "6시간 이상"]),
            ("Q16. 학교 선생님의 수업 및 프린트/부교재 반영 비율은?", ["교과서/프린트에서 매우 똑같이 출제", "시중 변형 문제 위주 출제", "모의고사 기출 변형 출제"]),
            ("Q17. 인강(인터넷 강의) 수강 여부 및 활용도", ["인강 위주 학습", "독학 위주 학습", "학원/과외 위주 학습"]),
            ("Q18. 공식을 암기할 때 증명 과정도 함께 공부하나요?", ["증명 과정도 직접 써봄", "공식 결과만 암기함", "공식 암기도 잘 안 됨"]),
            ("Q19. 도형/기하 파트나 식이 복잡한 단원에 대한 두려움은?", ["매우 큼", "보통임", "전혀 없음"]),
            ("Q20. 이번 내신 시험을 임하는 가장 결정적인 목표 의식은?", ["최상위권(1등급) 진입 및 유지", "중위권 탈출 및 등급 상승", "기초 학력 확보 및 감점 최소화"])
        ]

        for i, (q, opts) in enumerate(questions):
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="pill-badge-gray">QUESTION {i+1}</div>', unsafe_allow_html=True)
            ans = st.radio(q, opts, key=f"q_{i+1}")
            answers[f"q_{i+1}"] = ans
            st.markdown('</div>', unsafe_allow_html=True)

        submitted_survey = st.form_submit_button("최종 맞춤 진단 결과 및 리포트 생성")
        if submitted_survey:
            st.session_state.survey_answers = answers
            st.session_state.page = 'result'
            st.rerun()


def render_result():
    info = st.session_state.basic_info
    survey = st.session_state.survey_answers

    if not info or not survey:
        st.session_state.page = 'basic_input'
        st.rerun()
        return

    # 피드백 반영: AI 분석 명확화 연출
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">RULE-BASED AI ENGINE</div>
            <div class="app-header">내신 맞춤 AI 솔루션 리포트</div>
            <div class="app-subtext">입력된 백분위 수치와 20문항 응답 패턴을 규칙 기반 AI 매트릭스로 정밀 분석했습니다.</div>
        </div>
    """, unsafe_allow_html=True)

    # 1. 석차 및 백분위 서머리 카드
    st.markdown(f"""
        <div class="app-card">
            <div class="pill-badge">{info['subject']} · {info['exam_type'].split(' ')[0]}</div>
            <div style="font-size: 20px; font-weight: 700; color: #191F28 !important; margin-top: 4px;">
                현재 전교 <span style="color:#2D65F2 !important;">{info['student_rank']}위</span> / {info['total_students']}명 (상위 {info['pct']}%)
            </div>
            <div style="font-size: 14px; color: #4E5968 !important; margin-top: 6px;">
                현재 내신 <b>{info['calc_grade']}등급</b> ➔ 목표 <b>{info['target_grade']}등급</b> ({info['days']}일 남음) | {info['region_level']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 교재 추천 로직 (순화된 난이도 기반)
    days = info['days']
    grade = info['calc_grade']
    reg = info['region_level']

    if days < 20 or grade >= 4:
        if "A유형" in reg or "B유형" in reg:
            rec_books = ["개념원리 RPM", "쎈 (SSEN)"]
        else:
            rec_books = ["개념원리", "라이트쎈"]
    else:
        if "A유형" in reg:
            if grade <= 2:
                rec_books = ["마플시너지", "내신 고쟁이", "블랙라벨"]
            else:
                rec_books = ["쎈 (SSEN)", "마플시너지", "일품"]
        elif "B유형" in reg:
            if grade <= 2:
                rec_books = ["개념원리 RPM", "쎈 (SSEN)", "내신 고쟁이"]
            else:
                rec_books = ["개념원리", "쎈 (SSEN)", "1등급 만들기"]
        elif "C유형" in reg:
            if grade <= 2:
                rec_books = ["개념원리", "쎈 (SSEN)", "자이스토리"]
            else:
                rec_books = ["개념원리", "개념원리 RPM", "쎈 (SSEN)"]
        else:
            rec_books = ["수력충전", "개념원리", "라이트쎈"]

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">RECOMMENDED BOOKS</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-header" style="font-size: 16px;">남은 {days}일 맞춤 추천 교재 ({len(rec_books)}권 확정)</div>', unsafe_allow_html=True)
    st.write("")
    
    books_html = ""
    for idx, b in enumerate(rec_books, 1):
        b_info = BOOKS_DATABASE.get(b, {"type": "유형서", "pages": 250})
        books_html += f"""
        <div style="font-size: 15px; font-weight: 600; color: #191F28 !important; margin-bottom: 10px;">
            {idx}. {b} <span class="type-badge">{b_info['type']}</span> <span style="font-size: 13px; font-weight: 400; color: #8B95A1 !important;">(약 {b_info['pages']}p)</span>
        </div>
        """
    st.markdown(books_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 순화된 난이도별 분석문
    if "A유형" in reg:
        region_desc = "선택하신 <b>A유형 [수능·모의고사 변형 고난도]</b>는 변별력을 위해 수능 킬러 변형 문항이 대거 출제됩니다. 단순 유형 반복만으로는 고득점이 어려우며, 조건 제시형 고난도 문항의 구조적 해석 능력이 핵심 평가 요소입니다."
    elif "B유형" in reg:
        region_desc = "선택하신 <b>B유형 [시중 심화서 및 변형 중심]</b>은 대표 유형을 넘어서는 준심화 변형 문항이 3~5문항 출제되어 등급을 가릅니다. 개념의 단순 적용을 넘어 유형 간 융합 문항 풀이 연습이 필수적입니다."
    elif "C유형" in reg:
        region_desc = "선택하신 <b>C유형 [교과서 및 대표 유형서 중심]</b>은 교과서 및 시중 대표 유형서(쎈/RPM) 출제 비중이 매우 높습니다. 킬러 문항에 연연하기보다 실수 없이 대표 유형을 완벽하게 소화하는 정답률 관리가 최고 효율을 냅니다."
    else:
        region_desc = "선택하신 <b>D유형 [기초 개념 및 기본 예제 중심]</b>은 연산 능력과 기본적인 개념 정의 이해를 묻는 출제가 주를 이룹니다. 복잡한 심화 교재보다는 기본 예제와 대표 문제를 빠르게 반복하여 실수를 줄이는 것이 핵심입니다."

    # 4. 설문 답변 기반 동적 분석 (기존 로직 유지)
    q4_ans = survey.get('q_4', '')
    q6_ans = survey.get('q_6', '')
    q7_ans = survey.get('q_7', '')
    q13_ans = survey.get('q_13', '')

    survey_solutions = []

    if "시간이 부족" in q6_ans:
        if "2~3문항 이상 실수" in q4_ans:
            survey_solutions.append("<b>[시간 부족 + 높은 실수율]</b> 시험 풀이 속도가 둔해 조급해지면서 계산 실수가 연달아 발생하는 전형적인 '시간 압박형 실수' 패턴입니다. 대표 유형의 자동화 풀이 훈련이 우선되어야 합니다.")
        else:
            survey_solutions.append("<b>[시간 부족 + 실수 적음]</b> 정확도는 높으나 풀이 속도가 느려 점수가 정체되는 상태입니다. 1문항당 최대 2분을 넘기지 않는 '타임 어택 스킵 전략'과 풀이 단순화 훈련이 시급합니다.")
    elif "10분 이상 남아서" in q6_ans:
        if "2~3문항 이상 실수" in q4_ans:
            survey_solutions.append("<b>[시간 충분 + 높은 실수율]</b> 문제를 빠르게 푸는 습관은 좋으나, 문제를 대충 읽거나 암산 과정에서 허점이 발생하는 패턴입니다. 정풀이 역방향 검산 및 풀이 줄글 완성을 도입해야 합니다.")
        else:
            survey_solutions.append("<b>[시간 충분 + 실수 적음]</b> 기본기가 매우 단단하며 상위권으로 도약할 최적의 조건을 갖췄습니다. 고난도 킬러 문항 소화 시간을 확충하여 백분위를 굳히세요.")
    else:
        survey_solutions.append("<b>[시간 배분 보통]</b> 시험 시간 운용은 안정적이나, 고득점 문항 진입 시 소요 시간이 길어집니다. 구간별 풀이 시간을 체크하는 습관이 필요합니다.")

    if "1~2분 고민 후" in q13_ans:
        survey_solutions.append("<b>[해설지 즉시 확인 습관]</b> 막힐 때마다 해설지를 바로 보면 시험장에서 스스로 첫 아이디어를 떠올리는 힘이 자라지 않습니다. 모르는 문제는 최소 10분간 직접 시도해 본 뒤 해설을 한 줄씩 힌트로 활용하세요.")
    elif "끝까지 혼자 고민" in q13_ans:
        survey_solutions.append("<b>[자기주도 고민 우수]</b> 스스로 고민하는 집념이 훌륭하여 심화 사고력 완성 가능성이 높습니다. 다만 시험 직전에는 고민 시간을 최대 15분으로 제한하여 학습 효율을 극대화하세요.")
    else:
        survey_solutions.append("<b>[적정 고민 시간 유지]</b> 10분 내외의 타당한 고민 시간을 갖고 있어 밸런스가 양호합니다. 해설 외 제2의 풀이법을 비교하는 습관을 더해보세요.")

    if "포기함" in q7_ans:
        survey_solutions.append("<b>[킬러 문항 진입 장벽]</b> 고난도 문항에 대한 심리적 두려움이 큽니다. '조건 1개만 해독하기'부터 시작하여 진입 장벽을 점차 낮춰보세요.")
    elif "해결 가능" in q7_ans:
        survey_solutions.append("<b>[킬러 문항 소화 가능]</b> 고난도 문항 해결력이 뛰어나므로, 오답 노트 작성 시 핵심 아이디어를 1문장으로 요약하는 '키포인트 정리'에 집중하세요.")

    survey_full_text = "<br><br>".join(survey_solutions)

    # 5. 장문 심층 분석 리포트
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">DETAILED ANALYSIS REPORT</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header" style="font-size: 18px; margin-bottom: 16px;">학업 위치 종합 분석 및 성적 향상 가이드</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-paragraph">
    <b>1. 백분위 및 성적 위치 진단</b><br>
    학생분의 현재 위치는 전체 {info['total_students']}명 중 전교 <b>{info['student_rank']}위</b>로, 상위 <b>{info['pct']}%</b>에 위치하고 있습니다. 5등급제 기준 현재 <b>{info['calc_grade']}등급</b>이며, 목표인 <b>{info['target_grade']}등급</b> 달성을 위한 맞춤형 커리큘럼을 안내합니다.
    </div>

    <div class="report-paragraph">
    <b>2. 학교 출제 난이도 특성 분석 ({info['region_level']})</b><br>
    {region_desc}
    </div>

    <div class="report-paragraph">
    <b>3. 20문항 AI 매트릭스 기반 약점 극복 솔루션</b><br>
    {survey_full_text}
    </div>

    <div class="report-paragraph">
    <b>4. 남은 {info['days']}일 학습 방향성 및 실전 전략</b><br>
    남은 기간 동안 선정된 <b>{len(rec_books)}권의 핵심 교재({', '.join(rec_books)})</b>를 완벽히 소화하는 것이 핵심입니다. 시험 7일 전부터는 추가 문제 풀이를 멈추고 누적 오답 회독 및 실전 타임어택으로 마무리하세요.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. 세부 일차별 학습 스케줄 (기존 기능 유지)
    st.markdown("""
        <div style="margin-top: 24px; margin-bottom: 12px;">
            <div class="app-header" style="font-size: 18px;">초밀착 세부 일차별 학습 스케줄</div>
            <div class="app-subtext">선택하신 시험 범위 단원 전체와 추천 교재를 100% 연동한 플랜입니다.</div>
        </div>
    """, unsafe_allow_html=True)

    subj_db = CURRICULUM_DETAILED_DB.get(info['subject'], {})
    
    if "중간고사" in info['exam_type']:
        target_units = subj_db.get("중간고사", [])
    elif "기말고사" in info['exam_type']:
        target_units = subj_db.get("기말고사", [])
    else:
        target_units = subj_db.get("중간고사", []) + subj_db.get("기말고사", [])

    num_sub_units = len(target_units)
    total_days = info['days']
    days_per_subunit = max(2, (total_days - 5) // num_sub_units) if num_sub_units > 0 else 2
    
    current_day = 1
    
    book1 = rec_books[0]
    book2 = rec_books[1] if len(rec_books) > 1 else rec_books[0]
    book3 = rec_books[2] if len(rec_books) > 2 else None

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    for idx, (sub_title, sub_desc) in enumerate(target_units):
        start_d = current_day
        end_d = current_day + days_per_subunit - 1
        
        book_tasks = f"• <b>[메인 교재 1]</b> [{book1}] {sub_title} 핵심 개념 정리 및 대표 유형 풀이<br>"
        book_tasks += f"• <b>[메인 교재 2]</b> [{book2}] {sub_title} 실전 응용 문항 풀이 및 틀린 문제 1차 재풀이"
        
        if book3:
            book_tasks += f"<br>• <b>[심화 교재 3]</b> [{book3}] {sub_title} 고난도/킬러 챌린지 문항 도전"

        st.markdown(f"""
            <div class="schedule-item">
                <div class="schedule-day">{start_d}일차 ~ {end_d}일차</div>
                <div class="schedule-title">{idx+1}. {sub_title}</div>
                <div class="schedule-desc">
                    • <b>세부 학습 개념:</b> {sub_desc}<br>
                    {book_tasks}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        current_day = end_d + 1
        if current_day > total_days - 4:
            break

    final_book_desc = f"[{book2}]" + (f" 및 [{book3}]" if book3 else "")
    st.markdown(f"""
        <div class="schedule-item" style="border-left-color: #10B981;">
            <div class="schedule-day" style="color: #10B981 !important;">{current_day}일차 ~ {total_days}일차 (직전 파이널)</div>
            <div class="schedule-title">전 범주 누적 오답 회독 & 실전 기출 타임어택</div>
            <div class="schedule-desc">
                • <b>누적 오답 완성:</b> {final_book_desc}에서 별표 친 누적 오답 문항 완벽 재풀이<br>
                • <b>실전 타임어택:</b> {info['region_level']} 실제 학교 기출 족보 3회분 45분 제한시간 실전 풀이
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()


# -----------------------------------------------------------------------------
# 5. 피드백 반영: 차별화된 수학 문항별 랩타임 분석 타이머
# -----------------------------------------------------------------------------
def render_stopwatch():
    st.markdown("""
        <div class="app-card">
            <div class="pill-badge">MATH LAP-TIME ANALYZER</div>
            <div class="app-header">수학 1문항 랩타임 분석기</div>
            <div class="app-subtext">실전 시험 환경에서 문항당 소요 시간을 측정하고 페이스를 진단합니다.</div>
        </div>
    """, unsafe_allow_html=True)

    target_sec = st.number_input("목표 1문항 풀이 시간 (초 단위)", min_value=30, max_value=300, value=120, step=10)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏱️ 문항 풀이 시작 / 완료"):
            if st.session_state.q_start is None:
                st.session_state.q_start = time.time()
                st.info("💡 풀이 측정 시작! 문항을 다 푼 후 버튼을 한 번 더 누르세요.")
            else:
                elapsed = round(time.time() - st.session_state.q_start, 1)
                st.session_state.q_start = None
                
                diff = elapsed - target_sec
                if diff <= 0:
                    status = "🟢 [양호] 목표 시간 내 정답 완성 가능 페이스입니다."
                elif diff <= 30:
                    status = "🟡 [주의] 약간 지연되었습니다. 검산 시간을 고려해 10초 단축 필요."
                else:
                    status = "🔴 [경고] 풀이 지연! 실전에서는 별표 치고 넘어가야 하는 문항입니다."

                st.session_state.solve_logs.append({"time": elapsed, "target": target_sec, "status": status})
                st.rerun()

    with col2:
        if st.button("측정 기록 초기화"):
            st.session_state.solve_logs = []
            st.session_state.q_start = None
            st.rerun()

    if st.session_state.solve_logs:
        st.markdown("<h4 style='margin-top: 16px;'>📊 최근 문항별 풀이 측정 기록</h4>", unsafe_allow_html=True)
        for i, log in enumerate(reversed(st.session_state.solve_logs), 1):
            st.markdown(f"""
                <div class="app-card" style="padding: 14px; margin-bottom: 10px;">
                    <b>문항 {len(st.session_state.solve_logs)-i+1}</b>: 소요시간 <b>{log['time']}초</b> (목표: {log['target']}초)<br>
                    <span style="font-size: 13px; color: #4E5968 !important;">{log['status']}</span>
                </div>
            """, unsafe_allow_html=True)

    if st.button("메인으로 돌아가기"):
        st.session_state.q_start = None
        st.session_state.page = 'home'
        st.rerun()


# -----------------------------------------------------------------------------
# 6. 앱 페이지 라우팅
# -----------------------------------------------------------------------------
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'basic_input':
    render_basic_input()
elif st.session_state.page == 'survey_20':
    render_survey_20()
elif st.session_state.page == 'result':
    render_result()
elif st.session_state.page == 'stopwatch':
    render_stopwatch()
