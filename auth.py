from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import secrets
import warnings
from fastapi.security import OAuth2PasswordBearer
import requests

from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt

# Get secret key from environment variable, or generate random string with warning
SECRET_KEY = os.environ.get("JWT_SECRET_TOKEN")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(32)
    warnings.warn(
        "JWT_SECRET_TOKEN environment variable is not set. Using a randomly generated secret key. "
        "This means tokens will be invalidated on server restart. "
        "Please set JWT_SECRET_TOKEN environment variable for production use.",
        UserWarning
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(username: str, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token with username and expiration time."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "username": username,
        "expire": int(expire.timestamp())
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: Optional[str] = Header(None)):
    """Verify JWT token from Authorization header."""
    print("Verifying token...")
    print(f"Authorization header: {token}")
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Please login to access this resource"}
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        expire: int = payload.get("expire")
        
        if username is None or expire is None:
            raise HTTPException(
                status_code=401,
                detail={"error": "Invalid token. Please login."}
            )
        
        # Check if token has expired
        if datetime.now(timezone.utc).timestamp() > expire:
            raise HTTPException(
                status_code=401,
                detail={"error": "Token has expired. Please login."}
            )
        
        return username
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid token. Please login."}
        )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or "GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or "GOOGLE_CLIENT_SECRET"
GOOGLE_REDIRECT_URI =os.getenv("GOOGLE_REDIRECT_URI") or "GOOGLE_REDIRECT_URI"

def register_oauth_routes(app):
    @app.get("/login/google")
    async def login_google():
        return {
            "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email"
        }

    @app.get("/auth/google")
    async def auth_google(code: str):
        token_url = "https://accounts.google.com/o/oauth2/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=data)
        access_token = response.json().get("access_token")
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        name = user_info.json().get("name")
        access_token = create_access_token(
            username=name,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"token": access_token, "name": name}
