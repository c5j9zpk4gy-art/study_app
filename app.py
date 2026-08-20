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

# 3. AI 리포트 생성 함수 (Gemini 3.6 Flash & 규격화 템플릿 적용)
def generate_ai_report(basic_info, survey_answers):
    api_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")

    if not api_key:
        return "⚠️ **서버에 Gemini API 키가 설정되지 않았습니다.**\nStreamlit Cloud Settings -> Secrets에 GEMINI_API_KEY를 등록해주세요."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')

        prompt_content = f"""
        당신은 대한민국 대치동 최고 수준의 고등 수학 대입 입시 컨설턴트입니다.
        아래 입력된 학생의 성적 정보와 10가지 상세 습관 설문 응답을 바탕으로, 전문적이고 정돈된 **'1:1 고등 수학 내신 초밀착 심층 컨설팅 리포트'**를 작성하세요.

        [학생 기본 프로필]
        - 과목 및 시험: {basic_info.get('subject')} ({basic_info.get('exam_type')})
        - 현재 성적: 전교 {basic_info.get('student_rank')}등 / 전체 {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, 계산 등급: {basic_info.get('calc_grade')}등급)
        - 목표 성적: {basic_info.get('target_grade')}등급 (남은 기간: D-{basic_info.get('days')}일)
        - 학교 출제 스타일: {basic_info.get('region_level')}

        [학생 상세 설문 응답 데이터]
        {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

        [출력 형식 필수 규칙]
        1. 취소선(~~)이나 물결표(~), 굵은 가로줄 오류를 유발하는 잘못된 마크다운 특수문자를 절대 사용하지 마시오.
        2. 텍스트 강조는 오직 **굵은 글씨**만 사용하고, 수식이나 숫자 강조 시 마크다운 이스케이프 오류가 나지 않도록 주의하시오.
        3. 아래 제시된 [리포트 표준 출력 양식]의 목차와 틀을 단 하나도 변경하지 말고 똑같이 유지하여 작성하시오.

        ---
        [리포트 표준 출력 양식]

        ## 1. 종합 학업 위치 및 목표 달성 가능성 정밀 진단
        - **현재 위치 평가**: (현재 등급 및 상위 백분율 분석, 목표 등급 달성을 위한 현실적 격차 서술)
        - **핵심 총평**: (학생의 현재 상황을 관통하는 한 줄 입시 총평)

        ## 2. 설문 기반 학습 습관 및 약점 패턴 분석
        - **시간 및 몰입도 분석**: (Q1, Q2 응답을 인용하여 학습량과 연속 몰입도 문제점 분석)
        - **교재 및 회독 깊이 분석**: (Q3, Q4 응답을 인용하여 주부교재 활용 방식과 오답 복습 깊이 진단)
        - **시험 실전력 및 멘탈 진단**: (Q5, Q6, Q7 응답을 바탕으로 실전 타임어택, 킬러문항 대응력, 계산 실수 패턴 분석)
        - **개념 체계 및 취약 단원 분석**: (Q8, Q9, Q10 응답을 기반으로 개념 연결 능력과 정형화된 약점 진단)

        ## 3. 목표 등급 달성을 위한 3대 핵심 행동 교정 솔루션
        - **솔루션 1 [학습 방식]**: (구체적 행동 지침)
        - **솔루션 2 [오답 및 복습]**: (구체적 행동 지침)
        - **솔루션 3 [실전 타임어택]**: (구체적 행동 지침)

        ## 4. D-{basic_info.get('days')} 초밀착 주차별/일차별 전략 스케줄
        | 기간 | 핵심 목표 | 주교재 & 부교재 학습 범위 | 일일 권장 학습량 |
        | :--- | :--- | :--- | :--- |
        | D-{basic_info.get('days')} ~ D-{max(basic_info.get('days')-10, 1)} | 개념 정립 및 필수 유형 파독 | (교재명 지정) | (시간 및 문제 수 지정) |
        | D-{max(basic_info.get('days')-10, 1)} ~ D-5 | 고난도 킬러 문제 및 기출 회독 | (교재명 지정) | (시간 및 문제 수 지정) |
        | D-5 ~ D-Day | 실전 모의고사 및 오답 최종 점검 | (교재명 지정) | (시간 및 문제 수 지정) |

        ## 5. 입시 컨설턴트의 최종 격려 및 제언
        (학생의 의지를 북돋아주고 실행을 강조하는 따뜻하고 구체적인 마무리 제언)
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
        region_level = st.radio("학교 시험 출제 스타일", ["1유형: 강남/자사고 스타일 (킬러 문항 및 변형 비중 매우 높음)", "2유형: 일반고 심화 스타일 (시중 심화서 및 모의고사 변형 위주)", "3유형: 표준 내신 스타일 (유형서 및 교과서 충실 변형)", "4유형: 기본 개념 스타일 (교과서 중심 원형 출제)"])

        if st.form_submit_button("다음: 심층 학습 습관 설문 작성하기", use_container_width=True):
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
    st.title("2단계: 10대 심층 학습 습관 진단")
    st.caption("학생의 정확한 학습 패턴을 파악하기 위해 구체적인 질문으로 구성되었습니다.")

    # 질문 및 고밀도 선택지 정의 (10문항)
    questions = [
        ("Q1. 평일 기준 하루 순수 수학 공부 시간과 몰입도는 어떠한가요?", [
            "하루 1시간 미만으로 겨우 과제만 해결하는 수준이다.",
            "하루 1~2시간 투자하며, 개념 정리보다는 문제 풀이에 치중한다.",
            "하루 2~3시간 꾸준히 투자하며, 집중력을 일정하게 유지한다.",
            "하루 3~4시간 이상 몰입하며, 어려운 문제도 끝까지 탐구한다."
        ]),
        ("Q2. 현재 주 교재로 활용 중인 서적의 난이도와 조합은 어떠한가요?", [
            "개념서(개념원리, 개념쎈 등) 중심의 기본 개념 학습 단계이다.",
            "유형서(RPM, 쎈 B단계 등)를 중심으로 중급 문항을 반복 숙달 중이다.",
            "심화서(일품, 블랙라벨, TOT 등)를 메인으로 킬러 문항을 대비 중이다.",
            "수능/모의고사 기출문제집(기출의 고백, 마더텅 등)과 모의고사 변형 문제를 중심으로 풀고 있다."
        ]),
        ("Q3. 문제를 풀다가 막혔을 때(막힘 현상) 해설지를 참조하는 타이밍은 언제인가요?", [
            "2~3분 고민해보고 바로 해설지나 답안을 확인한다.",
            "5~10분 정도 시도해보다가 안 풀리면 해설지의 첫 줄(힌트)을 본다.",
            "최소 15~20분 이상 고민하고, 답지를 안 보고 다음 날 다시 도전한다.",
            "해설지는 절대 보지 않고, 선생님이나 친구에게 아이디어만 질문한다."
        ]),
        ("Q4. 틀린 문제(오답)를 다시 복습할 때 사용하는 구체적인 방식은 무엇인가요?", [
            "해설지의 풀이 과정을 눈으로 훑어보고 이해되면 넘어간다.",
            "틀린 문제 위에 다시 풀어서 답이 맞으면 그대로 마무리한다.",
            "별도의 오답노트나 풀이장에 풀이 과정 전체를 손으로 처음부터 끝까지 직접 작성한다.",
            "오답의 원인(개념 오류, 계산 실수, 조건 미확인)을 분류하고, 며칠 뒤 시차를 두고 재시험을 본다."
        ]),
        ("Q5. 실제 시험에서 '계산 실수'나 '조건 착오'가 발생하는 빈도와 양상은 어떠한가요?", [
            "쉬운 연산이나 부호 착오로 매 시험 2~3문항 이상 실수를 한다.",
            "시험 후반부 시간이 부족해 마음이 급해지면 풀이 과정이 꼬여 실수한다.",
            "문제의 제한 조건(예: 정수 조건, x > 0 등)을 놓쳐서 틀리는 경우가 종종 있다.",
            "풀이 공간을 정돈하여 풀기 때문에 연산 실수는 거의 발생하지 않는다."
        ]),
        ("Q6. 고난도 킬러 문항(상위 4% 변별력 문제)을 접근할 때의 상태는 어떠한가요?", [
            "문제를 읽자마자 막막함을 느끼며 거의 접근하지 못하고 포기한다.",
            "개념은 떠오르나 조건을 종합하여 식을 세우는 단계에서 막힌다.",
            "시간이 충분하면 풀 수 있으나, 제한된 시험 시간 내에는 아이디어가 안 떠오른다.",
            "새로운 유형의 킬러 문제도 조건을 분석하여 다각도로 접근 및 해결이 가능하다."
        ]),
        ("Q7. 시험지 전체를 다룰 때 시간 배분(타임어택) 및 운영 전략은 어떠한가요?", [
            "1번 문제부터 순서대로 풀며, 막히는 문제가 나와도 끝까지 붙잡고 있는다.",
            "막히는 문제가 나오면 당황하여 이후 문제 풀이 전체의 페이스가 흔들린다.",
            "어려운 문제는 일단 넘어가고 아는 문제부터 다 푼 뒤 남은 시간에 도전한다.",
            "문항별 (객관식/서술형) 풀이 배분 시간을 미리 정해두고 스톱워치를 활용해 엄격히 준수한다."
        ]),
        ("Q8. 수학 핵심 개념과 공식의 원리를 타인에게 설명할 수 있는 수준인가요?", [
            "공식은 암기하고 있으나, 왜 그렇게 도출되는지 유도 과정은 잘 모른다.",
            "기본적인 개념 증명은 할 수 있으나, 종합 문제에 개념이 어떻게 적용되는지는 헷갈린다.",
            "개념의 정의와 증명 과정을 정확히 알고 있으며 주요 유형에 적용할 수 있다.",
            "친구에게 개념의 원리와 접근 아이디어를 처음부터 끝까지 체계적으로 설명할 수 있다."
        ]),
        ("Q9. 단원별/유형별 중 가장 약하다고 느끼는 영역은 어디인가요?", [
            "복잡한 식의 계산, 인수분해, 부등식 등 순수 연산 및 식 변형 파트",
            "함수의 그래프 해석, 도형의 방정식 등 시각적/좌표적 이해가 필요한 파트",
            "수열, 확률과 통계, 경우의 수 등 규칙성 찾기 및 조건 분류 파트",
            "새로운 정의나 조건 제시형 문항 등 생소한 응용 파트"
        ]),
        ("Q10. 평소 시험 직전(D-7~D-1) 마무리는 어떤 방식으로 진행하나요?", [
            "새로운 문제집이나 모의고사 회차를 계속해서 새로 풀어본다.",
            "교과서와 학교 프린트 위주로 가볍게 눈으로 읽어보며 정리한다.",
            "그동안 정리해둔 오답노트와 틀린 문제만 집중적으로 재풀이한다.",
            "학교 출제 기출 유형을 바탕으로 자체 모의고사를 보고 실전 감각을 극대화한다."
        ])
    ]

    with st.form("survey_custom_form"):
        answers = {}
        for idx, (q_text, opts) in enumerate(questions, 1):
            st.markdown(f"**{q_text}**")
            ans = st.radio(f"cq_label_{idx}", opts, key=f"cq_{idx}", label_visibility="collapsed")
            answers[q_text] = ans
            st.divider()

        if st.form_submit_button("🎓 1:1 정밀 AI 컨설팅 리포트 생성하기", use_container_width=True):
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

    with st.spinner("🎓 대치동 AI 컨설턴트가 정밀 리포트를 규격에 맞춰 생성 중입니다..."):
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
