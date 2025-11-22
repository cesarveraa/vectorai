
from pydantic import BaseModel, Field, conlist
from typing import Any, Dict, List, Optional


class ClientBase(BaseModel):
    id: str = Field(description="Unique client identifier")
    name: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ClientOut(ClientBase):
    embedding_dim: Optional[int] = None
    detecciones_count: int = 0
    detecciones_recent: List[str] = Field(default_factory=list)


class FaceVectorIn(BaseModel):
    vector: conlist(float, min_length=1)


class DetectByVectorIn(BaseModel):
    vector: conlist(float, min_length=1)
    threshold: Optional[float] = None


class DetectResult(BaseModel):
    matched: bool
    client_id: Optional[str] = None
    score: Optional[float] = None
    message: str