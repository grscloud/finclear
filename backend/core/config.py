import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录路径
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    ENV: str = "local"
    
    
    # 【核心修改】直接定义 DATABASE_URL 字段
    # Pydantic 会自动按顺序寻找：
    # 1. Lambda 系统环境变量中的 DATABASE_URL (Terraform 注入的)
    # 2. 本地项目根目录 .env 文件中的 DATABASE_URL
    # 3. 如果都没有，则使用默认的本地兜底值
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/finclear"
    # 业务相关的通用配置
    BUCKET_NAME: str = "grscloud-finclear-dev"
    AWS_REGION: str = "ap-northeast-1"

    # Pydantic 配置
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"), 
        env_file_encoding="utf-8",
        extra="ignore" # 忽略环境中多余的变量，防止验证错误
    )

# 实例化全局配置对象
settings = Settings()