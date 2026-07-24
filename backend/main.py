from fastapi import FastAPI
from mangum import Mangum
from modules.iam.router import router as iam_router
from modules.expense.router import router as expense_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SaaS 后端 API", version="1.0.0")

# 配置允许的来源
origins = [
    "http://localhost:5173",  # 你的前端地址
    "http://127.0.0.1:5173",  # 有时候浏览器会识别为 IP 地址，建议加上
]

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # 允许哪些来源访问
    allow_credentials=True,         # 是否允许发送 Cookie
    allow_methods=["*"],            # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE 等)
    allow_headers=["*"],            # 允许所有请求头
)

# 1. 注册 IAM(权限) 模块路由
app.include_router(iam_router)
app.include_router(expense_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

@app.get("/")
def root():
    return {
        "message": "FinClear API"
    }

handler = Mangum(app)