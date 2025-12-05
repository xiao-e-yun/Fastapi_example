from datetime import datetime, timedelta
from functools import wraps
from typing import Optional
from inspect import signature

from fastapi import Header, HTTPException, Depends
from jose import JWTError, jwt

# Secret key for JWT encoding/decoding (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(username: str, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token with username and expiration time."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
        if datetime.utcnow().timestamp() > expire:
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
