

from fastapi import HTTPException, HTTPException, Security
import jwt
import jwt.algorithms
# from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from services import config, jwks_utils
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import json

security = HTTPBearer()
ALGORITHM = "HS256"

# verify token with Cognito. If correct, return the current user
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
        jwks = jwks_utils.get_cached_jwks()
        
        # Check JWKS structure
        if "keys" not in jwks:
            raise HTTPException(status_code=500, detail="Invalid JWKS format")
        
        public_keys = {key["kid"]: key for key in jwks["keys"]}

        if kid not in public_keys:
            raise HTTPException(status_code=401, detail="Invalid token: Key ID not found")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(public_keys[kid]))
        payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=config.COGNITO_APP_CLIENT_ID, issuer=config.COGNITO_ISSUER, leeway=300)
        
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email")
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid audience")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid issuer")
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Decode error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation error: {str(e)}")
    
