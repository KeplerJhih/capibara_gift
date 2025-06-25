from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.endpoints import captcha, config
from loguru import logger
import os
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

app = FastAPI(
    title="禮品碼兌換系統",
    description="提供禮品碼兌換服務的 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加根路徑重定向
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

# 註冊路由
app.include_router(captcha.router, prefix="/api")
app.include_router(config.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("應用程式啟動")
    logger.info(f"CAPTCHA BASE URL: {os.getenv('CAPTCHA_BASE_URL')}")
    logger.info(f"CAPTCHA GENERATE URL: {os.getenv('CAPTCHA_GENERATE_URL')}")
    logger.info(f"CLAIM API URL: {os.getenv('CLAIM_API_URL')}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("應用程式關閉") 