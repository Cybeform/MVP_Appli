# backend/auth.py
import json, os
from datetime import datetime, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, Header

# Clé secrète pour signer vos tokens (générez-en une longue et placez-la en SECRET_KEY)
SECRET_KEY = os.environ.get("SECRET_KEY", "change_me_very_secret")

# Chargez vos codes d’accès
with open(os.path.join(os.path.dirname(__file__), "codes.json")) as f:
    CODES = json.load(f)

def validate_code(code: str):
    expires = CODES.get(code)
    if not expires:
        raise HTTPException(401, "Code invalide")

    # on crée deux datetimes aware en UTC pour comparaison fiable
    expires_dt = datetime.fromisoformat(expires)
    # si expires_dt est naïf, on considère que c'est du UTC
    if expires_dt.tzinfo is None:
        expires_dt = expires_dt.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    if now_utc > expires_dt:
        raise HTTPException(401, "Code expiré")

    # Génère un token valable jusqu’à expires
    token = jwt.encode({"sub": code, "exp": expires}, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(authorization: str = Header(...)):
    """
    Vérifie le header Authorization: Bearer <token>
    """
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except (ValueError, JWTError):
        raise HTTPException(401, "Token invalide ou expiré")
    return payload["sub"]
