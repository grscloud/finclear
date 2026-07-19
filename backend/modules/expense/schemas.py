from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# ==========================================
# 1. Transport Detail Schemas (交通明细)
# ==========================================
class TransportDetailCreate(BaseModel):
    seq_num: int
    origin: str
    destination: str
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    is_round_trip: bool = False
    input_method: str = Field(..., description="manual, route_search, ic_card")

class TransportDetailOut(TransportDetailCreate):
    id: UUID
    expense_id: UUID

    class Config:
        from_attributes = True


# ==========================================
# 2. Receipt Schemas (凭证附件)
# ==========================================
class ReceiptCreate(BaseModel):
    original_filename: str
    mime_type: str
    file_size: int
    s3_key: str # 前端直传 S3 后拿到的 key

class ReceiptOut(BaseModel):
    id: UUID
    expense_id: UUID
    original_filename: str
    mime_type: str
    file_size: int
    raw_s3_key: str
    created_at: datetime
    # 注意：返回给前端时，通常会通过专门的接口或动态生成 presigned URL，这里不直接返回 S3 URL

    class Config:
        from_attributes = True


# ==========================================
# 3. Approval Log Schemas (审批日志)
# ==========================================
class ApprovalOut(BaseModel):
    id: UUID
    expense_id: UUID
    operator_id: UUID
    action: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# 审批动作提交用
class ApprovalActionCreate(BaseModel):
    action: str = Field(..., description="submit, approve, reject, cancel")
    comment: Optional[str] = None


# ==========================================
# 4. Expense Main Schemas (经费主表)
# ==========================================

# 基础共享属性
class ExpenseBase(BaseModel):
    trans_date: datetime
    vendor_name: str
    total_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    tax_8_amount: Decimal = Field(default=Decimal('0.00'), max_digits=10, decimal_places=2)
    tax_10_amount: Decimal = Field(default=Decimal('0.00'), max_digits=10, decimal_places=2)
    category: str = Field(..., description="general, transportation")
    account_item_id: Optional[UUID] = None
    t_number: Optional[str] = None
    invoice_type: str = Field(..., description="qualified, non_qualified")
    deduction_rate: Decimal = Field(..., max_digits=3, decimal_places=2)
    purpose: Optional[str] = None

# 创建/更新请求 (嵌套交通明细)
class ExpenseCreate(ExpenseBase):
    # 租户ID和用户ID由JWT Token解析，不从前端传入
    transport_details: Optional[List[TransportDetailCreate]] = []
    receipts: Optional[List[ReceiptCreate]] = []  # 👈 补上这一行

class ExpenseUpdate(ExpenseBase):
    transport_details: Optional[List[TransportDetailCreate]] = []
    # 状态更新通常走审批工作流流转接口，不在普通 update 里暴露

# 完整返回结果 (聚合根)
class ExpenseOut(ExpenseBase):
    id: UUID
    company_id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    # 嵌套关联的数据
    transport_details: List[TransportDetailOut] = []
    receipts: List[ReceiptOut] = []
    approvals: List[ApprovalOut] = []

    class Config:
        from_attributes = True # 允许从 SQLAlchemy ORM 模型自动转换