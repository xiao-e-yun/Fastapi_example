from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional
from inspect import signature
import os
import secrets
import warnings

from fastapi import Header, HTTPException
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


def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={"error": "Please login to access this resource"}
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail={"error": "Invalid authentication scheme. Please login."}
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid authorization header format. Please login."}
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


def verify(func):
    """Decorator to verify JWT token for protected endpoints."""
    sig = signature(func)
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get authorization from kwargs if it's there, otherwise raise error
        authorization = kwargs.pop('authorization', None)
        verify_token(authorization)
        return await func(*args, **kwargs)
    
    # Add authorization parameter to wrapper's signature
    wrapper.__signature__ = sig.replace(parameters=list(sig.parameters.values()) + [
        signature(verify_token).parameters['authorization']
    ])
    
    return wrapper
