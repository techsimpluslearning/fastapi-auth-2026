from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from database import SessionLocal
from models import *
from fastapi import HTTPException, Request
from datetime import datetime, timedelta, timezone
import jwt, os, secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from dotenv import load_dotenv
load_dotenv()

JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_MINUTES=os.getenv("JWT_EXPIRE_MINUTES", "30")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")
sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("APP_PASSWORD")


password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def _db() -> Session:
    return SessionLocal()


def get_user_by_email(email:str) -> UserDB | None:
    db: Session = _db()
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user:
        return user
    return None


def get_user_by_username(username:str) -> UserDB | None:
    db: Session = _db()
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user:
        return user
    return None



def authenticate_user(username, password) -> UserDB:
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="You entered wrong username")

    if not verify_password(password, user.hash_password):
        raise HTTPException(status_code=404, detail="You entered wrong password")

    return user

def generate_token(payload:dict):
    payload.update(
        {
            "iat":datetime.now(timezone.utc),
            "exp":datetime.now(timezone.utc) + timedelta(minutes=int(JWT_EXPIRE_MINUTES))
        }
    )

    token = jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

    
def get_current_user_by_jwt_token(request:Request):
    token = request.headers.get("authorization", "")
    if not token:
        raise HTTPException(status_code=404, detail="Token Not Found")

    token = token.removeprefix("jwt").strip()

    print(token)
    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        db:Session = _db()
        user = db.query(UserDB).filter(UserDB.id == payload["_id"], UserDB.is_active == True).first()
        if not user:
            raise HTTPException(status_code=404, detail="You are un-authorized")    

        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=404, detail="Token Expired")

    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=404, detail="Token is InValied")








# ----------- Send Email OTP ------------
def SendEmail(receiver_email:str, subject:str, body:str):
    "Send email"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body
    message.attach(MIMEText(body, "plain"))

    # Connect to Gmail SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        # Login
        server.login(sender_email, app_password)

        # Send email
        server.sendmail(
            sender_email,
            receiver_email,
            message.as_string()
        )

    return "Email sent successfully!"


def getOtp():
    otp = str(secrets.randbelow(900000) + 100000)
    return otp