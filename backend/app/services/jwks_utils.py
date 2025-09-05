# app/auth/jwks.py

import time
import threading
import requests
from fastapi import HTTPException
from services import config  # Adjust to your config import

_jwks_cache = {
    "keys": None,
    "last_updated": 0
}
_jwks_lock = threading.Lock()
JWKS_TTL = 3600  # Cache for 1 hour

def get_cached_jwks():
    with _jwks_lock:
        now = time.time()
        if _jwks_cache["keys"] and now - _jwks_cache["last_updated"] < JWKS_TTL:
            return _jwks_cache["keys"]
        
        try:
            response = requests.get(config.JWT_KEYS_URL, headers={"accept": "*/*"})
            jwks = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"JWKS fetch error: {e}")

        if "keys" not in jwks:
            raise HTTPException(status_code=500, detail="JWKS response missing 'keys'")
        
        _jwks_cache["keys"] = jwks
        _jwks_cache["last_updated"] = now

        return jwks
