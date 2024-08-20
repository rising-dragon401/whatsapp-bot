from fastapi import APIRouter, HTTPException
from database.models.adminuser import AdminUserDocument, AdminUserSignup, AdminUserSignin, AdminUserOut
from database.models.auth import AccessToken, RefreshToken
from utils.jwt import create_access_token, create_refresh_token, verify_token, hash_password

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

    access_token = create_access_token({"sub": adminuser.jwt_subject})
    refresh_token = create_refresh_token({"sub": adminuser.jwt_subject})
    
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh")
async def refresh(token: RefreshToken) -> AccessToken:
    payload = verify_token(token.refresh_token)
    if payload:
        access_token = create_access_token({"sub": payload["sub"]})
        return AccessToken(access_token=access_token)
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@router.post("/signup", response_model=AdminUserOut)
async def user_registration(user_auth: AdminUserSignup):
    adminuser = await AdminUserDocument.by_email(user_auth.email)
    if adminuser is not None:
        raise HTTPException(409, "User with that email already exists")
    
    hashed = hash_password(user_auth.password)

    adminuser = AdminUserDocument(name = user_auth.name, email = user_auth.email, password = hashed)
    await adminuser.create()

    return adminuser