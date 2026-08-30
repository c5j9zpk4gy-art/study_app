import streamlit as st
import time
import json
import google.generativeai as genai

# 1. 페이지 및 CSS 디자인 설정 (이모지 제거, 모던 소프트 라운드 UI)
st.set_page_config(page_title="Math Analytics & Consulting", layout="centered")

custom_css = """
<style>
    /* 메인 배경 및 폰트 설정 */
    .main {
        background-color: #FAFAFA;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 카드 스타일링 */
    .css-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #EFEFEF;
        margin-bottom: 20px;
    }
    
    /* 버튼 스타일링 */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        transition: all 0.2s ease;
    }
    
    /* 입력 폼 라운드 처리 */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        border-radius: 10px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. 세션 상태 초기화 (계정 및 데이터 지속성)
if 'user_profile' not in st.session_state: st.session_state.user_profile = None
if 'basic_info' not in st.session_state: st.session_state.basic_info = {}
if 'survey_answers' not in st.session_state: st.session_state.survey_answers = {}
if 'generated_report' not in st.session_state: st.session_state.generated_report = ""
if 'solve_logs' not in st.session_state: st.session_state.solve_logs = []
if 'planner_tasks' not in st.session_state: st.session_state.planner_tasks = []
if 'error_notes' not in st.session_state: st.session_state.error_notes = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'current_view' not in st.session_state: st.session_state.current_view = 'dashboard'
if 'confirm_reset' not in st.session_state: st.session_state.confirm_reset = False

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 3. AI 스트리밍 로직 (리포트 생성)
def generate_ai_report_stream(basic_info, survey_answers, solve_logs):
    api_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")
    if not api_key:
        yield "API 키가 설정되지 않았습니다. Secrets에 GEMINI_API_KEY를 등록해주세요."
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')

        lap_summary = "측정된 랩타임 기록 없음"
        if solve_logs:
            total_q = len(solve_logs)
            avg_time = round(sum(log['time'] for log in solve_logs) / total_q, 1)
            over_q = sum(1 for log in solve_logs if "지연" in log['status'] or "주의" in log['status'])
            lap_summary = f"총 {total_q}문항 측정, 평균 풀이시간 {avg_time}초, 지연 문항 수: {over_q}개"

        prompt_content = f"""
        당신은 고등 수학 전문 대입 입시 컨설턴트입니다.
        아래 학생 데이터를 바탕으로 정밀 진단 리포트를 작성하세요.

        [내신 등급 체계 기준]
        고교학점제 5등급제 기준을 엄격히 적용하세요.
        - 1등급: 상위 10% 이내 / 2등급: 10% 초과 ~ 34% 이내 / 3등급: 34% 초과 ~ 66% 이내 / 4등급: 66% 초과 ~ 90% 이내 / 5등급: 90% 초과 ~ 100% 이내

        [학생 프로필 Data]
        - 학생명: {basic_info.get('student_name')}
        - 과목 및 시험: {basic_info.get('subject')} ({basic_info.get('exam_type')})
        - 현재 성적: 전교 {basic_info.get('student_rank')}등 / 전체 {basic_info.get('total_students')}명 (상위 {basic_info.get('pct')}%, 5등급제 현재 등급: {basic_info.get('calc_grade')}등급)
        - 목표 성적: {basic_info.get('target_grade')}등급 (D-{basic_info.get('days')}일)
        - 출제 스타일: {basic_info.get('region_level')}
        - 주교재 및 약점 단원: {basic_info.get('textbook_info')}
        - 주요 걸림돌: {basic_info.get('user_obstacle')}
        - 랩타임 데이터: {lap_summary}

        [설문 응답 Data]
        {json.dumps(survey_answers, ensure_ascii=False, indent=2)}

        [출력 형식]
        1. 특수문자 오류(취소선 등)를 방지하고 굵은 글씨만 사용하시오.
        2. 아래 양식을 정확히 준수하시오.

        ## 1. 종합 학업 위치 및 목표 달성 가능성 정밀 진단
        - 현재 위치 평가:
        - 핵심 총평:

        ## 2. 설문 및 랩타임 기반 약점 원인 분석
        - 학습량 및 오답 원인 분석:
        - 실전 타임어택 및 랩타임 진단:
        - 개념 체계 및 주교재 분석:

        ## 3. 목표 등급 달성을 위한 3대 핵심 행동 교정 솔루션
        - 솔루션 1 [학습 방식]:
        - 솔루션 2 [오답 및 복습]:
        - 솔루션 3 [실전 타임어택]:

        ## 4. D-{basic_info.get('days')} 초밀착 주차별 전략 스케줄
        | 기간 | 핵심 목표 | 학습 범위 | 일일 권장 학습량 |
        | :--- | :--- | :--- | :--- |
        | D-{basic_info.get('days')} ~ D-{max(basic_info.get('days')-10, 1)} | 개념 정립 및 필수 유형 파독 | (주교재 기반) | (시간 및 문제 수) |
        | D-{max(basic_info.get('days')-10, 1)} ~ D-5 | 고난도 킬러 문제 및 기출 회독 | (주교재 기반) | (시간 및 문제 수) |
        | D-5 ~ D-Day | 실전 모의고사 및 오답 최종 점검 | (실전 모의고사) | (시간 및 문제 수) |

        ## 5. 입시 컨설턴트의 최종 제언
        """

        response = model.generate_content(prompt_content, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"오류가 발생했습니다: {str(e)}"

# 4. 화면 렌더링 - 온보딩 (로그인 / 프로필 입력)
def render_onboarding():
    st.title("Math Analytics Solution")
    st.caption("개인 맞춤형 고등 수학 학습 진단 및 관리 플랫폼")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("학습 프로필 등록")
    
    with st.form("onboarding_form"):
        student_name = st.text_input("학생 이름", placeholder="홍길동")
        subject = st.selectbox("진단 과목", ["공통수학1", "공통수학2", "대수", "미적분I", "확률과 통계"])
        exam_type = st.radio("시험 범위", ["중간고사", "기말고사", "전범위"], horizontal=True)
        
        col1, col2 = st.columns(2)
        with col1:
            total_students = st.number_input("전교 학생 수", min_value=10, max_value=1000, value=200)
            student_rank = st.number_input("현재 전교 석차", min_value=1, max_value=1000, value=15)
        with col2:
            target_grade = st.selectbox("목표 내신 등급 (5등급제)", [1, 2, 3, 4, 5], index=0)
            days = st.number_input("시험 D-Day", min_value=7, max_value=120, value=30)
            
        region_level = st.radio("출제 스타일", [
            "1유형: 강남/자사고 고난도 변형",
            "2유형: 일반고 심화 기출 변형",
            "3유형: 표준 유형서 및 교과서 중심",
            "4유형: 기본 개념 원형 출제"
        ])
        
        textbook_info = st.text_input("주교재 및 취약 단원", placeholder="예: 쎈 수학 / 이차함수")
        user_obstacle = st.text_input("주요 학습 걸림돌", placeholder="예: 문제 적용력 부족, 계산 실수")

        if st.form_submit_button("다음: 학습 습관 정밀 진단", use_container_width=True):
            if not student_name:
                st.error("이름을 입력해 주세요.")
                return
            
            pct = round((student_rank / total_students) * 100, 2)
            calc_grade = 1 if pct <= 10.0 else (2 if pct <= 34.0 else (3 if pct <= 66.0 else (4 if pct <= 90.0 else 5)))
            
            st.session_state.basic_info = {
                "student_name": student_name, "subject": subject, "exam_type": exam_type,
                "total_students": int(total_students), "student_rank": int(student_rank),
                "pct": pct, "calc_grade": calc_grade, "target_grade": target_grade,
                "days": int(days), "region_level": region_level,
                "textbook_info": textbook_info or "미입력", "user_obstacle": user_obstacle or "미입력"
            }
            st.session_state.current_view = 'survey'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 5. 화면 렌더링 - 설문지 (단일 제출 버튼 적용)
def render_survey():
    st.title("학습 습관 진단")
    st.caption("학생의 정확한 학습 행동 원인을 진단합니다.")

    tab1, tab2, tab3 = st.tabs(["학습량 & 교재", "오답 & 실전력", "개념 & 멘탈"])

    with st.form("survey_form"):
        with tab1:
            q1 = st.radio("Q1. 수학 공부 집중도가 떨어지는 가장 큰 이유는?", [
                "타 과목 숙제와 수행평가로 인한 시간 부족",
                "딴생각 및 집중력 저하",
                "고난도 문항 직면 시 의욕 저하",
                "꾸준히 목표 시간을 달성하는 편임"
            ])
            q2 = st.radio("Q2. 해설지를 참조하게 되는 주된 원인은?", [
                "접근 아이디어 미도출",
                "식 변형 및 연산 과정의 복잡함",
                "문제 조건 해석 오류",
                "고민 시간 단축 선호"
            ])

        with tab2:
            q3 = st.radio("Q3. 틀린 문제의 재복습이 미흡한 이유는?", [
                "눈으로만 이해하고 점검 생략",
                "답 재확인 후 풀이 정밀도 미검증",
                "시차를 둔 재풀이 미실시",
                "원인 분석 없는 문제 풀이 반복"
            ])
            q4 = st.radio("Q4. 시험 중 계산 실수가 발생하는 계기는?", [
                "시간 부족으로 인한 조급함",
                "풀이 공간 미정리로 인한 연산 착오",
                "제한 조건 미확인",
                "검산 습관 부재"
            ])

        with tab3:
            q5 = st.radio("Q5. 킬러 문항 접할 때의 대처 방식은?", [
                "즉시 포기",
                "개념 융합 능력 부족",
                "시간 압박으로 인한 아이디어 미도출",
                "다각도 분석 시도"
            ])
            q6 = st.radio("Q6. 시험지 운용 전략은?", [
                "순차 풀이 고수",
                "막힘 발생 시 페이스 흔들림",
                "쉬운 문항 우선 해결",
                "시간 배분 계획 준수"
            ])

            st.divider()
            # 마지막 탭 하단에만 단일 리포트 생성 버튼 배치
            if st.form_submit_button("진단 완료 및 분석 리포트 생성", use_container_width=True):
                st.session_state.survey_answers = {
                    "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5, "Q6": q6
                }
                st.session_state.user_profile = st.session_state.basic_info['student_name']
                st.session_state.current_view = 'report_loading'
                st.rerun()

# 6. 화면 렌더링 - 대시보드 (메인 제어 센터)
def render_dashboard():
    info = st.session_state.basic_info
    
    # 상단 프로필 헤더
    st.title(f"{info['student_name']} 님의 학습 대시보드")
    st.caption(f"{info['subject']} ({info['exam_type']}) | 현재 {info['calc_grade']}등급 (상위 {info['pct']}%) ➔ 목표 {info['target_grade']}등급 (D-{info['days']})")
    
    st.divider()

    # 4가지 메인 기능 카드 버튼
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("진단 리포트")
        st.write("AI가 분석한 정밀 리포트 및 솔루션을 확인합니다.")
        if st.button("리포트 보기", key="btn_rep", use_container_width=True):
            st.session_state.current_view = 'report_view'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("오답 정복 노트")
        st.write("틀린 문제와 원인을 기록하고 통계를 분석합니다.")
        if st.button("오답노트 관리", key="btn_err", use_container_width=True):
            st.session_state.current_view = 'error_note'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("D-Day 플래너")
        st.write("목표 달성을 위한 일차별 학습 체크리스트입니다.")
        if st.button("플래너 열기", key="btn_plan", use_container_width=True):
            st.session_state.current_view = 'planner'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("1:1 AI Q&A")
        st.write("공부법 및 리포트 내용에 대해 AI와 상담합니다.")
        if st.button("AI 상담 시작", key="btn_chat", use_container_width=True):
            st.session_state.current_view = 'chat'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 하단 안전 초기화 영역
    st.markdown("### 계정 관리")
    if not st.session_state.confirm_reset:
        if st.button("처음부터 다시 시작 (프로필 초기화)", use_container_width=False):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        st.warning("모든 진단 데이터와 오답 노드가 삭제됩니다. 계속하시겠습니까?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("예, 초기화합니다", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with c2:
            if st.button("취소", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

# 7. 세부 기능 페이지들
def render_report_view():
    st.title("AI 정밀 진단 리포트")
    if st.button("대시보드로 돌아가기"):
        st.session_state.current_view = 'dashboard'
        st.rerun()
    
    st.divider()

    if st.session_state.current_view == 'report_loading' or not st.session_state.generated_report:
        report_placeholder = st.empty()
        full_text = ""
        for chunk in generate_ai_report_stream(st.session_state.basic_info, st.session_state.survey_answers, st.session_state.solve_logs):
            full_text += chunk
            report_placeholder.markdown(full_text)
        st.session_state.generated_report = full_text
        st.session_state.current_view = 'report_view'
    else:
        st.markdown(st.session_state.generated_report)

    st.divider()
    st.download_button(
        label="리포트 파일(.md) 다운로드",
        data=st.session_state.generated_report,
        file_name=f"{st.session_state.basic_info['student_name']}_수학_진단_리포트.md",
        mime="text/markdown"
    )

def render_planner():
    st.title("D-Day 학습 플래너")
    if st.button("대시보드로 돌아가기"):
        st.session_state.current_view = 'dashboard'
        st.rerun()

    st.divider()
    
    # 기본 체크리스트 생성 (초기 1회)
    if not st.session_state.planner_tasks:
        days = st.session_state.basic_info.get('days', 30)
        st.session_state.planner_tasks = [
            {"day": f"D-{days}", "task": "기본 개념 및 정의 정독", "done": False},
            {"day": f"D-{days-2}", "task": "주교재 대표 유형 풀이", "done": False},
            {"day": f"D-{days-5}", "task": "오답 유형 1차 재풀이", "done": False},
            {"day": "D-5", "task": "실전 기출 모의고사 1회차", "done": False},
            {"day": "D-1", "task": "최종 약점 단원 점검", "done": False}
        ]

    # 달성률 계산
    completed = sum(1 for t in st.session_state.planner_tasks if t['done'])
    total = len(st.session_state.planner_tasks)
    progress = completed / total if total > 0 else 0

    st.markdown(f"**학습 달성률**: {int(progress * 100)}%")
    st.progress(progress)

    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    for idx, task in enumerate(st.session_state.planner_tasks):
        st.session_state.planner_tasks[idx]['done'] = st.checkbox(
            f"[{task['day']}] {task['task']}", 
            value=task['done'], 
            key=f"task_{idx}"
        )
    st.markdown('</div>', unsafe_allow_html=True)

def render_error_note():
    st.title("오답 정복 노트")
    if st.button("대시보드로 돌아가기"):
        st.session_state.current_view = 'dashboard'
        st.rerun()

    st.divider()

    # 오답 등록 폼
    with st.expander("신규 오답 등록하기", expanded=True):
        with st.form("error_form"):
            q_title = st.text_input("문제 출처/번호", placeholder="예: 쎈 345번")
            unit = st.text_input("단원명", placeholder="예: 이차함수와 직선의 위치관계")
            reason = st.selectbox("오답 원인", ["개념 미숙", "연산 실수", "조건 미확인", "시간 부족", "아이디어 미도출"])
            memo = st.text_area("복습 메모", placeholder="실수 원인이나 핵심 풀이 포인트를 적으세요.")
            
            if st.form_submit_button("오답 등록", use_container_width=True):
                st.session_state.error_notes.append({
                    "title": q_title, "unit": unit, "reason": reason, "memo": memo
                })
                st.success("오답이 기록되었습니다.")
                st.rerun()

    # 오답 목록 및 통계
    if st.session_state.error_notes:
        st.markdown("### 누적 오답 기록")
        for i, note in enumerate(reversed(st.session_state.error_notes), 1):
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.markdown(f"**{note['title']}** ({note['unit']})")
            st.caption(f"원인: {note['reason']}")
            st.write(note['memo'])
            st.markdown('</div>', unsafe_allow_html=True)

def render_chat():
    st.title("1:1 AI 학습 컨설팅 Q&A")
    if st.button("대시보드로 돌아가기"):
        st.session_state.current_view = 'dashboard'
        st.rerun()

    st.divider()

    # 기존 대화 기록 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 사용자 질의 입력
    if prompt := st.chat_input("공부법이나 리포트에 대해 궁금한 점을 물어보세요."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # AI 응답 생성
        with st.chat_message("assistant"):
            api_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                context_prompt = f"""
                학생 이름: {st.session_state.basic_info.get('student_name')}
                진단 과목: {st.session_state.basic_info.get('subject')}
                현재 등급: {st.session_state.basic_info.get('calc_grade')}등급
                질문: {prompt}
                위 학생의 프로필을 고려하여 명확하고 친절하게 답변하세요.
                """
                response = model.generate_content(context_prompt)
                st.write(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# 8. 앱 라우팅 및 뷰 제어
if st.session_state.user_profile is None:
    if st.session_state.current_view == 'survey':
        render_survey()
    else:
        render_onboarding()
else:
    if st.session_state.current_view == 'dashboard':
        render_dashboard()
    elif st.session_state.current_view in ['report_view', 'report_loading']:
        render_report_view()
    elif st.session_state.current_view == 'planner':
        render_planner()
    elif st.session_state.current_view == 'error_note':
        render_error_note()
    elif st.session_state.current_view == 'chat':
        render_chat()
