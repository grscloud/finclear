import os
import json
import boto3
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录路径
# 假设当前文件路径为: my-saas-backend/app/core/config.py
# .parent 三次会回退到 my-saas-backend 根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "local")
    
    # 业务相关的通用配置
    S3_INVOICE_BUCKET: str = os.getenv("S3_INVOICE_BUCKET", "grscloud-finclear-dev")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-1")
    
    # 动态获取数据库连接 URL
    @property
    def database_url(self) -> str:
        if self.ENV == "local":
            # 本地开发：直接读取 .env 中的 DATABASE_URL
            return os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/finclear")
            
        # 生产环境：从 AWS SSM Parameter Store 动态获取
        # 变量名建议改为 DB_SSM_PARAM_NAME，例如值配置为 "/prod/db/credentials"
        ssm_param_name = os.getenv("DB_SSM_PARAM_NAME") 
        # region_name = os.getenv("AWS_REGION")
        
        # 初始化 SSM 客户端
        client = boto3.client('ssm', region_name=AWS_REGION)
        
        # 核心差异：必须指定 WithDecryption=True 才能解密 SecureString
        response = client.get_parameter(
            Name=ssm_param_name, 
            WithDecryption=True
        )
        
        # SSM 的返回值结构与 Secrets Manager 不同，数据存在 ['Parameter']['Value'] 中
        secret = json.loads(response['Parameter']['Value'])
        
        # 去掉 Proxy，直接读取直连 RDS 的 Endpoint
        db_host = os.getenv("DB_HOST")
        
        return f"postgresql://{secret['username']}:{secret['password']}@{db_host}:{secret['port']}/{secret['dbname']}"

    # 强制让 Pydantic 去项目根目录寻找 .env 文件
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"), 
        env_file_encoding="utf-8",
        extra="ignore" # 忽略环境中多余的变量，防止 Pydantic 抛出验证错误
    )

settings = Settings()