from fastapi import FastAPI, HTTPException, APIRouter, Form, Depends, Cookie
from typing import Annotated

import datetime

from database.database import *
from utils import *
from models import *
import auth.auth as auth
import auth.utils as utils


router = APIRouter(prefix='/habits', tags=['Habits'])

@router.post('/create')
async def create_habit(habit: Habit = Form(), auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  print(habit)
  payload = utils.decode_jwt(auth_token)
  result = db.add_habit(payload, habit)
  db.print_table("habits")
  return result


@router.get('/read')
async def read_habit(read_column: str ,where_column: str | None = None,value: str | None = None, auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  try:
    if where_column == 'id': value=int(value)
    if where_column == 'period': value=int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  payload = utils.decode_jwt(auth_token)
  data = db.read_table(payload, read_column, where_column, value)
  return data


@router.post('/update')
async def update_habit(column:str, value, where_column:str, where_value:str, auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  try:
    if column == 'id': value = int(value)
    if column == 'period': value = int(value)
    if where_column == 'id': where_value = int(where_value)
    if where_column == 'period': where_value = int(where_value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = db.edit_habit(auth_token, column, value, where_column, where_value)
  if result == 'Error 404':
    raise HTTPException(status_code=404, detail="Поле не найдено")
  db.print_table("habits")
  return result


@router.delete('/delete')
async def delete_habit(column: str, value: str, auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  try:
    if column == 'id': value = int(value)
    if column == 'period': value = int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = db.delete_habit(auth_token, column, value)
  db.print_table("habits")
  return result


@router.post("/{habit_id}/check-ins")
async def create_check_in(habit_id: int, datetime: str|None=None, auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  if not datetime:
    datetime = current_datetime()
  result = db.add_check_in(auth_token, habit_id, datetime)
  db.print_table("check_ins")
  return result


@router.delete("/{habit_id}/check-ins/{datetime}")
async def delete_check_in(habit_id: int, datetime: str, auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  if not datetime:
    raise HTTPException(status_code=400, detail="дата не может быть равна нулю")
  result = db.delete_check_in(auth_token, habit_id, datetime)
  db.print_table("check_ins")

  return result


@router.get("/history")
async def history(habit_id: int, date_from: str, date_to: str, auth_token: Annotated[str, Cookie(alias="auth_token")] = None):
  date_to = (datetime.datetime.strptime(date_to, '%d-%m-%y %H:%M') + datetime.timedelta(minutes=1)).strftime('%d-%m-%y %H:%M')
  history = db.select_history(auth_token, habit_id, date_from, date_to)
  return history