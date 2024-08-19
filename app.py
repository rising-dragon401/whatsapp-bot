from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from database.database import lifespan
from middleware.jwtauth import JWTAuthMiddleware

app = FastAPI(
    lifespan=lifespan,
)

app.add_middleware(JWTAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)