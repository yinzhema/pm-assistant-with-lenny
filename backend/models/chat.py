"""
Pydantic models for chat endpoints.
"""
from enum import Enum
from typing import List

from pydantic import BaseModel


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class HistoryMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[HistoryMessage] = []


class Source(BaseModel):
    number: int
    guest: str = ""
    author: str = ""
    title: str = ""
    youtube_url: str = ""
    url: str = ""
    timestamp: str = ""
    source_name: str = ""
    similarity_score: float = 0.0
