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
        f"{profile.executive_summary or profile.summary}",
        "",
    ]

    if profile.strengths:
        lines.extend([
            "### 🌟 Core Candidate Strengths",
            *[f"- ✅ {s}" for s in profile.strengths],
            "",
        ])

    if profile.market_outlook:
        lines.extend([
            "### 📈 Macro Market Outlook",
            f"{profile.market_outlook}",
            "",
        ])

    if profile.future_self_simulation:
        lines.extend([
            "---",
            "",
            "## ⏳ Future Self Simulation Timeline",
        ])
        for yr, narrative in profile.future_self_simulation.items():
            formatted_yr = yr.replace("_", " ").title()
            lines.append(f"### 🚀 {formatted_yr} Horizon\n{narrative}\n")

    lines.extend([
        "---",
        "",
        "## 🔮 Future Me Simulated Trajectories",
    ])

    for idx, scenario in enumerate(profile.career_matches, start=1):
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
        projects = scenario.recommended_projects or profile.recommended_projects
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
    for gap in profile.skill_gaps:
        lines.append(f"| {gap.existing_strength} | {gap.missing_skill} |")

    lines.extend([
        "",
        "---",
        "",
        "## 🗺️ Milestone Execution Roadmap",
    ])
    for phase in profile.milestones or profile.roadmap:
        title_str = phase.title or phase.timeframe
        lines.append(f"\n### 📍 {title_str} ({phase.timeline})")
        if phase.objective:
            lines.append(f"**Objective:** {phase.objective}\n")
        for item in (phase.actions or phase.action_items):
            lines.append(f"- [ ] {item}")

    if profile.learning_path:
        lines.extend([
            "",
            "---",
            "",
            "## 📚 Phased Learning Path",
            *[f"- 🎯 {step}" for step in profile.learning_path],
        ])

    if profile.final_verdict:
        lines.extend([
            "",
            "---",
            "",
            "## 🏆 Final Strategic Verdict",
            f"{profile.final_verdict}",
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

# Session state initialization
if "career_profile" not in st.session_state:
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
profile: StudentCareerProfile = st.session_state.career_profile

# 1. Four-Column KPI Metric Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    top_role = (
        profile.top_trajectory
        if profile and profile.top_trajectory
        else (profile.career_matches[0].role if profile and profile.career_matches else "Pending Input")
    )
    st.metric(label="🎯 Top Trajectory", value=top_role)

with kpi2:
    fit_score = (
        f"{profile.fit_score}%"
        if profile and profile.fit_score is not None
        else (f"{profile.career_matches[0].match_percentage}%" if profile and profile.career_matches else "—")
    )
    st.metric(label="📊 Capability Fit", value=fit_score)

with kpi3:
    conf_score = (
        f"{profile.career_confidence}%"
        if profile and profile.career_confidence is not None
        else (f"{profile.career_matches[0].confidence_score}%" if profile and profile.career_matches else "—")
    )
    st.metric(label="🔮 Career Confidence", value=conf_score)

with kpi4:
    sprints_count = len(profile.milestones or profile.roadmap) if profile else 0
    sprints_val = f"{sprints_count} Milestones" if profile and sprints_count > 0 else "—"
    st.metric(label="🗺️ Sprints", value=sprints_val)

st.divider()

if profile:
    # 2. Executive Assessment & Market Outlook Bento Box
    with st.container(border=True):
        st.subheader("📋 Executive Strategic Assessment")
        st.info(profile.executive_summary or profile.summary)

        # Strengths & Market Outlook 2-column grid
        if profile.strengths or profile.market_outlook:
            col_str, col_mkt = st.columns([1, 1], gap="medium")

            with col_str:
                st.markdown("##### 🌟 Core Candidate Strengths")
                if profile.strengths:
                    for s in profile.strengths:
                        st.write(f"✅ {s}")
                else:
                    st.write("Demonstrated high capability fit across core technical competencies.")

            with col_mkt:
                st.markdown("##### 📈 Macro Market Outlook")
                if profile.market_outlook:
                    st.markdown(f"*{profile.market_outlook}*")
                else:
                    st.write("Strong enterprise hiring demand across next-generation software and AI roles.")

    # 3. ⏳ Future Self Simulation Timeline (1-Year, 3-Year, 5-Year Horizon)
    if profile.future_self_simulation:
        st.subheader("⏳ Future Self Simulation Timeline")
        st.caption("A multi-year projection simulating your progression from associate impact to senior technical leadership.")

        col_y1, col_y3, col_y5 = st.columns(3, gap="medium")

        with col_y1:
            with st.container(border=True):
                st.markdown("#### 🚀 Year 1 Horizon")
                st.caption("Associate Execution & Foundation")
                y1_text = profile.future_self_simulation.get("1_year") or profile.future_self_simulation.get("1-year") or "Active contribution on core pipelines and microservices."
                st.write(y1_text)

        with col_y3:
            with st.container(border=True):
                st.markdown("#### 🎯 Year 3 Horizon")
                st.caption("Mid-Level Ownership & Scale")
                y3_text = profile.future_self_simulation.get("3_year") or profile.future_self_simulation.get("3-year") or "Leading end-to-end production architectures and automated retraining."
                st.write(y3_text)

        with col_y5:
            with st.container(border=True):
                st.markdown("#### 👑 Year 5 Horizon")
                st.caption("Senior Lead & Technical Strategy")
                y5_text = profile.future_self_simulation.get("5_year") or profile.future_self_simulation.get("5-year") or "Driving strategic enterprise architecture and technical mentoring."
                st.write(y5_text)

        st.divider()

    # 4. Major Section: 🔮 Future Me Simulated Trajectories
    st.subheader("🔮 Future Me Simulated Trajectories")
    st.caption("Simulate your potential career futures: explore day-in-the-life routines, evaluate dream vs. reality skill bridges, navigate risks, and execute targeted projects.")

    if not profile.career_matches:
        with st.container(border=True):
            st.write("No career trajectories simulated yet.")
    else:
        # Dynamic tabs generated from recommended role names
        tabs = st.tabs([scenario.role for scenario in profile.career_matches])

        for tab_idx, (tab, scenario) in enumerate(zip(tabs, profile.career_matches)):
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
                        if profile.skill_gaps:
                            for gap_idx, gap in enumerate(profile.skill_gaps):
                                g1, g2 = st.columns(2)
                                with g1:
                                    st.caption("CURRENT STRENGTH")
                                    st.write(f"✅ **{gap.existing_strength}**")
                                Carriage = gap.missing_skill
                                with g2:
                                    st.caption("ROLE GAP TO BRIDGE")
                                    st.write(f"🎯 **{Carriage}**")
                                if gap_idx < len(profile.skill_gaps) - 1:
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
                    candidate_projects = scenario.recommended_projects or profile.recommended_projects
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
    roadmap_list = profile.milestones or profile.roadmap

    col_sprints, col_learning = st.columns([1.2, 1], gap="medium")

    with col_sprints:
        st.subheader("🗺️ Milestone Execution Sprints")
        st.caption("Structured phased milestones with concrete technical objectives.")

        with st.container(border=True):
            if not roadmap_list:
                st.write("No milestone roadmap generated.")
            else:
                for phase_idx, phase in enumerate(roadmap_list):
                    display_title = phase.title if phase.title != phase.timeline else phase.timeframe
                    with st.expander(
                        f"📍 {phase.timeline}: {display_title}",
                        expanded=(phase_idx == 0),
                    ):
                        if phase.objective:
                            st.info(f"**Objective:** {phase.objective}")

                        items = phase.actions or phase.action_items
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
            if profile.learning_path:
                for l_idx, step in enumerate(profile.learning_path, start=1):
                    st.markdown(f"**Step {l_idx}:** {step}")
                    if l_idx < len(profile.learning_path):
                        st.divider()
            else:
                st.write("Custom learning path will generate automatically with your profile.")

    # 6. Final Strategic Verdict
    if profile.final_verdict:
        st.divider()
        with st.container(border=True):
            st.subheader("🏆 Final Strategic Verdict")
            st.success(profile.final_verdict, icon="🎯")

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
        json_content = profile.model_dump_json(indent=2)
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
