import streamlit as st
import time
import math

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 네이티브 앱 UI CSS (이모티콘 완전히 제거 / 가독성 중심)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고등 수학 내신 솔루션", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #F5F7FA;
    }
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", "Segoe UI", Roboto, sans-serif;
        color: #191F28;
    }

    .app-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E8EB;
        margin-bottom: 20px;
    }

    .pill-badge {
        display: inline-block;
        background-color: #E8F3FF;
        color: #1B64DA;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
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

    .app-header {
        font-size: 22px;
        font-weight: 700;
        color: #191F28;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    
    .app-subtext {
        font-size: 14px;
        color: #8B95A1;
        margin-bottom: 0px;
        line-height: 1.4;
    }

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

    .schedule-item {
        border-left: 3px solid #2D65F2;
        padding-left: 16px;
        margin-bottom: 20px;
    }
    .schedule-day {
        font-size: 12px;
        font-weight: 700;
        color: #2D65F2;
    }
    .schedule-title {
        font-size: 16px;
        font-weight: 700;
        color: #333D4B;
        margin: 4px 0;
    }
    .schedule-desc {
        font-size: 13px;
        color: #4E5968;
        margin: 0;
        line-height: 1.6;
    }

    .report-paragraph {
        font-size: 14px;
        line-height: 1.75;
        color: #333D4B;
        margin-bottom: 16px;
        word-break: keep-all;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태 관리 (초기값 세팅)
# -----------------------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'basic_info' not in st.session_state:
    st.session_state.basic_info = {}
if 'survey_answers' not in st.session_state:
    st.session_state.survey_answers = {}
if 'sw_running' not in st.session_state:
    st.session_state.sw_running = False
if 'sw_start_time' not in st.session_state:
    st.session_state.sw_start_time = 0
if 'sw_elapsed_time' not in st.session_state:
    st.session_state.sw_elapsed_time = 0

# -----------------------------------------------------------------------------
# 3. 40여 종 시중 교재 DB & 학과 커리큘럼 DB (중간/기말 정확히 50% 분할)
# -----------------------------------------------------------------------------
BOOKS_DATABASE = {
    # 연산/개념 (Level 1)
    "수력충전": {"level": 1, "type": "연산기초", "pages": 220},
    "연산으로 개념잡기": {"level": 1, "type": "연산기초", "pages": 200},
    "개념원리": {"level": 1, "type": "기본개념", "pages": 310},
    "개념쎈": {"level": 1, "type": "개념강화", "pages": 290},
    "개념 해결의 법칙": {"level": 1, "type": "기본개념", "pages": 280},
    "풍성한 한샘 수학": {"level": 1, "type": "기본개념", "pages": 260},
    "기본정석": {"level": 1, "type": "전통개념", "pages": 350},

    # 라이트 유형 (Level 2-A)
    "라이트쎈": {"level": 2, "type": "쉬운유형", "pages": 250},
    "유형 해결의 법칙": {"level": 2, "type": "표준유형", "pages": 260},
    "개념원리 RPM": {"level": 2, "type": "표준유형", "pages": 270},
    "짱 쉬운 유형": {"level": 2, "type": "기초유형", "pages": 180},
    "짱 중요한 유형": {"level": 2, "type": "핵심유형", "pages": 200},

    # 표준/다량 유형 (Level 2-B)
    "쎈 (SSEN)": {"level": 2, "type": "대표유형", "pages": 320},
    "마플시너지": {"level": 2, "type": "다량유형", "pages": 460},
    "자이스토리": {"level": 2, "type": "내신기출", "pages": 420},
    "마더텅 고등수학": {"level": 2, "type": "기출망라", "pages": 440},
    "올림포스 고난도": {"level": 2, "type": "EBS연계", "pages": 180},
    "EBS 수능특강": {"level": 2, "type": "EBS수능형", "pages": 160},

    # 준심화 (Level 3)
    "일품": {"level": 3, "type": "준심화", "pages": 210},
    "내신 고쟁이": {"level": 3, "type": "심화유형", "pages": 270},
    "1등급 만들기": {"level": 3, "type": "내신고득점", "pages": 200},
    "실력정석": {"level": 3, "type": "심화개념", "pages": 380},
    "TOT (티오티)": {"level": 3, "type": "준심화", "pages": 190},
    "수학의 바이블 특강": {"level": 3, "type": "유형심화", "pages": 210},

    # 최심화/킬러 (Level 4)
    "블랙라벨": {"level": 4, "type": "최심화", "pages": 170},
    "531 프로젝트 HYPER": {"level": 4, "type": "최심화", "pages": 120},
    "절대등급": {"level": 4, "type": "최고난도", "pages": 160},
    "최강TOT": {"level": 4, "type": "최고난도", "pages": 150},
    "플래티넘 수학": {"level": 4, "type": "최심화기출", "pages": 180},
    "하이엔드": {"level": 4, "type": "극상위권", "pages": 140},
    "기출의 고백": {"level": 4, "type": "킬러분석", "pages": 220},
    "1등급 선점": {"level": 4, "type": "상위권특화", "pages": 160},
    "최고득점 수학": {"level": 4, "type": "심화기출", "pages": 190},
    "수능 기출의 미래": {"level": 4, "type": "수능고난도", "pages": 210},
    "경시대회 기출 100제": {"level": 4, "type": "경시/사관", "pages": 130},
    "수학의 신": {"level": 4, "type": "극상위권", "pages": 160},
    "일등급 수학": {"level": 4, "type": "최심화", "pages": 180},
    "매3수": {"level": 2, "type": "기출매일", "pages": 250},
    "시크릿 기출": {"level": 3, "type": "지역기출", "pages": 200},
    "파이널 모의고사": {"level": 3, "type": "실전모의", "pages": 120}
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
# 4. 화면 렌더링 함수
# -----------------------------------------------------------------------------

def render_home():
    st.markdown("""
        <div class="app-card">
            <div class="pill-badge">ACADEMIC SOLUTION</div>
            <div class="app-header">고등 수학 내신 정밀 진단 솔루션</div>
            <div class="app-subtext">학군지 수준 분석, 백분위 정밀 진단 및 20문항 개별화 스케줄링</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("내신 진단 시작하기", use_container_width=True):
            st.session_state.page = 'basic_input'
            st.rerun()
    with col2:
        if st.button("순공 타이머 실행", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()


def render_basic_input():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 1 / 2</div>
            <div class="app-header">기본 정보 및 환경 설정</div>
            <div class="app-subtext">정확한 백분위 수치 계산과 학군지 환경 진단을 위한 기본 정보입니다.</div>
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
        
        # 입력폼 버그 수정: 세션 상태와 완전 연동되는 인풋박스
        total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=1000, value=200, step=1, key="input_total_students")
        student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=int(total_students), value=min(34, int(total_students)), step=1, key="input_student_rank")
        
        target_grade = st.selectbox("목표 내신 등급 (5등급제 기준)", [1, 2, 3, 4, 5], index=0)
        days = st.number_input("시험까지 남은 기간 (일)", min_value=7, max_value=120, value=30, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-badge-gray">학군지 수준 상세 가이드</div>', unsafe_allow_html=True)
        st.markdown("""
        <b>학교 난이도 파악 가이드:</b><br>
        • <b>Level 4 [최상위 학군지]</b>: 강남3구, 대치, 서초, 목동, 중계, 분당, 수성구 등. 모의고사 킬러 변형이 다수 출제되며 서술형 채점이 매우 엄격함.<br>
        • <b>Level 3 [주요 거점 학군지]</b>: 천안, 청주, 전주, 창원, 수원, 해운대 등 거점 도시. 시중 대표 유형서 이상 출제, 준심화 3~5문항으로 변별력 확보.<br>
        • <b>Level 2 [일반계 고교]</b>: 전국 평준화/비평준화 일반계 고교 평균. 교과서 및 대표 유형서(쎈/RPM)를 완벽히 학습하면 상위권 진입 가능.<br>
        • <b>Level 1 [기초 개념 중심]</b>: 소규모/기초 학력 보장 위주 출제 학교. 연산 및 대표 개념 위주 출제로 실수 방지가 핵심.
        """, unsafe_allow_html=True)
        
        region_level = st.radio(
            "자신의 학군지 난이도를 선택하세요",
            ["Level 4 [최상위 학군지]", "Level 3 [주요 거점 학군지]", "Level 2 [일반계 고교]", "Level 1 [기초 개념 중심]"],
            index=1
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("다음: 20문항 상세 설문 진행")
        if submitted:
            # 실시간 입력값 가져오기
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
            <div class="app-subtext">개인 맞춤형 장문 리포트 작성을 위한 상세 설문 문항입니다.</div>
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
            ("Q7. 고난도 킬러 문제(모의고사 21, 29, 30번 변형)에 대한 태도는?", ["시도조차 못 하고 포기함", "접근법은 떠올리나 끝까지 못 돎", "시간이 주어지면 해결 가능"]),
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

    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">FINAL REPORT</div>
            <div class="app-header">내신 맞춤 솔루션 리포트</div>
            <div class="app-subtext">입력하신 백분위 수치 및 20문항 진단을 기반으로 심층 작성된 솔루션입니다.</div>
        </div>
    """, unsafe_allow_html=True)

    # 1. 석차 및 백분위 서머리 카드
    st.markdown(f"""
        <div class="app-card">
            <div class="pill-badge">{info['subject']} · {info['exam_type'].split(' ')[0]}</div>
            <div style="font-size: 20px; font-weight: 700; color: #191F28; margin-top: 4px;">
                현재 전교 <span style="color:#2D65F2;">{info['student_rank']}위</span> / {info['total_students']}명 (상위 {info['pct']}%)
            </div>
            <div style="font-size: 14px; color: #4E5968; margin-top: 6px;">
                현재 내신 <b>{info['calc_grade']}등급</b> ➔ 목표 <b>{info['target_grade']}등급</b> ({info['days']}일 남음) | {info['region_level']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 학군지 가중치 적용 추천 교재 라인업 (40여종 DB에서 선정)
    reg = info['region_level']
    pct = info['pct']
    
    if "Level 4" in reg:
        if pct <= 15:
            rec_books = ["마플시너지", "내신 고쟁이", "블랙라벨", "531 프로젝트 HYPER"]
        else:
            rec_books = ["쎈 (SSEN)", "마플시너지", "일품", "내신 고쟁이"]
    elif "Level 3" in reg:
        if pct <= 20:
            rec_books = ["개념원리 RPM", "쎈 (SSEN)", "일품", "내신 고쟁이"]
        else:
            rec_books = ["개념원리", "라이트쎈", "쎈 (SSEN)", "1등급 만들기"]
    elif "Level 2" in reg:
        if pct <= 30:
            rec_books = ["개념원리", "쎈 (SSEN)", "자이스토리", "일품"]
        else:
            rec_books = ["개념원리", "개념원리 RPM", "유형 해결의 법칙", "쎈 (SSEN)"]
    else: # Level 1
        rec_books = ["수력충전", "개념원리", "라이트쎈", "개념원리 RPM"]

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">RECOMMENDED BOOKS</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header" style="font-size: 16px;">학군지 및 위치 대비 맞춤 교재 라인업</div>', unsafe_allow_html=True)
    st.write("")
    for idx, b in enumerate(rec_books, 1):
        b_info = BOOKS_DATABASE.get(b, {"type": "유형서", "pages": 250})
        st.markdown(f"**{idx}. {b}** ` {b_info['type']} ` (약 {b_info['pages']}p)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 긴 장문 심층 분석 리포트
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">DETAILED ANALYSIS REPORT</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header" style="font-size: 18px; margin-bottom: 16px;">학업 위치 종합 분석 및 성적 향상 가이드</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-paragraph">
    <b>1. 백분위 및 성적 위치 진단</b><br>
    학생분의 현재 위치는 전체 {info['total_students']}명 중 전교 <b>{info['student_rank']}위</b>로, 상위 <b>{info['pct']}%</b>에 위치하고 있습니다. 5등급제 기준으로 현재 <b>{info['calc_grade']}등급</b> 선에 형성되어 있으며, 목표 등급인 <b>{info['target_grade']}등급</b>으로 진입하기 위해서는 상위 백분위를 확실하게 끌어올리는 전략적 학습이 필수적입니다. 현재 위치에서 등급을 올려줄 핵심 변수는 단순 문제 풀이 양이 아니라, 감점 요인을 최소화하는 실전 검산 능력과 고난도 문항의 해결력입니다.
    </div>

    <div class="report-paragraph">
    <b>2. 학군지 특성에 따른 출제 경향 분석 ({info['region_level']})</b><br>
    선택하신 <b>{info['region_level']}</b> 환경에서는 출제진이 변별력을 가르기 위해 기본 유형 문제 외에도 변형 고난도 문항을 반드시 배치합니다. 시중 일반 유형서만 단순 회독해서는 상위권 문턱에서 한계에 부딪힐 가능성이 높습니다. 특히 서술형 감점 기준이 까다롭게 적용되는 경향이 있으므로, 평소 풀이 과정을 줄글로 일목요연하게 작성하는 훈련이 병행되어야 합니다.
    </div>

    <div class="report-paragraph">
    <b>3. 20문항 설문 기반 약점 극복 솔루션</b><br>
    응답해주신 설문 내용을 종합한 결과, 학생분의 가장 큰 개선점은 <b>'{survey.get('q_4', '계산 실수')}'</b> 및 <b>'{survey.get('q_6', '시간 배분')}'</b> 항목에서 나타납니다. 시험 시간이 모자라거나 실수가 발생하는 근본적 이유는 문제 유형에 대한 조건 반응 속도가 둔하기 때문입니다. 이를 극복하기 위해 추천된 교재 중 1단계 메인 유형서를 통해 기본 유형을 보자마자 풀이법이 떠오르도록 '조건-공식'을 자동화해야 합니다. 또한 해설지 의존도({survey.get('q_13', '해설지 확인')})를 줄이고, 한 문제당 최소 10분 이상 스키마를 그려보는 고민 과정이 축적되어야 실전 킬러 문항을 풀 수 있는 힘이 생깁니다.
    </div>

    <div class="report-paragraph">
    <b>4. 남은 {info['days']}일 학습 방향성 및 실전 전략</b><br>
    남은 기간 동안 주말 학습 시간({survey.get('q_15', '학습 시간')})을 최대로 활용하여 추천 교재 2권(개념/유형서 1권 + 준심화/기출서 1권)을 병행 완료하는 구조를 가져가야 합니다. 시험 7일 전부터는 누적 오답 노트 회독과 함께 실제 학교 기출 족보를 제한 시간(45분)을 두고 풀어보는 타임어택 실전 훈련을 반드시 수행하시길 권장합니다.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. 정확한 시험 범위 반영 커리큘럼 스케줄
    st.markdown("""
        <div style="margin-top: 24px; margin-bottom: 12px;">
            <div class="app-header" style="font-size: 18px;">초밀착 세부 일차별 학습 스케줄</div>
            <div class="app-subtext">선택하신 시험 범위 단원 전체를 빠짐없이 구성한 세부 계획입니다.</div>
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
    
    book_a = rec_books[0]
    book_b = rec_books[1] if len(rec_books) > 1 else rec_books[0]
    book_c = rec_books[2] if len(rec_books) > 2 else rec_books[-1]

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    for idx, (sub_title, sub_desc) in enumerate(target_units):
        start_d = current_day
        end_d = current_day + days_per_subunit - 1
        
        st.markdown(f"""
            <div class="schedule-item">
                <div class="schedule-day">{start_d}일차 ~ {end_d}일차</div>
                <div class="schedule-title">{idx+1}. {sub_title}</div>
                <div class="schedule-desc">
                    • <b>학습 범위:</b> {sub_desc}<br>
                    • <b>병행 과제 1 (개념/유형):</b> [{book_a}] {sub_title} 단원 대표 유형 및 B단계 문제 전체 풀이<br>
                    • <b>병행 과제 2 (심화/오답):</b> [{book_b}] {sub_title} 고난도 문항 풀이 + [{book_a}] 틀린 문제 오답 고치기
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        current_day = end_d + 1
        if current_day > total_days - 4:
            break

    # 파이널 마무리 스케줄
    st.markdown(f"""
        <div class="schedule-item" style="border-left-color: #10B981;">
            <div class="schedule-day" style="color: #10B981;">{current_day}일차 ~ {total_days}일차 (직전 파이널)</div>
            <div class="schedule-title">전 범주 누적 오답 회독 & 실전 기출 타임어택</div>
            <div class="schedule-desc">
                • <b>최종 심화 완독:</b> [{book_c}] 고난도 킬러 파트 오답 및 핵심 유형 재점검<br>
                • <b>실전 훈련:</b> {info['region_level']} 기출 모의고사 3회분 45분 타임어택 풀이 및 서술형 작성 훈련
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
            <div class="app-subtext">오늘의 순수 학습 시간을 정확히 측정하세요.</div>
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
        timer_placeholder.markdown(f"<h1 style='text-align: center; color: #2D65F2; font-size: 44px; margin: 24px 0;'>{format_time(st.session_state.sw_elapsed_time)}</h1>", unsafe_allow_html=True)
        time.sleep(0.1)
        st.rerun()
    else:
        timer_placeholder.markdown(f"<h1 style='text-align: center; color: #8B95A1; font-size: 44px; margin: 24px 0;'>{format_time(st.session_state.sw_elapsed_time)}</h1>", unsafe_allow_html=True)

    if st.button("메인으로 돌아가기"):
        st.session_state.sw_running = False
        st.session_state.page = 'home'
        st.rerun()


# -----------------------------------------------------------------------------
# 5. 앱 페이지 라우팅
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
