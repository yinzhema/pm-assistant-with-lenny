"""
Pydantic models for artifact builder and translation endpoints.
"""
from typing import Literal, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

class QuestionOut(BaseModel):
    id: str
    text: str
    section_key: str
    section_label: str
    placeholder: str
    why_it_matters: str
    kb_query: Optional[str] = None
    allow_skip: bool = True


class ArtifactTypeOut(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    question_count: int


# ---------------------------------------------------------------------------
# Artifact Builder
# ---------------------------------------------------------------------------

class StartArtifactSessionRequest(BaseModel):
    session_id: str
    artifact_type: str  # "play-to-win" | "opportunity-assessment" | "idea-to-agent"


class StartArtifactSessionResponse(BaseModel):
    artifact_session_id: str
    artifact_type: str
    questions: list[QuestionOut]


class AnswerQuestionRequest(BaseModel):
    question_id: str
    answer: str


class SkipQuestionRequest(BaseModel):
    question_id: str


class JumpToQuestionRequest(BaseModel):
    question_id: str


class JumpToQuestionResponse(BaseModel):
    current_index: int


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

class GapItem(BaseModel):
    category: Literal[
        "implicit_judgment",
        "missing_escalation",
        "ambiguous_scope",
        "missing_constraints",
        "metric_ambiguity",
        "tool_permissions",
    ]
    section: str
    description: str
    severity: Literal["high", "medium", "low"]
    suggested_question: str


class StartTranslationRequest(BaseModel):
    session_id: str
    prd_text: str
    prd_filename: Optional[str] = None


class ClarifyGapRequest(BaseModel):
    question_id: str   # maps to GapItem.category + section
    answer: str


# ---------------------------------------------------------------------------
# Artifact types list
# ---------------------------------------------------------------------------

class ArtifactTypesResponse(BaseModel):
    artifact_types: list[ArtifactTypeOut]
