import uuid
from datetime import datetime
from sqlalchemy import DateTime # 确保顶部导入了 DateTime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Table, Column, TIMESTAMP, func, Boolean, UniqueConstraint, Numeric, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime

# --- 辅助混入类 ---
class BaseMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

# 权限关联表 (Many-to-Many)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

# 1. companies (租户/企业表)
class Company(Base, BaseMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(14), nullable=True)

    tenant_user_roles: Mapped[List["TenantUserRole"]] = relationship(back_populates="company")

# 2. users (用户表)
class User(Base, BaseMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_initial_password: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    
    # SaaS 优化：记录用户最后一次操作的公司，方便上下文切换
    last_company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    
    tenant_user_roles: Mapped[List["TenantUserRole"]] = relationship(back_populates="user")

# 3. permissions (权限定义表)
class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )

# 4. roles (角色定义表)
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False) 
    name: Mapped[str] = mapped_column(String, nullable=False)

    permissions: Mapped[List[Permission]] = relationship(
        secondary=role_permissions, back_populates="roles"
    )
    tenant_user_roles: Mapped[List["TenantUserRole"]] = relationship(back_populates="role")

# 5. tenant_user_roles (核心纽带表：实现 SaaS 多租户角色控制)
class TenantUserRole(Base, BaseMixin):
    __tablename__ = "tenant_user_roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)

    # 保证同一个用户在同一个公司只能有一个角色 (超级管理员 company_id 为 null，记录全局唯一)
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_user"),
    )

    company: Mapped[Optional["Company"]] = relationship(back_populates="tenant_user_roles")
    user: Mapped["User"] = relationship(back_populates="tenant_user_roles")
    role: Mapped["Role"] = relationship(back_populates="tenant_user_roles")


##########
#📸 モジュール3：経費管理 ＆ 承認フロー（電帳法・交通費特例対応）
##########
class Expense(Base, BaseMixin):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 租户和用户关联 (参考了你提供的 ForeignKey 写法)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    
    # 核心业务字段
    trans_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vendor_name: Mapped[str] = mapped_column(String, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_8_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    tax_10_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    
    category: Mapped[str] = mapped_column(String, nullable=False) # 'general', 'transportation'
    account_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # 发票/电帐法相关
    t_number: Mapped[Optional[str]] = mapped_column(String(14), nullable=True)
    invoice_type: Mapped[str] = mapped_column(String, nullable=False) # 'qualified', 'non_qualified'
    deduction_rate: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    
    # 状态与备注
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    purpose: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # # 审计时间戳 (如果你的 BaseMixin 里已经包含这三个字段，这里可以删掉)
    # created_at: Mapped[datetime] = mapped_column(datetime, default=datetime.utcnow)
    # updated_at: Mapped[datetime] = mapped_column(datetime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # deleted_at: Mapped[Optional[datetime]] = mapped_column(datetime, nullable=True)

    # 💡 复合索引 (电帐法要求)
    __table_args__ = (
        Index("idx_expenses_search", "company_id", "trans_date", "vendor_name", "total_amount"),
    )

    # 上级关联 (Many-to-One)
    company: Mapped["Company"] = relationship()
    user: Mapped["User"] = relationship()

    # 下级关联 (One-to-Many)
    receipts: Mapped[List["ExpenseReceipt"]] = relationship(back_populates="expense", cascade="all, delete-orphan")
    transport_details: Mapped[List["ExpenseTransportDetail"]] = relationship(back_populates="expense", cascade="all, delete-orphan", order_by="ExpenseTransportDetail.seq_num")
    approvals: Mapped[List["ExpenseApproval"]] = relationship(back_populates="expense", cascade="all, delete-orphan", order_by="desc(ExpenseApproval.created_at)")


class ExpenseReceipt(Base, BaseMixin):
    __tablename__ = "expense_receipts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # 文件元数据
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # S3 路径
    raw_s3_key: Mapped[str] = mapped_column(String, nullable=False)
    proc_s3_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # 预留 AI 字段
    ocr_raw_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # # 审计 (同上，如果 BaseMixin 有则可省略)
    # created_at: Mapped[datetime] = mapped_column(datetime, default=datetime.utcnow)
    # deleted_at: Mapped[Optional[datetime]] = mapped_column(datetime, nullable=True)

    # 关联 (Many-to-One)
    expense: Mapped["Expense"] = relationship(back_populates="receipts")


class ExpenseTransportDetail(Base, BaseMixin):
    __tablename__ = "expense_transport_details"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), index=True, nullable=False)
    
    seq_num: Mapped[int] = mapped_column(Integer, nullable=False)
    origin: Mapped[str] = mapped_column(String, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_round_trip: Mapped[bool] = mapped_column(Boolean, default=False)
    input_method: Mapped[str] = mapped_column(String, nullable=False) # 'manual', 'route_search', 'ic_card'

    # 关联 (Many-to-One)
    expense: Mapped["Expense"] = relationship(back_populates="transport_details")


class ExpenseApproval(Base, BaseMixin):
    __tablename__ = "expense_approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # 审批人 ID (关联用户表)
    operator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    
    action: Mapped[str] = mapped_column(String, nullable=False) # 'submit', 'approve', 'reject', 'cancel'
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # # 审计 (同上，如果 BaseMixin 有则可省略)
    # created_at: Mapped[datetime] = mapped_column(datetime, default=datetime.utcnow)

    # 关联 (Many-to-One)
    expense: Mapped["Expense"] = relationship(back_populates="approvals")
    operator: Mapped["User"] = relationship()