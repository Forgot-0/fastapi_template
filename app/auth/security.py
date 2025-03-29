from datetime import datetime, timedelta, timezone
from uuid import uuid4

from passlib.context import CryptContext
from jose import jwt, JWTError

from app.auth.config import auth_config
from app.auth.schemas.token import ResetToken, TokenPayload, VerifyToken


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash the user's password using bcrypt.

    :param password: The plain text password to hash.
    :return: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the user's password against the hashed password.

    :param plain_password: The plain text password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(*, data: dict[str, str], jti: str=str(uuid4()), expires_delta: timedelta | None = None) -> str:
    """
    Create an access token with an optional expiration time.

    :param data: The data to encode in the token.
    :param expires_delta: Optional timedelta for token expiration.
    :return: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"jti": jti, "exp": expire, "type": "access"}) # type: ignore
    encoded_jwt = jwt.encode(to_encode, auth_config.JWT_SECRET_KEY, algorithm=auth_config.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(*, data: dict[str, str], jti: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a refresh token with an optional expiration time.

    :param jti: jti token
    :param expires_delta: Optional timedelta for token expiration.
    :return: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"jti": jti, "exp": expire, "type": "refresh"}) # type: ignore
    encoded_jwt = jwt.encode(to_encode, auth_config.JWT_SECRET_KEY, algorithm=auth_config.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str) -> TokenPayload:
    """
    Verify a token and return the payload if valid.

    :param token: The JWT token to verify.
    :param token_type: The expected type of the token (e.g., 'access', 'refresh').
    :return: The decoded payload of the token.
    :raises JWTError: If the token is invalid or the type does not match.
    """
    payload = jwt.decode(token, auth_config.JWT_SECRET_KEY, algorithms=[auth_config.JWT_ALGORITHM])
    if payload.get("type") != token_type:
        raise JWTError("Not a valid JWT token")
    return TokenPayload(**payload)


def generate_reset_token(email: str) -> str:
    now = datetime.now()
    expires = now + timedelta(minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES)

    return jwt.encode(
        {'exp': expires, 'sub': email},
        key=auth_config.JWT_SECRET_KEY,
        algorithm=auth_config.JWT_ALGORITHM,
    )

def decode_reset_token(token: str) -> ResetToken:
    payload = jwt.decode(
        token=token,
        key=auth_config.JWT_SECRET_KEY,
        algorithms=[auth_config.JWT_ALGORITHM],
        options={'require': ['exp']},
    )

    return ResetToken(**payload)



def generate_verify_token(email: str) -> str:
    now = datetime.now()
    expires = now + timedelta(minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES)

    return jwt.encode(
        {'exp': expires, 'sub': email},
        key=auth_config.JWT_SECRET_KEY,
        algorithm=auth_config.JWT_ALGORITHM,
    )

def decode_verify_token(token: str) -> VerifyToken:
    payload = jwt.decode(
        token=token,
        key=auth_config.JWT_SECRET_KEY,
        algorithms=[auth_config.JWT_ALGORITHM],
        options={'require': ['exp']},
    )

    return VerifyToken(**payload)
