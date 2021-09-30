import telebot
from telebot import types
import database
import config

bot = telebot.TeleBot(config.bottoken)

@bot.message_handler(commands=["start"])
def welcome(message: types.Message) -> None:
  bot.send_message(message.chat.id, "Добро пожаловать в нашу клинику")
  start_menu(message)

def start_menu(message: types.Message) -> None:
    keyBoard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyBoard.add(telebot.types.KeyboardButton(text="Записаться"), telebot.types.KeyboardButton(text="Посмотреть запись"))
    msg = bot.send_message(message.chat.id, "Выберите пункт", reply_markup=keyBoard)
    bot.register_next_step_handler(msg, switch)
 
 
def switch(message: types.Message) -> None:
    try:
        if message.text == "Записаться":
            appointments(message)
        elif message.text == "Посмотреть запись":
            bot.send_message(message.chat.id, database.show_client_note(message.from_user.id))
            start_menu(message)
            # дополнить
    except (Exception):
        print(str(Exception))
 
 
def appointments(message: types.Message) -> None:
    keyBoard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyBoard.add(telebot.types.KeyboardButton(text="Я знаю своего врача"),
                 telebot.types.KeyboardButton(text="Я не знаю своего врача"))
    msg = bot.send_message(message.chat.id, "Выберите", reply_markup=keyBoard)
    bot.register_next_step_handler(msg, switchAppointments)
 
 
def switchAppointments(message: types.Message) -> None:
    if message.text == "Я знаю своего врача":
        doctor_appointments(message)
    else:
        datetime_appointments(message)
 

# Выбор врача, даты и времени 
def doctor_appointments(message: types.Message) -> None:
  choice_made = []

  if database.check_client_note(message.from_user.id):
    bot.send_message(message.chat.id, 'Вы уже записаны')
    start_menu(message)
    return

  def choose_doctor(message: types.Message) -> None:
    doctors = database.show_doctors()
    keyBoard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in doctors:
      keyBoard.add(name)
    msg = bot.send_message(message.chat.id, 'Выберите врача', reply_markup=keyBoard)
    bot.register_next_step_handler(msg, choose_day)

  def choose_day(message: types.Message) -> None:
    chat_id = message.chat.id
    days = ['01.10', '02.10', '03.10', '04.10', '05.10'] # select from DB ERROR
    keyBoard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for day in days:
      keyBoard.add(day)
    msg = bot.send_message(chat_id, 'Выберите день приема', reply_markup=keyBoard)
    choice_made.append(message.from_user.id)
    choice_made.append(message.text)
    bot.register_next_step_handler(msg, choose_time)
    
  def choose_time(message: types.Message) -> None:
    chat_id = message.chat.id
    times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00"] # select from DB ERROR
    keyBoard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for hour in times:
      keyBoard.add(hour)
    choice_made.append(message.text)
    msg = bot.send_message(chat_id, 'Выберите время приема', reply_markup=keyBoard)
    bot.register_next_step_handler(msg, send_database)

  def send_database(message: types.Message) -> None:
    choice_made.append(message.text)
    database.add_note(choice_made)
    data_input(message)


  choose_doctor(message)

# Ввод данных пользователя  
def data_input(message: types.Message) -> None:
  client = Client(message.from_user.id)
  if database.check_client_info(message.from_user.id):
    bot.send_message(message.chat.id, database.show_client_info(message.from_user.id))
    bot.send_message(message.chat.id, 'Запись на прием успешно завершена')
    start_menu(message)
    return

  def input_name(message: types.Message) -> None:
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Введите ФИО')
    bot.register_next_step_handler(msg, input_birthday)

  def input_birthday(message: types.Message) -> None:
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Введите день рождения')
    client.name = message.text
    bot.register_next_step_handler(msg, input_tel_number)

  def input_tel_number(message: types.Message) -> None:
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Введите тел. номер')
    client.birthday = message.text
    bot.register_next_step_handler(msg, input_other_info)

  def input_other_info(message: types.Message) -> None:
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Введите доп. инфо')
    client.tel_num = message.text
    bot.register_next_step_handler(msg, send_client_info)

  def send_client_info(message: types.Message) -> None:
    client.other_info = message.text
    database.add_client(client)
 
  input_name(message)
 
 
def datetime_appointments(message: types.Message) -> None:
    pass


class Client:
  def __init__(self, client_id, name='NULL', birthday='NULL', tel_num='NULL', other_info='NULL'):
    self.client_id = client_id
    self.name = name
    self.birthday = birthday
    self.tel_num = tel_num
    self.other_info = other_info 

bot.polling(none_stop=True)