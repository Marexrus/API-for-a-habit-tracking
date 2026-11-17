import datetime
import utils
import itertools
import sqlite3
from fastapi import HTTPException
import auth.utils
import models

import psycopg2
from psycopg2 import Error

"""
Date: 'DD-MM-YYYY'


habit: id name color period_type period start_date
check_ins: id habit_id check_datetime

"""

class Database:
    def __init__(self, user, password, host, port):
        user = user
        password = password
        host = host
        port = port
        connection = psycopg2.connect(dbname="habits", user=user, password=password, host=host,port=port)
        connection.autocommit = True

        self.cursor = connection.cursor()
        self.prints()

    def add_habit(self,auth_token, habit):
        try:
            self.cursor.execute("""
                INSERT INTO habits (user_id, name, color, period, start_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (auth_token['id'], habit.name, habit.color, habit.period, habit.date_start))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=404, detail="Поле не найдено")
        return {"Success": True}

    def edit_habit(self, auth_token, column, value, where_column, where_value):
        try:
            print(where_value)
            self.cursor.execute (f"UPDATE habits SET {column} = %s WHERE {where_column} = %s, user_id = %s", (value, where_value, auth_token['id']))
        except psycopg2.Error as e:
            print(e)
            raise HTTPException(status_code=404, detail="Поле не найдено")
        return {"Success": True}

    def print_table(self, name):
        self.cursor.execute(f"SELECT * FROM {name}")
        data = self.cursor.fetchall()
        for el in data:
            print(el)

    def prints(self):
        self.print_table("habits")
        print("-----------------")
        self.print_table("check_ins")
        print("-----------------")
        self.print_table("users")
        print("-----------------")

    def read_table(self, auth_token: dict, read_column:str, where_column:str|None = None, value:str|None = None):
        try:
            if read_column == "*" and where_column == None:
                self.cursor.execute("SELECT * FROM habits where user_id = %s", (auth_token['id'],))
            elif read_column == "*" and where_column:
                self.cursor.execute(f"SELECT * FROM habits WHERE {where_column} = %s, user_id = %s", (value, auth_token['id']))
            elif not where_column and not value:
                self.cursor.execute(f"SELECT {read_column} FROM habits user_id = %s", (auth_token['id'],))
            else:
                self.cursor.execute(f"SELECT {read_column} FROM habits WHERE {where_column} = %s, user_id = %s",(value, auth_token['id']))
            data = self.cursor.fetchall()
        except psycopg2.Error:
            raise HTTPException(status_code=404, detail="Поле не найдено")
    
        return data

    def delete_habit(self, auth_token, column, value):
        try:
            self.cursor.execute(f'DELETE FROM habits WHERE {column} = %s, user_id = %s', (value, auth_token['id']))
        except psycopg2.Error:
            raise HTTPException(status_code=404, detail="Поле не найдено")
        return {"Success": True}

    def add_check_in(self, auth_token, habit_id, datetime):
        try:
            self.cursor.execute('select check_datetime from check_ins where habit_id = %s, user_id = %s',(habit_id, auth_token['id']))
            data = self.cursor.fetchall()
            dates = []
            for el in data:
                dates.append((el[0][0:8:1]))
            if datetime[0:8:1] in dates:
                raise HTTPException(status_code=409, detail="Отметка уже существует")
            self.cursor.execute("""INSERT INTO check_ins(habit_id, check_datetime, user_id) VALUES(%s, %s, %s)""", (habit_id, datetime, auth_token['id']))
        except psycopg2.Error:
            raise HTTPException(status_code=404, detail="Поле не найдено")
        return {"Success": True}

    def delete_check_in(self, auth_token, habit_id, check_datetime):
        try:
            self.cursor.execute('DELETE FROM check_ins WHERE habit_id = %s AND check_datetime = %s AND user_id = %s', (habit_id, check_datetime, auth_token['id']))
        except psycopg2.Error:
            raise HTTPException(status_code=404, detail="Поле не найдено")
        return {"Success": True}

    def select_history(self, auth_token, habit_id, date_from, date_to):
        try:
            self.cursor.execute('select check_datetime from check_ins where check_datetime between %s and %s and habit_id = %s and user_id = %s',
                        (date_from, date_to, habit_id, auth_token['id']))
        except psycopg2.Error:
            raise HTTPException(status_code=404, detail="Поле не найдено")
        data = self.cursor.fetchall()
    
        dates= []
        for el in data:
            a = datetime.datetime.strptime(el[0], '%d-%m-%y %H:%M')
            dates.append(a)
        current_streak, max_streak = utils.calculate_streaks(dates)
    
        return {'check datetime': data, 'count of check': len(data),
                'current streak': current_streak, 'max streak': max_streak}

    def add_user(self, user):
        print(str(user.hash_password))
        hash_password = auth.utils.hash_password(str(user.hash_password))
        self.cursor.execute("INSERT INTO users(username, hash_password, email, active, last_online, role) values(%s,%s,%s,%s,%s,%s)",(user.username, hash_password, user.email, user.active, user.last_online, user.role))
        return {"Success": "True"}


db = Database(user='admin', password='380251Max!', host='127.0.0.1', port=50500)