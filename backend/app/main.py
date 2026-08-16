from dotenv import load_dotenv

# 加载.env文件（必须在其他导入之前）
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.config import get_settings
# from app.api.v1 import events, game, laws, plans, auth, legal_analysis, plan_generation, cases

# New Sprint imports
from app.api import agents as agents_api_new
from app.api import plans_new
from app.api import simulation  # S5推演引擎
from app.api import events_new
from app.api import laws_new
from app.services.llm_client import init_llm_client, close_llm_client

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)

settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="国家层面争议事件智能化法律博弈分析平台 (48h Sprint)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sprint: 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
from app.database import init_db

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    init_db()
    logger.info("✓ Database initialized")

    await init_llm_client()
    logger.info("✓ 48h Sprint Mode: LLM ready (DeepSeek API)")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    await close_llm_client()
    logger.info("✓ LLM Client closed")

# 注册路由 (Sprint版本 - Only New APIs)
# Note: All routers already have their own prefix defined
app.include_router(events_new.router)  # has /api/v1/events
app.include_router(agents_api_new.router)  # has /api/v1/agents
app.include_router(plans_new.router)  # has /api/v1/plans
app.include_router(simulation.router)  # has /simulation (will add /api/v1 below)
app.include_router(laws_new.router, prefix="/api/v1/laws", tags=["laws"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
# app.include_router(events.router, prefix="/api/v1/events", tags=["事件管理"])
# app.include_router(game.router, prefix="/api/v1/game", tags=["博弈推演"])
# app.include_router(laws.router, prefix="/api/v1/laws", tags=["法律库"])
# app.include_router(cases.router, prefix="/api/v1/cases", tags=["方案库"])
# app.include_router(plans.router, prefix="/api/v1/plans", tags=["方案管理"])
# app.include_router(legal_analysis.router, prefix="/api/v1/legal-analysis", tags=["法律分析"])
# app.include_router(plan_generation.router, prefix="/api/v1/plan-generation", tags=["方案生成"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "mode": "48h-sprint",
        "llm": "DeepSeek API"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
