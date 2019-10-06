# -*- coding: utf-8 -*-

import sys
from importlib import reload

reload(sys)
# sys.setdefaultencoding('utf-8')

import telebot
from telebot import types
from telebot.types import Message
import mysql.connector
import time
import math
import json

bot = telebot.TeleBot("649733406:AAF76MqAsMbZUJspvf-4JtrI6p99qRP2H7g")

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database='clarabot'
)

db = mydb.cursor()


def select_all_users():
    query = "SELECT * FROM tb_users"
    db.execute(query)
    result = db.fetchall()
    return result


def get_user(chat_id):
    query = "SELECT * FROM tb_users WHERE chat_id =" + str(chat_id)
    db.execute(query)
    result = db.fetchone()
    return result


def check_user(chat_id):
    query = "SELECT id FROM tb_users WHERE chat_id =" + str(chat_id)
    db.execute(query)
    result = db.fetchone()
    return result


def insert_user(username, chat_id):
    query = "INSERT INTO tb_users (username, chat_id) VALUES (%s, %s)"
    val = (username, chat_id)
    db.execute(query, val)
    mydb.commit()


def insert_step(chat_id, step_number):
    query = "INSERT INTO tb_steps (chat_id, step_number) VALUES (%s, %s)"
    val = (chat_id, step_number)
    db.execute(query, val)
    mydb.commit()


def insert_user_data(chat_id, user_id):
    query = "INSERT INTO tb_user_data (user_id, chat_id) VALUES (%s, %s)"
    val = (user_id, chat_id)
    db.execute(query, val)
    mydb.commit()


def update_user_data(chat_id, column, value):
    db.execute("UPDATE tb_user_data SET " + str(column) + " = " + str(value) + " WHERE chat_id =" + str(chat_id))
    mydb.commit()


def update_step(chat_id, step_number):
    db.execute("UPDATE tb_steps SET step_number =" + str(step_number) + " WHERE chat_id =" + str(chat_id))
    mydb.commit()


def get_current_step(chat_id):
    query = "SELECT step_number FROM tb_steps WHERE chat_id =" + str(chat_id)
    db.execute(query)
    result = db.fetchone()
    return result[0]


def send_msg(chat_id, message):
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1)
    bot.send_message(chat_id, message)


def send_settings(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Информация')
    itembtn2 = types.KeyboardButton('Перезагрузка')
    markup.add(itembtn1, itembtn2)
    bot.send_message(chat_id, "Настройки", reply_markup=markup)


def send_msg_array(chat_id, message):
    for text in message:
        count = len(text)
        if count < 20:
            interval = 1
        else:
            interval = math.floor(count / 20)

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(interval)
        bot.send_message(chat_id, text)


def send_btn_array(chat_id, buttons, last_text):
    markup = types.ReplyKeyboardMarkup(True, True)
    for btn in buttons:
        markup.row(btn)
    bot.send_message(chat_id, last_text, reply_markup=markup)


welcome_message = '. Меня зовут Клара и я могу вычислить количетво потраченных калорий на основе ваших данных'


@bot.message_handler(commands=['start'])
def handle_start(message):
    if check_user(message.chat.id) == None:
        insert_user(message.chat.username, message.chat.id)
        id = db.lastrowid
        insert_user_data(message.chat.id, id)
        insert_step(message.chat.id, 0)
        send_btn_array(message.chat.id, ['Расчитать потраченные калории'],
                       'Привет ' + message.chat.first_name + welcome_message)


@bot.message_handler(content_types=['text'])
def send_message_handler(message):
    try:

        if "Расчитать потраченные калории" in message.text and get_current_step(message.chat.id) == 0:
            update_step(message.chat.id, 1)
            send_msg_array(message.chat.id, ['Поехали', 'Введите ваши данные:', 'Ваш вес? (в кг):'])
        elif message.text.isdigit() and get_current_step(message.chat.id) == 1:
            update_user_data(message.chat.id, "weight", message.text)
            update_step(message.chat.id, 2)
            send_msg_array(message.chat.id, ['Отлично!', 'Теперь введите ваш рост (в см):'])
        elif message.text.isdigit() and get_current_step(message.chat.id) == 2:
            update_user_data(message.chat.id, "growth", message.text)
            update_step(message.chat.id, 3)
            send_msg_array(message.chat.id, ['Отлично!', 'Теперь укажите ваш возраст:'])
        elif message.text.isdigit() and get_current_step(message.chat.id) == 3:
            update_user_data(message.chat.id, "age", message.text)
            update_step(message.chat.id, 4)
            send_msg_array(message.chat.id, ['Да у вас еще вся жизнь впереди!', 'Ок', 'Теперь'])
            send_btn_array(message.chat.id, ['Мужской', 'Женский'], 'Ваш пол: ')
        elif get_current_step(message.chat.id) == 4:
            if message.text == 'Мужской':
                update_user_data(message.chat.id, "gender", 1)
            elif message.text == 'Женский':
                update_user_data(message.chat.id, "gender", 0)
            update_step(message.chat.id, 5)
            send_msg_array(message.chat.id, ['Ок', 'Теперь'])
            send_btn_array(message.chat.id, ['Бег', 'Ходьба'], 'Выберите тип занятия:')
        elif get_current_step(message.chat.id) == 5:
            if message.text == 'Бег':
                send_msg_array(message.chat.id,
                               ['Хороший тип занятия', 'Как говориться: Если хочешь быть красивым, то бегай)', 'Ок',
                                'Теперь укажите сколько километров вы пробегали'])
                update_step(message.chat.id, 6)
            elif message.text == 'Ходьба':
                send_msg_array(message.chat.id, ['Ок', 'Теперь укажите растояние (в км)'])
                update_step(message.chat.id, 7)
        elif get_current_step(message.chat.id) == 6 and message.text.isdigit():
            km = int(message.text) * int(320)
            send_msg_array(message.chat.id, ['Вы потратили примерно ' + str(km) + ' калорий'])
        elif get_current_step(message.chat.id) == 7 and message.text.isdigit():
            km = int(message.text) * int(200)
            send_msg_array(message.chat.id, ['Вы потратили примерно ' + str(km) + ' калорий'])
    except Exception as e:
        print(e)


# @bot.message_handler(lambda message: get_current_step(message.chat.id) == 2, content_types=['text'])
# def qwe(message):
#     send_msg(message.chat.id, "Success")

bot.polling(timeout=60)