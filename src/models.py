"""
Pydantic data models for the PathWise career recommendation engine.
Features the Future Me Simulator data structures with resilient multi-schema validators.
"""

import re
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class FutureScenario(BaseModel):
    """Represents a simulated future career scenario for a student."""
    role: str = Field(default="Target Technology Role", description="Target job title or career role")
    career: Optional[str] = Field(default=None, description="Alias for role")
    match_percentage: int = Field(
        default=85,
        ge=0,
        le=100,
        description="Fit score from 0 to 100 based on skills and interests",
    )
    score: Optional[int] = Field(default=None, description="Alias for match_percentage")
    confidence_score: int = Field(
        default=88,
        ge=0,
        le=100,
        description="Career confidence score from 0 to 100 indicating likelihood of long-term success",
    )
    reasoning: str = Field(
        default="",
        description="Explanation of why this role matches their degree, skills, and interests",
    )
    reason: Optional[str] = Field(default=None, description="Alias for reasoning")
    day_in_the_life: str = Field(
        default="A typical day in this role involves solving complex engineering challenges, collaborating with distributed cross-functional teams, and shipping production-grade solutions.",
        description="A short narrative of what a typical workday looks like in the future",
    )
    risk_radar: List[str] = Field(
        default_factory=list,
        description="Potential burnout risks, mismatches, or industry challenges",
    )
    recommended_projects: List[str] = Field(
        default_factory=list,
        description="Specific hackathons, certs, or github projects to build",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_scenario(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Role / Career normalization
            role = data.get("role") or data.get("career") or data.get("title") or data.get("job_title") or "Technology Specialist"
            data["role"] = str(role)
            data["career"] = str(role)

            # Score / Match normalization
            score_val = data.get("match_percentage") if "match_percentage" in data else data.get("score", data.get("fit_score", 85))
            data["match_percentage"] = score_val
            data["score"] = score_val

            if "confidence_score" not in data:
                data["confidence_score"] = score_val

            # Reasoning / Reason normalization
            reasoning = data.get("reasoning") or data.get("reason") or data.get("rationale") or data.get("description") or ""
            data["reasoning"] = str(reasoning)
            data["reason"] = str(reasoning)

        return data

    @field_validator("match_percentage", "confidence_score", mode="before")
    @classmethod
    def coerce_percentage(cls, v: Any) -> int:
        """Coerce percentages that might be strings (e.g., '92%') or floats into clamped ints."""
        if v is None:
            return 85
        if isinstance(v, (int, float)):
            return max(0, min(100, int(round(v))))
        if isinstance(v, str):
            cleaned = re.sub(r"[^\d.]", "", v)
            if cleaned:
                try:
                    return max(0, min(100, int(round(float(cleaned)))))
                except ValueError:
                    return 85
        return 85

    @field_validator("day_in_the_life", mode="before")
    @classmethod
    def coerce_day_narrative(cls, v: Any) -> str:
        """Allow lists or strings for the workday narrative."""
        if isinstance(v, list):
            return "\n\n".join(str(item) for item in v)
        return str(v) if v is not None else ""

    @field_validator("risk_radar", "recommended_projects", mode="before")
    @classmethod
    def coerce_string_list(cls, v: Any) -> List[str]:
        """Convert single strings or lists into clean string lists."""
        if isinstance(v, str):
            return [line.strip("- *").strip() for line in v.split("\n") if line.strip()]
        if isinstance(v, list):
            return [str(item).strip("- *").strip() for item in v if str(item).strip()]
        return []


# Backward-compatibility alias
CareerMatch = FutureScenario


class SkillGap(BaseModel):
    """Highlights current strengths against missing capabilities needed for target roles."""
    existing_strength: str = Field(
        default="Current Technical Foundation",
        description="Existing skill or strength the student currently possesses",
    )
    missing_skill: str = Field(
        default="High-Leverage Production Skill",
        description="Critical skill or tool required to bridge into the role",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_gap(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {
                "existing_strength": "Current Foundation",
                "missing_skill": data.strip(),
            }
        if isinstance(data, dict):
            if "existing_strength" not in data:
                data["existing_strength"] = (
                    data.get("current_skill")
                    or data.get("strength")
                    or data.get("current")
                    or "Current Technical Foundation"
                )
            if "missing_skill" not in data:
                data["missing_skill"] = (
                    data.get("target_skill")
                    or data.get("missing")
                    or data.get("gap")
                    or data.get("skill")
                    or "High-Leverage Production Skill"
                )
        return data


class RoadmapPhase(BaseModel):
    """A structured milestone in the student's career preparation journey."""
    title: str = Field(
        default="Sprint Phase",
        description="Milestone title",
    )
    timeline: str = Field(
        default="Phase 1: Foundation",
        description="Timeline or duration (e.g. Months 1-3)",
    )
    timeframe: str = Field(
        default="Phase 1: Foundation",
        description="Timeline period (legacy alias for timeline)",
    )
    objective: str = Field(
        default="",
        description="Strategic objective of this sprint phase",
    )
    actions: List[str] = Field(
        default_factory=list,
        description="Concrete, actionable steps, projects, or certifications",
    )
    action_items: List[str] = Field(
        default_factory=list,
        description="Legacy alias for actions",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_phase(cls, data: Any) -> Any:
        if isinstance(data, dict):
            title = data.get("title") or data.get("name") or data.get("phase") or "Milestone Phase"
            timeline = data.get("timeline") or data.get("timeframe") or data.get("duration") or "Upcoming Sprint"
            objective = data.get("objective") or data.get("goal") or data.get("summary") or ""

            actions = (
                data.get("actions")
                or data.get("action_items")
                or data.get("items")
                or data.get("tasks")
                or []
            )
            if isinstance(actions, str):
                actions = [line.strip("- *").strip() for line in actions.split("\n") if line.strip()]
            elif isinstance(actions, list):
                actions = [str(item).strip("- *").strip() for item in actions if str(item).strip()]

            data["title"] = str(title)
            data["timeline"] = str(timeline)
            data["timeframe"] = str(timeline)
            data["objective"] = str(objective)
            data["actions"] = actions
            data["action_items"] = actions
        return data


class StudentCareerProfile(BaseModel):
    """Complete analyzed career guidance profile produced for a student."""
    summary: str = Field(
        default="",
        description="High-level overview of the student's profile, readiness, and trajectory",
    )
    executive_summary: Optional[str] = Field(
        default=None,
        description="Executive summary of the candidate trajectory",
    )
    top_trajectory: str = Field(
        default="Technology Specialist",
        description="The primary recommended career trajectory",
    )
    fit_score: int = Field(
        default=90,
        ge=0,
        le=100,
        description="Overall capability fit percentage",
    )
    career_confidence: int = Field(
        default=88,
        ge=0,
        le=100,
        description="Confidence score for career transition and long-term success",
    )
    top_3_career_rankings: List[FutureScenario] = Field(
        default_factory=list,
        description="Ranked top 3 career pathways",
    )
    career_matches: List[FutureScenario] = Field(
        default_factory=list,
        description="Ranked future career scenarios matching student background",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Core technical and architectural candidate strengths",
    )
    skill_gaps: List[SkillGap] = Field(
        default_factory=list,
        description="Key skill gap comparisons to focus on",
    )
    market_outlook: str = Field(
        default="",
        description="Macro market demand, hiring velocity, and compensation outlook",
    )
    future_self_simulation: Dict[str, str] = Field(
        default_factory=dict,
        description="Projections over time (e.g., 1_year, 3_year, 5_year)",
    )
    milestones: List[RoadmapPhase] = Field(
        default_factory=list,
        description="Structured execution roadmap with objectives and action items",
    )
    roadmap: List[RoadmapPhase] = Field(
        default_factory=list,
        description="Step-by-step phased roadmap towards career readiness",
    )
    recommended_projects: List[str] = Field(
        default_factory=list,
        description="High-impact portfolio projects and certifications",
    )
    learning_path: List[str] = Field(
        default_factory=list,
        description="Structured curriculum learning sequence across phases",
    )
    final_verdict: str = Field(
        default="",
        description="Authoritative closing strategic recommendation",
    )
    engine_source: str = Field(
        default="Google Gemma 3 AI",
        description="Engine that generated this simulation (Live Gemma AI or Mock Fallback)",
    )

    @model_validator(mode="before")
    @classmethod
    def handle_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Summary / Executive Summary
            summary_text = (
                data.get("executive_summary")
                or data.get("summary")
                or data.get("overview")
                or ""
            )
            data["summary"] = summary_text
            data["executive_summary"] = summary_text

            # Career Matches / Top 3 Rankings
            matches = (
                data.get("top_3_career_rankings")
                or data.get("career_matches")
                or data.get("future_scenarios")
                or data.get("scenarios")
                or data.get("matches")
                or data.get("roles")
                or []
            )
            data["career_matches"] = matches
            data["top_3_career_rankings"] = matches

            # Derive Top Trajectory, Fit Score, Career Confidence
            if not data.get("top_trajectory"):
                if matches and isinstance(matches, list) and len(matches) > 0:
                    first = matches[0]
                    if isinstance(first, dict):
                        data["top_trajectory"] = first.get("career") or first.get("role") or first.get("title") or "Technology Specialist"
                    elif hasattr(first, "role"):
                        data["top_trajectory"] = first.role
                else:
                    data["top_trajectory"] = "Technology Specialist"

            if data.get("fit_score") is None:
                if matches and isinstance(matches, list) and len(matches) > 0:
                    first = matches[0]
                    if isinstance(first, dict):
                        data["fit_score"] = first.get("score") or first.get("match_percentage") or 90
                    elif hasattr(first, "match_percentage"):
                        data["fit_score"] = first.match_percentage
                else:
                    data["fit_score"] = 90

            if data.get("career_confidence") is None:
                if matches and isinstance(matches, list) and len(matches) > 0:
                    first = matches[0]
                    if isinstance(first, dict):
                        data["career_confidence"] = first.get("confidence_score") or first.get("score") or 88
                    elif hasattr(first, "confidence_score"):
                        data["career_confidence"] = first.confidence_score
                else:
                    data["career_confidence"] = 88

            # Skill Gaps
            gaps = (
                data.get("skill_gaps")
                or data.get("skills_gap")
                or data.get("skill_gap")
                or data.get("gaps")
                or []
            )
            data["skill_gaps"] = gaps

            # Roadmap / Milestones
            milestones = (
                data.get("milestones")
                or data.get("roadmap")
                or data.get("action_plan")
                or data.get("phases")
                or []
            )
            data["milestones"] = milestones
            data["roadmap"] = milestones

            # Future self simulation normalization
            future_sim = data.get("future_self_simulation") or {}
            if isinstance(future_sim, dict):
                data["future_self_simulation"] = {str(k): str(v) for k, v in future_sim.items()}
            else:
                data["future_self_simulation"] = {}

            # Final verdict fallback
            if not data.get("final_verdict") and summary_text:
                data["final_verdict"] = summary_text

        return data
