from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base, engine


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50),unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hash_password = Column(String(255), nullable=True)
    
    is_active = Column( Boolean, default=True, nullable=False)
    is_otp_active = Column( Boolean, default=False, nullable=False)

    # OTP Based auth
    is_verified = Column( Boolean, default=True, nullable=False)

    role = Column(String(30))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    api_keys = relationship("ApiKeys", back_populates="user")
    oauth_clients = relationship("OAuthClientDB", back_populates="owner")
    otps = relationship("OtpDB", back_populates="user")



class ApiKeys(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(250), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("UserDB", back_populates="api_keys")


#### Client Id and Client Secret Based Auth
class OAuthClientDB(Base):
    __tablename__ = "oauth_clients"

    id                 = Column(Integer, primary_key=True, index=True)
    client_id          = Column(String(100), unique=True, index=True, nullable=False)
    client_secret_hash = Column(String(200), nullable=False)
    client_name        = Column(String(200), nullable=False)
    owner_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    scopes             = Column(String(500), default="read")
    is_active          = Column(Boolean,     default=True)
    created_at         = Column(DateTime,    default=func.now())

    # Relationship: lets us write  client.owner.username
    owner = relationship("UserDB", back_populates="oauth_clients")


class OtpDB(Base):
    __tablename__ = "otps"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    purpose    = Column(String(30),  nullable=False)       # "verify_email" | "reset_password"
    otp_hash   = Column(String(128), nullable=False)
    attempts   = Column(Integer, default=0, nullable=False) # wrong guesses so far
    is_used    = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)      
    created_at = Column(DateTime, nullable=False)      

    user = relationship("UserDB", back_populates="otps")


def init_db():
    Base.metadata.create_all(bind = engine)
