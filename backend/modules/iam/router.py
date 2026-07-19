from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import Optional
from uuid import UUID
import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from modules.iam.schemas import InviteUserReq, CompanyResponse, CompanyUpdate, PaginatedCompanyList, CompanyCreate, UpdateUserReq, LoginResponse
from core.dependencies import get_current_company_id, get_db, get_current_user
from common.models import User, TenantUserRole
from common import schemas 
from common.schemas import ResponseModel
from modules.iam import services
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta

from modules.iam.services import (
    get_company_by_id, 
    create_company, 
    update_company_details, 
    get_all_companies, 
    soft_delete_company
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

router = APIRouter(tags=["IAM - 权限与用户管理"])

SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"

# ==========================================
# API 1: 认证与登录
# ==========================================
@router.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(payload: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. 直接全局查用户 (Async 写法)
    user_stmt = select(User).where(User.username == payload.username, User.is_deleted == False)
    
    # 【修改处 1】: 将 .scalar_first() 改为 .scalar_one_or_none() 
    # 或者用 (await db.execute(user_stmt)).scalars().first()
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
        
    # 2. 校验密码
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
        
    # 3. 动态去找他所属的租户/公司 
    role_stmt = select(TenantUserRole).options(selectinload(TenantUserRole.role)).where(
        TenantUserRole.user_id == user.id, 
        TenantUserRole.is_deleted == False
    )
    
    # 【修改处 2】: 同样修改这里的 .scalar_first()
    tenant_role = (await db.execute(role_stmt)).scalars().first()

    # 假设用户校验通过，查库获得用户信息：
    user_data = {
        "user_id": str(user.id),        # 用户ID
        "company_id": str(tenant_role.company_id if tenant_role else None),  # 所属公司ID
        "role_code": tenant_role.role.code if tenant_role and tenant_role.role else None,  # 角色
    }
    
    # 设置过期时间
    expire = datetime.utcnow() + timedelta(hours=24)
    # 将角色和公司信息写入 token
    to_encode = user_data.copy()
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # 4. 组装返回数据
    return LoginResponse(
        token="mock-jwt-token", 
        user_id=user.id,
        username=user.username,
        email=user.email,
        company_id=tenant_role.company_id if tenant_role else None, 
        role_code=tenant_role.role.code if tenant_role and tenant_role.role else None, 
        is_initial_password=user.is_initial_password,
        access_token=token,
        token_type="bearer"
    )

# ==========================================
# API 2: 重置密码
# ==========================================
@router.post("/api/v1/auth/reset-password", response_model=schemas.ResponseModel)
async def reset_password(
    req: schemas.ResetPasswordReq,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """重置密码：支持管理员重置或用户重置"""
    # 增加 await 关键字
    await services.reset_password(
        db=db, 
        user_id=req.user_id, 
        new_password_hash=req.new_password, 
        requester_id=req.user_id 
    )
    return schemas.ResponseModel(message="Password reset successfully")

# ==========================================
# 租户下的用户管理子路由
# ==========================================
tenant_users_router = APIRouter(prefix="/api/v1/tenant/users")

@tenant_users_router.get("", response_model=schemas.ResponseModel)
async def get_tenant_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    role_id: Optional[int] = None,
    keyword: Optional[str] = None,
    # company_id: Optional[str] = None, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取本公司的成员列表"""
    data = await services.get_tenant_users(db, current_user.company_id, page, limit, status, role_id, keyword)
    return schemas.ResponseModel(data=data)

@tenant_users_router.post("/invite", response_model=schemas.ResponseModel)
async def invite_user(
    req: InviteUserReq,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """邀请用户加入公司/分配角色"""
    try:
        data = await services.invite_tenant_user(db, req)
        return schemas.ResponseModel(code=201, message="User invited successfully", data=data)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail="Internal server error")

@tenant_users_router.delete("/{user_id}", response_model=schemas.ResponseModel)
async def remove_tenant_user(
    user_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """将用户移出系统（删除用户租户关联）"""
    await services.remove_tenant_user(db, user_id)
    return schemas.ResponseModel(message="User removed from tenant successfully")

@tenant_users_router.put("/{user_id}", response_model=schemas.ResponseModel)
async def update_user(
    user_id: UUID,
    req: UpdateUserReq,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """修改指定用户的信息（包含基本信息与租户角色）"""
    try:
        data = await services.update_tenant_user(db, user_id, req)
        return schemas.ResponseModel(code=200, message="User updated successfully", data=data)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ========================================================
# 🏢 公司/租户路由接口
# ========================================================

# 1. 获取自己公司
@router.get("/api/v1/companies/me", response_model=ResponseModel[CompanyResponse], tags=["Company - 企业租户"])
async def get_my_company(
    company_id: UUID = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    company = await get_company_by_id(db, company_id)
    return ResponseModel(data=company)

# 2. 修改自己公司
@router.put("/api/v1/companies/me", response_model=ResponseModel[CompanyResponse], tags=["Company - 企业租户"])
async def update_my_company(
    req: CompanyUpdate,
    # company_id: UUID = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    company = await update_company_details(db, current_user.company_id, req)
    return ResponseModel(message="Company information updated", data=company)

# 3. 超管全局查列表
@router.get("/api/v1/companies", response_model=ResponseModel[PaginatedCompanyList], tags=["Company - 超管后台"])
async def list_companies_global(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = await get_all_companies(db, page, limit, current_user.is_superuser, current_user.company_id, keyword)
    return ResponseModel(data=data)

# 4. 超管创建新租户
@router.post("/api/v1/companies", response_model=ResponseModel[CompanyResponse], status_code=201, tags=["Company - 超管后台"])
async def create_company_global(
    req: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    company = await create_company(db, req)
    return ResponseModel(code=201, message="Company created successfully", data=company)

# 5. 超管看指定 UUID 详情
@router.get("/api/v1/companies/{target_company_id}", response_model=ResponseModel[CompanyResponse], tags=["Company - 超管后台"])
async def get_company_global(
    target_company_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    company = await get_company_by_id(db, target_company_id)
    return ResponseModel(data=company)

# 6. 超管逻辑删除
@router.delete("/api/v1/companies/{target_company_id}", response_model=ResponseModel, tags=["Company - 超管后台"])
async def delete_company_global(
    target_company_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    res = await soft_delete_company(db, target_company_id)
    return ResponseModel(message=res["message"])

# 7. 超管修改指定 UUID 公司详情
@router.put("/api/v1/companies/{target_company_id}", response_model=ResponseModel[CompanyResponse], tags=["Company - 超管后台"])
async def update_company_global(
    req: CompanyUpdate,
    target_company_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    company = await update_company_details(db, target_company_id, req)
    return ResponseModel(message="Target company updated successfully", data=company)

# 挂载路由
router.include_router(tenant_users_router)