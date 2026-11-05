import jwt
from models import *
import bcrypt
from datetime import *

private_key = auth_jwt.read_text(auth_jwt.private_key_path)
public_key = auth_jwt.read_text(auth_jwt.public_key_path)


def encode_jwt(payload: dict, private_key: str = private_key, algorithm: str = auth_jwt.algorithm, expire_minutes: int =  auth_jwt.expire_minutes):
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    payload.update(exp=expire, iat=now)
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(token: str, public_key: str = public_key, algorithm: str = auth_jwt.algorithm):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)

