from pydantic import BaseModel
import utils


class AuthJWT(BaseModel):
  private_key_path: str = 'certs/jwt-private.pem'
  public_key_path: str = 'certs/jwt-public.pem'
  algorithm: str = "RS256"
  expire_minutes: int = 15

  def read_text(self,path: str):
    with open(path,'r') as file:
      text = file.read()
      return text


class Habit(BaseModel):
  user_id: int
  name: str
  color: str
  period: int
  date_start: str | None = utils.current_datetime()


class UserModel(BaseModel):
  id: int | None = None
  username: str
  hash_password: str
  email: str | None = None
  active: bool = True
  last_online: str | None = None
  role: str | None = 'user'


class TokenInfo(BaseModel):
  access_token: str
  token_type: str

auth_jwt = AuthJWT()