import streamlit as st
import time
import json
import urllib.request

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 UI CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="고등 수학 내신 맞춤 솔루션", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F5F7FA !important; color: #191F28 !important; }
    html, body, p, span, div, label, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "Pretendard", sans-serif !important;
        color: #191F28 !important;
    }
    .app-card {
        background-color: #FFFFFF !important;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E8EB;
        margin-bottom: 20px;
    }
    .pill-badge {
        display: inline-block;
        background-color: #E8F3FF !important;
        color: #1B64DA !important;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
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
    .app-header {
        font-size: 22px;
        font-weight: 700;
        color: #191F28 !important;
        margin-bottom: 6px;
    }
    .app-subtext {
        font-size: 14px;
        color: #8B95A1 !important;
        line-height: 1.4;
    }
    .stButton>button {
        width: 100%;
        background-color: #2D65F2 !important;
        color: #FFFFFF !important;
        border-radius: 14px;
        padding: 14px;
        font-size: 15px;
        font-weight: 600;
        border: none;
    }
    header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태 관리
# -----------------------------------------------------------------------------
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'basic_info' not in st.session_state: st.session_state.basic_info = {}
if 'survey_answers' not in st.session_state: st.session_state.survey_answers = {}
if 'q_start' not in st.session_state: st.session_state.q_start = None
if 'solve_logs' not in st.session_state: st.session_state.solve_logs = []

# OpenAI API 키 설정 (Streamlit secrets 또는 직접 입력 지원)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

# -----------------------------------------------------------------------------
# 3. AI 리포트 생성 함수 (OpenAI GPT API 호출)
# -----------------------------------------------------------------------------
def generate_ai_report(basic_info, survey_answers):
    prompt_content = f"""
    당신은 대한민국 고등학교 수학 내신 전문 컨설턴트 AI입니다.
    다음 학생의 내신 정보와 상세 설문 답변을 바탕으로 개별 맞춤형 진단 리포트를 작성해주세요.

    [학생 기본 정보]
    - 과목: {basic_info.get('subject')}
    - 시험 범위: {basic_info.get('exam_type')}
    - 현재 성적: 전교 {basic_info.get('student_rank')}위 / {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, {basic_info.get('calc_grade')}등급)
    - 목표 성적: {basic_info.get('target_grade')}등급 (시험까지 {basic_info.get('days')}일 남음)
    - 학교 출제 난이도: {basic_info.get('region_level')}

    [학생 맞춤형 설문 답변]
    {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

    [작성 규칙]
    1. 학생의 답변을 구체적으로 인용하며 취약점을 명확히 짚어줄 것.
    2. 개별화된 고득점 전략과 오답 관리법을 제안할 것.
    3. 말투는 격려하면서도 전문적이고 단호한 어조로 작성할 것.
    4. HTML 태그(<b>, <br>)를 적절히 활용하여 가독성 있게 작성할 것.
    """

    if not OPENAI_API_KEY:
        # API 키가 설정되지 않았을 경우 생성하는 맞춤형 폴백 분석
        return f"""
        <b>[AI 정밀 개별 진단]</b><br>
        학생분의 현재 상위 <b>{basic_info.get('pct')}% ({basic_info.get('calc_grade')}등급)</b> 위치와 설문 응답을 기반으로 AI 분석을 진행했습니다.<br><br>
        <b>1. 주요 감점요인 및 취약 패턴 분석</b><br>
        응답해 주신 내용 중 <b>'{survey_answers.get('Q1. 시험에서 가장 자주 발생하는 오답/감점 패턴은?')}'</b>과 <b>'{survey_answers.get('Q2. 수학 문제를 풀다가 막혔을 때 주로 보이는 행동은?')}'</b> 현상이 성적 상승의 가장 큰 걸림돌로 작용하고 있습니다.<br><br>
        <b>2. 목표 등급({basic_info.get('target_grade')}등급) 달성을 위한 AI 처방</b><br>
        • <b>취약 유형 집중 조치:</b> {survey_answers.get('Q3. 가장 취약하거나 두려움을 느끼는 단원 유형은?')} 단원에 대한 개념 재정립과 대표 문항 유형 3회 회독이 필수적입니다.<br>
        • <b>오답 재풀이 루틴:</b> {survey_answers.get('Q4. 틀린 문제(오답)를 다시 공부하는 방식과 주기는?')} 방식을 보완하여, 문제 풀이 직후 아이디어 키워드를 한 줄로 요약하는 훈련을 병행하세요.
        """

    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a professional math education consultant AI."},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": 0.7
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 분석 생성 중 오류가 발생하여 기본 진단으로 전환됩니다: {str(e)}"

# -----------------------------------------------------------------------------
# 4. 화면 렌더링
# -----------------------------------------------------------------------------

def render_home():
    st.markdown("""
        <div class="app-card">
            <div class="pill-badge">GENERATIVE AI SOLUTION</div>
            <div class="app-header">고등 수학 내신 맞춤 솔루션</div>
            <div class="app-subtext">OpenAI GPT 기반 실시간 맞춤 분석 및 문항별 랩타임 분석기</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("AI 내신 진단 시작하기"):
            st.session_state.page = 'basic_input'
            st.rerun()
    with col2:
        if st.button("⏱️ 문항별 랩타임 분석기"):
            st.session_state.page = 'stopwatch'
            st.rerun()

def render_basic_input():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 1 / 2</div>
            <div class="app-header">기본 정보 및 학교 난이도 설정</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("basic_info_form"):
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        subject = st.selectbox("진단 과목 선택", ["공통수학1", "공통수학2", "대수", "미적분I", "확률과 통계"])
        exam_type = st.radio("시험 범위 선택", ["중간고사", "기말고사", "전범위"], index=0)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=1000, value=200, step=1)
        student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=int(total_students), value=min(34, int(total_students)), step=1)
        target_grade = st.selectbox("목표 내신 등급", [1, 2, 3, 4, 5], index=0)
        days = st.number_input("시험까지 남은 기간 (일)", min_value=7, max_value=120, value=30, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        region_level = st.radio(
            "학교 출제 난이도 유형",
            ["A유형 [수능·모의고사 변형 고난도]", "B유형 [시중 심화서 및 변형 중심]", "C유형 [교과서 및 대표 유형서 중심]", "D유형 [기초 개념 및 기본 예제 중심]"],
            index=1
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("다음: 개별 맞춤 정밀 설문"):
            pct = round((student_rank / total_students) * 100, 2)
            calc_grade = 1 if pct <= 10.0 else (2 if pct <= 34.0 else (3 if pct <= 66.0 else (4 if pct <= 90.0 else 5)))

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

# -----------------------------------------------------------------------------
# 개편된 개별 맞춤형 설문조사 (10문항 정밀 구성)
# -----------------------------------------------------------------------------
def render_survey_custom():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 2 / 2</div>
            <div class="app-header">개별 맞춤형 정밀 진단 설문</div>
            <div class="app-subtext">AI가 개별화된 맞춤 리포트를 생성할 수 있도록 본인의 솔직한 학습 습관을 선택해 주세요.</div>
        </div>
    """, unsafe_allow_html=True)

    # 맞춤형 결과 도출에 유리한 정밀 10문항
    questions = [
        ("Q1. 시험에서 가장 자주 발생하는 오답/감점 패턴은?", 
         ["계산 실수 및 복잡한 식에서의 기호 오용", "문제의 조건 해석을 잘못하여 접근 오류", "시간이 부족하여 뒤쪽 서술형/고난도 풀이 포기", "개념 적용 자체를 하지 못함"]),
        
        ("Q2. 수학 문제를 풀다가 막혔을 때 주로 보이는 행동은?", 
         ["1~2분만 고민하고 바로 해설지 확인", "10분 이상 스스로 고민하고 조건 재해석 시도", "막히면 해당 문제를 넘기고 나중에 다시 봄", "더 이상 풀지 않고 해설 강의를 바로 수강"]),
        
        ("Q3. 가장 취약하거나 두려움을 느끼는 단원 유형은?", 
         ["도형 및 기하학적 성질이 융합된 문항", "방정식, 부등식 및 복잡한 식의 계산 파트", "함수 그래프 해석 및 추론 문항", "순열, 조합, 확률 등 경우의 수 파트"]),
        
        ("Q4. 틀린 문제(오답)를 다시 공부하는 방식과 주기는?", 
         ["시험 직전에만 모아서 눈으로 훑어봄", "틀린 당일 1회 재풀이 후 별도 복습 없음", "주기적으로 오답 노트에 풀이 과정을 직접 써보며 회독", "맞힌 문제까지 포함해 완벽히 이해될 때까지 반복"]),
        
        ("Q5. 수능/모의고사 기출 변형 문제에 대한 적응도는?", 
         ["변형 문항을 만나면 처음 보는 유형이라 생각하여 손을 못 댐", "기본 아이디어는 잡으나 계산이나 조건 추가 시 막힘", "기출 변형 문항도 원리를 파악하여 무난히 해결"]),
        
        ("Q6. 고난도 문제 해결 시 본인의 서술형 작성 습관은?", 
         ["두서없이 계산 과정만 구석에 늘어놓음", "핵심 공식만 적고 중간 논리 과정을 생략함", "단계별 조건 해석과 정갈한 풀이 과정을 차례로 작성"]),
        
        ("Q7. 개념서 수강/공부 시 공식을 다루는 자세는?", 
         ["공식만 외우고 증명 과정은 그냥 넘어감", "증명 과정을 이해는 하나 직접 써보진 않음", "증명 과정도 직접 도출해 보고 조건의 의미를 파악함"]),
        
        ("Q8. 시험 시간 배분 시 본인의 페이스 전략은?", 
         ["1번부터 순서대로 풀다가 막히는 문제에서 시간을 오래 끌어 망침", "아는 문제부터 빠르게 풀고 고난도 문제는 뒤로 미룸", "문항별 제한 시간을 정해두고 체계적으로 타임어택 시행"]),
        
        ("Q9. 평소 복습 시 맞힌 문제에 대한 처리 방식은?", 
         ["맞힌 문제는 다시 보지 않고 넘어감", "맞힌 문제 중 찝찝하게 맞힌 것은 해설과 풀이 비교", "모든 맞힌 문제의 제2의 풀이법을 다각도로 탐색"]),
        
        ("Q10. 이번 내신을 준비하며 AI 솔루션에 기대하는 핵심 피드백은?", 
         ["시험 시간 안배 및 타임어택 실전 전략", "취약 단원 및 오답 관리의 구체적 루틴 처방", "고난도 변형 문항 대비를 위한 심화 학습 방향"])
    ]

    with st.form("survey_custom_form"):
        answers = {}
        for idx, (q, opts) in enumerate(questions, 1):
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="pill-badge-gray">QUESTION {idx}</div>', unsafe_allow_html=True)
            ans = st.radio(q, opts, key=f"cq_{idx}")
            answers[q] = ans
            st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("🤖 AI 정밀 맞춤 분석 리포트 생성"):
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
            <div class="pill-badge">OPENAI GPT-BASED AI REPORT</div>
            <div class="app-header">실시간 AI 맞춤 진단 리포트</div>
            <div class="app-subtext">입력하신 응답 데이터를 바탕으로 AI가 생성한 개별 맞춤 솔루션입니다.</div>
        </div>
    """, unsafe_allow_html=True)

    # 성적 서머리
    st.markdown(f"""
        <div class="app-card">
            <div class="pill-badge">{info['subject']} · {info['exam_type']}</div>
            <div style="font-size: 20px; font-weight: 700; color: #191F28 !important; margin-top: 4px;">
                현재 전교 <span style="color:#2D65F2 !important;">{info['student_rank']}위</span> / {info['total_students']}명 (상위 {info['pct']}%)
            </div>
            <div style="font-size: 14px; color: #4E5968 !important; margin-top: 6px;">
                현재 <b>{info['calc_grade']}등급</b> ➔ 목표 <b>{info['target_grade']}등급</b> ({info['days']}일 남음) | {info['region_level']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # AI 호출 및 분석 결과 표시
    with st.spinner("🤖 OpenAI GPT AI가 응답 데이터를 기반으로 정밀 맞춤 리포트를 생성 중입니다..."):
        ai_report_html = generate_ai_report(info, survey)

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">AI INDIVIDUAL REPORT</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="line-height: 1.8; color: #333D4B !important;">{ai_report_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()

# -----------------------------------------------------------------------------
# 5. 수학 문항별 랩타임 분석 타이머 (유지)
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
if st.session_state.page == 'home': render_home()
elif st.session_state.page == 'basic_input': render_basic_input()
elif st.session_state.page == 'survey_custom': render_survey_custom()
elif st.session_state.page == 'result': render_result()
elif st.session_state.page == 'stopwatch': render_stopwatch()
