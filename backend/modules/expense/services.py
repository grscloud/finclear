from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from common.models import Expense, ExpenseTransportDetail, ExpenseReceipt, ExpenseApproval
from modules.expense.schemas import ExpenseCreate  # 假设你的 schemas 放在 schemas.py
from sqlalchemy.orm import selectinload # 记得导入

class ExpenseService:
    @staticmethod
    async def create_expense(db: AsyncSession, company_id: UUID, user_id: UUID, data: ExpenseCreate, is_superuser: bool) -> Expense:
        # 1. 创建主表对象
        expense = Expense(
            company_id=company_id,
            user_id=user_id,
            # **data.model_dump(exclude={"transport_details"}),
            **data.model_dump(exclude={"transport_details", "receipts"}), # 👈 排除 receipts
            status="draft"
        )
        
        # 2. 处理交通明细 (如果存在)
        if data.transport_details:
            for detail in data.transport_details:
                detail_obj = ExpenseTransportDetail(
                    **detail.model_dump(),
                    expense=expense
                )
                expense.transport_details.append(detail_obj)

        # 3. 处理附件保存 (新加以下内容) 👈
        if data.receipts:
            for r in data.receipts:
                receipt_obj = ExpenseReceipt(
                    original_filename=r.original_filename,
                    mime_type=r.mime_type,
                    file_size=r.file_size,
                    raw_s3_key=r.s3_key,  # 💡 注意：数据库字段名是 raw_s3_key，对应 schemas 的 s3_key
                    expense=expense
                )
                expense.receipts.append(receipt_obj)

        db.add(expense)
        await db.commit()
        # 重新查询一遍，并使用 selectinload 加载关联关系
        result = await db.execute(
            select(Expense)
            .options(
                selectinload(Expense.transport_details),
                selectinload(Expense.receipts),
                selectinload(Expense.approvals)
            )
            .where(Expense.id == expense.id)
        )
        return result.scalar_one()

    @staticmethod
    async def get_expense_list(
        db: AsyncSession, 
        company_id: UUID, 
        skip: int = 0, 
        limit: int = 10,
        is_superuser: bool = False,
        is_company_admin: bool = False,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Expense]:
        
        # 使用 .options(selectinload(...)) 进行预加载
        query = select(Expense).options(
            selectinload(Expense.transport_details),
            selectinload(Expense.receipts),
            selectinload(Expense.approvals)
        ).where(
            and_(Expense.is_deleted == False)
        )
        if not is_superuser:
            query = query.where(Expense.company_id == company_id)
        if not is_company_admin:
            query = query.where(Expense.user_id == user_id)
        if start_date: query = query.where(Expense.trans_date >= start_date)
        if end_date: query = query.where(Expense.trans_date <= end_date)
        
        # 使用 .order_by 让结果更稳定
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def soft_delete_expense(db: AsyncSession, expense_id: UUID, company_id: UUID):
        query = update(Expense).where(
            and_(Expense.id == expense_id, Expense.company_id == company_id)
        ).values(is_deleted=True, status="canceled")
        await db.execute(query)
        await db.commit()

    @staticmethod
    async def _log_approval(db: AsyncSession, expense_id: UUID, operator_id: UUID, action: str, comment: Optional[str] = None):
        """内部工具：记录审批日志"""
        log = ExpenseApproval(
            expense_id=expense_id,
            operator_id=operator_id,
            action=action,
            comment=comment
        )
        db.add(log)

    @staticmethod
    async def transition_status(
        db: AsyncSession, 
        expense_id: UUID, 
        company_id: UUID, 
        operator_id: UUID, 
        action: str, 
        comment: Optional[str] = None
    ):
        # 1. 获取报销单 (确保租户隔离)
        result = await db.execute(
            select(Expense).where(Expense.id == expense_id, Expense.company_id == company_id)
        )
        expense = result.scalar_one_or_none()
        
        if not expense:
            raise HTTPException(status_code=404, detail="报销单不存在")

        # 2. 状态流转逻辑 (简单的状态机)
        if action == "submit":
            if expense.status not in ["draft", "rejected"]:
                raise HTTPException(status_code=400, detail="只有草稿或驳回状态可以提交")
            expense.status = "pending"
            
        elif action == "approve":
            if expense.status != "pending":
                raise HTTPException(status_code=400, detail="只有待审批状态可以被通过")
            expense.status = "approved"
            
        elif action == "reject":
            if expense.status != "pending":
                raise HTTPException(status_code=400, detail="只能驳回待审批的报销单")
            expense.status = "rejected"
            
        elif action == "cancel":
            if expense.status != "pending":
                raise HTTPException(status_code=400, detail="无法撤销非待审批状态的报销单")
            expense.status = "draft"
            
        else:
            raise HTTPException(status_code=400, detail="无效的操作")

        # 3. 记录日志并提交
        # await ExpenseService._log_approval(db, expense.id, operator_id, action, comment)
        log = ExpenseApproval(
            expense_id=expense_id,
            operator_id=operator_id,
            action=action,
            comment=comment
        )
        db.add(log)
        await db.commit()
        return expense