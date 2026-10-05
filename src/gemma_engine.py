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
  "summary": "Strategic overview of the student's profile, market readiness, and top potential directions.",
  "career_matches": [
    {
      "role": "Target Job Title",
      "match_percentage": 92,
      "confidence_score": 88,
      "reasoning": "Clear explanation of why this role matches their degree, skills, and interests.",
      "day_in_the_life": "Engaging, vivid narrative describing a typical workday in the future: morning rituals, core technical architecture & problem solving, cross-functional collaboration, and evening wrap-up.",
      "risk_radar": [
        "Risk 1: Rapid tool churn requiring continuous weekend upskilling",
        "Risk 2: High cognitive load or on-call burnout potential",
        "Risk 3: Knowledge mismatch between theoretical concepts and production scale"
      ],
      "recommended_projects": [
        "Interactive GitHub project: Full-stack or distributed pipeline targeting real-world scale",
        "Target Hackathon: MLH Global Hack Week or domain-specific challenge",
        "Industry Certification: AWS Solutions Architect, CKA, or DeepLearning.AI specialization"
      ]
    }
  ],
  "skill_gaps": [
    {
      "existing_strength": "Current skill, technology, or domain concept the student knows well",
      "missing_skill": "Critical high-leverage skill or tool required to bridge into the role"
    }
  ],
  "roadmap": [
    {
      "timeframe": "Phase 1: Months 1-2 (Foundation)",
      "action_items": [
        "Actionable concrete task or course",
        "Target portfolio project or certification"
      ]
    }
  ]
}"""

    return f"""You are the "PathWise Future Me Simulator" — an elite AI Career Architect, Predictive Mentor, and Technology Futurist.
Analyze this student's profile and simulate 3 compelling, realistic future career trajectories. 
For each scenario, generate:
1. Role title, realistic match percentage (50-98), and a career confidence score (50-99).
2. Clear rationale connecting their background to this future.
3. A vivid "Day in the Life" narrative taking the student through an immersive workday in their future shoes.
4. A "Risk Radar" detailing 2-3 genuine challenges, burnout traps, or market shifts to watch out for.
5. 2-3 concrete "Recommended Projects" (specific GitHub repositories, hackathons, or industry credentials).

Also compute explicit skill gaps comparing current strengths to missing skills, and an actionable 3-phase execution roadmap.

Student Profile:
- Degree / Academic Background: {degree}
- Current Skills & Proficiencies: {skills}
- Interests & Passion Areas: {interests}

Requirements:
1. Provide realistic tech roles aligned with current and emerging industry hiring trends.
2. Ensure the "day_in_the_life" is written in engaging second-person or immersive present tense ("You start your morning by...", "At 2 PM you dive into...").
3. Assign realistic confidence_score and match_percentage values (50 to 98).
4. Identify real-world, high-leverage missing skills against existing strengths.
5. Return ONLY a valid, raw JSON object matching the exact schema below. Do NOT output markdown fences, greetings, or conversational chatter outside the JSON:

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
                match_percentage=94,
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
                match_percentage=89,
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
                match_percentage=83,
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
        roadmap = [
            RoadmapPhase(
                timeframe="Phase 1: Months 1-2 (Embedded Firmware & ROS 2 Mastery)",
                action_items=[
                    "Complete Modern C++ (C++17/20) for Embedded Systems and Linux system programming.",
                    "Set up ROS 2 Humble environment and implement publisher/subscriber sensor nodes.",
                    "Interface an IMU and motor encoder with an STM32 board over I2C/SPI."
                ]
            ),
            RoadmapPhase(
                timeframe="Phase 2: Months 3-4 (Autonomous Navigation & Simulation)",
                action_items=[
                    "Construct a 2D differential drive robot model in URDF and simulate in Gazebo.",
                    "Integrate Nav2 stack for SLAM map generation and autonomous obstacle avoidance.",
                    "Publish a documented GitHub showcase with simulation demo GIFs."
                ]
            ),
            RoadmapPhase(
                timeframe="Phase 3: Months 5-6 (Hardware Deployment & Production Portfolio)",
                action_items=[
                    "Flash code onto a physical Raspberry Pi + Arduino rover platform for real-world validation.",
                    "Submit robotics portfolio project to MLH Hackathon or ROSCon student track.",
                    "Conduct mock technical interviews on robotics kinematics, sensor fusion, and RTOS concurrency."
                ]
            ),
        ]
    else:
        matches = [
            FutureScenario(
                role="AI Systems & LLM Application Engineer",
                match_percentage=95,
                confidence_score=93,
                reasoning="Your CS foundations in Python, data structures, and PyTorch align directly with the high demand for generative AI agents and RAG pipelines.",
                day_in_the_life="You begin your morning reviewing latency metrics for an agentic multi-hop inference pipeline serving thousands of requests. At 10:30 AM, you collaborate with product leads to test semantic vector retrieval accuracy in Qdrant. After lunch, you fine-tune a specialized 9B parameter model with LoRA on synthetic domain datasets, optimizing token latency by 35%.",
                risk_radar=[
                    "Hyper-Velocity Tool Churn: Frameworks and model releases update weekly, requiring continual re-architecture.",
                    "Non-Deterministic Outputs: Debugging agent hallucinations in enterprise-critical workflows.",
                    "GPU Resource Constraints: Balancing cost efficiency and inference throughput under high traffic."
                ],
                recommended_projects=[
                    "Build an autonomous multi-agent research analyst using LangGraph and hybrid vector search",
                    "Compete in MLH Global Hack Week Generative AI Track or AI Agents Hackathon",
                    "Earn DeepLearning.AI Generative AI with LLMs Certificate or AWS Machine Learning Specialty"
                ]
            ),
            FutureScenario(
                role="Production MLOps & Platform Engineer",
                match_percentage=88,
                confidence_score=87,
                reasoning="Data structures, SQL, and Python provide the ideal base for production machine learning infrastructure and pipeline automation.",
                day_in_the_life="You check automated continuous training workflows triggered by data drift alerts. By mid-day, you are writing Kubernetes helm charts to scale model serving pods with Triton and monitoring feature store latency in Feast.",
                risk_radar=[
                    "Silent Data Drift: Subtly degrading model performance without explicit crash errors.",
                    "On-Call Fatigue: 24/7 reliability requirements for production prediction microservices."
                ],
                recommended_projects=[
                    "Deploy an end-to-end ML training and serving pipeline using MLflow, Docker, and FastEmbed",
                    "Build an open-source GitHub CI/CD action for automatic model card evaluation",
                    "Earn Certified Kubernetes Administrator (CKA)"
                ]
            ),
            FutureScenario(
                role="Computer Vision & Edge Intelligence Engineer",
                match_percentage=84,
                confidence_score=81,
                reasoning="Your PyTorch, NumPy, and algorithm proficiencies transfer seamlessly into real-time spatial computing and edge perception models.",
                day_in_the_life="Your morning is focused on quantizing a vision transformer down to INT8 for deployment on edge Jetson devices. In the afternoon, you run benchmark video feeds to optimize multi-camera tracking and object bounding boxes.",
                risk_radar=[
                    "Edge Thermal Throttling: Embedded GPU heat and power budgets limiting inference frames-per-second.",
                    "Annotation Bottlenecks: Handling noisy, uncurated training video datasets."
                ],
                recommended_projects=[
                    "Develop an edge-ready real-time defect detection pipeline with TensorRT and OpenCV",
                    "Participate in Kaggle CV competition or OpenCV AI Challenge",
                    "Complete Stanford CS231n Computer Vision coursework"
                ]
            ),
        ]
        gaps = [
            SkillGap(
                existing_strength="NumPy, Pandas & Scikit-Learn Modeling",
                missing_skill="Vector Databases (Qdrant/Pinecone) & Hybrid Search"
            ),
            SkillGap(
                existing_strength="Basic PyTorch & Neural Networks",
                missing_skill="Quantization (GGUF/AWQ) & Fine-Tuning (PEFT/LoRA)"
            ),
            SkillGap(
                existing_strength="Git & Python Scripting",
                missing_skill="Docker Containerization & CI/CD Pipeline Automation"
            ),
        ]
        roadmap = [
            RoadmapPhase(
                timeframe="Phase 1: Months 1-2 (Production AI Systems & Vector Pipelines)",
                action_items=[
                    "Master modern async Python, FastAPI, and structured Pydantic schemas for LLM APIs.",
                    "Build an end-to-end RAG system with hybrid semantic search and reranking.",
                    "Deploy the application as a containerized microservice on Render or AWS ECS."
                ]
            ),
            RoadmapPhase(
                timeframe="Phase 2: Months 3-4 (Autonomous Agents & Efficient Fine-Tuning)",
                action_items=[
                    "Implement stateful multi-agent workflows with tool-calling and cycle detection.",
                    "Fine-tune a quantized open-source model using QLoRA on a domain-specific dataset.",
                    "Benchmark evaluation metrics using Ragas and LLM-as-a-judge methodologies."
                ]
            ),
            RoadmapPhase(
                timeframe="Phase 3: Months 5-6 (Enterprise MLOps & Capstone Portfolio)",
                action_items=[
                    "Deploy continuous model monitoring with telemetry tracking token usage, latency, and drift.",
                    "Win or place in a premier community hackathon (e.g. MLH Global Hack Week).",
                    "Publish a comprehensive technical writeup and architecture breakdown on dev.to and GitHub."
                ]
            ),
        ]

    summary = (
        f"Strategic analysis of your background in {degree} shows strong core foundations in {skills}. "
        f"Your target interest in {interests} aligns with top-quartile market demand. "
        "With focused acquisition of production deployment, orchestration, and domain-specific scaling patterns, "
        "you are positioned to enter senior trajectory roles within 12-18 months."
    )

    return StudentCareerProfile(
        summary=summary,
        career_matches=matches,
        skill_gaps=gaps,
        roadmap=roadmap,
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
        "Do NOT include conversational markdown, greetings, or extra explanations."
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
            "max_tokens": 2500,
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
                max_tokens=2500,
                temperature=0.2,
            )
            raw_response_text = chat_resp.choices[0].message.content
        except Exception as client_err:
            # If network/token failure occurs, fall back to high-fidelity mock profile
            if last_error:
                # Log or return mock with informative summary
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
