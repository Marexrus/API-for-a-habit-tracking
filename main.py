from fastapi import FastAPI, HTTPException, APIRouter, Form

import datetime

import database
from utils import *
from models import *
import auth.auth as auth
import habits

# Создаем экземпляр приложения
app = FastAPI()
app.include_router(auth.router)
app.include_router(habits.router)

database.start_database()

# Определяем GET-запрос по корневому пути "/"
@app.get("/")
def read_root():
  return {"message": "Привет, FastAPI!"}



@app.post('/user/add')
async def add_user(user: UserModel = Form()):
  print(user)
  if not user.last_online:
    user.last_online = current_datetime()
  result = database.add_user(user)
  return result