 
from fastapi import APIRouter, Depends, Request
from ..core.security import api_key_guard
from ..core.config import settings
from ..models.schemas import DetectByVectorIn, DetectResult
from ..services import firebase_client as fb
from ..services.face_embedder import FaceEmbedder
from ..services.matcher import best_match


router = APIRouter(prefix="/detect/vector", tags=["detect-vector"])
_embedder = FaceEmbedder()


async def _all_candidates(limit: int = 1000):
    return fb.list_clients(limit=limit)


@router.post("/", dependencies=[Depends(api_key_guard)], response_model=DetectResult)
async def detect_by_vector(req: Request, payload: DetectByVectorIn):
    q = _embedder.normalize_vector(payload.vector)
    cands = await _all_candidates()
    match = best_match(q, cands)
    thr = payload.threshold or settings.MATCH_THRESHOLD
    if match is None:
        return DetectResult(matched=False, message="No clients registered yet")
    client_id, score = match
    if score >= thr:
        fb.log_detection(client_id, score, source={"path": str(req.url.path), "ip": req.client.host if req.client else None, "mode": "vector"})
        return DetectResult(matched=True, client_id=client_id, score=score, message="Face recognized")
    else:
        return DetectResult(matched=False, message="Face not found (below threshold)")