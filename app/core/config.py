import os
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 👇 Carga .env en os.environ (necesario para leer FIREBASE_* con os.environ[...])
try:
    from dotenv import load_dotenv
    # intenta cargar el .env desde la raíz del proyecto (dos niveles arriba de este archivo)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ENV_PATH = os.path.join(BASE_DIR, ".env")
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
    else:
        # fallback: busca .env en el cwd
        load_dotenv()
except Exception:
    # si no está instalado (aunque está en requirements), seguimos sin romper
    pass


class FirebaseServiceAccount(BaseModel):
    type: str = Field(default="service_account")
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str = Field(default="https://accounts.google.com/o/oauth2/auth")
    token_uri: str = Field(default="https://oauth2.googleapis.com/token")
    auth_provider_x509_cert_url: str = Field(default="https://www.googleapis.com/oauth2/v1/certs")
    client_x509_cert_url: str
    universe_domain: str = Field(default="googleapis.com")

    @classmethod
    def from_env(cls) -> "FirebaseServiceAccount":
        # MUY IMPORTANTE: en .env el PRIVATE_KEY debe tener \n ESCAPADOS.
        # Aquí los convertimos a saltos reales.
        pk = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
        return cls(
            project_id=os.environ["FIREBASE_PROJECT_ID"],
            private_key_id=os.environ["FIREBASE_PRIVATE_KEY_ID"],
            private_key=pk,
            client_email=os.environ["FIREBASE_CLIENT_EMAIL"],
            client_id=os.environ["FIREBASE_CLIENT_ID"],
            auth_uri=os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            token_uri=os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            auth_provider_x509_cert_url=os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
            client_x509_cert_url=os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
            universe_domain=os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com"),
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",   # ignora variables extra del .env que no estén aquí
    )

    ENV: str = "dev"
    API_PREFIX: str = "/api/v1"
    INTERNAL_SECRET: str
    CORS_ALLOW_ORIGINS: str = "*"  # comma-separated

    EMBEDDER_BACKEND: str = "mock"  # insightface | facerecognition | mock
    EMBEDDING_DIM: int = 512
    MATCH_THRESHOLD: float = 0.6  # cosine similarity threshold

    MAX_UPLOAD_MB: int = 8

    ENCRYPT_VECTORS: bool = False
    ENCRYPTION_KEY: Optional[str] = None  # urlsafe base64 32-byte key

    @property
    def cors_origins_list(self) -> List[str]:
        raw = self.CORS_ALLOW_ORIGINS.strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def firebase_sa(self) -> FirebaseServiceAccount:
        return FirebaseServiceAccount.from_env()


settings = Settings()
