from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

import models
import auth.utils as utils
import database as db
from datetime import *
from utils import *

http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/jwt/login/')
router = APIRouter(prefix='/auth', tags=['Auth'])

def select_user(username:str) -> models.UserModel:
    db.cursor.execute("select * from users where username = ?", (username,))
    row = db.cursor.fetchone()
    columns = [column[0] for column in db.cursor.description]

    user_data = dict(zip(columns, row))

    user = models.UserModel(**user_data)
    return user

def validate_user_auth(username: str = Form(), password: str = Form()):
    unauth_exc = HTTPException(status_code=401, detail='invalid username or password')
    user = select_user(username)

    if user is None:
        raise unauth_exc
    is_valid = utils.check_password(password, user.hash_password)
    if not is_valid:
        raise unauth_exc
    if not user.active:
        raise HTTPException(status_code=403, detail='user inactive')
    return user


def get_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = utils.decode_jwt(token = token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, details="invalid token")
    print(payload)
    user = select_user(payload['username'])
    return user


@router.post(path="/login/")
def jwt_after_auth(user: models.UserModel = Depends(validate_user_auth)):
    print(user)
    jwt_payload = {"username":user.username, 'email': user.email, 'login_at': current_datetime()}
    token = utils.encode_jwt(payload=jwt_payload)
    return models.TokenInfo(access_token=token, token_type='Bearer')

@router.get("/user/me/")
def user_info(user: UserModel = Depends(get_user)):
    return user