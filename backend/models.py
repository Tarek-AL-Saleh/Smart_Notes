from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Note(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    tags: Optional[List[str]] = []
    summary: Optional[str] = None
    created_at:  datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None 