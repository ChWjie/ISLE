"""
统一响应模型
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


DataT = TypeVar('DataT')


class BaseResponse(BaseModel, Generic[DataT]):
    """标准响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[DataT] = None


class ErrorResponse(BaseModel):
    """错误响应格式"""
    code: int
    message: str
    detail: Optional[str] = None
