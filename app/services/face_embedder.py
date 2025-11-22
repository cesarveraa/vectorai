# app/services/face_embedder.py
import io
from typing import List, Optional
from PIL import Image
import numpy as np
from ..core.config import settings

class FaceEmbedder:
    def __init__(self):
        self.backend = settings.EMBEDDER_BACKEND.lower().strip()
        if self.backend == "insightface":
            self._init_insightface()
        elif self.backend == "facerecognition":
            self._init_facerecognition()
        else:
            self.backend = "mock"

    def _init_insightface(self):
        import insightface
        import onnxruntime  # noqa: F401
        self.app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def _init_facerecognition(self):
        import face_recognition  # noqa: F401

    def embed_image(self, content: bytes) -> Optional[List[float]]:
        if self.backend == "insightface":
            img = Image.open(io.BytesIO(content)).convert("RGB")
            arr = np.array(img)[:, :, ::-1]  # RGB->BGR
            faces = self.app.get(arr)
            if not faces:
                return None
            face = max(
                faces,
                key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1])
            )
            emb = face.normed_embedding.astype(float).tolist()
            return emb

        elif self.backend == "facerecognition":
            import face_recognition
            img = face_recognition.load_image_file(io.BytesIO(content))
            locs = face_recognition.face_locations(img)
            if not locs:
                return None
            encs = face_recognition.face_encodings(img, known_face_locations=[locs[0]])
            if not encs:
                return None
            return encs[0].astype(float).tolist()

        else:
            # MOCK: convierte a gris 32x32 y usa los pixeles normalizados como embedding
            img = Image.open(io.BytesIO(content)).convert("L").resize((32, 32))
            arr = np.asarray(img).astype(np.float32)
            vec = arr.flatten()
            vec = vec / (np.linalg.norm(vec) + 1e-9)
            want = settings.EMBEDDING_DIM
            if vec.shape[0] < want:
                pad = np.zeros((want - vec.shape[0],), dtype=np.float32)
                vec = np.concatenate([vec, pad])
            return vec[:want].astype(float).tolist()

    def normalize_vector(self, v: List[float]) -> List[float]:
        a = np.asarray(v, dtype=np.float32)
        a = a / (np.linalg.norm(a) + 1e-9)
        return a.astype(float).tolist()
