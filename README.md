# Pathwise 🔮 — Future Me Simulator

> An AI-driven career trajectory simulator transforming post-graduation paralysis into data-backed clarity using open-weight intelligence. Built for the Hacktoberfest Weekend Challenge.

**👉 [Live Demo](https://pathwise-cl9l.onrender.com)**

---

## 📖 What is Pathwise?
Choosing a career trajectory in a shifting tech landscape often results in decision fatigue and anxiety. Traditional career advice is static, generic, and divorced from individual skillsets.

**Pathwise** operates as a dynamic **"Future Me Simulator"**:
1. **Models Personal Scenarios:** Ingests skills, current interests, and industry verticals to project 5-year outlooks.
2. **Evaluates Friction:** Quantifies transition difficulty, industry volatility, and skill saturation.
3. **Outputs Actionable Steps:** Translates ambiguous goals into concrete milestones and structured project roadmaps.

## ✨ Key Features
- **🔮 Future Me Simulator:** Simulates dynamic career branches using structured prompt flows powered by Gemma-2.
- **🕸️ Visual Risk Radar:** Visualizes market saturation, technological disruption risk, and educational barriers.
- **🗺️ 5-Year Actionable Roadmap:** Breaks down long-term aspirations into quarterly skill sprints and verifiable portfolio milestones.
- **🍱 Bento-Grid Dashboard:** High-density, modular UI built cleanly on Streamlit.

## 🛠️ Tech Stack
| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Responsive Bento dashboard & interactive inputs |
| **AI Model** | Google Gemma-2-9b-it | High-reasoning open-weight language model |
| **API Provider** | Hugging Face Serverless API | Low-latency inference pipeline |
| **Validation** | Pydantic / Python | Strict output validation & error handling |
| **Hosting** | Render Web Services | Cloud production container running 24/7 |

## 🏗️ Architecture Flow
```text
User Input (Streamlit UI) 
    ──> Pydantic Schema Validation 
    ──> Prompt Engine 
    ──> Hugging Face Inference API (Gemma-2-9b-it) 
    ──> Structured JSON Parsing 
    ──> Bento Dashboard & Radar Visualizer
