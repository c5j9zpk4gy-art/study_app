import streamlit as st
import time
import json
import google.generativeai as genai

# 1. 페이지 기본 설정
st.set_page_config(page_title="고등 수학 내신 맞춤 솔루션", layout="centered")

# 2. 세션 상태 초기화
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'basic_info' not in st.session_state: st.session_state.basic_info = {}
if 'survey_answers' not in st.session_state: st.session_state.survey_answers = {}
if 'q_start' not in st.session_state: st.session_state.q_start = None
if 'solve_logs' not in st.session_state: st.session_state.solve_logs = []

# Streamlit Secrets에서 Gemini API 키 로드
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 3. AI 리포트 생성 함수 (자동 사용 가능한 모델 검색 적용)
def generate_ai_report(basic_info, survey_answers):
    api_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")

    if not api_key:
        return "⚠️ **서버에 Gemini API 키가 설정되지 않았습니다.**\nStreamlit Cloud Settings -> Secrets에 GEMINI_API_KEY를 등록해주세요."

    try:
        genai.configure(api_key=api_key)
        
        # 1) 현재 API 키로 사용 가능한 모델 자동 조회
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            return "⚠️ 현재 API 키로 사용 가능한 Gemini 모델이 없습니다. Google AI Studio에서 API 키를 다시 발급받아주세요."

        # 2) 사용 가능한 모델 중 최적의 모델 선택 (없으면 지원 가능한 첫 번째 모델로 대체)
        target_model_name = None
        for model_option in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if model_option in available_models:
                target_model_name = model_option
                break
        
        if not target_model_name:
            target_model_name = available_models[0] # 검색된 첫 모델로 강제 지정

        # 3) 모델 호출
        model = genai.GenerativeModel(target_model_name)

        prompt_content = f"""
        당신은 대한민국 최고 수준의 고등 수학 전문 대입 입시 컨설턴트입니다.
        아래 학생의 프로필과 상세 설문 응답을 분석하여 현실적이고 구체적인 맞춤형 컨설팅 리포트를 상세히 작성하세요.

        [학생 기본 입력 데이터]
        - 과목 및 범위: {basic_info.get('subject')} ({basic_info.get('exam_type')})
        - 현재 성적: 전교 {basic_info.get('student_rank')}등 / 전체 {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, {basic_info.get('calc_grade')}등급)
        - 목표 성적: {basic_info.get('target_grade')}등급 (시험까지 D-{basic_info.get('days')}일)
        - 학교 출제 유형: {basic_info.get('region_level')}

        [설문 응답 상세 데이터]
        {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

        [작성 요구 조건]
        1. 요약하지 말고 세밀하고 길게 서술할 것.
        2. 학생이 입력한 설문 대답을 직접 인용하면서, 그 습관이 성적에 미치는 영향과 해결책을 구체적으로 설명할 것.
        3. D-{basic_info.get('days')}일 간의 일차별 스케줄을 구체적인 분량, 교재명과 함께 정밀하게 직접 짜줄 것.
        4. 다음 목차 구조를 반드시 준수할 것:
           - 1. 현재 학업 위치 및 목표 달성 가능성 정밀 진단
           - 2. 설문 응답 기반 1:1 약점 패턴 분석 및 행동 교정 처방
           - 3. 학교 출제 난이도 맞춤형 주교재/부교재 및 회독 전략
           - 4. AI 맞춤 D-{basic_info.get('days')} 초밀착 일차별 학습 스케줄
           - 5. 실전 시험장 타임어택 및 실수 방지 페이스메이킹 전략
        """

        response = model.generate_content(prompt_content)
        return response.text

    except Exception as e:
        return f"⚠️ AI 생성 중 오류가 발생했습니다: {str(e)}"

# 4. 화면 렌더링 로직
def render_home():
    st.title("고등 수학 내신 맞춤 솔루션")
    st.write("Gemini AI 기반 맞춤 리포트 및 랩타임 분석기")
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
        region_level = st.radio("학교 시험 출제 스타일", ["1유형: 강남/자사고 스타일", "2유형: 일반고 심화 스타일", "3유형: 표준 내신 스타일", "4유형: 기본 개념 스타일"])

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
    questions = [
        ("질문 1. 하루에 순수하게 수학 공부에 투자할 수 있는 시간은 얼마인가요?", ["하루 1~2시간 이하", "하루 2~3시간", "하루 3~4시간", "하루 4시간 이상 몰입 가능"]),
        ("질문 2. 현재 주로 풀고 있는 주교재와 부교재의 종류는 무엇인가요?", ["개념서 위주", "유형서 위주", "심화서 위주", "기출문제집 위주"]),
        ("질문 3. 시험에서 가장 자주 발생하는 오답의 주요 원인은 무엇인가요?", ["계산 실수", "조건 해석 오류", "시간 부족", "개념 미숙"]),
        ("질문 4. 수학 문제를 풀다가 막혔을 때 주로 어떻게 행동하나요?", ["바로 해설지 확인", "5~10분 고민 후 확인", "시험 전날 모아서 봄", "끝까지 스스로 돎"]),
        ("질문 5. 가장 약하다고 느끼는 유형은 무엇인가요?", ["기하/도형", "복잡한 식/부등식", "함수/그래프", "확률과 통계"]),
        ("질문 6. 틀린 문제 복습 방법은?", ["눈으로 훑음", "당일 1번 다시 풂", "오답노트에 직접 풂", "다른 풀이법도 찾음"]),
        ("질문 7. 고난도 문항을 접했을 때 상태는?", ["포기함", "아이디어는 떠오르나 막힘", "시간 충분하면 풂"])
    ]

    with st.form("survey_custom_form"):
        answers = {}
        for idx, (q, opts) in enumerate(questions, 1):
            st.subheader(f"Q{idx}. {q[4:]}")
            ans = st.radio(q, opts, key=f"cq_{idx}")
            answers[q] = ans
            st.divider()

        if st.form_submit_button("🎓 AI 심층 컨설팅 리포트 생성", use_container_width=True):
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

    st.title("📋 1:1 AI 초밀착 심층 컨설팅 리포트")
    st.info(f"**{info['subject']} ({info['exam_type']})** | 전교 {info['student_rank']}위 / {info['total_students']}명 ➔ 목표 {info['target_grade']}등급")

    with st.spinner("🎓 AI 컨설턴트가 정밀 리포트를 작성 중입니다..."):
        ai_report_text = generate_ai_report(info, survey)

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
                st.info("측정 중... 완료 후 다시 누르세요.")
            else:
                elapsed = round(time.time() - st.session_state.q_start, 1)
                st.session_state.q_start = None
                diff = elapsed - target_sec
                status = "🟢 [양호] 목표 내 완료" if diff <= 0 else ("🟡 [주의] 10초 단축 필요" if diff <= 30 else "🔴 [경고] 풀이 지연")
                st.session_state.solve_logs.append({"time": elapsed, "target": target_sec, "status": status})
                st.rerun()
    with col2:
        if st.button("초기화", use_container_width=True):
            st.session_state.solve_logs = []
            st.session_state.q_start = None
            st.rerun()

    if st.session_state.solve_logs:
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
