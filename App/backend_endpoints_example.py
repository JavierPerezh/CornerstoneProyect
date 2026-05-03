# backend_endpoints_example.py
# ─────────────────────────────────────────────────────────────────────────────
# Estos son los endpoints que tu backend Python necesita exponer
# para que la app móvil funcione. Adáptalos a tu código existente.
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import shutil, os

app = FastAPI()
security = HTTPBearer()

# ── MODELOS ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str  # JWT

class AIVoiceResponse(BaseModel):
    audio_url: str      # URL pública del audio de respuesta (TTS)
    transcript: str     # Transcripción de lo que dijo el usuario
    response_text: str  # Texto de respuesta de la IA

# ── HELPERS ───────────────────────────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verifica JWT. Reemplaza con tu lógica real."""
    token = credentials.credentials
    # TODO: validar con tu librería JWT (python-jose, PyJWT, etc.)
    # Si inválido: raise HTTPException(status_code=401)
    return token  # Devuelve user_id o email del token

# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    """
    Autentica al usuario y devuelve un JWT.
    Conecta esto con tu sistema de usuarios existente.
    """
    # TODO: validar email/password contra tu BD
    # user = db.get_user_by_email(body.email)
    # if not user or not verify_password(body.password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Generar JWT
    # token = create_jwt(user.id)
    token = "tu_jwt_aqui"  # Reemplazar
    return LoginResponse(token=token)


@app.post("/ai/voice", response_model=AIVoiceResponse)
async def process_voice(
    audio: UploadFile = File(...),
    user_id: str = Depends(verify_token),
):
    """
    Recibe un archivo de audio, lo procesa con la IA y devuelve:
    - transcript: lo que dijo el usuario (STT)
    - response_text: respuesta de la IA
    - audio_url: URL del audio TTS generado
    """
    # 1. Guardar audio temporalmente
    temp_path = f"/tmp/{audio.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    try:
        # 2. Speech-to-Text (STT)
        # transcript = tu_stt_service(temp_path)
        transcript = "Texto de ejemplo"  # Reemplazar

        # 3. Procesar con tu IA existente
        # response_text = tu_ia.chat(transcript, user_id=user_id)
        response_text = "Respuesta de ejemplo de la IA"  # Reemplazar

        # 4. Text-to-Speech (TTS) → generar audio de respuesta
        # audio_path = tu_tts_service(response_text)
        # audio_url = subir_a_storage(audio_path)  # S3, GCS, etc.
        audio_url = "https://tu-backend.com/static/respuesta.mp3"  # Reemplazar

        return AIVoiceResponse(
            audio_url=audio_url,
            transcript=transcript,
            response_text=response_text,
        )
    finally:
        os.remove(temp_path)

# ── CORS (necesario para desarrollo) ──────────────────────────────────────────
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: restringe a tu dominio
    allow_methods=["*"],
    allow_headers=["*"],
)
