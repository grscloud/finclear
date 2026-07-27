from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status
# 1. 引入 AsyncSession 和 SQLAlchemy 2.0 的核心操作函数
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from passlib.context import CryptContext

from common.models import Company, TenantUserRole, User, Role
from modules.iam.schemas import InviteUserReq, UpdateUserReq
from . import schemas

# 初始化加密算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_tenant_users(
    db: AsyncSession, 
    company_id: Optional[UUID],  
    page: int, 
    limit: int,
    status: Optional[str] = None, 
    role_id: Optional[int] = None, 
    keyword: Optional[str] = None
) -> dict:
    """获取租户用户列表（已包含逻辑删除过滤，支持跨租户查询）"""
    
    # 1. 使用 select 构建查询语句 (SQLAlchemy 2.0 语法)
    stmt = select(TenantUserRole, User, Role, Company)\
        .join(User, TenantUserRole.user_id == User.id)\
        .join(Role, TenantUserRole.role_id == Role.id)\
        .outerjoin(Company, TenantUserRole.company_id == Company.id)\
        .where(User.is_deleted == False, TenantUserRole.is_deleted == False)
        
    if company_id:
        stmt = stmt.where(TenantUserRole.company_id == company_id)
        
    if status:
        stmt = stmt.where(User.status == status)
    if role_id:
        stmt = stmt.where(TenantUserRole.role_id == role_id)
    if keyword:
        # 使用 or_ 进行多条件模糊匹配
        stmt = stmt.where(
            or_(User.email.ilike(f"%{keyword}%"), User.username.ilike(f"%{keyword}%"))
        )
    
    # 2. 异步统计总数 (Async 不再支持 .count()，需要使用 func.count)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    # 3. 增加分页并执行查询
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    records = result.all()  # 获取所有行记录
    
    items = []
    # 4. 循环解包 Row
    for rel, user, role, company in records:
        items.append({
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "status": user.status,
            "role": {
                "role_id": role.id, 
                "code": role.code, 
                "name": role.name
            },
            "company": {
                "company_id": company.id if company else None,
                "name": company.name if company else None
            }
        })
    
    return {"total": total, "page": page, "limit": limit, "items": items}


async def invite_tenant_user(db: AsyncSession, req: InviteUserReq) -> dict:
    """邀请/创建用户：同步写入 users 表与 tenant_user_roles 表"""
    
    company_id = req.company_id
    
    if req.role_id == 1:
        raise HTTPException(status_code=403, detail="Cannot assign Super Admin role in a tenant.")

    # 1. 检查用户是否已在该租户内激活
    if company_id:
        exist_stmt = select(TenantUserRole).join(User, TenantUserRole.user_id == User.id).where(
            TenantUserRole.company_id == company_id,
            User.email == req.email,
            TenantUserRole.is_deleted == False
        )
        exist_relation = (await db.execute(exist_stmt)).scalar_one_or_none()
        
        if exist_relation:
            raise HTTPException(status_code=400, detail="User already active in this tenant")

    try:
        # 2. 查找系统中是否已存在该邮箱的用户
        user_stmt = select(User).where(User.email == req.email)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        
        if not user:
            provided_username = req.username or req.email.split('@')[0]
            user = User(
                username=provided_username,
                full_name=req.full_name or '', 
                email=req.email,
                password_hash=get_password_hash(req.password),
                is_initial_password=True,
                status="active",
                last_company_id=company_id,
                is_deleted=False
            )
            db.add(user)
            await db.flush()  # 异步 flush 获取新生成的 user.id
        else:
            user.is_deleted = False
            user.status = "active"
            if req.username:
                user.username = req.username
            if req.full_name:
                user.full_name = req.full_name
            await db.flush()

        # 3. 处理角色关联
        rel_stmt = select(TenantUserRole).where(
            TenantUserRole.company_id == company_id,
            TenantUserRole.user_id == user.id
        )
        relation = (await db.execute(rel_stmt)).scalar_one_or_none()

        if relation:
            relation.is_deleted = False
            relation.role_id = req.role_id
        else:
            new_relation = TenantUserRole(
                company_id=company_id, 
                user_id=user.id, 
                role_id=req.role_id,
                is_deleted=False
            )
            db.add(new_relation)
        
        await db.commit()  # 异步 commit
    except Exception as e:
        await db.rollback()  # 异步 rollback
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"user_id": user.id, "email": user.email}


async def reset_password(db: AsyncSession, user_id: UUID, new_password_hash: str, requester_id: UUID):
    """重置密码功能"""
    user_stmt = select(User).where(User.id == user_id, User.is_deleted == False)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # [待补充] 权限校验逻辑
    
    user.password_hash = new_password_hash
    user.is_initial_password = False 
    await db.commit()
    return {"message": "Password reset successful"}


async def remove_tenant_user(db: AsyncSession, user_id: UUID):
    """同步删除用户：同时将用户本体与所有相关的租户角色映射逻辑删除"""
    
    # 1. 查找该用户所有处于激活状态的租户角色关联记录
    rel_stmt = select(TenantUserRole).where(
        TenantUserRole.user_id == user_id,
        TenantUserRole.is_deleted == False
    )
    relations = (await db.execute(rel_stmt)).scalars().all()
    
    if not relations:
        raise HTTPException(status_code=404, detail="Active user relations not found")

    # 2. 检查管理员数量限制
    for relation in relations:
        if relation.role_id == 2 and relation.company_id: 
            count_stmt = select(func.count()).select_from(TenantUserRole).where(
                TenantUserRole.company_id == relation.company_id, 
                TenantUserRole.role_id == 2,
                TenantUserRole.is_deleted == False
            )
            admin_count = await db.scalar(count_stmt)
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot remove user. They are the last administrator of their company."
                )

    try:
        # 3. 同步软删除
        for relation in relations:
            relation.is_deleted = True
        
        # 4. 同步软删除：将 User 本体也标记为已删除
        user_stmt = select(User).where(User.id == user_id)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        if user:
            user.is_deleted = True

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"message": "User and associated roles removed successfully"}


async def update_tenant_user(db: AsyncSession, user_id: UUID, req: UpdateUserReq) -> dict:
    """修改用户信息及租户角色关联"""
    
    # 1. 查找目标用户是否存在
    user_stmt = select(User).where(User.id == user_id, User.is_deleted == False)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. 检查邮箱唯一性
    if req.email and req.email != user.email:
        email_stmt = select(User).where(
            User.email == req.email, 
            User.id != user_id,
            User.is_deleted == False
        )
        if (await db.execute(email_stmt)).scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use by another user")
        user.email = req.email

    # 3. 检查用户名唯一性
    if req.username and req.username != user.username:
        username_stmt = select(User).where(
            User.username == req.username, 
            User.id != user_id,
            User.is_deleted == False
        )
        if (await db.execute(username_stmt)).scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already in use by another user")
        user.username = req.username

    if req.full_name is not None:
        user.full_name = req.full_name
    if req.status is not None:
        user.status = req.status

    # 5. 更新租户角色关联
    if req.role_id is not None:
        if req.role_id == 1:
            raise HTTPException(status_code=403, detail="Cannot assign Super Admin role.")

        rel_stmt = select(TenantUserRole).where(
            TenantUserRole.user_id == user_id,
            TenantUserRole.company_id == req.company_id,
            TenantUserRole.is_deleted == False
        )
        relation = (await db.execute(rel_stmt)).scalar_one_or_none()

        if relation:
            if relation.role_id == 2 and req.role_id != 2 and req.company_id:
                count_stmt = select(func.count()).select_from(TenantUserRole).where(
                    TenantUserRole.company_id == req.company_id,
                    TenantUserRole.role_id == 2,
                    TenantUserRole.is_deleted == False
                )
                admin_count = await db.scalar(count_stmt)
                
                if admin_count <= 1:
                    raise HTTPException(
                        status_code=400, 
                        detail="Cannot change role. This user is the last administrator of the company."
                    )
            
            relation.role_id = req.role_id
        else:
            new_relation = TenantUserRole(
                company_id=req.company_id,
                user_id=user_id,
                role_id=req.role_id,
                is_deleted=False
            )
            db.add(new_relation)

    try:
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "status": user.status
    }


############### Company ##################

async def get_all_companies(db: AsyncSession, page: int, limit: int, is_superuser: False, company_id: str, keyword: Optional[str] = None) -> dict:
    """全局获取公司列表（超管专用，已过滤逻辑删除）"""
    stmt = select(Company).where(Company.is_deleted == False)
    
    if keyword:
        stmt = stmt.where(Company.name.ilike(f"%{keyword}%"))
    
    if not is_superuser:
        stmt = stmt.where(Company.id == company_id)
    print(stmt)
    # 异步 count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    # 异步获取分页数据
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    records = (await db.execute(stmt)).scalars().all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": records
    }


async def get_company_by_id(db: AsyncSession, company_id: UUID) -> Company:
    """根据ID获取指定公司"""
    stmt = select(Company).where(Company.id == company_id, Company.is_deleted == False)
    company = (await db.execute(stmt)).scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


async def create_company(db: AsyncSession, company_in: schemas.CompanyCreate) -> Company:
    """创建新公司（开通新租户）"""
    if company_in.invoice_number:
        stmt = select(Company).where(
            Company.invoice_number == company_in.invoice_number, 
            Company.is_deleted == False
        )
        if (await db.execute(stmt)).scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Invoice number already registered")

    db_company = Company(
        name=company_in.name,
        invoice_number=company_in.invoice_number
    )
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company


async def update_company_details(db: AsyncSession, company_id: UUID, company_in: schemas.CompanyUpdate) -> Company:
    """更新公司信息"""
    db_company = await get_company_by_id(db, company_id)
    
    update_data = company_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)
        
    await db.commit()
    await db.refresh(db_company)
    return db_company


async def soft_delete_company(db: AsyncSession, company_id: UUID):
    """逻辑删除公司"""
    db_company = await get_company_by_id(db, company_id)
    db_company.is_deleted = True
    await db.commit()
    return {"message": "Company deleted successfully"}