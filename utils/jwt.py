from fastapi_jwt import JwtAuthorizationCredentials
from datetime import datetime, timedelta
from config import CONFIG
from database.models.adminuser import AdminUserDocument
import bcrypt
import jwt

ACCESS_EXPIRES = timedelta(hours=6)
REFRESH_EXPIRES = timedelta(days=3)
ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expiration = datetime.utcnow() + ACCESS_EXPIRES
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, CONFIG.authjwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expiration = datetime.utcnow() + REFRESH_EXPIRES
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, CONFIG.authjwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, CONFIG.authjwt_secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# async def user_from_credentials(auth: JwtAuthorizationCredentials) -> AdminUserDocument | None:
#     return await AdminUserDocument.by_email(auth.subject["email"])

# async def user_from_token(token: str) -> AdminUserDocument | None:
#     payload = access_security._decode(token)
#     return await AdminUserDocument.by_email(payload["subject"]["email"])

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), CONFIG.salt).decode()
