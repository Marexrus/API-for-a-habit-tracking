from fastapi import APIRouter, Depends, Form, HTTPException, Response, Cookie
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from typing import Annotated

import models
from auth.utils import *
from database.database import *
from utils import *

http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/')
router = APIRouter(prefix='/auth', tags=['Auth'])


def update_last_online(username):
    db.cursor.execute("UPDATE users SET last_online = %s WHERE username = %s", (current_datetime(), username))

def select_user(username:str) -> models.UserModel:
    db.cursor.execute("select * from users where username = %s", (username,))
    row = db.cursor.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail='Unauthorized')
    columns = [column[0] for column in db.cursor.description]

    user_data = dict(zip(columns, row))

    user = models.UserModel(**user_data)
    return user

def validate_user_auth(username: str = Form(), password: str = Form()):
    unauth_exc = HTTPException(status_code=401, detail='invalid username or password')
    user = select_user(username)

    if user is None:
        raise unauth_exc
    is_valid = check_password(password, user.hash_password)
    if not is_valid:
        raise unauth_exc
    if not user.active:
        raise HTTPException(status_code=403, detail='user inactive')
    update_last_online(username)
    return user


def get_user(token: str = Depends(oauth2_scheme)) -> models.UserModel:
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")
    user = select_user(payload['username'])
    return user.model_dump(exclude={"hash_password"})


@router.post(path="/login/")
def jwt_after_auth(response: Response, user: models.UserModel = Depends(validate_user_auth)):
    print(user)
    jwt_payload = {"username": user.username, 'id': user.id, 'email': user.email, 'login_at': current_datetime()}
    token = encode_jwt(payload=jwt_payload)
    response.set_cookie('auth_token', token)
    return models.TokenInfo(access_token=token, token_type='Bearer')


@router.get("/user/me/")
def user_info(user: UserModel = Depends(get_user)):
    return user


# добавить валидность данных
@router.post("/register")
def register(username: str, password: str, email: str | None = None):
    now = current_datetime()
    user = models.UserModel(username=username, hash_password=password, email=email, active="True", last_online=now, role="user")
    result = db.add_user(user)

    return result