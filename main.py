from fastapi import FastAPI
from models import init_db
from auth.jwt_auth import router as auth_route
from auth.api_key import router as api_route
from auth.otp_auth import router as  otp_route
from auth.google_auth import router as  google_route
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
load_dotenv()

import os


app = FastAPI(
    title="Authentication",
    description="Different type of authentications"
)

app.add_middleware(
    SessionMiddleware, 
    secret_key= os.getenv("JWT_SECRET_KEY")
)

init_db()

@app.get("/health", status_code=200)
def health():
    return {
        "status":"OK"
    }


app.include_router(auth_route)
app.include_router(otp_route)
app.include_router(api_route)
app.include_router(google_route)

