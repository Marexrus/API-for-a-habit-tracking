import datetime
import utils
import itertools
import sqlite3
from fastapi import HTTPException

"""
Date: 'DD-MM-YYYY'


habit: id name color period_type period start_date
check_ins: id habit_id check_datetime

"""


def create_base(cursor):
    cursor.execute("""CREATE TABLE habits(id INTEGER PRIMARY KEY AUTOINCREMENT,
     name TEXT NOT NULL, color TEXT, period_type TEXT DEFAULT "daily", period INTEGER, start_date TEXT)""")


def create_base_check_in(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS check_ins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    check_datetime TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id),
    UNIQUE (habit_id, check_date)
);""")


def add_habit(cursor,data):
    name, color, period_type, period, start_date = data
    try:
        cursor.execute("""
            INSERT INTO habits (name, color, period_type, period, start_date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, color,period_type, period, start_date))
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")
    return {"Success": True}


def edit_habit(cursor, column, value, where_column, where_value):
    try:
        cursor.execute (f"UPDATE habits SET {column} = ? WHERE {where_column} = ?", (value, where_value))
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")
    return {"Success": True}


def print_table(cursor, name):
    cursor.execute(f"SELECT * FROM {name}")
    data = cursor.fetchall()
    for el in data:
        print(el)


def read_table(cursor, read_column:str, where_column:str|None = None, value:str|None = None):
    try:
        if read_column == "*":
            cursor.execute(f"SELECT * FROM habits")
        elif not where_column and not value:
            cursor.execute(f"SELECT {read_column} FROM habits")
        else:
            cursor.execute(f"SELECT {read_column} FROM habits WHERE {where_column} = {value}")
        data = cursor.fetchall()
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")

    return data


def delete_habit(cursor, column, value):
    try:
        cursor.execute(f'DELETE FROM habits WHERE {column} = {value}')
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")
    return {"Success": True}


def add_check_in(cursor,dt):
    habit_id, check_datetime = dt
    try:
        cursor.execute('select check_datetime from check_ins where habit_id = ?',(habit_id,))
        data = cursor.fetchall()
        dates = []
        for el in data:
            dates.append((el[0][0:8:1]))
        if check_datetime[0:8:1] in dates:
            raise HTTPException(status_code = 409, detail="Отметка уже существует")
        cursor.execute("INSERT INTO check_ins('habit_id', 'check_datetime') VALUES(?, ?)", (habit_id, check_datetime))
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")
    return {"Success": True}


def delete_check_in(cursor,data):
    habit_id, check_datetime = data
    try:
        cursor.execute('DELETE FROM check_ins WHERE habit_id = ? AND check_datetime = ?', (habit_id, check_datetime))
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")
    return {"Success": True}


def select_history(cursor, habit_id, date_from, date_to):
    try:
        cursor.execute('select check_datetime from check_ins where check_datetime between ? and ? and habit_id = ?',
                    (date_from, date_to, habit_id))
    except sqlite3.OperationalError:
        raise HTTPException(status_code=404, detail="Поле не найдено")
    data = cursor.fetchall()

    dates= []
    for el in data:
        a = datetime.datetime.strptime(el[0], '%d-%m-%y %H:%M')
        dates.append(a)
    current_streak, max_streak = utils.calculate_streaks(dates)

    return {'check datetime': data, 'count of check': len(data),
            'current streak': current_streak, 'max streak': max_streak}
