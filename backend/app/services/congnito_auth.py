

from fastapi import HTTPException, HTTPException, Security
import jwt
import jwt.algorithms
# from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from services import config
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
        response = requests.get(config.JWT_KEYS_URL, headers={"accept": "*/*"})
        jwks = response.json()
        
        # Check JWKS structure
        if "keys" not in jwks:
            raise HTTPException(status_code=500, detail="Invalid JWKS format")
        
        public_keys = {key["kid"]: key for key in jwks["keys"]}

        if kid not in public_keys:
            raise HTTPException(status_code=401, detail="Invalid token: Key ID not found")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(public_keys[kid]))
        payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=config.COGNITO_APP_CLIENT_ID, issuer=config.COGNITO_ISSUER)
        
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email")
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"JWKS request error: {str(e)}")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
