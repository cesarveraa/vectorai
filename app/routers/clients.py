
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from ..models.schemas import ClientCreate, ClientOut, ClientUpdate, FaceVectorIn
from ..core.security import api_key_guard
from ..core.config import settings
from ..services import firebase_client as fb
from ..services.face_embedder import FaceEmbedder
from typing import List

router = APIRouter(prefix="/clients", tags=["clients"])


_embedder = FaceEmbedder()


@router.post("/", dependencies=[Depends(api_key_guard)], response_model=ClientOut)
async def create_client(payload: ClientCreate):
    fb.create_client(payload.model_dump())
    data = fb.read_client(payload.id)
    return data # type: ignore


@router.get("/", dependencies=[Depends(api_key_guard)], response_model=List[ClientOut])
async def list_clients(limit: int = 100):
    return fb.list_clients(limit=limit)  # type: ignore


@router.get("/{client_id}", dependencies=[Depends(api_key_guard)], response_model=ClientOut)
async def get_client(client_id: str):
    data = fb.read_client(client_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return data # type: ignore


@router.patch("/{client_id}", dependencies=[Depends(api_key_guard)])
async def update_client(client_id: str, payload: ClientUpdate):
    fb.update_client(client_id, {k: v for k, v in payload.model_dump(exclude_none=True).items()})
    return {"ok": True}


@router.delete("/{client_id}", dependencies=[Depends(api_key_guard)])
async def remove_client(client_id: str):
    fb.delete_client(client_id)
    return {"ok": True}


@router.post("/{client_id}/face-vectors", dependencies=[Depends(api_key_guard)])
async def set_vector(client_id: str, vec: FaceVectorIn):
    v = _embedder.normalize_vector(vec.vector)
    fb.set_client_vector(client_id, v, settings.EMBEDDING_DIM)
    return {"ok": True, "embedding_dim": settings.EMBEDDING_DIM}


@router.post("/{client_id}/face-image", dependencies=[Depends(api_key_guard)])
async def set_vector_from_image(client_id: str, file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Only image uploads are supported")
    content = await file.read()
    emb = _embedder.embed_image(content)
    if emb is None:
        raise HTTPException(status_code=422, detail="No face detected in image")
    v = _embedder.normalize_vector(emb)
    fb.set_client_vector(client_id, v, len(v))
    return {"ok": True, "embedding_dim": len(v)}