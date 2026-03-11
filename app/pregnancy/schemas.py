from typing import Optional

from pydantic import BaseModel, Field


class ClickLogCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=100)
    source_page: Optional[str] = Field(default=None, max_length=255)
    cta_name: Optional[str] = Field(default=None, max_length=255)
    target_url: Optional[str] = Field(default=None, max_length=1000)
    city: Optional[str] = Field(default=None, max_length=100)
    test_name: Optional[str] = Field(default=None, max_length=150)


class ClickLogResponse(BaseModel):
    ok: bool
    id: int

    class Config:
        from_attributes = True


class ToolUsageLogCreate(BaseModel):
    tool_name: str = Field(..., min_length=1, max_length=100)
    method_used: Optional[str] = Field(default=None, max_length=100)
    source_page: Optional[str] = Field(default=None, max_length=255)


class ToolUsageLogResponse(BaseModel):
    ok: bool
    id: int

    class Config:
        from_attributes = True