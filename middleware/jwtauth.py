import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from config import CONFIG

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        bypass_paths = [
            "/api/auth/signin",
            "/api/auth/signup",
            "/api/messaging/webhook",
            "/api/payment/success"
        ]

        if request.url.path in bypass_paths:
            response = await call_next(request)
            return response

        authorization: str = request.headers.get("authorization")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1]
            try:
                payload = jwt.decode(token, CONFIG.authjwt_secret_key, algorithms=["HS256"])
                request.state.user = payload
            except jwt.ExpiredSignatureError:
                return Response("Token has expired", status_code=401)
            except jwt.InvalidTokenError:
                return Response("Invalid token", status_code=401)
        else:
            return Response("Authorization header missing or invalid", status_code=401)

        response = await call_next(request)
        return response