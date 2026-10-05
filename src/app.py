"""
PathWise - Future Me Simulator & High-Density Student Career Dashboard.
Modern Bento-grid layout built strictly with native Streamlit components.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models import StudentCareerProfile
from src.gemma_engine import analyze_student_profile

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pathwise 🔮 Future Me Simulator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Demo Presets
# ---------------------------------------------------------
DEMO_PRESETS = {
    "B.Tech CSE -> AI/ML": {
        "degree": "B.Tech in Computer Science and Engineering (3rd Year)",
        "skills": "Python, Data Structures, SQL, NumPy, Pandas, Scikit-Learn, Git, Basic PyTorch",
        "interests": "Generative AI, LLM Application Development, Autonomous Agents, MLOps, Computer Vision",
    },
    "Mechanical -> Robotics": {
        "degree": "B.S. in Mechanical Engineering",
        "skills": "SolidWorks, MATLAB, Basic C++, Kinematics, Statics, Hardware Prototyping, Arduino",
        "interests": "Industrial Robotics, ROS (Robot Operating System), Embedded Control Systems, Mechatronics, Sensor Fusion",
    },
}


def generate_markdown_report(
    profile: StudentCareerProfile, degree: str, skills: str, interests: str
) -> str:
    """Generates an executive-ready Markdown export of the entire career plan and simulations."""
    summary_text = getattr(profile, "executive_summary", None) or getattr(profile, "summary", "")
    lines = [
        "# Pathwise 🔮 Future Me Simulator — Strategic Career Roadmap",
        "",
        "## 👤 Student Profile",
        f"- **Academic Background:** {degree}",
        f"- **Current Strengths & Skills:** {skills}",
        f"- **Interests & Passions:** {interests}",
        "",
        "---",
        "",
        "## 📋 Executive Strategic Assessment",
        f"{summary_text}",
        "",
    ]

    strengths = getattr(profile, "strengths", [])
    if strengths:
        lines.extend([
            "### 🌟 Core Candidate Strengths",
            *[f"- ✅ {s}" for s in strengths],
            "",
        ])

    market_outlook = getattr(profile, "market_outlook", "")
    if market_outlook:
        lines.extend([
            "### 📈 Macro Market Outlook",
            f"{market_outlook}",
            "",
        ])

    future_sim = getattr(profile, "future_self_simulation", {})
    if future_sim:
        lines.extend([
            "---",
            "",
            "## ⏳ Future Self Simulation Timeline",
        ])
        for yr, narrative in future_sim.items():
            formatted_yr = yr.replace("_", " ").title()
            lines.append(f"### 🚀 {formatted_yr} Horizon\n{narrative}\n")

    lines.extend([
        "---",
        "",
        "## 🔮 Future Me Simulated Trajectories",
    ])

    career_matches = getattr(profile, "career_matches", []) or []
    for idx, scenario in enumerate(career_matches, start=1):
        lines.append(
            f"### {idx}. {scenario.role} — {scenario.confidence_score}% Confidence | {scenario.match_percentage}% Capability Overlap"
        )
        lines.append(f"**Fit Rationale:** {scenario.reasoning}\n")
        lines.append("#### 🌅 A Day in the Life")
        lines.append(f"{scenario.day_in_the_life}\n")

        lines.append("#### ⚠️ Risk Radar")
        if scenario.risk_radar:
            for risk in scenario.risk_radar:
                lines.append(f"- ⚠️ {risk}")
        else:
            lines.append("- No critical risks flagged.")
        lines.append("")

        lines.append("#### 🚀 Recommended Projects & Certifications")
        projects = scenario.recommended_projects or getattr(profile, "recommended_projects", [])
        if projects:
            for proj in projects:
                lines.append(f"- [ ] {proj}")
        else:
            lines.append("- No specific projects listed.")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## ⚖️ Skill Gap Diagnostics (Dream vs Reality)",
        "| Current Foundation | Target Missing Skill |",
        "| :--- | :--- |",
    ])
    skill_gaps = getattr(profile, "skill_gaps", []) or []
    for gap in skill_gaps:
        lines.append(f"| {gap.existing_strength} | {gap.missing_skill} |")

    lines.extend([
        "",
        "---",
        "",
        "## 🗺️ Milestone Execution Roadmap",
    ])
    milestones_list = getattr(profile, "milestones", None) or getattr(profile, "roadmap", None) or []
    for phase in milestones_list:
        title_str = getattr(phase, "title", None) or getattr(phase, "timeframe", "Milestone Phase")
        timeline_str = getattr(phase, "timeline", getattr(phase, "timeframe", "Upcoming Sprint"))
        objective_str = getattr(phase, "objective", "")
        lines.append(f"\n### 📍 {title_str} ({timeline_str})")
        if objective_str:
            lines.append(f"**Objective:** {objective_str}\n")
        actions_list = getattr(phase, "actions", None) or getattr(phase, "action_items", None) or []
        for item in actions_list:
            lines.append(f"- [ ] {item}")

    learning_path = getattr(profile, "learning_path", [])
    if learning_path:
        lines.extend([
            "",
            "---",
            "",
            "## 📚 Phased Learning Path",
            *[f"- 🎯 {step}" for step in learning_path],
        ])

    final_verdict = getattr(profile, "final_verdict", "")
    if final_verdict:
        lines.extend([
            "",
            "---",
            "",
            "## 🏆 Final Strategic Verdict",
            f"{final_verdict}",
        ])

    lines.append(
        "\n---\n*Generated by Pathwise 🔮 Future Me Simulator — Powered by Gemma AI.*"
    )
    return "\n".join(lines)


# ---------------------------------------------------------
# Sidebar Inputs
# ---------------------------------------------------------
with st.sidebar:
    st.title("🧭 Profile Navigator")
    st.caption("Load a targeted student preset or customize inputs to simulate your future career trajectories.")

    preset_choice = st.selectbox(
        "Load demo preset:",
        options=["Custom Profile"] + list(DEMO_PRESETS.keys()),
        index=1,
    )

    if preset_choice in DEMO_PRESETS:
        default_degree = DEMO_PRESETS[preset_choice]["degree"]
        default_skills = DEMO_PRESETS[preset_choice]["skills"]
        default_interests = DEMO_PRESETS[preset_choice]["interests"]
    else:
        default_degree = ""
        default_skills = ""
        default_interests = ""

    with st.form("student_profile_form"):
        degree_input = st.text_area(
            "🎓 Degree / Current Academic Program",
            value=default_degree,
            placeholder="e.g. B.Tech in CSE, 3rd year",
            height=85,
            help="Major, current academic standing, or degree specialization.",
        )

        skills_input = st.text_area(
            "💻 Current Foundation & Skills",
            value=default_skills,
            placeholder="e.g. Python, SQL, Git, Problem Solving, Data Analysis",
            height=105,
            help="Technical proficiencies, frameworks, tools, and coursework you are confident in.",
        )

        interests_input = st.text_area(
            "💡 Interests & Target Domains",
            value=default_interests,
            placeholder="e.g. Cloud architectures, AI agents, robotics automation",
            height=105,
            help="Industries, domains, and problem spaces you want to work in.",
        )

        with st.expander("⚙️ Advanced Settings"):
            hf_token_input = st.text_input(
                "Hugging Face Token Override",
                type="password",
                placeholder="hf_...",
                help="Optional override if HF_TOKEN is already configured in your .env file.",
            )
            fast_demo_mode = st.checkbox(
                "⚡ Fast Offline Demo Mode",
                value=False,
                help="Instantly simulate without waiting for Hugging Face API or network calls.",
            )
            from src.gemma_engine import resolve_hf_token
            has_token = bool(resolve_hf_token(hf_token_input.strip() or None))
            if has_token:
                st.caption("🟢 **HF Token:** Active & Detected")
            else:
                st.caption("🟠 **HF Token:** Not Detected (Offline Mock will be used)")

        submit_btn = st.form_submit_button(
            "🔮 Launch Future Me Simulator",
            type="primary",
            use_container_width=True,
        )

# ---------------------------------------------------------
# Main Canvas - Dashboard Header
# ---------------------------------------------------------
st.title("Pathwise 🔮 Future Me Simulator")
st.caption("AI-Powered Predictive Career Simulator, Skill Gap Diagnostics & Milestone Execution Engine")

# Session state initialization & resilient schema migration
if "career_profile" not in st.session_state:
    st.session_state.career_profile = None
elif st.session_state.career_profile is not None:
    # Ensure any older profile instance in session state is upgraded safely
    try:
        current_obj = st.session_state.career_profile
        if not hasattr(current_obj, "top_trajectory"):
            dumped = (
                current_obj.model_dump()
                if hasattr(current_obj, "model_dump")
                else current_obj.dict()
            )
            st.session_state.career_profile = StudentCareerProfile.model_validate(dumped)
    except Exception:
        st.session_state.career_profile = None

# Handle Form Submission
if submit_btn:
    if not degree_input.strip() or not skills_input.strip() or not interests_input.strip():
        st.warning("⚠️ Please provide Degree, Foundation Skills, and Target Interests in the sidebar.")
    else:
        with st.spinner("Synthesizing Future Me simulations via Gemma AI... This will take a few seconds."):
            try:
                profile_result = analyze_student_profile(
                    degree=degree_input.strip(),
                    skills=skills_input.strip(),
                    interests=interests_input.strip(),
                    hf_token=hf_token_input.strip() or None,
                    force_mock=fast_demo_mode,
                )
                st.session_state.career_profile = profile_result
                st.toast("Future Me Simulator generated your career roadmap successfully!", icon="🔮")
            except Exception as e:
                st.error(f"Computation Error: {e}")
                st.info(
                    "💡 Tip: Ensure HF_TOKEN is set in `.env` or in the sidebar Advanced Settings, "
                    "or toggle '⚡ Fast Offline Demo Mode' under Advanced Settings for an instant preview."
                )

# ---------------------------------------------------------
# Bento Grid Dashboard Layout
# ---------------------------------------------------------
profile = st.session_state.career_profile

if profile:
    engine_name = getattr(profile, "engine_source", "Google Gemma 3 AI")
    if "Offline" in engine_name or "Fallback" in engine_name:
        st.warning(f"⚠️ **Simulation Source:** {engine_name}", icon="⚠️")
    else:
        st.success(f"⚡ **Simulation Source:** {engine_name} — Live inference verified", icon="🟢")

# 1. Four-Column KPI Metric Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    top_role = "Pending Input"
    if profile:
        top_role = getattr(profile, "top_trajectory", None)
        if not top_role:
            matches = getattr(profile, "career_matches", None)
            top_role = matches[0].role if matches else "Pending Input"
    st.metric(label="🎯 Top Trajectory", value=top_role)

with kpi2:
    fit_score = "—"
    if profile:
        sc = getattr(profile, "fit_score", None)
        if sc is not None:
            fit_score = f"{sc}%"
        else:
            matches = getattr(profile, "career_matches", None)
            fit_score = f"{matches[0].match_percentage}%" if matches else "—"
    st.metric(label="📊 Capability Fit", value=fit_score)

with kpi3:
    conf_score = "—"
    if profile:
        cs = getattr(profile, "career_confidence", None)
        if cs is not None:
            conf_score = f"{cs}%"
        else:
            matches = getattr(profile, "career_matches", None)
            conf_score = f"{matches[0].confidence_score}%" if matches else "—"
    st.metric(label="🔮 Career Confidence", value=conf_score)

with kpi4:
    sprints_val = "—"
    if profile:
        m_list = getattr(profile, "milestones", None) or getattr(profile, "roadmap", None) or []
        sprints_val = f"{len(m_list)} Milestones" if m_list else "—"
    st.metric(label="🗺️ Sprints", value=sprints_val)

st.divider()

if profile:
    # 2. Executive Assessment & Market Outlook Bento Box
    with st.container(border=True):
        st.subheader("📋 Executive Strategic Assessment")
        assessment_text = getattr(profile, "executive_summary", None) or getattr(profile, "summary", "")
        st.info(assessment_text)

        # Strengths & Market Outlook 2-column grid
        strengths = getattr(profile, "strengths", [])
        market_outlook = getattr(profile, "market_outlook", "")
        if strengths or market_outlook:
            col_str, col_mkt = st.columns([1, 1], gap="medium")

            with col_str:
                st.markdown("##### 🌟 Core Candidate Strengths")
                if strengths:
                    for s in strengths:
                        st.write(f"✅ {s}")
                else:
                    st.write("Demonstrated high capability fit across core technical competencies.")

            with col_mkt:
                st.markdown("##### 📈 Macro Market Outlook")
                if market_outlook:
                    st.markdown(f"*{market_outlook}*")
                else:
                    st.write("Strong enterprise hiring demand across next-generation software and AI roles.")

    # 3. ⏳ Future Self Simulation Timeline (1-Year, 3-Year, 5-Year Horizon)
    future_sim = getattr(profile, "future_self_simulation", {})
    if future_sim:
        st.subheader("⏳ Future Self Simulation Timeline")
        st.caption("A multi-year projection simulating your progression from associate impact to senior technical leadership.")

        col_y1, col_y3, col_y5 = st.columns(3, gap="medium")

        with col_y1:
            with st.container(border=True):
                st.markdown("#### 🚀 Year 1 Horizon")
                st.caption("Associate Execution & Foundation")
                y1_text = future_sim.get("1_year") or future_sim.get("1-year") or "Active contribution on core pipelines and microservices."
                st.write(y1_text)

        with col_y3:
            with st.container(border=True):
                st.markdown("#### 🎯 Year 3 Horizon")
                st.caption("Mid-Level Ownership & Scale")
                y3_text = future_sim.get("3_year") or future_sim.get("3-year") or "Leading end-to-end production architectures and automated retraining."
                st.write(y3_text)

        with col_y5:
            with st.container(border=True):
                st.markdown("#### 👑 Year 5 Horizon")
                st.caption("Senior Lead & Technical Strategy")
                y5_text = future_sim.get("5_year") or future_sim.get("5-year") or "Driving strategic enterprise architecture and technical mentoring."
                st.write(y5_text)

        st.divider()

    # 4. Major Section: 🔮 Future Me Simulated Trajectories
    st.subheader("🔮 Future Me Simulated Trajectories")
    st.caption("Simulate your potential career futures: explore day-in-the-life routines, evaluate dream vs. reality skill bridges, navigate risks, and execute targeted projects.")

    career_matches = getattr(profile, "career_matches", [])
    if not career_matches:
        with st.container(border=True):
            st.write("No career trajectories simulated yet.")
    else:
        # Dynamic tabs generated from recommended role names
        tabs = st.tabs([scenario.role for scenario in career_matches])

        for tab_idx, (tab, scenario) in enumerate(zip(tabs, career_matches)):
            with tab:
                # Header: Display the Role and a large st.metric for "Career Confidence Score"
                head_left, head_right = st.columns([3, 1.2])
                with head_left:
                    st.subheader(f"Role: {scenario.role}")
                    st.caption(f"**Fit Rationale:** {scenario.reasoning}")
                    clamped_pct = max(0, min(100, scenario.match_percentage))
                    st.progress(
                        clamped_pct / 100.0,
                        text=f"Capability Overlap: {clamped_pct}%",
                    )
                with head_right:
                    st.metric(
                        label="Career Confidence Score",
                        value=f"{scenario.confidence_score}%",
                        delta=f"{scenario.match_percentage}% Capability Fit",
                    )

                st.divider()

                # Bento-grid 2-column layout: Column 1 (The Vision) & Column 2 (The Reality & Risks)
                col_vision, col_reality = st.columns([1.1, 1], gap="medium")

                # Column 1 (The Vision): A container displaying the "Day in the Life" narrative
                with col_vision:
                    with st.container(border=True):
                        st.subheader("🌅 The Vision: Day in the Life")
                        st.caption("A vivid preview of your future daily rhythm, engineering responsibilities, and team impact.")
                        st.write(scenario.day_in_the_life)

                # Column 2 (The Reality & Risks): A container for "Dream vs Reality" and a "⚠️ Risk Radar"
                with col_reality:
                    with st.container(border=True):
                        st.subheader("⚖️ Dream vs Reality")
                        st.caption("Mapping your current skill foundation against missing skills required for this role.")
                        gaps = getattr(profile, "skill_gaps", [])
                        if gaps:
                            for gap_idx, gap in enumerate(gaps):
                                g1, g2 = st.columns(2)
                                with g1:
                                    st.caption("CURRENT STRENGTH")
                                    st.write(f"✅ **{gap.existing_strength}**")
                                with g2:
                                    st.caption("ROLE GAP TO BRIDGE")
                                    st.write(f"🎯 **{gap.missing_skill}**")
                                if gap_idx < len(gaps) - 1:
                                    st.divider()
                        else:
                            st.write("No critical skill disparities detected.")

                        st.divider()

                        st.subheader("⚠️ Risk Radar")
                        st.caption("Potential burnout risks, market churn, and industry challenges to navigate.")
                        if scenario.risk_radar:
                            for risk in scenario.risk_radar:
                                st.warning(risk, icon="⚠️")
                        else:
                            st.write("No severe industry risks flagged for this path.")

                # Full-width Bottom Container: "🚀 Execution & Projects" featuring interactive checkboxes
                with st.container(border=True):
                    st.subheader("🚀 Execution & Projects")
                    st.caption("Hands-on hackathons, production repositories, and industry certifications to make this future a reality.")
                    candidate_projects = scenario.recommended_projects or getattr(profile, "recommended_projects", [])
                    if candidate_projects:
                        st.write("Track recommended milestones for this scenario:")
                        for proj_idx, proj in enumerate(candidate_projects):
                            st.checkbox(
                                proj,
                                key=f"sim_proj_{tab_idx}_{proj_idx}",
                            )
                    else:
                        st.write("No specific recommended projects listed for this role.")

    # 5. Phased Milestone Roadmap & Learning Curriculum
    st.divider()
    roadmap_list = getattr(profile, "milestones", None) or getattr(profile, "roadmap", None) or []

    col_sprints, col_learning = st.columns([1.2, 1], gap="medium")

    with col_sprints:
        st.subheader("🗺️ Milestone Execution Sprints")
        st.caption("Structured phased milestones with concrete technical objectives.")

        with st.container(border=True):
            if not roadmap_list:
                st.write("No milestone roadmap generated.")
            else:
                for phase_idx, phase in enumerate(roadmap_list):
                    timeline_str = getattr(phase, "timeline", getattr(phase, "timeframe", "Upcoming Sprint"))
                    title_str = getattr(phase, "title", timeline_str)
                    display_title = title_str if title_str != timeline_str else timeline_str
                    with st.expander(
                        f"📍 {timeline_str}: {display_title}",
                        expanded=(phase_idx == 0),
                    ):
                        objective_str = getattr(phase, "objective", "")
                        if objective_str:
                            st.info(f"**Objective:** {objective_str}")

                        items = getattr(phase, "actions", None) or getattr(phase, "action_items", None) or []
                        if items:
                            st.write("Actionable sprint milestones:")
                            for item_idx, action_item in enumerate(items):
                                st.checkbox(
                                    action_item,
                                    key=f"global_sprint_{phase_idx}_{item_idx}",
                                )
                        else:
                            st.write("No specific action items listed for this phase.")

    with col_learning:
        st.subheader("📚 Phased Learning Path")
        st.caption("Targeted curriculum sequence bridging into production roles.")

        with st.container(border=True):
            learning_path = getattr(profile, "learning_path", [])
            if learning_path:
                for l_idx, step in enumerate(learning_path, start=1):
                    st.markdown(f"**Step {l_idx}:** {step}")
                    if l_idx < len(learning_path):
                        st.divider()
            else:
                st.write("Custom learning path will generate automatically with your profile.")

    # 6. Final Strategic Verdict
    final_verdict = getattr(profile, "final_verdict", "")
    if final_verdict:
        st.divider()
        with st.container(border=True):
            st.subheader("🏆 Final Strategic Verdict")
            st.success(final_verdict, icon="🎯")

    # 7. Full Report Downloads
    st.divider()
    dl_col1, dl_col2 = st.columns([1, 1], gap="medium")

    with dl_col1:
        markdown_content = generate_markdown_report(
            profile=profile,
            degree=degree_input,
            skills=skills_input,
            interests=interests_input,
        )
        st.download_button(
            label="📥 Download Future Me Roadmap (Markdown)",
            data=markdown_content,
            file_name="pathwise_future_me_roadmap.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary",
        )

    with dl_col2:
        json_content = (
            profile.model_dump_json(indent=2)
            if hasattr(profile, "model_dump_json")
            else str(profile)
        )
        st.download_button(
            label="📦 Export Profile Telemetry (JSON)",
            data=json_content,
            file_name="pathwise_future_me_profile.json",
            mime="application/json",
            use_container_width=True,
        )

else:
    # Empty State Dashboard Preview (Bento Layout)
    st.info("👈 Select a demo preset or specify your details in the sidebar, then click **🔮 Launch Future Me Simulator**.")

    preview_c1, preview_c2 = st.columns([1.6, 1.4], gap="medium")

    with preview_c1:
        with st.container(border=True):
            st.subheader("📋 Executive Strategic Assessment")
            st.write(
                "Provides a high-level executive diagnostic summarizing your profile's market readiness, "
                "differentiating strengths, and strategic trajectory alignment."
            )

        with st.container(border=True):
            st.subheader("⏳ Future Self Simulation (1, 3 & 5 Years)")
            st.write(
                "Dynamic multi-year career horizon projections simulating your trajectory from associate execution "
                "to mid-level ownership and senior strategic engineering leadership."
            )

    with preview_c2:
        with st.container(border=True):
            st.subheader("⚖️ Dream vs Reality & ⚠️ Risk Radar")
            st.write(
                "Direct side-by-side comparison of your Current Foundation against Priority Acquisition targets, "
                "paired with early-warning radars for industry churn and burnout pitfalls."
            )

        with st.container(border=True):
            st.subheader("🚀 Milestone Sprints & Phased Learning Curriculum")
            st.write(
                "Concrete sprint trackers with interactive checkboxes for GitHub repos, "
                "hackathon challenges, and structured phased learning paths."
            )
