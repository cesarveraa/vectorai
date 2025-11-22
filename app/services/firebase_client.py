 
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Any, Dict, List, Optional
from ..core.config import settings
from ..core.timeutil import now_iso
import json
from datetime import datetime, date, time, timezone


_db = None


# Optional encryption for vectors
try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception: # pragma: no cover
    Fernet = None # type: ignore
    InvalidToken = Exception # type: ignore


_cipher = None
if settings.ENCRYPT_VECTORS and settings.ENCRYPTION_KEY and Fernet is not None:
    try:
        _cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    except Exception:
        _cipher = None




def _init_app():
    global _db
    if _db is None:
        sa = settings.firebase_sa
        cred = credentials.Certificate(sa.model_dump())
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db




def db():
    return _init_app()




def _enc_vector(vec: List[float]) -> Any:
    if _cipher is None:
        return vec
    blob = json.dumps(vec).encode()
    token = _cipher.encrypt(blob)
    return {"enc": True, "v": token.decode()}




def _dec_vector(raw: Any) -> Optional[List[float]]:
    if isinstance(raw, list):
        return [float(x) for x in raw]
    if isinstance(raw, dict) and raw.get("enc") and _cipher is not None:
        try:
            data = _cipher.decrypt(raw["v"].encode())
            return json.loads(data.decode())
        except Exception:
            return None
    return None


COLL = "clientes"



def get_client_doc(client_id: str):
    return db().collection(COLL).document(client_id)




def create_client(client: Dict[str, Any]):
    ref = get_client_doc(client["id"])
    data = {
        "id": client["id"],
        "name": client.get("name"),
        "meta": client.get("meta", {}),
        "embedding_dim": client.get("embedding_dim"),
        "detecciones_count": 0,
        "detecciones_recent": [],
    }
    ref.set(data, merge=True)
    return data




def read_client(client_id: str) -> Optional[Dict[str, Any]]:
    snap = get_client_doc(client_id).get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    vec = data.get("vector")
    if vec is not None:
        data["vector"] = _dec_vector(vec)
    return data




def update_client(client_id: str, fields: Dict[str, Any]):
    ref = get_client_doc(client_id)
    ref.set(fields, merge=True)




def delete_client(client_id: str):
    get_client_doc(client_id).delete()




def list_clients(limit: int = 100) -> List[Dict[str, Any]]:
    res = []
    for doc in db().collection(COLL).limit(limit).stream():
        item = doc.to_dict()
        vec = item.get("vector")
        if vec is not None:
            item["vector"] = _dec_vector(vec)
        res.append(item)
    return res




def set_client_vector(client_id: str, vector: List[float], embedding_dim: int):
    ref = get_client_doc(client_id)
    ref.set({
        "vector": _enc_vector(vector),
        "embedding_dim": embedding_dim,
    }, merge=True)




def log_detection(client_id: str, score: float, source: Optional[Dict[str, Any]] = None):
    ts = now_iso()
    ref = get_client_doc(client_id)
    ref.collection("detecciones").document().set({
        "ts": ts,
        "score": float(score),
        "source": source or {},
    })
    snap = ref.get()
    base = []
    if snap.exists:
        base = snap.get("detecciones_recent") or []
    base.append(ts)
    if len(base) > 50:
        base = base[-50:]
    ref.set({
        "detecciones_recent": base,
        "detecciones_count": firestore.Increment(1),
    }, merge=True)
    return ts

def list_detections_for_date(target_date: date) -> List[Dict[str, Any]]:
    """
    Devuelve todas las detecciones cuyo timestamp (ts) cae en el día target_date.
    Lee todas las detecciones del collection_group 'detecciones' y filtra en Python.
    Estructura esperada de cada detección:
      - ts: string ISO (generado por now_iso())
      - score: float
      - source: dict
    Además, agrega:
      - client_id: id del cliente dueño de la detección
      - timestamp: datetime parseado desde ts
    """
    # Rango de fecha [start_dt, end_dt]
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)


    # Leemos TODO el collection_group 'detecciones' (sin filtros)
    q = db().collection_group("detecciones")

    results: List[Dict[str, Any]] = []

    for doc in q.stream():
        data = doc.to_dict()
        ts_raw = data.get("ts")

        # Parsear ts
        if isinstance(ts_raw, str):
            try:
                ts_parsed = datetime.fromisoformat(ts_raw)
            except Exception:
                continue
        else:
            continue

        # Normalizar a naive UTC (quitar tzinfo pero manteniendo la hora correcta)
        if ts_parsed.tzinfo is not None:
            ts_parsed = ts_parsed.astimezone(timezone.utc).replace(tzinfo=None)

        # Filtrar por rango de fecha en Python (todos naive)
        if not (start_dt <= ts_parsed <= end_dt):
            continue

        # Obtener client_id a partir del padre:
        parent_client_ref = doc.reference.parent.parent
        client_id = parent_client_ref.id if parent_client_ref else None

        data["client_id"] = client_id
        data["timestamp"] = ts_parsed
        results.append(data)


    return results