from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import boto3

from core.dependencies import get_current_company_id, get_db, get_current_user
from modules.expense.services import ExpenseService
from modules.expense.schemas import ExpenseCreate, ExpenseOut, ApprovalActionCreate
from botocore.config import Config
from core.config import settings

router = APIRouter(prefix="/api/v1/expenses", tags=["Expenses"])

@router.get("/upload-url")
async def get_s3_presigned_url(filename: str, current_user = Depends(get_current_user)):
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,  #  (東京 ap-northeast-1)
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'} # 确保使用 virtual-hosted 风格的 URL
        )
    )
    
    s3_key = f"{current_user.company_id}/{current_user.id}/{filename}"
    
    url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.S3_INVOICE_BUCKET,
            'Key': s3_key
        },
        ExpiresIn=3600
    )
    return {"upload_url": url, "s3_key": s3_key}


# 2. 创建报销单
@router.post("/", response_model=ExpenseOut)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await ExpenseService.create_expense(db, current_user.company_id, current_user.id, data, current_user.is_superuser)

# 3. 获取列表
@router.get("/", response_model=List[ExpenseOut])
async def list_expenses(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await ExpenseService.get_expense_list(db, current_user.company_id, skip=skip, limit=limit, is_superuser=current_user.is_superuser, is_company_admin=current_user.is_company_admin, user_id=current_user.id)

# 4. 逻辑删除
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await ExpenseService.soft_delete_expense(db, expense_id, current_user.company_id)
    return None

@router.post("/{expense_id}/approve")
async def approve_expense(
    expense_id: UUID,
    action_data: ApprovalActionCreate, # Pydantic 模型
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await ExpenseService.transition_status(
        db=db,
        expense_id=expense_id,
        company_id=current_user.company_id, # 自动带上租户 ID，防止越权
        operator_id=current_user.id,
        action=action_data.action,
        comment=action_data.comment
    )