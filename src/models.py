"""
Pydantic data models for the PathWise career recommendation engine.
Features the Future Me Simulator data structures with resilient validators.
"""

import re
from typing import List, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class FutureScenario(BaseModel):
    """Represents a simulated future career scenario for a student."""
    role: str = Field(..., description="Target job title or career role")
    match_percentage: int = Field(
        default=85,
        ge=0,
        le=100,
        description="Fit score from 0 to 100 based on skills and interests",
    )
    confidence_score: int = Field(
        default=88,
        ge=0,
        le=100,
        description="Career confidence score from 0 to 100 indicating likelihood of long-term success and fulfillment",
    )
    reasoning: str = Field(
        default="",
        description="Explanation of why this role matches their degree, skills, and interests",
    )
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
                    or "High-Leverage Production Skill"
                )
        return data


class RoadmapPhase(BaseModel):
    """A structured milestone in the student's career preparation journey."""
    timeframe: str = Field(
        default="Phase 1: Foundation",
        description="Timeline period (e.g., Phase 1: Months 1-2, Immediate, 3-6 Months)",
    )
    action_items: List[str] = Field(
        default_factory=list,
        description="Concrete, actionable steps, projects, or certifications to undertake",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_phase(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "timeframe" not in data:
                data["timeframe"] = (
                    data.get("phase")
                    or data.get("timeline")
                    or data.get("title")
                    or "Upcoming Sprint Phase"
                )
            if "action_items" not in data:
                data["action_items"] = (
                    data.get("items")
                    or data.get("tasks")
                    or data.get("actions")
                    or []
                )
            if isinstance(data.get("action_items"), str):
                data["action_items"] = [data["action_items"]]
        return data


class StudentCareerProfile(BaseModel):
    """Complete analyzed career guidance profile produced for a student."""
    summary: str = Field(
        ...,
        description="High-level overview of the student's profile, readiness, and trajectory",
    )
    career_matches: List[FutureScenario] = Field(
        default_factory=list,
        description="Ranked future career scenarios matching the student's degree, skills, and interests",
    )
    skill_gaps: List[SkillGap] = Field(
        default_factory=list,
        description="Key skill gap comparisons to focus on",
    )
    roadmap: List[RoadmapPhase] = Field(
        default_factory=list,
        description="Step-by-step phased roadmap towards career readiness",
    )

    @model_validator(mode="before")
    @classmethod
    def handle_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "career_matches" not in data:
                for alt in ["future_scenarios", "scenarios", "matches", "roles"]:
                    if alt in data and isinstance(data[alt], list):
                        data["career_matches"] = data[alt]
                        break
            if "skill_gaps" not in data:
                for alt in ["skills_gap", "skill_gap", "gaps"]:
                    if alt in data and isinstance(data[alt], list):
                        data["skill_gaps"] = data[alt]
                        break
            if "roadmap" not in data:
                for alt in ["milestones", "action_plan", "phases"]:
                    if alt in data and isinstance(data[alt], list):
                        data["roadmap"] = data[alt]
                        break
        return data
