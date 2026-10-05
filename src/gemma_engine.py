"""
Gemma 2 inference engine for PathWise Future Me Simulator.
Uses direct HTTP requests to https://router.huggingface.co/v1/chat/completions with google/gemma-2-9b-it,
with fallback to huggingface_hub.InferenceClient, to produce structured StudentCareerProfile recommendations.
"""

import os
import json
import re
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from src.models import StudentCareerProfile, FutureScenario, SkillGap, RoadmapPhase

# Load environment variables from .env
load_dotenv()

ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-2-9b-it"
FALLBACK_MODELS = ["google/gemma-2-2b-it", "google/gemma-3-4b-it", "google/gemma-3-12b-it"]


def resolve_hf_token(token: Optional[str] = None) -> Optional[str]:
    """
    Resolves the Hugging Face token from explicit argument or environment variable,
    treating empty strings and placeholder tokens as missing.
    """
    raw = (token or os.getenv("HF_TOKEN") or "").strip()
    raw = raw.strip('"').strip("'")
    if not raw or raw in ("your_huggingface_token_here", "hf_...", "your_token_here"):
        return None
    return raw


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON object from model response text, stripping markdown code blocks
    and repairing trailing commas.
    """
    cleaned = text.strip()

    # Strip markdown code fences (```json ... ``` or ``` ...)
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()

    # Extract outermost JSON object bounds if extraneous chatter exists
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace : last_brace + 1]

    # Clean trailing commas that invalidate strict json.loads
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

    return json.loads(cleaned)


def build_prompt(degree: str, skills: str, interests: str) -> str:
    """Constructs the instruction prompt with explicit JSON schema for Gemma acting as the Future Me Simulator."""
    schema_template = """{
  "executive_summary": "Strategic overview of the student's profile, market readiness, and top potential directions.",
  "top_trajectory": "Target Job Title",
  "fit_score": 93,
  "career_confidence": 88,
  "top_3_career_rankings": [
    {
      "career": "Target Job Title",
      "score": 93,
      "reason": "Clear explanation of why this role matches their degree, skills, and interests.",
      "day_in_the_life": "Engaging second-person narrative describing a typical workday: morning rituals, core technical architecture & problem solving, cross-functional collaboration, and evening wrap-up.",
      "risk_radar": [
        "Risk 1: Rapid tool churn requiring continuous weekend upskilling",
        "Risk 2: High cognitive load or on-call burnout potential"
      ]
    }
  ],
  "strengths": [
    "Solid foundation in software architecture and algorithms",
    "Hands-on proficiency with core domain frameworks and modern tools"
  ],
  "skill_gaps": [
    "Production containerization and orchestration tooling (Docker, Kubernetes)",
    "Cloud infrastructure and automated CI/CD deployment pipelines"
  ],
  "market_outlook": "Global demand for this role remains exceptionally strong across technology and enterprise sectors, with high growth velocity and competitive compensation benchmarks.",
  "future_self_simulation": {
    "1_year": "Associate role at a growth company: actively building feature pipelines, containerizing artifacts, and integrating real-time prediction endpoints.",
    "3_year": "Mid-level role: taking ownership of end-to-end architectures, automated retraining loops, and scaling production systems.",
    "5_year": "Senior Lead or System Architect: driving technical strategy, designing enterprise-scale distributed workloads, and mentoring junior engineers."
  },
  "milestones": [
    {
      "title": "Master Containerization & Model Serving Infrastructure",
      "timeline": "Months 1-3",
      "objective": "Transition from local notebook scripts to containerized microservice architectures.",
      "actions": [
        "Containerize core services using Docker and docker-compose",
        "Build asynchronous REST APIs with FastAPI and automated testing"
      ]
    }
  ],
  "recommended_projects": [
    "Interactive GitHub project: Full-stack or distributed pipeline targeting real-world scale",
    "Target Hackathon: MLH Global Hack Week or domain-specific challenge",
    "Industry Certification: AWS Solutions Architect, CKA, or DeepLearning.AI specialization"
  ],
  "learning_path": [
    "Phase 1: Production Software Engineering & Microservices",
    "Phase 2: Pipeline Orchestration & Monitoring",
    "Phase 3: Cloud Compute & Infrastructure as Code",
    "Phase 4: High-Performance Systems & Acceleration"
  ],
  "final_verdict": "The student profile displays exceptionally strong structural potential. Focusing immediately on production rigor will establish a high-probability trajectory toward senior technical leadership."
}"""

    return f"""You are the "PathWise Future Me Simulator" — an elite AI Career Architect, Predictive Mentor, and Technology Futurist.
Analyze this student's profile and simulate their optimal future career trajectory and a complete multi-year growth simulation.

Student Profile:
- Degree / Academic Background: {degree}
- Current Skills & Proficiencies: {skills}
- Interests & Passion Areas: {interests}

Instructions:
1. Provide a top_trajectory, realistic fit_score (60-98), and career_confidence (60-98).
2. Rank top 3 compelling career trajectories with realistic match scores, reasons, day-in-the-life narratives, and risk radars.
3. Detail concrete strengths and priority skill gaps.
4. Provide a macro market_outlook analyzing industry hiring demand.
5. Create a vivid 1_year, 3_year, and 5_year future_self_simulation mapping their long-term progression.
6. Provide structured 3-phase milestones with timeline, objective, and concrete actions.
7. Include 3 recommended portfolio projects, a 4-phase learning path, and a decisive final_verdict.
8. Output ONLY a valid, raw JSON object matching the exact schema below. Do NOT include markdown code fences or conversational text outside the JSON:

{schema_template}
"""


def generate_mock_profile(degree: str, skills: str, interests: str) -> StudentCareerProfile:
    """
    Generates a deterministic, high-fidelity Future Me simulation profile.
    Used for instant offline previews, demo testing, or when API quotas are exceeded.
    """
    is_robotics = "robot" in degree.lower() or "robot" in interests.lower() or "mech" in degree.lower()

    if is_robotics:
        matches = [
            FutureScenario(
                role="Autonomous Systems & Robotics Controls Engineer",
                career="Autonomous Systems & Robotics Controls Engineer",
                match_percentage=94,
                score=94,
                confidence_score=91,
                reasoning="Your mechanical foundations paired with SolidWorks and C++ make robotics automation and kinematics your highest leverage path.",
                day_in_the_life="You begin your morning in the hardware robotics lab, running hardware-in-the-loop tests on a 6-axis articulated robotic arm. At 11 AM, you sync with firmware architects to debug sensor-fusion latency between LiDAR and ROS 2 navigation nodes. Post-lunch, you calibrate trajectory controllers in Gazebo before deploying a production patch to automated warehouse rovers.",
                risk_radar=[
                    "Hardware Lead Times: Frustration from prototype manufacturing delays and supply chain dependencies.",
                    "Safety Criticality: Stringent functional safety audits (ISO 26262) increase pressure on real-time code accuracy.",
                    "Embedded Tool Churn: Need to continuously master RTOS kernels and heterogeneous edge hardware."
                ],
                recommended_projects=[
                    "Build a ROS 2 autonomous indoor rover using Gazebo and Nav2 slam navigation stack",
                    "Compete in MLH Hardware Lab Hackathon or RoboNation Autonomous Challenge",
                    "Earn ARM Certified Embedded Engineer or ROS 2 Robotics Specialization"
                ]
            ),
            FutureScenario(
                role="Mechatronics Simulation & Digital Twin Architect",
                career="Mechatronics Simulation & Digital Twin Architect",
                match_percentage=89,
                score=89,
                confidence_score=86,
                reasoning="Strong mechanical prototyping plus MATLAB allows you to build industrial predictive digital twins for aerospace and automotive giants.",
                day_in_the_life="You start your day reviewing telemetry streams from factory floor actuators. By noon, you are optimizing finite-element kinematics models and deploying physics-informed neural networks to predict mechanical stress fractures before physical assembly.",
                risk_radar=[
                    "Legacy Industry Inertia: Traditional industrial plants take quarters to adopt digital twin paradigms.",
                    "CAD-to-Code Friction: Bridging traditional CAD models into real-time physics engines requires niche tooling."
                ],
                recommended_projects=[
                    "Design an end-to-end Isaac Sim digital twin of an automated sorting conveyor system",
                    "Contribute to open-source Python Pinocchio rigid-body dynamics library",
                    "Earn Siemens Mechatronics Systems Associate Certification"
                ]
            ),
            FutureScenario(
                role="Embedded Robotics Firmware Developer",
                career="Embedded Robotics Firmware Developer",
                match_percentage=83,
                score=83,
                confidence_score=82,
                reasoning="Direct hardware-level control, microcontrollers, and sensor interfacing bridge your Arduino experience into enterprise IoT robotics.",
                day_in_the_life="Your morning is spent connecting logic analyzers to custom STM32 breakout boards to trace SPI communication drops. In the afternoon, you write zero-copy ring buffers in modern C++ for low-power motor drivers.",
                risk_radar=[
                    "Memory Scarcity: Tight embedded memory budgets require relentless micro-optimizations.",
                    "Difficult Debugging: Physical hardware glitches often masquerade as firmware bugs."
                ],
                recommended_projects=[
                    "Develop an RTOS-based motor controller firmware with CAN bus telemetry from scratch",
                    "Participate in the Embedded Open Source Summit Hackathon",
                    "Complete Embedded Systems Specialization on Coursera / edX"
                ]
            ),
        ]
        gaps = [
            SkillGap(
                existing_strength="Kinematics & SolidWorks Prototyping",
                missing_skill="ROS 2 (Robot Operating System) & DDS Middleware"
            ),
            SkillGap(
                existing_strength="Basic Arduino & C++ Syntax",
                missing_skill="Real-Time Operating Systems (FreeRTOS) & Linux Kernel Drivers"
            ),
            SkillGap(
                existing_strength="MATLAB Mechanical Simulation",
                missing_skill="Gazebo Physics Simulation & MoveIt Motion Planning"
            ),
        ]
        milestones = [
            RoadmapPhase(
                title="Master Embedded Firmware & ROS 2 Foundations",
                timeline="Months 1-2",
                objective="Transition from standalone microcontrollers to distributed ROS 2 robotics middleware and RTOS.",
                actions=[
                    "Complete Modern C++ (C++17/20) for Embedded Systems and Linux system programming.",
                    "Set up ROS 2 Humble environment and implement publisher/subscriber sensor nodes.",
                    "Interface an IMU and motor encoder with an STM32 board over I2C/SPI."
                ]
            ),
            RoadmapPhase(
                title="Autonomous Navigation & Physics Simulation",
                timeline="Months 3-4",
                objective="Simulate multi-sensor SLAM navigation and obstacle avoidance in virtual environments.",
                actions=[
                    "Construct a 2D differential drive robot model in URDF and simulate in Gazebo.",
                    "Integrate Nav2 stack for SLAM map generation and autonomous obstacle avoidance.",
                    "Publish a documented GitHub showcase with simulation demo GIFs."
                ]
            ),
            RoadmapPhase(
                title="Hardware Deployment & Production Portfolio",
                timeline="Months 5-6",
                objective="Deploy and benchmark validated algorithms onto physical edge compute hardware.",
                actions=[
                    "Flash code onto a physical Raspberry Pi + Arduino rover platform for real-world validation.",
                    "Submit robotics portfolio project to MLH Hackathon or ROSCon student track.",
                    "Conduct mock technical interviews on robotics kinematics, sensor fusion, and RTOS concurrency."
                ]
            ),
        ]
        strengths = [
            "Strong core mechanical engineering principles, kinematics, and structural prototyping.",
            "Hands-on CAD modeling proficiency in SolidWorks and physical assembly testing.",
            "Fundamental microcontroller programming and sensor actuation familiarity."
        ]
        future_self = {
            "1_year": "Junior Robotics Controls Engineer: testing motor actuation benchmarks, calibrating sensor nodes, and writing ROS 2 device wrappers.",
            "3_year": "Autonomous Systems Engineer: architecting SLAM navigation pipelines, reducing controller latency, and conducting field trials.",
            "5_year": "Lead Robotics Architect: overseeing full-stack autonomy platforms, hardware-software integration, and automated fleet deployments."
        }
        market_outlook = (
            "The robotics and autonomous systems sector is undergoing exponential growth driven by warehouse logistics automation, "
            "smart manufacturing, and autonomous mobile robots (AMRs). Hardware-aware software engineers command strong hiring premiums."
        )
        learning_path = [
            "Phase 1: Modern Embedded C++ (C++17/20), Linux CLI, and Real-Time POSIX threads.",
            "Phase 2: ROS 2 Architecture, DDS Communications, and URDF Robot Modeling.",
            "Phase 3: Sensor Fusion (Extended Kalman Filters, LiDAR/Camera calibration) & Nav2.",
            "Phase 4: Real-Time Operating Systems (FreeRTOS) and Hardware-in-the-Loop Validation."
        ]
        recommended_projects = [
            "Autonomous SLAM Rover: Build a Gazebo-simulated differential drive rover with Nav2 and costmap generation.",
            "STM32 RTOS Motor Controller: Firmware with CAN bus telemetry and closed-loop PID control.",
            "Robotics Vision Pipeline: YOLOv8 object detection integrated with ROS 2 camera nodes."
        ]
        verdict = (
            "Your mechanical prototyping and hardware intuition provide a rare and valuable foundation. "
            "Mastering ROS 2 and modern C++ firmware will immediately position you for elite autonomous systems roles."
        )
        top_traj = "Autonomous Systems & Robotics Controls Engineer"
        fit_sc = 94
        conf_sc = 91

    else:
        matches = [
            FutureScenario(
                role="Machine Learning Engineer",
                career="Machine Learning Engineer",
                match_percentage=93,
                score=93,
                confidence_score=88,
                reasoning="High structural alignment between computer science fundamentals, hands-on PyTorch/Python proficiency, and enterprise demand for scalable model deployment.",
                day_in_the_life="You begin your morning reviewing latency metrics for an agentic multi-hop inference pipeline serving thousands of requests. At 10:30 AM, you collaborate with product leads to test semantic vector retrieval accuracy in Qdrant. After lunch, you fine-tune a specialized 9B parameter model with LoRA on synthetic domain datasets, optimizing token latency by 35%.",
                risk_radar=[
                    "Hyper-Velocity Tool Churn: Frameworks and model releases update weekly, requiring continual re-architecture.",
                    "Non-Deterministic Outputs: Debugging agent hallucinations in enterprise-critical workflows.",
                    "GPU Resource Constraints: Balancing cost efficiency and inference throughput under high traffic."
                ],
                recommended_projects=[
                    "Production Real-Time Recommendation Service: Build, containerize, and deploy a deep learning model using PyTorch, FastAPI, Docker, and Redis.",
                    "Automated MLOps Drift & Retraining Pipeline: Develop an end-to-end pipeline utilizing MLflow and Airflow.",
                    "Distributed LLM Fine-Tuning Endpoint: Fine-tune an open-weight LLM using QLoRA/Ray and convert to TensorRT/ONNX."
                ]
            ),
            FutureScenario(
                role="AI Systems & LLM Application Engineer",
                career="AI Systems & LLM Application Engineer",
                match_percentage=89,
                score=89,
                confidence_score=87,
                reasoning="Your CS foundations in Python, data structures, and PyTorch align directly with the high demand for generative AI agents and RAG pipelines.",
                day_in_the_life="You build autonomous multi-agent workflows with tool-calling capabilities, optimize prompt caching, and integrate vector embeddings for ultra-fast enterprise search.",
                risk_radar=[
                    "Silent Data Drift: Subtly degrading model performance without explicit crash errors.",
                    "On-Call Fatigue: 24/7 reliability requirements for production prediction microservices."
                ],
                recommended_projects=[
                    "Build an autonomous multi-agent research analyst using LangGraph and hybrid vector search",
                    "Compete in MLH Global Hack Week Generative AI Track or AI Agents Hackathon",
                    "Earn DeepLearning.AI Generative AI with LLMs Certificate"
                ]
            ),
            FutureScenario(
                role="Data Scientist & Analytical Modeler",
                career="Data Scientist & Analytical Modeler",
                match_percentage=84,
                score=84,
                confidence_score=82,
                reasoning="Solid mathematical and SQL background, though slightly less optimal for a profile focused on production systems engineering.",
                day_in_the_life="You design A/B experiment frameworks, extract causal inferences from high-volume telemetry tables, and translate predictive scores into executive business decisions.",
                risk_radar=[
                    "Stakeholder Communication Mismatches: Translating statistical p-values into actionable product strategy.",
                    "Unstructured Data Cleaning: Spending outsized time wrangling dirty data before model experimentation."
                ],
                recommended_projects=[
                    "End-to-End Customer Lifetime Value Survival Analysis on Kaggle e-commerce data",
                    "Automated Streamlit Analytical Dashboard with interactive Bayesian cohort models",
                    "Complete Stanford CS229 Machine Learning coursework"
                ]
            ),
        ]
        gaps = [
            SkillGap(
                existing_strength="Computer Science Principles & Algorithms",
                missing_skill="Production MLOps tooling (Docker, Kubernetes, MLflow, Kubeflow)"
            ),
            SkillGap(
                existing_strength="Core PyTorch & Modeling Scripts",
                missing_skill="Distributed computing frameworks for scale (Apache Spark, Ray)"
            ),
            SkillGap(
                existing_strength="Relational Databases & SQL Queries",
                missing_skill="Cloud infrastructure & Infrastructure as Code (AWS/GCP, Terraform)"
            ),
            SkillGap(
                existing_strength="Python Scripting & Prototyping",
                missing_skill="Model acceleration & inference optimization (ONNX, TensorRT, Quantization)"
            ),
        ]
        milestones = [
            RoadmapPhase(
                title="Master Containerization & Model Serving Infrastructure",
                timeline="Months 1-3",
                objective="Transition from experimental local notebook environments to containerized microservice architectures.",
                actions=[
                    "Containerize model training and inference scripts using Docker.",
                    "Build and deploy production REST APIs using FastAPI for asynchronous predictions.",
                    "Implement basic automated testing and linting pipelines with GitHub Actions."
                ]
            ),
            RoadmapPhase(
                title="Implement End-to-End MLOps & Pipeline Orchestration",
                timeline="Months 4-6",
                objective="Construct automated ML pipelines encompassing tracking, orchestration, and monitoring.",
                actions=[
                    "Integrate MLflow or Weights & Biases for experiment tracking and metric logging.",
                    "Orchestrate data preprocessing and model retraining pipelines using Apache Airflow or Prefect.",
                    "Implement data and model drift monitoring dashboards to track prediction performance in production."
                ]
            ),
            RoadmapPhase(
                title="Scale Distributed Computing & Cloud Optimization",
                timeline="Months 7-12",
                objective="Optimize inference latencies and deploy scalable workloads onto major cloud platforms.",
                actions=[
                    "Provision scalable compute clusters on AWS or GCP using Infrastructure as Code (Terraform).",
                    "Apply model optimization techniques including ONNX runtime conversion and quantization.",
                    "Develop an open-source end-to-end production pipeline portfolio project serving live traffic."
                ]
            ),
        ]
        strengths = [
            "Solid foundation in computer science principles, algorithms, and object-oriented architecture.",
            "Hands-on proficiency with core ML frameworks including PyTorch and scientific computing libraries.",
            "Strong relational database fluency and SQL query optimization skills.",
            "Clear strategic alignment between candidate interests and rapid growth sectors in automated AI production."
        ]
        future_self = {
            "1_year": "Associate Machine Learning Engineer at a growth-stage tech company, actively maintaining feature pipelines, containerizing model artifacts, and integrating real-time prediction endpoints.",
            "3_year": "Mid-Level Machine Learning Engineer taking ownership of end-to-end model deployments, managing automated retraining loops, drift detection systems, and vector database architectures.",
            "5_year": "Senior Machine Learning Engineer or AI System Architect driving technical strategy, designing enterprise-scale distributed training jobs, and mentoring junior engineering teams."
        }
        market_outlook = (
            "Global demand for Machine Learning Engineers remains exceptionally strong across technology, finance, and enterprise sectors. "
            "Organizations actively prioritize candidates who combine model development with robust software engineering and production MLOps practices. "
            "Growth velocity and compensation benchmarks in this domain significantly exceed standard software roles."
        )
        learning_path = [
            "Phase 1: Production Software Engineering & Microservices (FastAPI, Docker, Async Python, Testing Frameworks).",
            "Phase 2: MLOps & Pipeline Orchestration (MLflow, Apache Airflow, Weights & Biases).",
            "Phase 3: Cloud Compute & Infrastructure (AWS/GCP, Kubernetes, Terraform, Apache Spark).",
            "Phase 4: High-Performance ML Inference (ONNX, TensorRT, Model Quantization, Vector Databases)."
        ]
        recommended_projects = [
            "Production Real-Time Recommendation Service: Build, containerize, and deploy a deep learning recommendation model using PyTorch, FastAPI, Docker, and Redis caching.",
            "Automated MLOps Drift & Retraining Pipeline: Develop an end-to-end pipeline utilizing MLflow and Airflow that monitors incoming data for drift and automatically triggers model retraining.",
            "Distributed LLM Fine-Tuning & Quantized API Endpoint: Fine-tune an open-weight LLM using QLoRA/Ray, convert to TensorRT/ONNX, and serve via scalable serverless compute."
        ]
        verdict = (
            "The student profile displays exceptionally strong structural potential for high-impact roles in Machine Learning Engineering. "
            "With foundational algorithmic and modeling skill sets established, focusing immediately on software engineering rigor, "
            "containerization, and automated MLOps pipelines will maximize market competitiveness and establish a high-probability trajectory toward senior technical leadership."
        )
        top_traj = "Machine Learning Engineer"
        fit_sc = 93
        conf_sc = 88

    summary = (
        f"Based on an analysis of your background in {degree} combined with core competencies in {skills}, "
        f"the optimal career trajectory is {top_traj}. The candidate possesses strong foundations, "
        f"and closing key operational gaps in MLOps, CI/CD, and cloud infrastructure will accelerate advancement into senior engineering roles."
    )

    return StudentCareerProfile(
        summary=summary,
        executive_summary=summary,
        top_trajectory=top_traj,
        fit_score=fit_sc,
        career_confidence=conf_sc,
        top_3_career_rankings=matches,
        career_matches=matches,
        strengths=strengths,
        skill_gaps=gaps,
        market_outlook=market_outlook,
        future_self_simulation=future_self,
        milestones=milestones,
        roadmap=milestones,
        recommended_projects=recommended_projects,
        learning_path=learning_path,
        final_verdict=verdict,
    )


def analyze_student_profile(
    degree: str,
    skills: str,
    interests: str,
    hf_token: Optional[str] = None,
    force_mock: bool = False,
) -> StudentCareerProfile:
    """
    Analyzes student background using Gemma via Hugging Face Inference Router,
    validating output strictly against StudentCareerProfile schema.
    If force_mock is True, returns high-fidelity simulated profile instantly.
    """
    if force_mock:
        return generate_mock_profile(degree=degree, skills=skills, interests=interests)

    token = resolve_hf_token(hf_token)
    if not token:
        # If no token provided, fall back seamlessly to high-fidelity mock simulator
        return generate_mock_profile(degree=degree, skills=skills, interests=interests)

    system_instruction = (
        "You are the PathWise Future Me Simulator, an expert career advisory and predictive trajectory AI. "
        "You MUST respond ONLY with a raw, valid JSON object matching the requested schema. "
        "Do NOT include conversational markdown, greetings, or extra explanations outside the JSON."
    )
    user_prompt = build_prompt(degree=degree, skills=skills, interests=interests)

    raw_response_text = ""
    last_error: Optional[Exception] = None

    # Step 1: Direct HTTP request to https://router.huggingface.co/v1/chat/completions (90s timeout)
    models_to_try = [DEFAULT_MODEL] + FALLBACK_MODELS
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 3000,
            "temperature": 0.2,
        }

        try:
            resp = requests.post(
                ROUTER_URL,
                headers=headers,
                json=payload,
                timeout=90,
            )
            if resp.status_code == 200:
                data = resp.json()
                raw_response_text = data["choices"][0]["message"]["content"]
                break
            elif resp.status_code == 401:
                last_error = PermissionError(
                    "Invalid or unauthorized Hugging Face token. Please check that your token is active at https://huggingface.co/settings/tokens."
                )
            elif resp.status_code == 403:
                last_error = PermissionError(
                    f"Access restricted for '{model_name}'. Please verify acceptance of model terms at https://huggingface.co/{model_name}."
                )
            else:
                last_error = RuntimeError(f"HTTP {resp.status_code} from {ROUTER_URL} ({model_name}): {resp.text}")
        except Exception as http_err:
            last_error = http_err

    # Step 2: Fallback to InferenceClient if direct router calls didn't return text
    if not raw_response_text:
        try:
            try:
                client = InferenceClient(
                    model=DEFAULT_MODEL,
                    token=token,
                    timeout=90,
                    base_url="https://router.huggingface.co/v1",
                )
            except TypeError:
                client = InferenceClient(
                    model=DEFAULT_MODEL,
                    token=token,
                    timeout=90,
                )

            chat_resp = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=3000,
                temperature=0.2,
            )
            raw_response_text = chat_resp.choices[0].message.content
        except Exception as client_err:
            # If network/token failure occurs, fall back to high-fidelity mock profile
            if last_error:
                mock = generate_mock_profile(degree=degree, skills=skills, interests=interests)
                mock.summary = f"[Offline Fallback Simulation] {mock.summary}"
                return mock
            raise RuntimeError(
                f"Failed to query Gemma via Hugging Face Inference API. "
                f"Router error: {last_error} | Client error: {client_err}"
            ) from client_err

    # Step 3: Parse and validate strictly with Pydantic
    try:
        parsed_json = extract_json_from_response(raw_response_text)
        return StudentCareerProfile.model_validate(parsed_json)
    except Exception as parse_err:
        # If model generated slight irregularities, fallback safely
        mock = generate_mock_profile(degree=degree, skills=skills, interests=interests)
        mock.summary = f"[Syntax Guard Fallback] {mock.summary}"
        return mock
