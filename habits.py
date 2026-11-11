from fastapi import FastAPI, HTTPException, APIRouter, Form, Depends

import datetime

from database.database import *
from utils import *
from models import *
import auth.auth as auth


router = APIRouter(prefix='/habits', tags=['Habits'])

@router.post('/create')
async def create_habit(habit: Habit = Form(), user: UserModel = Depends(auth.get_user)):
  print(habit)
  result = db.add_habit(user, habit)
  db.print_table("habits")
  return result


@router.get('/read')
async def read_habit(read_column: str ,where_column: str | None = None,value: str | None = None, user: UserModel = Depends(auth.get_user)):
  try:
    if where_column == 'id': value=int(value)
    if where_column == 'period': value=int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  data = db.read_table(user, read_column, where_column, value)
  return data


@router.post('/update')
async def update_habit(column:str, value, where_column:str, where_value:str, user: UserModel = Depends(auth.get_user)):
  try:
    if column == 'id': value = int(value)
    if column == 'period': value = int(value)
    if where_column == 'id': where_value = int(where_value)
    if where_column == 'period': where_value = int(where_value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = db.edit_habit(user, column, value, where_column, where_value)
  if result == 'Error 404':
    raise HTTPException(status_code=404, detail="Поле не найдено")
  db.print_table("habits")
  return result


@router.delete('/delete')
async def delete_habit(column: str, value: str, user: models.UserModel = Depends(auth.get_user)):
  try:
    if column == 'id': value = int(value)
    if column == 'period': value = int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = db.delete_habit(user, column, value)
  db.print_table("habits")
  return result


@router.post("/{habit_id}/check-ins")
async def create_check_in(habit_id: int, datetime: str|None=None, user: models.UserModel = Depends(auth.get_user)):
  if not datetime:
    datetime = current_datetime()
  result = db.add_check_in(user, habit_id, datetime)
  db.print_table("check_ins")
  return result


@router.delete("/{habit_id}/check-ins/{datetime}")
async def delete_check_in(habit_id: int, datetime: str, user: models.UserModel = Depends(auth.get_user)):
  if not datetime:
    raise HTTPException(status_code=400, detail="дата не может быть равна нулю")
  result = db.delete_check_in(user, habit_id, datetime)
  db.print_table("check_ins")

  return result


@router.get("/history")
async def history(habit_id: int, date_from: str, date_to: str, user: models.UserModel = Depends(auth.get_user)):
  date_to = (datetime.datetime.strptime(date_to, '%d-%m-%y %H:%M') + datetime.timedelta(minutes=1)).strftime('%d-%m-%y %H:%M')
  history = db.select_history(user, habit_id, date_from, date_to)
  return history