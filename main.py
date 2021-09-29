import telebot
from telebot import types

bot = telebot.TeleBot("1929596335:AAEntMJTwm9v7vsguWRNxiwoYcMFYUYrx-o")


@bot.message_handler(commands=["start"])
def welcome(message):
    keyBoard = telebot.types.ReplyKeyboardMarkup()
    keyBoard.add(telebot.types.KeyboardButton(text="Записаться"), telebot.types.KeyboardButton(text="Посмотреть запись"))
    msg = bot.send_message(message.chat.id, "Добро пожаловать в нашу клинику", reply_markup=keyBoard)
    print(msg.text)
    bot.register_next_step_handler(msg, switch)


def switch(message):
    try:
        chat_id = message.chat.id
        if message.text == "Записаться":
            appointments(message.chat.id)
        else:
            pass
            # дополнить
    except Exception as e:
        print(str(e))


def appointments(chat_id):
    keyBoard = telebot.types.ReplyKeyboardMarkup()
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


def doctor_appointments(chat_id):
    print("хаха")




def datetime_appointments(chat_id):
    pass
# @bot.message_handler(content_types=["text"])
# def answer(message):
#     print(message.chat.id)
#     print(message.text)
#     bot.send_message(524397584, "Вы Вова ")
#     if message.text == "Записаться":
#         bot.send_message(message.chat.id, text="Выберите время", reply_markup=keyBoard)
#
#         @bot.callback_query_handler(func=lambda call: True)
#         def query_handler(call):
#             bot.answer_callback_query(callback_query_id=call.id, text='Вы успешно записались на прием')
#             bot.send_message(call.message.chat.id, "Вы были записанны на " + call.data)

# @bot.callback_query_handler(func=lambda call: True)
# def query_handler(call):
#     bot.answer_callback_query(callback_query_id=call.id, text='Вы успешно записались на прием')
#     bot.send_message(call.message.chat.id, "Вы были записанны на " + call.data)


bot.polling(none_stop=True)

