from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from dtos import OTPUserCreateDTO, VarifyOTPDTO, OTPUserLoginDTO, UserLoginResponseDTO, UserResponseDTO
from models import UserDB, OtpDB
from helper import ( 
    get_password_hash, authenticate_user, 
    get_user_by_email,  getOtp, SendEmail,
    get_user_by_username,  verify_password,
    generate_token, get_current_user_by_jwt_token
    )
from database import get_db
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/otp")


@router.post("/register", status_code=201)
def Register(body:OTPUserCreateDTO, bgTask:BackgroundTasks, db:Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == body.email).first()
    if user and user.is_verified:
        raise HTTPException(status_code=401, detail="This email address already exists..")

    if user and not user.is_verified:
        all_otps = db.query(OtpDB).filter(OtpDB.user_id == user.id).all()
        db.delete_all(all_otps)
        db.delete(user)
        db.commit()


    userObj = body.model_dump()
    userObj.update(
        {
            "username":body.email,
            "is_otp_active":True,
            "is_verified":False,
            "is_active":False,

        }
    )

    user = UserDB(**userObj)
    db.add(user)
    db.commit()
    db.refresh(user)

    otp = getOtp()
    otpObj = OtpDB(
        user_id  = user.id,
        purpose = "verify_email",
        otp_hash = get_password_hash(otp),
        created_at = datetime.now(timezone.utc),
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(otpObj)
    db.commit()
    db.refresh(otpObj)

    bgTask.add_task(SendEmail, receiver_email=user.email, subject="Varify Your TechSimPlus Account", body=f"Here is your 6 Digit OTP to verify your techsimplus account: OTP: {otp}")


    return {"status":"OTP Send Successfully, Please Enter and Varify your account"}
    

@router.post("/varify", status_code=201, response_model=UserLoginResponseDTO)
def Verify(body:VarifyOTPDTO, db:Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == body.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="This email address does not exists..")

    otp = db.query(OtpDB).filter(OtpDB.user_id == user.id, OtpDB.is_used == False).first()
    if not otp:
        raise HTTPException(status_code=401, detail="This email address does not exists..")

    if not verify_password(body.otp, otp.otp_hash):
        raise HTTPException(status_code=401, detail="OTP Does not match")

    otp.is_used = True
    user.is_verified = True
    user.is_active = True
    db.commit()

    token = generate_token({
        "_id":user.id,
        "email":user.email
    })

    return {"token":token, "user":user}
    

@router.post("/login")
def Login(body:OTPUserLoginDTO, bgTask:BackgroundTasks, db:Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == body.email).first()
    print(user.is_verified)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="This email address does not exists..")

    all_otps = db.query(OtpDB).filter(OtpDB.user_id == user.id, OtpDB.is_used == False).all()
    db.delete_all(all_otps)
    db.commit()

    otp = getOtp()
    otpObj = OtpDB(
        user_id  = user.id,
        purpose = "account_login",
        otp_hash = get_password_hash(otp),
        created_at = datetime.now(timezone.utc),
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(otpObj)
    db.commit()
    db.refresh(otpObj)

    bgTask.add_task(SendEmail, receiver_email=user.email, subject="Varify Your TechSimPlus Account", body=f"Here is your 6 Digit OTP to verify your techsimplus account: OTP: {otp}")

    return {"status":"OTP Sent Successfully..."}

    

@router.get("/me", response_model=UserResponseDTO)
def Me(user: UserDB = Depends(get_current_user_by_jwt_token)):
    return user


    

    






    
    

