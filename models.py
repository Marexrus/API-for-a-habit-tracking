from pydantic import BaseModel


class Habit(BaseModel):
  user_id: int
  name: str
  color: str
  period: int
  date_start: str


class AuthJWT(BaseModel):
  private_key_path: str = 'certs/jwt-private.pem'
  public_key_path: str = 'certs/jwt-public.pem'
  algorithm: list = "RS256"
  expire_minutes: int = 15

  def read_text(self,path: str):
    with open(path,'r') as file:
      text = file.read()
      return text


class UserModel(BaseModel):
  id: int
  username: str
  hash_password: bytes
  email: str | None = None
  active: bool = True
  last_online: str | None = None
  role: str | None = 'user'


class TokenInfo(BaseModel):
  access_token: str
  token_type: str

auth_jwt = AuthJWT()