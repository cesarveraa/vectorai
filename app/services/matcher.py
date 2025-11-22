
from typing import Dict, List, Optional, Tuple
import numpy as np




def cosine_similarity(a: List[float], b: List[float]) -> float:
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) + 1e-9
    return float(np.dot(va, vb) / denom)




def best_match(query: List[float], candidates: List[Dict]) -> Optional[Tuple[str, float]]:
    best_id = None
    best_score = -1.0
    for c in candidates:
        vec = c.get("vector")
        cid = c.get("id")
        if not vec or not cid:
            continue
        s = cosine_similarity(query, vec)
        if s > best_score:
            best_score = s
            best_id = cid
    if best_id is None:
        return None
    return best_id, best_score