from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer
from datetime import timedelta
from config import CONFIG
from database.models.adminuser import AdminUserDocument
import bcrypt

ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)

access_security = JwtAccessBearer(
    CONFIG.authjwt_secret_key,
    access_expires_delta=ACCESS_EXPIRES,
    refresh_expires_delta=REFRESH_EXPIRES,
)

refresh_security = JwtRefreshBearer(
    CONFIG.authjwt_secret_key,
    access_expires_delta=ACCESS_EXPIRES,
    refresh_expires_delta=REFRESH_EXPIRES,
)

async def user_from_credentials(auth: JwtAuthorizationCredentials) -> AdminUserDocument | None:
    """Return the user associated with auth credentials."""
    return await AdminUserDocument.by_email(auth.subject["username"])

async def user_from_token(token: str) -> AdminUserDocument | None:
    """Return the user associated with a token value."""
    payload = access_security._decode(token)
    return await AdminUserDocument.by_email(payload["subject"]["username"])

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    print("\### salt ###\n", CONFIG.salt)
    return bcrypt.hashpw(password.encode(), CONFIG.salt).decode()
