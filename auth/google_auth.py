import os
from datetime import datetime, timedelta, timezone
from helper import generate_token
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from starlette.requests import Request


router = APIRouter(prefix="/google")

config = Config(".env")
oauth = OAuth(config)

GOOGLE_CALLBACK_URL = os.getenv("GOOGLE_CALLBACK_URL", "")

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    client_kwargs={
        "scope": "openid email profile",
    },
)



@router.get("/login", summary="Start Google OAUTH Login")
async def google_login(request:Request):
    if not os.environ.get("GOOGLE_CLIENT_ID", ""):
        raise HTTPException(
            status_code=503,
            detail="Google Oauth is not connected..."
        )

    return await oauth.google.authorize_redirect(request, GOOGLE_CALLBACK_URL)
        

@router.get("/callback")
async def google_callback(request:Request):
    try:
        google_token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth Error"
        )

    user_info = google_token.get("userinfo", {})
    email = user_info.get("email")

    token = generate_token(
        {
            "sub":email,
            "name":user_info.get("name"),
            "picture":user_info.get("picture"),
            "role":"user"
        }
    )

    return {
        "message":"LoggedIn with google successfully.",
        "user_profile": user_info,
        "token": token
    }




