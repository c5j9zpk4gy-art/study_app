import streamlit as st
import time
import json
import urllib.request

# 1. 페이지 및 기본 설정 (다크모드 자동 지원)
st.set_page_config(page_title="고등 수학 내신 맞춤 솔루션", layout="centered")

st.markdown("""
    <style>
    /* 다크모드/라이트모드 공통 가독성 개선 */
    .stApp {
        padding-top: 1rem;
    }
    .report-card {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 세션 상태 초기화
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'basic_info' not in st.session_state: st.session_state.basic_info = {}
if 'survey_answers' not in st.session_state: st.session_state.survey_answers = {}
if 'q_start' not in st.session_state: st.session_state.q_start = None
if 'solve_logs' not in st.session_state: st.session_state.solve_logs = []

# API 키 가져오기 (Secrets 또는 사용자 직접 입력)
openai_key = st.secrets.get("OPENAI_API_KEY", "")

# 3. 5,000자 이상 초장문 AI 컨설팅 프롬프트 엔진
def generate_ai_report(basic_info, survey_answers, api_key):
    prompt_content = f"""
    [시스템 지침]
    당신은 대한민국 최고 수준의 고등 수학 전문 대입 입시 컨설턴트입니다.
    아래 학생의 프로필과 상세 설문 응답을 분석하여 현실적이고 구체적인 5,000자 이상의 초장문 맞춤형 컨설팅 리포트를 작성하세요.

    [학생 기본 입력 데이터]
    - 과목 및 범위: {basic_info.get('subject')} ({basic_info.get('exam_type')})
    - 현재 성적: 전교 {basic_info.get('student_rank')}등 / 전체 {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, {basic_info.get('calc_grade')}등급)
    - 목표 성적: {basic_info.get('target_grade')}등급 (시험까지 D-{basic_info.get('days')}일)
    - 학교 출제 유형: {basic_info.get('region_level')}

    [설문 응답 상세 데이터]
    {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

    [요구하는 프롬프트 구조 및 작성 조건]
    1. **요약하지 말고 매우 세밀하고 길게 서술할 것 (5,000자 이상 분량 필수)**.
    2. 학생이 입력한 설문 대답 하나하나를 직접 인용하면서, 그 습관이 성적에 미치는 영향과 해결책을 구체적으로 설명할 것.
    3. **D-{basic_info.get('days')}일 간의 일차별 스케줄을 1일차부터 D-DAY까지 중간 생략 없이 구체적인 분량, 교재명, 풀이 권수와 함께 정밀하게 직접 짜줄 것.**
    4. 다음 목차 구조를 반드시 준수할 것:
       - 1. 현재 학업 위치 및 목표 달성 가능성 정밀 진단
       - 2. 설문 응답 기반 1:1 약점 패턴 분석 및 행동 교정 처방 (입력받은 설문 항목 전체 분석)
       - 3. 학교 출제 난이도 맞춤형 주교재/부교재 및 회독 전략
       - 4. AI 맞춤 D-{basic_info.get('days')} 초밀착 일차별 학습 스케줄 (1일차부터 시험 당일까지의 일자별 세부 플랜)
       - 5. 실전 시험장 타임어택 및 실수 방지 페이스메이킹 전략
    """

    if not api_key:
        return "⚠️ **OpenAI API 키가 설정되지 않았습니다.**\nStreamlit Secrets에 `OPENAI_API_KEY`를 등록하거나 sidebar에서 키를 입력해주세요."

    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an expert high school math admissions consultant in South Korea. Write a highly detailed, professional, and compassionate personalized consulting report in Korean with a length of at least 5000 characters."},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ AI 생성 중 오류가 발생했습니다: {str(e)}"

# 4. 화면 렌더링 함수들

def render_home():
    st.title("고등 수학 내신 맞춤 솔루션")
    st.write("GPT AI 기반 5,000자 이상 초밀착 맞춤 리포트 및 랩타임 분석기")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎓 AI 정밀 진단 시작하기", use_container_width=True):
            st.session_state.page = 'basic_input'
            st.rerun()
    with col2:
        if st.button("⏱️ 문항별 랩타임 분석기", use_container_width=True):
            st.session_state.page = 'stopwatch'
            st.rerun()

def render_basic_input():
    st.title("1단계: 기본 정보 입력")
    st.caption("학생의 현재 위치와 시험 정보를 정확히 입력해주세요.")
    
    with st.form("basic_info_form"):
        subject = st.selectbox("진단 과목", ["공통수학1", "공통수학2", "대수", "미적분I", "확률과 통계"])
        exam_type = st.radio("시험 범위", ["중간고사", "기말고사", "전범위"], horizontal=True)
        
        col1, col2 = st.columns(2)
        with col1:
            total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=1000, value=200, step=1)
            student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=1000, value=15, step=1)
        with col2:
            target_grade = st.selectbox("목표 내신 등급", [1, 2, 3, 4, 5], index=0)
            days = st.number_input("시험까지 남은 기간 (일)", min_value=7, max_value=120, value=30, step=1)
            
        region_level = st.radio(
            "학교 시험 출제 스타일",
            [
                "1유형: 강남/자사고 스타일 (수능·모의고사 고난도 변형 위주)",
                "2유형: 일반고 심화 스타일 (시중 심화서 및 변형문항 위주)",
                "3유형: 표준 내신 스타일 (교과서 및 대표 유형서 위주)",
                "4유형: 기본 개념 스타일 (기초 개념 및 예제 위주)"
            ]
        )

        if st.form_submit_button("다음: 개별 맞춤 설문 작성하기", use_container_width=True):
            pct = round((student_rank / total_students) * 100, 2)
            calc_grade = 1 if pct <= 4.0 else (2 if pct <= 11.0 else (3 if pct <= 23.0 else (4 if pct <= 40.0 else 5)))

            st.session_state.basic_info = {
                "subject": subject, "exam_type": exam_type, "total_students": int(total_students),
                "student_rank": int(student_rank), "pct": pct, "calc_grade": calc_grade,
                "target_grade": target_grade, "days": int(days), "region_level": region_level
            }
            st.session_state.page = 'survey_custom'
            st.rerun()

    if st.button("메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()

def render_survey_custom():
    st.title("2단계: 초밀착 학습 습관 진단")
    st.caption("AI가 5,000자 이상의 개별 스케줄을 작성할 수 있도록 솔직하게 답해주세요.")

    questions = [
        ("질문 1. 하루에 순수하게 수학 공부에 투자할 수 있는 시간은 얼마인가요?",
         ["하루 1~2시간 이하", "하루 2~3시간", "하루 3~4시간", "하루 4시간 이상 몰입 가능"]),
        
        ("질문 2. 현재 주로 풀고 있는 주교재와 부교재의 종류는 무엇인가요?",
         ["교과서 및 개념서(개념원리, 개념쎈 등)", "유형서 중심(RPM, 쎈 B단계 등)", "심화서 중심(일품, 고쟁이, 블랙라벨 등)", "모의고사 기출문제집(자이스토리, 마더텅 등)"]),

        ("질문 3. 시험에서 가장 자주 발생하는 오답과 감점의 주요 원인은 무엇인가요?", 
         ["계산 실수 및 중간 과정의 기호 오용", "조건 해석 오인으로 인한 초기 접근 오류", "시간 부족으로 인한 뒤쪽 고난도/서술형 미풀이", "개념 적용 차 자체를 못함"]),
        
        ("질문 4. 수학 문제를 풀다가 막혔을 때 주로 어떻게 행동하나요?", 
         ["1~2분 고민 후 바로 해설지를 확인한다", "5~10분간 조건 재해석을 시도한 뒤 해설을 본다", "일단 넘어갔다가 시험 전날 모아서 본다", "끝까지 스스로 풀 때까지 답지를 안 본다"]),
        
        ("질문 5. 가장 약하다고 느끼거나 두려움을 느끼는 단원/문항 유형은 무엇인가요?", 
         ["도형 및 기하 성질 융합 문항", "복잡한 식 계산 및 부등식 영역", "함수 그래프 추론 및 변형 문항", "경우의 수 및 확률 파트"]),
        
        ("질문 6. 틀린 문제(오답)를 복습하는 주기와 방법은 어떻게 되나요?", 
         ["눈으로 훑어보고 넘어간다", "틀린 당일 1번 다시 풀어본다", "주기적으로 오답노트에 직접 다시 풀어본다", "맞힌 문제도 제2의 풀이법을 찾아본다"]),

        ("질문 7. 고난도 변형 문항을 접했을 때 느끼는 솔직한 상태는 어떤가요?",
         ["아예 손도 대지 못하고 포기한다", "기본 아이디어는 떠올리나 중간에 막힌다", "시간만 충분하다면 해결할 수 있다"])
    ]

    with st.form("survey_custom_form"):
        answers = {}
        for idx, (q, opts) in enumerate(questions, 1):
            st.subheader(f"Q{idx}. {q[4:]}")
            ans = st.radio(q, opts, key=f"cq_{idx}")
            answers[q] = ans
            st.divider()

        user_api_key = st.text_input("OpenAI API Key (선택: Secrets 설정이 안 되어 있다면 직접 입력)", type="password", value=openai_key)

        if st.form_submit_button("🎓 5,000자+ AI 심층 컨설팅 리포트 생성", use_container_width=True):
            st.session_state.survey_answers = answers
            st.session_state.user_api_key = user_api_key
            st.session_state.page = 'result'
            st.rerun()

def render_result():
    info = st.session_state.basic_info
    survey = st.session_state.survey_answers
    api_key = st.session_state.get('user_api_key', openai_key)

    if not info or not survey:
        st.session_state.page = 'basic_input'
        st.rerun()
        return

    st.title("📋 1:1 AI 초밀착 심층 컨설팅 리포트")
    
    st.info(f"**{info['subject']} ({info['exam_type']})** | 현재 전교 {info['student_rank']}위 / {info['total_students']}명 (상위 {info['pct']}%, {info['calc_grade']}등급) ➔ 목표 {info['target_grade']}등급 (D-{info['days']}일)")

    with st.spinner("🎓 AI 컨설턴트가 입력하신 모든 데이터와 설문 응답을 바탕으로 5,000자 이상의 정밀 리포트를 작성하고 있습니다 (약 20~30초 소요)..."):
        ai_report_text = generate_ai_report(info, survey, api_key)

    # 마크다운 형태로 깨짐 없이 출력
    st.markdown(ai_report_text)

    st.divider()
    if st.button("처음으로 돌아가기", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

def render_stopwatch():
    st.title("⏱️ 수학 1문항 랩타임 분석기")
    
    target_sec = st.number_input("목표 1문항 풀이 시간 (초)", min_value=30, max_value=300, value=120, step=10)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏱️ 측정 시작 / 완료", use_container_width=True):
            if st.session_state.q_start is None:
                st.session_state.q_start = time.time()
                st.info("측정 중... 풀이 완료 후 한 번 더 누르세요.")
            else:
                elapsed = round(time.time() - st.session_state.q_start, 1)
                st.session_state.q_start = None
                
                diff = elapsed - target_sec
                status = "🟢 [양호] 목표 시간 내 정답 완성" if diff <= 0 else ("🟡 [주의] 10초 단축 필요" if diff <= 30 else "🔴 [경고] 풀이 지연! 넘어가야 할 문항")
                st.session_state.solve_logs.append({"time": elapsed, "target": target_sec, "status": status})
                st.rerun()

    with col2:
        if st.button("초기화", use_container_width=True):
            st.session_state.solve_logs = []
            st.session_state.q_start = None
            st.rerun()

    if st.session_state.solve_logs:
        st.subheader("최근 측정 기록")
        for i, log in enumerate(reversed(st.session_state.solve_logs), 1):
            st.write(f"**문항 {len(st.session_state.solve_logs)-i+1}**: {log['time']}초 (목표: {log['target']}초) - {log['status']}")

    if st.button("메인으로 돌아가기"):
        st.session_state.q_start = None
        st.session_state.page = 'home'
        st.rerun()

# 5. 페이지 라우팅
if st.session_state.page == 'home': render_home()
elif st.session_state.page == 'basic_input': render_basic_input()
elif st.session_state.page == 'survey_custom': render_survey_custom()
elif st.session_state.page == 'result': render_result()
elif st.session_state.page == 'stopwatch': render_stopwatch()
