from fastapi import FastAPI, HTTPException

import sqlite3
import datetime

import database
from utils import *
from models import *


# Создаем экземпляр приложения
app = FastAPI()

connection = sqlite3.connect('database/database.db', autocommit=True)

cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

database.print_table(cursor, "habits")
print("-----------------")
database.print_table(cursor, "check_ins")
print("-----------------")


# Определяем GET-запрос по корневому пути "/"
@app.get("/")
def read_root():
  return {"message": "Привет, FastAPI!"}


@app.post('/habits/create')
async def create_habit(habit: Habit):
  print(habit)
  data = (habit.name, habit.color, habit.period_type, habit.period, habit.date_start)
  result = database.add_habit(cursor, data)
  database.print_table(cursor, "habits")
  return result


@app.post('/habits/read')
async def read_habit(read_column: str,where_column: str | None = None,value: str | None = None):
  try:
    if where_column == 'id': value=int(value)
    if where_column == 'period': value=int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  data = database.read_table(cursor, read_column, where_column, value)
  return data


@app.post('/habits/update')
async def update_habit(column:str, value, where_column:str, where_value:str):
  try:
    if where_column == 'id': value = int(value)
    if where_column == 'period': value = int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = database.edit_habit(cursor, column, value, where_column, where_value)
  if result == 'Error 404':
    raise HTTPException(status_code=404, detail="Поле не найдено")
  database.print_table(cursor, "habits")
  return result


@app.post('/habits/delete')
async def delete_habit(column: str, value: str):
  try:
    if column == 'id': value = int(value)
    if column == 'period': value = int(value)
  except ValueError:
    raise HTTPException(status_code=400, detail='Данные неверны')
  result = database.delete_habit(cursor, column, value)
  database.print_table(cursor, "habits")
  return result


@app.post("/habits/{habit_id}/check-ins")
async def create_check_in(habit_id: int, datetime: str|None=None):
  if not datetime:
    datetime = current_datetime()
  result = database.add_check_in(cursor, (habit_id, datetime))
  database.print_table(cursor, "check_ins")
  return result


@app.post("/habits/{habit_id}/check-ins/{datetime}")
async def delete_check_in(habit_id: int, datetime: str):
  if not datetime:
    raise HTTPException(status_code=400, detail="дата не может быть равна нулю")
  result = database.delete_check_in(cursor, (habit_id, datetime))
  database.print_table(cursor, "check_ins")

  return result


@app.post("/habits/history")
async def history(habit_id: int, date_from: str, date_to: str):
  date_to = (datetime.datetime.strptime(date_to, '%d-%m-%y %H:%M') + datetime.timedelta(minutes=1)).strftime('%d-%m-%y %H:%M')
  history = database.select_history(cursor, habit_id, date_from, date_to)
  return history



