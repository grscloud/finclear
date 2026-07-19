from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings

# 1. 确保使用异步驱动 (asyncpg)
ASYNC_DB_URL = settings.database_url
# if raw_db_url.startswith("postgresql://"):
#     # 将标准的 postgresql:// 替换为异步的 postgresql+asyncpg://
#     ASYNC_DB_URL = raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
# else:
#     ASYNC_DB_URL = raw_db_url

# 2. 创建异步引擎 (针对 Serverless 环境深度优化)
engine = create_async_engine(
    ASYNC_DB_URL,
    # 本地开发时打印 SQL 语句，线上环境关闭以减少 CloudWatch 日志成本
    echo=(settings.ENV == "local"), 
    
    # Serverless 直连 RDS 护城河设置：
    pool_size=1,        # 限制每个 Lambda 实例只保持 1 个数据库连接
    max_overflow=0,     # 严禁创建超出 pool_size 的临时连接
    pool_pre_ping=True  # 悲观测试：每次执行 SQL 前检查连接是否因 Lambda 冻结而失效
)

# 3. 创建会话工厂
SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 4. ORM 模型的基类
Base = declarative_base()