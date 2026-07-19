from fastapi import Header, HTTPException
from uuid import UUID
from typing import Generator
from typing import AsyncGenerator
from core.database import SessionLocal
from common.models import User # 假设你有 User 模型
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
import logging

# 设置一个简单的日志记录器
logger = logging.getLogger(__name__)

SECRET_KEY = "your-super-secret-key"


# 1. 之前写的：获取租户 ID
async def get_current_company_id(x_tenant_id: UUID = Header(alias="X-Tenant-Id")) -> UUID:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing Tenant ID")
    return x_tenant_id

# 2. 新增：获取数据库 Session 的依赖函数
async def get_db() -> AsyncGenerator:
    # 使用 async with 自动管理 session 生命周期
    async with SessionLocal() as db:
        try:
            yield db  # 交给 API 路由使用
        finally:
            # 必须 await，确保连接真正归还给连接池
            await db.close()



# 用于定义用户对象的结构（或者你可以直接返回 ORM 对象）
class CurrentUser:
    def __init__(self, user: User, is_superuser: bool, is_company_admin: bool, db: Generator = Depends(get_db)):
        self.id = user.id
        self.company_id = user.last_company_id 
        self.email = user.email
        self.is_superuser = is_superuser
        self.is_company_admin = is_company_admin
        # self.role_code = user.role.code
        # self.exp = user.exp

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme),
    db: Generator = Depends(get_db)):
    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        user_id = payload.get("user_id")
        is_superuser = False
        if payload.get("role_code") == "SUPER_ADMIN":
            is_superuser = True
        is_company_admin = False
        if payload.get("role_code") == "COMPANY_ADMIN":
            is_company_admin = True
        # 2. 查询用户并验证是否存在 
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或 Token 已失效"
            )
        
        return CurrentUser(user, is_superuser, is_company_admin)
    except Exception as e:
        # 捕获其他所有异常（如数据库查询错误等）
        logger.error(f"认证过程发生未知错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="系统内部认证错误"
        )