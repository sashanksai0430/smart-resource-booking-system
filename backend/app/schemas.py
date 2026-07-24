from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from .models import RoleEnum, ResourceTypeEnum, ResourceStatusEnum, BookingStatusEnum


# ---------- Auth / User ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    department: Optional[str] = None
    role: Optional[RoleEnum] = RoleEnum.USER


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    department: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum


class RoleUpdate(BaseModel):
    role: RoleEnum


# ---------- Resource ----------
class ResourceCreate(BaseModel):
    name: str
    type: ResourceTypeEnum
    description: Optional[str] = None
    location: Optional[str] = None
    requires_approval: bool = True


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[ResourceStatusEnum] = None
    requires_approval: Optional[bool] = None


class ResourceOut(BaseModel):
    id: int
    name: str
    type: ResourceTypeEnum
    description: Optional[str] = None
    location: Optional[str] = None
    status: ResourceStatusEnum
    requires_approval: bool

    class Config:
        from_attributes = True


# ---------- Booking ----------
class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime
    purpose: Optional[str] = None


class BookingOut(BaseModel):
    id: int
    resource_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    purpose: Optional[str] = None
    status: BookingStatusEnum
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingDecision(BaseModel):
    approve: bool
    reason: Optional[str] = None


# ---------- Penalty ----------
class PenaltyOut(BaseModel):
    id: int
    booking_id: int
    user_id: int
    amount: float
    reason: str
    is_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True
