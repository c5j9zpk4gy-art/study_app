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

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

# -----------------------------------------------------------------------------
# 3. 1,500자 이상 초밀착 입시 컨설팅 AI 프롬프트 엔진
# -----------------------------------------------------------------------------
def generate_ai_report(basic_info, survey_answers):
    prompt_content = f"""
    당신은 대한민국 최고 수준의 고등 수학 전문 대입 입시 컨설턴트입니다. 
    학생이 작성한 진단 데이터와 설문 응답을 바탕으로, 마치 1:1 대면 컨설팅 룸에서 정성껏 케어해주는 듯한 **최소 1,500자 이상의 초밀착 개별 맞춤 솔루션 리포트**를 작성해 주세요.

    [학생 기본 프로필]
    - 과목 및 범위: {basic_info.get('subject')} ({basic_info.get('exam_type')})
    - 현재 성적: 전교 {basic_info.get('student_rank')}위 / 전체 {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, {basic_info.get('calc_grade')}등급)
    - 목표 성적: {basic_info.get('target_grade')}등급 (시험까지 D-{basic_info.get('days')}일)
    - 학교 출제 경향: {basic_info.get('region_level')}

    [학생 정밀 설문 답변 모음]
    {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

    [작성 요구사항 및 목차 구조 - 필수 1500자 이상]
    글자 수가 부족하지 않도록 아래 5가지 목차에 따라 학생 하나만을 위한 정밀 진단서를 구체적이고 정성스럽게 서술하세요.

    1. **[1:1 총평 및 학업 위치 정밀 진단]**
       - 학생의 현재 백분위({basic_info.get('pct')}%)와 목표 등급 간의 격차를 수학 입시 팩트에 입각해 진단.
       - 공감과 따뜻한 격려로 시작하되, 현재 상태에 대한 냉철한 진단 제시.

    2. **[설문 응답 기반 약점 패턴 3차원 심층 분석]**
       - Q1~Q10 질문 중 학생이 고른 답변을 최소 4개 이상 '직접 인용'하며, 왜 그 습관이 성적을 정체시키는지 원인 분석.
       - 오답 패턴, 막혔을 때의 행동, 취약 단원, 오답 주기 등을 연결하여 학생의 성향을 완벽히 케어해주는 어조로 작성.

    3. **[학교 출제 유형 맞춤 교재 및 학습 전략]**
       - {basic_info.get('region_level')} 출제 스타일에 맞춰 완독해야 할 시중 교재 2~3권을 추천하고 그 이유를 구체적으로 설명.

    4. **[AI 맞춤 D-{basic_info.get('days')} 초밀착 일차별 학습 커리큘럼]**
       - 남은 {basic_info.get('days')}일을 계산하여, 1일차부터 D-DAY까지의 학습 계획을 일차별(또는 주차별/구간별)로 AI가 직접 세부적으로 완성해 줄 것.
       - 추천한 교재와 단원 공부법을 일차별 계획 속에 구체적으로 명시.

    5. **[실전 시험장 멘탈 및 타임어택 페이스메이킹 처방]**
       - 시험 당일 50분 동안 유용하게 쓸 수 있는 타임어택 전략 및 감점 최소화 팁 제공.

    * 작성 팁: HTML 태그(<b>, <br>, <h3> 등)를 활용하여 가독성을 극대화하고 풍성한 분량으로 서술해 주세요.
    """

    if not OPENAI_API_KEY:
        # API 키 미설정 시에도 풍부한 분량을 제공하는 Fallback 템플릿
        return f"""
        <h3>🩺 1:1 초밀착 AI 입시 컨설팅 리포트</h3>
        <p><b>안녕하세요, 학생분.</b> 현재 {basic_info.get('subject')} 과목에서 목표로 하는 {basic_info.get('target_grade')}등급 달성을 위해, 작성해주신 데이터를 바탕으로 정밀 진단을 시작해보겠습니다.<br>
        현재 전교 {basic_info.get('student_rank')}위(상위 {basic_info.get('pct')}%)로 {basic_info.get('calc_grade')}등급권에 위치해 있습니다. 목표 등급 진입을 위해서는 고난도 변형 문항에서의 정답률 확보가 필수적입니다.</p>

        <hr>
        <h4>1. 설문 응답 기반 약점 패턴 정밀 분석</h4>
        <p>• <b>오답 감점 패턴:</b> 학생분께서는 <i>"{survey_answers.get('Q1. 시험에서 가장 자주 발생하는 오답/감점 패턴은?')}"</i>을 가장 큰 문제로 꼽아주셨습니다. 이는 계산 능력의 부족보다는 실전 시간 압박 시 시야가 좁아지며 발생하는 전형적인 '조급함에 의한 오답'입니다.<br>
        • <b>문제 해결 행동:</b> 막혔을 때 <i>"{survey_answers.get('Q2. 수학 문제를 풀다가 막혔을 때 주로 보이는 행동은?')}"</i>라는 습관은 스스로 조건의 힌트를 찾아내는 사고력을 약화시킵니다. 앞으로는 최소 5분간 조건에 밑줄을 치며 재해석하는 훈련이 필요합니다.<br>
        • <b>취약 단원 관리:</b> <i>"{survey_answers.get('Q3. 가장 취약하거나 두려움을 느끼는 단원 유형은?')}"</i>에 대한 두려움은 기초 개념 약화라기보다는 대표 유형 연습량의 부족에서 비롯됩니다.</p>

        <hr>
        <h4>2. AI 추천 맞춤 교재 및 출제 전략 ({basic_info.get('region_level')})</h4>
        <p>선택하신 학교 출제 난이도 유형에 맞춰 <b>[개념원리 RPM]</b>으로 유형별 정답률을 90% 이상으로 끌어올린 후, <b>[쎈 (SSEN)]</b>과 <b>[내신 고쟁이]</b>의 B~C단계를 통해 변형 문항 적응력을 기르는 것을 강력히 추천합니다.</p>

        <hr>
        <h4>3. AI 맞춤 D-{basic_info.get('days')} 일차별 학습 스케줄</h4>
        <p><b>• 1일차 ~ {max(2, basic_info.get('days')//3)}일차:</b> 취약 단원 대표 유형 완전 정복 및 [개념원리 RPM] 전 문항 풀이<br>
        <b>• {max(2, basic_info.get('days')//3)+1}일차 ~ {max(4, (basic_info.get('days')*2)//3)}일차:</b> [쎈] B, C단계 심화 유형 풀이 및 오답 1차 회독<br>
        <b>• {max(4, (basic_info.get('days')*2)//3)+1}일차 ~ D-{basic_info.get('days')}일 (직전 파이널):</b> 기출 변형 타임어택 훈련 및 오답 키워드 요약노트 최종 점검</p>
        """

    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        data = {
            "model": "gpt-4o-mini", # 풍부하고 완성도 높은 장문 생성을 위한 모델
            "messages": [
                {"role": "system", "content": "You are a warm, highly-detailed, and expert high school math admissions consultant in South Korea. Write in professional and empathetic Korean with a comprehensive length over 1,500 characters."},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": 0.7
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 진단 생성 도중 오류가 발생했습니다: {str(e)}"

# -----------------------------------------------------------------------------
# 4. 화면 렌더링
# -----------------------------------------------------------------------------

def render_home():
    st.markdown("""
        <div class="app-card">
            <div class="pill-badge">GENERATIVE AI SOLUTION</div>
            <div class="app-header">고등 수학 내신 초밀착 맞춤 솔루션</div>
            <div class="app-subtext">GPT AI 기반 1,500자 정밀 리포트 및 문항별 랩타임 분석기</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("AI 정밀 진단 시작하기"):
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

        if st.form_submit_button("다음: 초밀착 맞춤 정밀 설문"):
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

def render_survey_custom():
    st.markdown("""
        <div style="margin-bottom: 16px;">
            <div class="pill-badge">STEP 2 / 2</div>
            <div class="app-header">초밀착 1:1 맞춤 진단 설문</div>
            <div class="app-subtext">AI 입시 컨설턴트가 하나하나 세심하게 분석할 수 있도록 솔직한 습관을 골라주세요.</div>
        </div>
    """, unsafe_allow_html=True)

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

        if st.form_submit_button("🎓 1:1 AI 입시 컨설팅 심층 리포트 생성"):
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
            <div class="pill-badge">VIP AI CONSULTING REPORT</div>
            <div class="app-header">1:1 AI 초밀착 심층 컨설팅 리포트</div>
            <div class="app-subtext">수학 입시 팩트에 기반하여 생성된 1,500자 이상의 맞춤 케어 분석서입니다.</div>
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
                현재 <b>{info['calc_grade']}등급</b> ➔ 목표 <b>{info['target_grade']}등급</b> (D-{info['days']}일) | {info['region_level']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # AI 호출 및 결과 표시
    with st.spinner("🎓 입시 컨설턴트 AI가 설문 답변 하나하나를 정밀하게 분석하여 1:1 맞춤 리포트를 작성하고 있습니다..."):
        ai_report_html = generate_ai_report(info, survey)

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-badge">PREMIUM CARE REPORT</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="line-height: 1.85; font-size: 15px; color: #333D4B !important;">{ai_report_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()

# -----------------------------------------------------------------------------
# 5. 수학 문항별 랩타임 분석 타이머
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
# 6. 라우팅
# -----------------------------------------------------------------------------
if st.session_state.page == 'home': render_home()
elif st.session_state.page == 'basic_input': render_basic_input()
elif st.session_state.page == 'survey_custom': render_survey_custom()
elif st.session_state.page == 'result': render_result()
elif st.session_state.page == 'stopwatch': render_stopwatch()
