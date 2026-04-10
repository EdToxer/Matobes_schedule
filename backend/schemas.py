"""
Pydantic schemas for request validation and response serialization.
Kept separate from ORM models for clean layering.
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import date, time, datetime
from models import ShiftStatus, ShiftType, EmployeeRole


# ─── Organization ────────────────────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Team ────────────────────────────────────────────────────────────────────

class TeamCreate(BaseModel):
    name: str
    organization_id: int
    parent_team_id: Optional[int] = None

class TeamOut(BaseModel):
    id: int
    name: str
    organization_id: int
    parent_team_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Employee ────────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    name: str
    email: str
    password: str  # plain-text, будет захеширован в роуте
    role: EmployeeRole = EmployeeRole.EMPLOYEE
    team_id: Optional[int] = None
    position: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return v

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[EmployeeRole] = None
    team_id: Optional[int] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None

class EmployeeOut(BaseModel):
    id: int
    name: str
    email: str
    role: EmployeeRole
    team_id: Optional[int]
    position: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Shift ───────────────────────────────────────────────────────────────────

class ShiftCreate(BaseModel):
    employee_id: int
    date: date
    start_time: time
    end_time: time
    shift_type: ShiftType = ShiftType.PLANNED
    notes: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, end: time, info) -> time:
        start = info.data.get("start_time")
        if start and end <= start:
            raise ValueError("end_time must be after start_time")
        return end

class ShiftUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    notes: Optional[str] = None
    status: Optional[ShiftStatus] = None

class ShiftConfirm(BaseModel):
    """Используется менеджером для подтверждения план/факт по смене.
    confirmed_by_id намеренно убран — берётся из JWT-токена на сервере.
    """
    actual_start_time: Optional[time] = None
    actual_end_time: Optional[time] = None
    status: ShiftStatus  # confirmed или rejected

class ShiftOut(BaseModel):
    id: int
    employee_id: int
    date: date
    start_time: time
    end_time: time
    shift_type: ShiftType
    status: ShiftStatus
    notes: Optional[str]
    actual_start_time: Optional[time]
    actual_end_time: Optional[time]
    confirmed_by_id: Optional[int]
    confirmed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Reports ─────────────────────────────────────────────────────────────────

class PlanFactRow(BaseModel):
    employee_id: int
    employee_name: str
    date: date
    planned_start: Optional[time]
    planned_end: Optional[time]
    actual_start: Optional[time]
    actual_end: Optional[time]
    planned_hours: Optional[float]
    actual_hours: Optional[float]
    delta_hours: Optional[float]
    status: Optional[ShiftStatus]
