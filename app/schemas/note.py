from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class NoteUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class NoteRead(BaseModel):
    id: str
    application_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
