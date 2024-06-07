from typing import List, Generic, TypeVar, Optional
from pydantic import BaseModel
from starlette.responses import JSONResponse


T = TypeVar("T")  # 定義型態變數 T，繼承 BaseModel


# 泛型的列表回應模型
class ListResponse(BaseModel, Generic[T]):
    list: List[T]
    page: int
    total: int
    limit: int

    class Config:
        arbitrary_types_allowed = True


# 泛型的回應模型
class MyResponse(BaseModel, Generic[T]):
    message: str = "success"
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True


# dashboard shema
class DashboardSchema(BaseModel):
    total_short_urls: int
    total_clicks: int
    total_unique_clicks: int
