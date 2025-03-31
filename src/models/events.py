from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class NewsEventDetail(BaseModel):
    """Event detail structure for news processing events"""
    eventType: Literal["collect", "build"]
    providerId: str
    locale: str
    tags: List[str]
    dispatchDay: Optional[int] = None


class LambdaEvent(BaseModel):
    """AWS Lambda event structure"""
    source: str
    detail: NewsEventDetail
    time: Optional[str] = None
    id: Optional[str] = None
    region: Optional[str] = None
    resources: Optional[List[str]] = None
    detail_type: Optional[str] = Field(None, alias="detail-type")
    account: Optional[str] = None
    version: Optional[str] = None
