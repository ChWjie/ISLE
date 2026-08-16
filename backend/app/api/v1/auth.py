from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """用户登录"""
    # 模拟登录（实际应该验证用户名密码）
    return TokenResponse(
        access_token="mock-jwt-token-" + request.username,
        token_type="bearer"
    )


@router.post("/logout")
async def logout():
    """用户登出"""
    return {"message": "登出成功"}


@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    return {
        "id": "user-1",
        "username": "admin",
        "role": "admin",
        "name": "管理员"
    }
