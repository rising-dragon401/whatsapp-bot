from fastapi import APIRouter, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.models.adminuser import AdminUserDocument, AdminUserSignup, AdminUserSignin, AdminUserOut
from database.models.auth import AccessToken, RefreshToken
from utils.jwt import access_security, refresh_security, hash_password

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

@router.post("/signin")
async def signin(user_auth: AdminUserSignin) ->  RefreshToken:
    adminuser = await AdminUserDocument.by_email(user_auth.email)

    if adminuser is None or hash_password(user_auth.password) != adminuser.password:
        raise HTTPException(status_code=401, detail="Bad emaill or password")
    # if adminuser.email_confirmed_at is None:
    #     raise HTTPException(status_code=400, detail="Email is not yet verified")
    
    access_token = access_security.create_access_token(adminuser.jwt_subject)
    refresh_token = refresh_security.create_refresh_token(adminuser.jwt_subject)

    return RefreshToken(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh")
async def refresh(
    auth: JwtAuthorizationCredentials = Security(refresh_security)
) -> AccessToken:
    access_token = access_security.create_access_token(subject=auth.subject)
    return AccessToken(access_token=access_token)

@router.post("/signup", response_model=AdminUserOut)
async def user_registration(user_auth: AdminUserSignup):
    print("\n*** SignUp ***\n", user_auth)
    adminuser = await AdminUserDocument.by_email(user_auth.email)
    if adminuser is not None:
        raise HTTPException(409, "User with that email already exists")
    
    hashed = hash_password(user_auth.password)

    adminuser = AdminUserDocument(name = user_auth.name, email = user_auth.email, password = hashed)
    await adminuser.create()

    return adminuser