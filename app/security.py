"""
Password hashing utilities using bcrypt and JWT token generation.

Provides secure password hashing, verification functions, and JWT handling.
"""
import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password: Plain-text password to hash
        
    Returns:
        Hashed password string
        
    Raises:
        ValueError: If password is empty or invalid
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    # bcrypt generates a random salt and includes it in the hash
    # Default cost factor is 12, which is secure and reasonably fast
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    
    Args:
        password: Plain-text password to verify
        password_hash: Bcrypt hash to verify against
        
    Returns:
        True if password matches hash, False otherwise
        
    Raises:
        ValueError: If either parameter is invalid
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    if not password_hash or not isinstance(password_hash, str):
        raise ValueError("Password hash must be a non-empty string")
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except ValueError:
        # Invalid hash format
        return False


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary containing token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to extract and validate the current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials containing Bearer token
        
    Returns:
        User ID from the token
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # In a real application, you'd fetch the user from the database
        # For now, we'll return the username from the token
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
