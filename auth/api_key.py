from fastapi import APIRouter, Depends, HTTPException
from dtos import UserCreateDTO, UserLoginDTO, UserResponseDTO, UserLoginResponseDTO
from models import UserDB, ApiKeys
from helper import ( 
    get_password_hash, authenticate_user, 
    get_user_by_email, 
    get_user_by_username, 
    generate_token, get_current_user_by_jwt_token
    )
from database import get_db
from sqlalchemy.orm import Session
import uuid

router = APIRouter(prefix="/api-key")


@router.post("/generate")
def create_api_key(user: UserDB = Depends(get_current_user_by_jwt_token), db:Session = Depends(get_db)):
    key = f"auth_{uuid.uuid4().hex}"
    api_key = ApiKeys(
        key = key,
        user_id = user.id
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)


    return api_key


@router.post("/chat")
def openai_api(api_key:str, db:Session = Depends(get_db)):
    apiKeyObj = db.query(ApiKeys).filter(ApiKeys.key == api_key).first()
    if not apiKeyObj:
        raise HTTPException(status_code=404, detail="Invalid API Key")

    if apiKeyObj.is_revoked:
        raise HTTPException(status_code=404, detail="Revoked API Key")

    
    
    return {"answer":"This answer is coming from the AI", "user":apiKeyObj.user}


@router.get("/reveoke")
def revoke_api_key(api_key:str, user: UserDB = Depends(get_current_user_by_jwt_token), db:Session = Depends(get_db)):

    apiKeyObj = db.query(ApiKeys).filter(ApiKeys.key == api_key).first()
    if not apiKeyObj:
        raise HTTPException(status_code=404, detail="Invalid API Key")

    if apiKeyObj.is_revoked:
        return {"status":"API Key Revoked"}

    if apiKeyObj.user_id != user.id:
        raise HTTPException(status_code=404, detail="You are not allowed to revoked this api key")

    apiKeyObj.is_revoked = True
    db.commit()
    db.refresh(apiKeyObj)
    return {
        "status":"Done","api_key":apiKeyObj
    }





