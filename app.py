import json
from collections import Counter

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Math Analytics Solution", layout="centered")

st.markdown(
    """
    <style>
        .stApp { background: #f7f8fc; }
        .block-container { max-width: 860px; padding-top: 1.6rem; padding-bottom: 2.5rem; }
        .card {
            background: #fff;
            border: 1px solid #e8ebf3;
            border-radius: 18px;
            padding: 1.1rem 1rem;
            margin: 0.7rem 0;
            box-shadow: 0 6px 18px rgba(20, 30, 55, 0.04);
        }
        .stButton > button, .stDownloadButton > button {
            width: 100%;
            min-height: 46px;
            border-radius: 12px;
            font-weight: 700;
        }
        @media (max-width: 640px) {
            .block-container { padding: 1rem 0.8rem 2rem; }
            h1 { font-size: 1.65rem !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULTS = {
    "current_view": "onboarding",
    "basic_info": {},
    "survey_answers": {},
    "generated_report": "",
    "planner_tasks": [],
    "error_notes": [],
    "chat_history": [],
    "confirm_reset": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip().strip('"').strip("'")


def go(view):
    st.session_state.current_view = view
    st.rerun()


def get_model():
    if not API_KEY:
        return None
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel("gemini-3.6-flash")


def calc_grade(rank, total):
    pct = round(rank / total * 100, 2)
    if pct <= 10:
        grade = 1
    elif pct <= 34:
        grade = 2
    elif pct <= 66:
        grade = 3
    elif pct <= 90:
        grade = 4
    else:
        grade = 5
    return pct, grade


def back_btn():
    if st.button("대시보드로 돌아가기"):
        go("dashboard")


def render_onboarding():
    st.title("Math Analytics Solution")
    st.caption("내신 수학 학습 습관을 진단하고 실행 계획으로 바꾸는 대회용 데모 앱")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("학습 프로필 등록")
    with st.form("onboarding_form"):
        student_name = st.text_input("학생 이름", placeholder="예: 홍길동")
        subject = st.selectbox("진단 과목", ["공통수학1", "공통수학2", "대수", "미적분I", "확률과 통계"])
        exam_type = st.radio("시험 범위", ["중간고사", "기말고사", "전범위"], horizontal=True)

        c1, c2 = st.columns(2)
        with c1:
            total_students = st.number_input("전교 학생 수", min_value=10, max_value=5000, value=200)
            student_rank = st.number_input("현재 전교 석차", min_value=1, max_value=5000, value=15)
        with c2:
            target_grade = st.selectbox("목표 내신 등급", [1, 2, 3, 4, 5])
            days = st.number_input("시험까지 남은 일수", min_value=1, max_value=365, value=30)

        region_level = st.selectbox("출제 스타일", ["고난도 변형 중심", "심화 기출 변형", "표준 유형 및 교과서 중심", "기본 개념 중심"])
        textbook_info = st.text_input("주교재 및 취약 단원", placeholder="예: 쎈 수학 / 이차함수")
        user_obstacle = st.text_input("주요 학습 걸림돌", placeholder="예: 계산 실수, 시간 부족")
        submitted = st.form_submit_button("다음: 학습 습관 진단")

    if submitted:
        name = student_name.strip()
        if not name:
            st.error("학생 이름을 입력해 주세요.")
            return

        total_students = int(total_students)
        student_rank = min(int(student_rank), total_students)
        pct, calc_grade_v = calc_grade(student_rank, total_students)

        st.session_state.basic_info = {
            "student_name": name,
            "subject": subject,
            "exam_type": exam_type,
            "total_students": total_students,
            "student_rank": student_rank,
            "pct": pct,
            "calc_grade": calc_grade_v,
            "target_grade": int(target_grade),
            "days": int(days),
            "region_level": region_level,
            "textbook_info": textbook_info.strip() or "미입력",
            "user_obstacle": user_obstacle.strip() or "미입력",
        }
        go("survey")

    st.markdown("</div>", unsafe_allow_html=True)


def render_survey():
    st.title("학습 습관 진단")
    st.caption("정답이 아니라 가장 가까운 답을 고르면 됩니다.")

    with st.form("survey_form"):
        q1 = st.radio("집중력이 떨어지는 가장 큰 이유", [
            "다른 과목 때문에 시간이 부족하다",
            "딴생각이 많아 집중이 흔들린다",
            "어려운 문제에서 의욕이 떨어진다",
            "대체로 목표 시간을 지킨다",
        ])
        q2 = st.radio("해설지를 보게 되는 주된 이유", [
            "접근 아이디어가 떠오르지 않는다",
            "식 변형과 계산이 복잡하다",
            "문제 조건을 잘못 해석한다",
            "오래 고민하는 것을 피한다",
        ])
        q3 = st.radio("오답 복습이 부족한 이유", [
            "이해만 하고 다시 풀지 않는다",
            "답만 확인하고 풀이를 검증하지 않는다",
            "시간을 두고 재풀이하지 않는다",
            "원인 분석 없이 문제만 반복한다",
        ])
        q4 = st.radio("시험 계산 실수의 주된 계기", [
            "시간이 부족해 조급하다",
            "풀이 공간이 정리되지 않는다",
            "조건을 끝까지 확인하지 않는다",
            "검산 습관이 부족하다",
        ])
        q5 = st.radio("어려운 문항을 만났을 때", [
            "바로 포기하는 편이다",
            "개념을 연결하기 어렵다",
            "시간 압박으로 생각이 막힌다",
            "여러 관점으로 시도한다",
        ])
        q6 = st.radio("시험지 풀이 순서", [
            "처음부터 순서대로 푼다",
            "막히면 흐름이 많이 흔들린다",
            "쉬운 문제부터 먼저 푼다",
            "시간 배분 계획을 지킨다",
        ])
        submitted = st.form_submit_button("진단 완료하고 대시보드 열기")

    if submitted:
        st.session_state.survey_answers = {
            "집중": q1,
            "해설": q2,
            "오답": q3,
            "계산": q4,
            "고난도": q5,
            "운용": q6,
        }
        go("dashboard")


def report_text():
    model = get_model()
    if model is None:
        return "AI 기능을 사용하려면 Streamlit Secrets에 GEMINI_API_KEY를 등록해 주세요."

    info = st.session_state.basic_info
    reason_summary = dict(Counter(note["reason"] for note in st.session_state.error_notes))
    prompt = f"""
당신은 고등학교 수학 학습 코치입니다. 학생 데이터를 바탕으로 실행 가능한 맞춤 리포트를 한국어로 작성하세요.
과장하지 말고, 사실과 조언을 구분하세요.

[학생 정보]
{json.dumps(info, ensure_ascii=False)}

[학습 습관 설문]
{json.dumps(st.session_state.survey_answers, ensure_ascii=False)}

[오답 원인 통계]
{json.dumps(reason_summary, ensure_ascii=False)}

[출력 형식]
## 현재 위치
## 약점 진단
## 이번 주 핵심 행동 3가지
## D-Day 학습 전략
## 오답 복습 루틴
## 최종 조언
"""
    try:
        response = model.generate_content(prompt)
        return response.text or "리포트를 생성하지 못했습니다."
    except Exception:
        return "AI 응답 생성에 실패했습니다. API 키, 모델명, 사용량을 확인해 주세요."


def render_dashboard():
    info = st.session_state.basic_info
    st.title(f"{info['student_name']}의 학습 대시보드")
    st.caption(f"{info['subject']} · 현재 {info['calc_grade']}등급(상위 {info['pct']}%) · 목표 {info['target_grade']}등급 · D-{info['days']}")

    completed = sum(1 for t in st.session_state.planner_tasks if t.get("done"))
    total = len(st.session_state.planner_tasks)
    if total:
        st.progress(completed / total, text=f"플래너 진행률 {completed}/{total}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("AI 진단 리포트"):
            go("report")
        if st.button("오답 정복 노트"):
            go("errors")
    with c2:
        if st.button("D-Day 플래너"):
            go("planner")
        if st.button("AI 학습 Q&A"):
            go("chat")

    st.divider()
    if not st.session_state.confirm_reset:
        if st.button("프로필과 기록 초기화"):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        st.warning("모든 프로필, 설문, 오답, 플래너, 대화 기록이 삭제됩니다.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("삭제 진행", type="primary"):
                st.session_state.clear()
                st.rerun()
        with c2:
            if st.button("취소"):
                st.session_state.confirm_reset = False
                st.rerun()


def render_report():
    st.title("AI 정밀 진단 리포트")
    back_btn()
    st.divider()

    if not st.session_state.generated_report:
        if st.button("리포트 생성", type="primary"):
            with st.spinner("학생 데이터를 분석 중입니다."):
                st.session_state.generated_report = report_text()
            st.rerun()
        st.info("프로필과 설문을 바탕으로 맞춤형 리포트를 생성합니다.")
        return

    st.markdown(st.session_state.generated_report)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "리포트 다운로드 (.md)",
            data=st.session_state.generated_report,
            file_name=f"{st.session_state.basic_info['student_name']}_수학_진단리포트.md",
            mime="text/markdown",
        )
    with c2:
        if st.button("리포트 다시 생성"):
            st.session_state.generated_report = ""
            st.rerun()


def render_planner():
    st.title("D-Day 학습 플래너")
    back_btn()

    if not st.session_state.planner_tasks:
        days = int(st.session_state.basic_info["days"])
        st.session_state.planner_tasks = [
            {"day": f"D-{days}", "task": "취약 단원 개념 정리", "done": False},
            {"day": f"D-{max(days - 7, 1)}", "task": "대표 유형 풀이와 채점", "done": False},
            {"day": f"D-{max(days - 14, 1)}", "task": "오답 1차 재풀이", "done": False},
            {"day": "D-7", "task": "실전 모의고사 풀이", "done": False},
            {"day": "D-1", "task": "오답과 핵심 개념 최종 점검", "done": False},
        ]

    for i, task in enumerate(st.session_state.planner_tasks):
        st.session_state.planner_tasks[i]["done"] = st.checkbox(
            f"{task['day']} · {task['task']}",
            value=task["done"],
            key=f"planner_{i}",
        )

    completed = sum(1 for t in st.session_state.planner_tasks if t["done"])
    total = len(st.session_state.planner_tasks)
    st.progress(completed / total, text=f"완료 {completed}/{total}")


def render_errors():
    st.title("오답 정복 노트")
    back_btn()

    with st.form("error_form", clear_on_submit=True):
        title = st.text_input("문제 출처 및 번호", placeholder="예: 쎈 345번")
        unit = st.text_input("단원", placeholder="예: 이차함수")
        reason = st.selectbox("오답 원인", ["개념 미숙", "연산 실수", "조건 미확인", "시간 부족", "아이디어 미도출"])
        memo = st.text_area("다음 풀이에서 지킬 규칙", placeholder="예: 조건에 밑줄을 긋고, 마지막에 부호를 검산한다.")
        submitted = st.form_submit_button("오답 저장")

    if submitted:
        if not title.strip() or not unit.strip():
            st.error("문제 출처/번호와 단원을 모두 입력해 주세요.")
        else:
            st.session_state.error_notes.append({
                "title": title.strip(),
                "unit": unit.strip(),
                "reason": reason,
                "memo": memo.strip() or "메모 없음",
            })
            st.success("오답을 저장했습니다.")
            st.rerun()

    if not st.session_state.error_notes:
        st.info("아직 기록된 오답이 없습니다. 첫 오답을 등록해 보세요.")
        return

    counts = Counter(note["reason"] for note in st.session_state.error_notes)
    st.caption("가장 많이 기록된 원인: " + counts.most_common(1)[0][0])

    for idx in range(len(st.session_state.error_notes) - 1, -1, -1):
        note = st.session_state.error_notes[idx]
        with st.expander(f"{note['title']} · {note['unit']}"):
            st.write(f"원인: {note['reason']}")
            st.write(f"복습 규칙: {note['memo']}")
            if st.button("이 오답 삭제", key=f"delete_{idx}"):
                st.session_state.error_notes.pop(idx)
                st.rerun()


def render_chat():
    st.title("AI 학습 Q&A")
    back_btn()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("공부법, 오답 복습, 시간 관리 등을 물어보세요.")
    if not prompt:
        return

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = get_model()
        if model is None:
            answer = "AI 기능을 사용하려면 Streamlit Secrets에 GEMINI_API_KEY를 설정해 주세요."
        else:
            context = f"학생 정보: {json.dumps(st.session_state.basic_info, ensure_ascii=False)}\n설문: {json.dumps(st.session_state.survey_answers, ensure_ascii=False)}\n질문: {prompt}\n학생이 바로 실천할 수 있게 짧고 구체적으로 답하세요."
            try:
                response = model.generate_content(context)
                answer = response.text or "답변을 생성하지 못했습니다."
            except Exception:
                answer = "AI 응답 생성에 실패했습니다. 잠시 후 다시 시도해 주세요."

        st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})


view = st.session_state.current_view
if view == "onboarding":
    render_onboarding()
elif view == "survey":
    render_survey()
elif view == "dashboard":
    render_dashboard()
elif view == "report":
    render_report()
elif view == "planner":
    render_planner()
elif view == "errors":
    render_errors()
elif view == "chat":
    render_chat()
else:
    st.session_state.current_view = "onboarding"
    st.rerun()
