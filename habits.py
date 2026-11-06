from fastapi import FastAPI, HTTPException, APIRouter, Form

import datetime

import database
from utils import *
from models import *


router = APIRouter(prefix='/habits', tags=['Habits'])

@router.post('/create')
async def create_habit(habit: Habit = Form()):
  print(habit)
  result = database.add_habit(habit)
  database.print_table("habits")
  return result


@router.post('/read')
async def read_habit(read_column: str,where_column: str | None = None,value: str | None = None):
  try:
    if where_column == 'id': value=int(value)
    if where_column == 'period': value=int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  data = database.read_table(read_column, where_column, value)
  return data


@router.post('/update')
async def update_habit(column:str, value, where_column:str, where_value:str):
  try:
    if where_column == 'id': value = int(value)
    if where_column == 'period': value = int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = database.edit_habit(column, value, where_column, where_value)
  if result == 'Error 404':
    raise HTTPException(status_code=404, detail="Поле не найдено")
  database.print_table("habits")
  return result


@router.post('/delete')
async def delete_habit(column: str, value: str):
  try:
    if column == 'id': value = int(value)
    if column == 'period': value = int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = database.delete_habit(column, value)
  database.print_table("habits")
  return result


@router.post("/{habit_id}/check-ins")
async def create_check_in(habit_id: int, datetime: str|None=None):
  if not datetime:
    datetime = current_datetime()
  result = database.add_check_in((habit_id, datetime))
  database.print_table("check_ins")
  return result


@router.post("{habit_id}/check-ins/{datetime}")
async def delete_check_in(habit_id: int, datetime: str):
  if not datetime:
    raise HTTPException(status_code=400, detail="дата не может быть равна нулю")
  result = database.delete_check_in((habit_id, datetime))
  database.print_table("check_ins")

  return result


@router.post("/history")
async def history(habit_id: int, date_from: str, date_to: str):
  date_to = (datetime.datetime.strptime(date_to, '%d-%m-%y %H:%M') + datetime.timedelta(minutes=1)).strftime('%d-%m-%y %H:%M')
  history = database.select_history(habit_id, date_from, date_to)
  return history