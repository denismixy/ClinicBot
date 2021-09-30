import datetime
import telebot
from telebot import types
import database

bot = telebot.TeleBot('')

@bot.message_handler(commands=["start"])
def welcome(message):
    keyBoard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyBoard.add(telebot.types.KeyboardButton(text="Записаться"), telebot.types.KeyboardButton(text="Посмотреть запись"))
    msg = bot.send_message(message.chat.id, "Добро пожаловать в нашу клинику", reply_markup=keyBoard)
    print(msg.text)
    bot.register_next_step_handler(msg, switch)
 
 
def switch(message):
    try:
        chat_id = message.chat.id
        if message.text == "Записаться":
            appointments(message.chat.id)
        elif message.text == "Посмотреть запись":
            bot.send_message(message.chat.id, database.show_client_note(message.from_user.id))
            welcome(message)
            # дополнить
    except Exception as e:
        print(str(e))
 
 
def appointments(chat_id):
    keyBoard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyBoard.add(telebot.types.KeyboardButton(text="Я знаю своего врача"),
                 telebot.types.KeyboardButton(text="Я не знаю своего врача"))
    msg = bot.send_message(chat_id, "Выберите", reply_markup=keyBoard)
    bot.register_next_step_handler(msg, switchAppointments)
 
 
def switchAppointments(message):
    chat_id = message.chat.id
    if message.text == "Я знаю своего врача":
        doctor_appointments(chat_id)
    else:
        datetime_appointments(chat_id)
 

# Выбор врача, даты и времени 
def doctor_appointments(chat_id):
  choice_made = []

  def choose_doctor(chat_id):
    doctors = database.show_doctors()
    keyBoard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in doctors:
      keyBoard.add(name)
    msg = bot.send_message(chat_id, 'Choose a doctor', reply_markup=keyBoard)
    bot.register_next_step_handler(msg, choose_day)

  def choose_day(message):
    chat_id = message.chat.id
    days = ['Mon', 'Tue', 'Wed'] # select from DB ERROR
    keyBoard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for day in days:
      keyBoard.add(day)
    msg = bot.send_message(chat_id, 'Choose a day', reply_markup=keyBoard)
    choice_made.append(message.from_user.id)
    choice_made.append(message.text)
    bot.register_next_step_handler(msg, choose_time)
    
  def choose_time(message):
    chat_id = message.chat.id
    times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00"] # select from DB ERROR
    keyBoard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for hour in times:
      keyBoard.add(hour)
    #choice_made.append(msg)
    choice_made.append(message.text)
    msg = bot.send_message(chat_id, 'Choose a hour', reply_markup=keyBoard)
    bot.register_next_step_handler(msg, send_database)

  def send_database(message):
    choice_made.append(message.text)

    print(choice_made)
    database.add_note(choice_made)
    data_input(message)


  choose_doctor(chat_id)

# Ввод данных пользователя  
def data_input(message):
  client = Client(message.from_user.id)

  def input_name(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Input FIO')
    bot.register_next_step_handler(msg, input_birthday)

  def input_birthday(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Input birthday')
    client.name = message.text
    bot.register_next_step_handler(msg, input_telnumber)

  def input_telnumber(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Input telnum')
    client.birthday = message.text
    bot.register_next_step_handler(msg, input_otherinfo)

  def input_otherinfo(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Input other info')
    client.tel_num = message.text
    bot.register_next_step_handler(msg, send_client_info)

  def send_client_info(message):
    client.other_info = message.text

    print(client)
    database.add_client(client)
 
  input_name(message)
 
 
def datetime_appointments(chat_id):
    pass


class Client:
  def __init__(self, client_id, name='NULL', birthday='NULL', tel_num='NULL', other_info='NULL'):
    self.client_id = client_id
    self.name = name
    self.birthday = birthday
    self.tel_num = tel_num
    self.other_info = other_info 

bot.polling(none_stop=True)