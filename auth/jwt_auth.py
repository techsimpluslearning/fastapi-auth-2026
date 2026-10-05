from fastapi import APIRouter, Depends, HTTPException
from dtos import UserCreateDTO, UserLoginDTO, UserResponseDTO, UserLoginResponseDTO
from models import UserDB
from helper import ( 
    get_password_hash, authenticate_user, 
    get_user_by_email, 
    get_user_by_username, 
    generate_token, get_current_user_by_jwt_token
    )
from database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/jwt")

@router.post("/signup", status_code=201, response_model=UserResponseDTO)
def Register(body:UserCreateDTO, db:Session = Depends(get_db)):
    #### is user already exist
    if get_user_by_username(body.username):
        raise HTTPException(status_code=401, detail="This username already exists..")

    if get_user_by_email(body.email):
        raise HTTPException(status_code=401, detail="This email address already exists..")
    
    body:dict = body.model_dump()
    body["hash_password"] = get_password_hash(body["password"])
    body.pop("password")
    user = UserDB(**body)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@router.post("/login", status_code=200, response_model=UserLoginResponseDTO)
def Login(body:UserLoginDTO):
    user:UserDB = authenticate_user(body.username, body.password)
    token = generate_token({
        "_id":user.id,
        "role":user.role,
        "username":user.username
    })

    return {
        "token":token,
        "user":user
    }


@router.get("/me", response_model=UserResponseDTO)
def Me(user: UserDB = Depends(get_current_user_by_jwt_token)):
    return user







