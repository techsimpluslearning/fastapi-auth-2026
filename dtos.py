
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import datetime

class UserCreateDTO(BaseModel):
    name: str
    username: str
    email: str
    password : str
    role : Literal["user", "admin"] = "user"

class UserResponseDTO(BaseModel):
    id:int
    name: str
    username: str
    role: str
    email: str
    is_active: bool
    is_verified:bool
    is_otp_active:bool
    created_at: datetime
    updated_at: datetime


class UserLoginDTO(BaseModel):
    username: str
    password : str


class UserLoginResponseDTO(BaseModel):
    token: str
    user: UserResponseDTO


class OTPUserCreateDTO(BaseModel):
    name: str = "Update Your Name"
    email: EmailStr
    role : Literal["user", "admin"] = "user"


class OTPUserLoginDTO(BaseModel):
    email: EmailStr

class VarifyOTPDTO(BaseModel):
    email: str
    otp:str