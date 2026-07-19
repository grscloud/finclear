from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# --- 基础/通用请求 ---
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

class LoginRequest(BaseModel):
    username: str  # 前端通常叫 username，也可兼容邮箱输入
    password: str

class ResetPasswordReq(BaseModel):
    user_id: UUID
    new_password: str

# --- 租户/用户管理请求 ---
class InviteUserReq(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    company_id: Optional[str] = None
    role_id: int = Field(
        ..., 
        description="角色ID：1-超级管理员(不通过此接口创建), 2-公司管理员, 3-普通员工, 4-访客"
    )

class UpdateUserStatusReq(BaseModel):
    status: str

class UpdateUserRoleReq(BaseModel):
    role_id: int

# --- 响应模型 ---
class LoginResponse(BaseModel):
    token: str
    user_id: UUID
    username: str
    email: str  # 👈 确保这一行在 Schema 里也存在
    company_id: Optional[UUID] = None
    role_code: Optional[str] = None
    is_initial_password: bool
    access_token: str
    token_type: str = "bearer"

class RoleItem(BaseModel):
    role_id: int
    code: str
    name: str

class UserListItem(BaseModel):
    user_id: UUID
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: EmailStr
    status: str
    role: RoleItem

class PaginatedUserList(BaseModel):
    total: int
    page: int
    limit: int
    items: List[UserListItem]

class InvitedUserResp(BaseModel):
    user_id: UUID
    email: EmailStr

class UpdatedUserResp(BaseModel):
    user_id: UUID
    status: Optional[str] = None
    role_id: Optional[int] = None


###############Company##################
# --- 请求模型 (Requests) ---
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="公司名称")
    invoice_number: Optional[str] = Field(None, max_length=14, description="纳税人识别号/统一社会信用代码")

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="公司名称")
    invoice_number: Optional[str] = Field(None, max_length=14, description="纳税人识别号")

# --- 响应模型 (Responses) ---
class CompanyResponse(BaseModel):
    id: UUID
    name: str
    invoice_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 允许 SQLAlchemy 模型对象直接转换为 Pydantic

class PaginatedCompanyList(BaseModel):
    total: int
    page: int
    limit: int
    items: List[CompanyResponse]

class UpdateUserReq(BaseModel):
    company_id: Optional[UUID] = None  # 当前操作的公司 ID（用于修改该用户在此公司的角色）
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None      # 新的角色 ID
    status: Optional[str] = None       # 账号状态，例如 "active" / "inactive"