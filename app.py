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
if 'generated_report' not in st.session_state: st.session_state.generated_report = ""

# Streamlit Secrets에서 Gemini API 키 로드
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 3. AI 리포트 생성 스트리밍 함수 (5등급제, 랩타임 연동, 스트리밍 출력 적용)
def generate_ai_report_stream(basic_info, survey_answers, solve_logs):
    api_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")

    if not api_key:
        yield "⚠️ **서버에 Gemini API 키가 설정되지 않았습니다.**\nStreamlit Cloud Settings -> Secrets에 GEMINI_API_KEY를 등록해주세요."
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')

        # 랩타임 데이터 요약 계산
        lap_summary = "측정된 랩타임 기록 없음"
        if solve_logs:
            total_q = len(solve_logs)
            avg_time = round(sum(log['time'] for log in solve_logs) / total_q, 1)
            over_q = sum(1 for log in solve_logs if "경고" in log['status'] or "주의" in log['status'])
            lap_summary = f"총 {total_q}문항 측정, 문항당 평균 풀이시간 {avg_time}초, 목표시간 초과/지연 문항 수: {over_q}개"

        prompt_content = f"""
        당신은 대한민국 대치동 최고 수준의 고등 수학 전문 대입 입시 컨설턴트입니다.
        아래 입력된 학생의 프로필, 랩타임 측정 데이터, 심층 학습 습관/이유 응답을 바탕으로 1:1 맞춤형 컨설팅 리포트를 작성하세요.

        [⚠️ 내신 등급 체계 기준]
        이 평가 시스템은 **'고교학점제 5등급제'** 기준입니다. 아래 기준을 엄격히 적용하세요.
        - 1등급: 상위 10% 이내 / 2등급: 10% 초과 ~ 34% 이내 / 3등급: 34% 초과 ~ 66% 이내 / 4등급: 66% 초과 ~ 90% 이내 / 5등급: 90% 초과 ~ 100% 이내

        [학생 프로필 데이터]
        - 과목 및 시험: {basic_info.get('subject')} ({basic_info.get('exam_type')})
        - 현재 성적: 전교 {basic_info.get('student_rank')}등 / 전체 {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, 5등급제 현재 등급: {basic_info.get('calc_grade')}등급)
        - 목표 성적: {basic_info.get('target_grade')}등급 (남은 기간: D-{basic_info.get('days')}일)
        - 출제 스타일: {basic_info.get('region_level')}
        - 주교재 및 약점 단원: {basic_info.get('textbook_info')}
        - 본인이 느낀 최대 걸림돌: {basic_info.get('user_obstacle')}

        [학생 실전 랩타임 측정 데이터]
        - {lap_summary}

        [학생 심층 설문 응답 (행동 이유 및 환경)]
        {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

        [출력 형식 필수 규칙]
        1. 취소선(~~)이나 물결표(~), 굵은 가로줄 오류를 유발하는 잘못된 마크다운 특수문자를 절대 사용하지 마시오.
        2. 텍스트 강조는 오직 **굵은 글씨**만 사용하시오.
        3. 아래 제시된 [리포트 표준 출력 양식]의 목차와 틀을 단 하나도 변경하지 말고 똑같이 유지하여 작성하시오.

        ---
        [리포트 표준 출력 양식]

        ## 1. 종합 학업 위치 및 목표 달성 가능성 정밀 진단
        - **현재 위치 평가**: (5등급제 기준 상위 백분율 및 현재 등급 위치 분석, 목표 등급 달성을 위한 현실적 전교 석차 격차 서술)
        - **핵심 총평**: (학생이 입력한 걸림돌과 현재 위치를 관통하는 한 줄 입시 총평)

        ## 2. 설문 및 랩타임 기반 약점 원인 분석
        - **학습량 및 오답 원인 분석**: (설문 응답에서 언급된 '이유'들을 직접 인용하여 분석)
        - **실전 타임어택 및 랩타임 진단**: (실제 측정된 문항당 평균 풀이시간 및 초과 문항 데이터를 직접 언급하며 분석)
        - **개념 체계 및 주교재 분석**: (입력받은 주교재 및 약점 단원에 맞춤 분석)

        ## 3. 목표 등급 달성을 위한 3대 핵심 행동 교정 솔루션
        - **솔루션 1 [학습 방식]**: (학생의 주교재/약점 단원에 맞춘 구체적 행동 지침)
        - **솔루션 2 [오답 및 복습]**: (오답을 만드는 근본 원인 해결 지침)
        - **솔루션 3 [실전 타임어택]**: (랩타임 데이터 기반 시간 단축 전략)

        ## 4. D-{basic_info.get('days')} 초밀착 주차별/일차별 전략 스케줄
        | 기간 | 핵심 목표 | 주교재 & 부교재 학습 범위 | 일일 권장 학습량 |
        | :--- | :--- | :--- | :--- |
        | D-{basic_info.get('days')} ~ D-{max(basic_info.get('days')-10, 1)} | 개념 정립 및 필수 유형 파독 | (입력된 주교재 기반 작성) | (시간 및 문제 수 지정) |
        | D-{max(basic_info.get('days')-10, 1)} ~ D-5 | 고난도 킬러 문제 및 기출 회독 | (입력된 주교재 기반 작성) | (시간 및 문제 수 지정) |
        | D-5 ~ D-Day | 실전 모의고사 및 오답 최종 점검 | (실전 모의고사 및 오답노트) | (시간 및 문제 수 지정) |

        ## 5. 입시 컨설턴트의 최종 격려 및 제언
        (학생의 의지를 북돋아주고 실행을 강조하는 따뜻하고 구체적인 마무리 제언)
        """

        response = model.generate_content(prompt_content, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"⚠️ AI 생성 중 오류가 발생했습니다: {str(e)}"

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
    st.title("1단계: 기본 프로필 & 환경 입력")
    with st.form("basic_info_form"):
        subject = st.selectbox("진단 과목", ["공통수학1", "공통수학2", "대수", "미적분I", "확률과 통계"])
        exam_type = st.radio("시험 범위", ["중간고사", "기말고사", "전범위"], horizontal=True)
        col1, col2 = st.columns(2)
        with col1:
            total_students = st.number_input("전교 학생 수 (명)", min_value=10, max_value=1000, value=200, step=1)
            student_rank = st.number_input("현재 수학 전교 석차 (등)", min_value=1, max_value=1000, value=15, step=1)
        with col2:
            target_grade = st.selectbox("목표 내신 등급 (5등급제 기준)", [1, 2, 3, 4, 5], index=0)
            days = st.number_input("시험까지 남은 기간 (일)", min_value=7, max_value=120, value=30, step=1)
        
        region_level = st.radio("학교 시험 출제 스타일", [
            "1유형: 강남/자사고 스타일 (킬러 문항 및 변형 비중 매우 높음)",
            "2유형: 일반고 심화 스타일 (시중 심화서 및 모의고사 변형 위주)",
            "3유형: 표준 내신 스타일 (유형서 및 교과서 충실 변형)",
            "4유형: 기본 개념 스타일 (교과서 중심 원형 출제)"
        ])

        st.divider()
        st.markdown("**주관식 초밀착 맞춤 정보**")
        textbook_info = st.text_input("현재 사용 중인 주교재 및 가장 약한 단원", placeholder="예: 쎈 수학 / 이차함수의 최대최소 단원")
        user_obstacle = st.text_input("내가 생각하는 내 수학 성적의 가장 큰 걸림돌", placeholder="예: 개념은 아는데 문제를 보면 아이디어가 안 떠오름, 계산 실수가 많음")

        if st.form_submit_button("다음: 심층 학습 습관 및 이유 진단하기", use_container_width=True):
            pct = round((student_rank / total_students) * 100, 2)
            calc_grade = 1 if pct <= 10.0 else (2 if pct <= 34.0 else (3 if pct <= 66.0 else (4 if pct <= 90.0 else 5)))
            st.session_state.basic_info = {
                "subject": subject, "exam_type": exam_type, "total_students": int(total_students),
                "student_rank": int(student_rank), "pct": pct, "calc_grade": calc_grade,
                "target_grade": target_grade, "days": int(days), "region_level": region_level,
                "textbook_info": textbook_info if textbook_info else "미입력",
                "user_obstacle": user_obstacle if user_obstacle else "미입력"
            }
            st.session_state.page = 'survey_custom'
            st.rerun()

    if st.button("메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()

def render_survey_custom():
    st.title("2단계: 심층 학습 습관 및 원인 진단")
    st.progress(0.66, text="진행률: 2/3 단계 완료")

    # 이유 및 시나리오 중심 질문 재설계
    tab1, tab2, tab3 = st.tabs(["📚 학습량 & 교재", "✏️ 오답 & 실전력", "🧠 개념 & 시험 멘탈"])

    survey_answers = {}

    with st.form("survey_custom_form"):
        with tab1:
            st.markdown("### 1. 학습량 및 교재 활용 스타일")
            q1 = st.radio("Q1. 평일 수학 공부 집중도가 떨어지거나 시간을 못 채우는 가장 큰 이유는?", [
                "타 과목 숙제와 수행평가가 밀려서 수학 시간이 밀린다.",
                "책상에 오래 앉아있지만 딴생각을 하거나 스마트폰을 자주 본다.",
                "조금만 어려운 문제를 만나면 의욕이 꺾여 장시간 딴짓을 한다.",
                "꾸준히 집중하여 목표한 공부 시간을 차분히 채우는 편이다."
            ])
            q2 = st.radio("Q2. 문제를 풀다가 막혔을 때 해설지를 참조하게 되는 주된 원인은?", [
                "어떤 공식과 개념을 적용할지 접근 아이디어 자체가 안 떠올라서",
                "아이디어는 떠오르는데 식 변형 및 연산 과정이 너무 복잡해서",
                "문제의 제한 조건이나 지문을 잘못 해석해서",
                "고민하는 시간 자체가 아깝고 빨리 다음 문제로 넘어가고 싶어서"
            ])

        with tab2:
            st.markdown("### 2. 오답 복습 및 실전 실수 패턴")
            q3 = st.radio("Q3. 틀린 문제를 다시 풀 때 완전한 복습이 되지 않는 이유는?", [
                "해설지 풀이를 눈으로 이해하면 다 안다고 착각하고 넘어가서",
                "다시 풀어서 답만 맞으면 풀이 과정의 정밀함을 확인하지 않아서",
                "오답노트를 쓰지만 며칠 뒤 시차를 두고 다시 풀어보지 않아서",
                "어떤 유형/개념에서 틀렸는지 원인 분석 없이 문제만 계속 풀어내서"
            ])
            q4 = st.radio("Q4. 실제 시험에서 '계산 실수'가 발생하는 가장 결정적인 순간은?", [
                "시험 후반부 시간이 부족해 마음이 급해져서 풀이가 꼬일 때",
                "풀이 공간이 좁아 연산 과정을 지저분하게 적다가 부호/숫자를 착오할 때",
                "문제의 제한 조건(예: x > 0, 정수 조건 등)을 마지막에 놓칠 때",
                "체계적인 검산 습관이 없어서 오답을 그냥 제출할 때"
            ])

        with tab3:
            st.markdown("### 3. 개념 체계화 및 시험지 운용 전략")
            q5 = st.radio("Q5. 고난도 킬러 문제를 마주했을 때 본인의 반응 및 태도는?", [
                "문제를 읽자마자 막막함을 느끼고 1분 내로 포기한다.",
                "여러 개념을 하나로 융합하여 풀이 순서를 설계하는 것이 어렵다.",
                "시간이 충분하면 풀 수 있으나, 시험장에서는 압박감 때문에 아이디어가 안 떠오른다.",
                "조건을 하나씩 해석하며 다각도로 시도해 본다."
            ])
            q6 = st.radio("Q6. 시험지를 받아 들었을 때 첫 5분 동안의 운영 행동 방식은?", [
                "1번부터 무작정 풀며, 막히는 문제가 나와도 될 때까지 붙잡고 있는다.",
                "막히는 문제를 만나면 당황하여 이후 전체 페이스와 멘탈이 흔들린다.",
                "풀 수 있는 문제부터 스캔하여 빠르게 확보하고 어려운 문제는 뒤로 미룬다.",
                "문항별 배분 시간을 엄격히 설정해두고 스톱워치를 보며 풀이한다."
            ])

        if st.form_submit_button("🎓 1:1 AI 초밀착 컨설팅 리포트 생성하기", use_container_width=True):
            survey_answers["Q1_학습량_저해원인"] = q1
            survey_answers["Q2_해설지_의존이유"] = q2
            survey_answers["Q3_오답복습_약점"] = q3
            survey_answers["Q4_계산실수_원인"] = q4
            survey_answers["Q5_킬러문항_태도"] = q5
            survey_answers["Q6_시험지_운용방식"] = q6
            st.session_state.survey_answers = survey_answers
            st.session_state.page = 'result'
            st.rerun()

def render_result():
    info = st.session_state.basic_info
    survey = st.session_state.survey_answers
    logs = st.session_state.solve_logs

    if not info or not survey:
        st.session_state.page = 'basic_input'
        st.rerun()
        return

    st.title("📋 1:1 AI 초밀착 심층 컨설팅 리포트")
    st.info(f"**{info['subject']} ({info['exam_type']})** | 전교 {info['student_rank']}위 / {info['total_students']}명 ➔ 목표 {info['target_grade']}등급 (5등급제 기준)")

    # 실시간 스트리밍 출력 연동
    if not st.session_state.generated_report:
        report_placeholder = st.empty()
        full_text = ""
        for chunk in generate_ai_report_stream(info, survey, logs):
            full_text += chunk
            report_placeholder.markdown(full_text)
        st.session_state.generated_report = full_text
    else:
        st.markdown(st.session_state.generated_report)

    st.divider()

    # 리포트 다운로드 및 복사 기능 추가
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 리포트 텍스트 파일(.md) 다운로드",
            data=st.session_state.generated_report,
            file_name=f"{info['subject']}_AI_컨설팅_리포트.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        if st.button("🔄 리포트 다시 생성하기", use_container_width=True):
            st.session_state.generated_report = ""
            st.rerun()

    if st.button("처음으로 돌아가기", use_container_width=True):
        st.session_state.generated_report = ""
        st.session_state.page = 'home'
        st.rerun()

def render_stopwatch():
    st.title("⏱️ 수학 1문항 랩타임 분석기")
    st.caption("여기서 측정한 랩타임 기록은 AI 리포트 생성 시 타임어택 분석 데이터로 자동 연동됩니다.")
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
