# backend/app/schemas/user.py

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str
    email: EmailStr | None = None
    name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    company: str | None = None
    location: str | None = None
    github_url: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    github_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    location: str | None = None