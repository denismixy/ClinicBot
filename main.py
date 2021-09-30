import telebot
from telebot import types
import database
import config
import re

'''
Copyright "PARTY ON BAAAAAD"
Donate please on SBERBANK ONLINE 89964007036, NOT LESS 300$
FUCKING SLAVES
STICK UR FINGER IN MY ASS
'''

bot = telebot.TeleBot(config.bottoken)


@bot.message_handler(commands=["start"])
def welcome(message: types.Message) -> None:
    bot.send_message(message.chat.id, "Добро пожаловать в нашу клинику")
    start_menu(message)


def start_menu(message: types.Message) -> None:
    key_board = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_board.add(telebot.types.KeyboardButton(text="Записаться"),
                  telebot.types.KeyboardButton(text="Посмотреть запись"))
    msg = bot.send_message(message.chat.id, "Выберите пункт", reply_markup=key_board)
    bot.register_next_step_handler(msg, switch)


def switch(message: types.Message) -> None:
    try:
        if message.text == "Записаться":
            appointments(message)
        elif message.text == "Посмотреть запись":
            bot.send_message(message.chat.id, database.show_client_note(message.from_user.id))
            start_menu(message)
            # дополнить
    except Exception as e:
        print(str(e))


def appointments(message: types.Message) -> None:
    key_board = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_board.add(telebot.types.KeyboardButton(text="Я знаю своего врача"),
                  telebot.types.KeyboardButton(text="Я не знаю своего врача"))
    msg = bot.send_message(message.chat.id, "Выберите", reply_markup=key_board)
    bot.register_next_step_handler(msg, switch_appointments)


def switch_appointments(message: types.Message) -> None:
    if message.text == "Я знаю своего врача":
        doctor_appointments(message)
    else:
        datetime_appointments(message)


# Выбор врача, даты и времени 
def doctor_appointments(message: types.Message) -> None:
    note = Note(message.from_user.id)

    if database.check_client_note(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы уже записаны')
        start_menu(message)
        return

    def choose_doctor(message: types.Message) -> None:
        doctors = database.show_doctors()
        key_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in doctors:
            key_board.add(name)
        msg = bot.send_message(message.chat.id, 'Выберите врача', reply_markup=key_board)
        bot.register_next_step_handler(msg, choose_day)

    def choose_day(message: types.Message) -> None:
        chat_id = message.chat.id
        days = ['01.10', '02.10', '03.10', '04.10', '05.10']  # select from DB ERROR
        key_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for day in days:
            key_board.add(day)
        msg = bot.send_message(chat_id, 'Выберите день приема', reply_markup=key_board)
        note.doctor = message.text
        bot.register_next_step_handler(msg, choose_time)

    def choose_time(message: types.Message) -> None:
        chat_id = message.chat.id
        times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00"]  # select from DB ERROR
        key_board = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for hour in times:
            key_board.add(hour)
        note.date = message.text
        msg = bot.send_message(chat_id, 'Выберите время приема', reply_markup=key_board)
        bot.register_next_step_handler(msg, send_database)

    def send_database(message: types.Message) -> None:
        note.hour = message.text
        database.add_note(note)
        data_input(message)

    choose_doctor(message)


# just for fun
def datetime_appointments(message: types.Message) -> None:
    note = Note(message.from_user.id)

    if database.check_client_note(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы уже записаны')
        start_menu(message)
        return

    def choose_day(message: types.Message) -> None:
        chat_id = message.chat.id
        days = ['01.10', '02.10', '03.10', '04.10', '05.10']  # select from DB ERROR
        key_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for day in days:
            key_board.add(day)
        msg = bot.send_message(chat_id, 'Выберите день приема', reply_markup=key_board)
        bot.register_next_step_handler(msg, choose_time)

    def choose_time(message: types.Message) -> None:
        chat_id = message.chat.id
        times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00"]  # select from DB ERROR
        key_board = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for hour in times:
            key_board.add(hour)
        note.date = message.text
        msg = bot.send_message(chat_id, 'Выберите время приема', reply_markup=key_board)
        bot.register_next_step_handler(msg, choose_doctor)
    
    def choose_doctor(message: types.Message) -> None:
        doctors = database.show_doctors()
        key_board = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for name in doctors:
            key_board.add(name)
        note.hour = message.text
        msg = bot.send_message(message.chat.id, 'Выберите врача', reply_markup=key_board)
        bot.register_next_step_handler(msg, send_database)


    def send_database(message: types.Message) -> None:
        note.doctor = message.text
        database.add_note(note)
        data_input(message)

    choose_day(message)    

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
        
        # check = re.match('^(\d{2}|\d{1}).(\d{2}|\d{1}).(\d{4})$', message.text)
        # if check == None:
        #     bot.send_message(chat_id, 'Вы ввели некорректное ФИО')
        #     input_name(message)
        #     return
        if client.name == 'NULL':
            client.name = message.text
        msg = bot.send_message(chat_id, 'Введите день рождения')
        bot.register_next_step_handler(msg, input_tel_number)

    def input_tel_number(message: types.Message) -> None:
        chat_id = message.chat.id
        if client.birthday == 'NULL':
            check_date = re.match('^(\d{2}|\d{1})\.(\d{2}|\d{1})\.(\d{4})$', message.text) # Переделать валидатор
            if check_date == None:
                bot.send_message(chat_id, 'Вы ввели некорректную дату рождения')
                bot.send_message(chat_id, 'Пример: дд.мм.гггг')
                input_birthday(message) 
                return   
        if client.birthday == 'NULL':
            client.birthday = message.text
        msg = bot.send_message(chat_id, 'Введите тел. номер')
        bot.register_next_step_handler(msg, input_other_info)

    def input_other_info(message: types.Message) -> None:
        chat_id = message.chat.id
        if client.tel_num == 'NULL':
            check_tel = re.match('^(\+7|7|8){1}\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$', message.text)
            if check_tel == None:
                bot.send_message(chat_id, 'Вы ввели некорректный номер телефона')
                input_tel_number(message)
                return
        if client.tel_num == 'NULL':
            client.tel_num = message.text
        msg = bot.send_message(chat_id, 'Введите доп. инфо')
        bot.register_next_step_handler(msg, send_client_info)

    def send_client_info(message: types.Message) -> None:
        client.other_info = message.text
        database.add_client(client)
        bot.send_message(message.chat.id, 'Запись на прием успешно завершена')
        start_menu(message)

    input_name(message)


class Client:
    def __init__(self, client_id, name='NULL', birthday='NULL', tel_num='NULL', other_info='NULL'):
        self.client_id = client_id
        self.name = name
        self.birthday = birthday
        self.tel_num = tel_num
        self.other_info = other_info


class Note:
    def __init__(self, client_id, doctor='NULL', date='NULL', hour='NULL'):
        self.client_id = client_id
        self.doctor = doctor
        self.date = date
        self.hour = hour


bot.polling(none_stop=True)
