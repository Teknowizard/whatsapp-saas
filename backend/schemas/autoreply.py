from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class AutoReplyCreate(BaseModel):
    keyword: str
    response: str

    @field_validator("keyword", "response")
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class AutoReplyUpdate(BaseModel):
    keyword: Optional[str] = None
    response: Optional[str] = None


class AutoReplyResponse(BaseModel):
    id: int
    user_id: int
    keyword: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True
