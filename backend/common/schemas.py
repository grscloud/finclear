from pydantic import BaseModel, EmailStr, Field
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

# 接收前端传来的登录数据格式
class LoginRequest(BaseModel):
    username: str  # 前端传入的账号，通常是邮箱
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: UUID
    email: str
    company_id: Optional[UUID] = None
    role_code: Optional[str] = None

class ResetPasswordReq(BaseModel):
    user_id: UUID = Field(..., description="要重置密码的用户ID")
    new_password: str = Field(..., min_length=8, description="新密码，建议后端接收后进行hash处理")