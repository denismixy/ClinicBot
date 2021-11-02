import re
import database
import properties
from datetime import date
import datetime
from enums import Keys

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# configure and run bot
property_file = properties.Properties("config.json")
bot: Bot = Bot(property_file.get_property("bot_token"))
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)


class Menu(StatesGroup):
    start_menu = State()
    keyboard_menu = State()
    check_appointment = State()
    switch_check_appointment = State()
    sign_up = State()
    switch_sign_up = State()
    show_appointment = State()
    choice_search_method = State()
    switch_choice_search_method = State()
    switch_show_appointment = State()
    choose_doctor = State()


class Appointment(StatesGroup):
    know_doctor = State()
    dont_know_doctor = State()
    dont_know_date = State()
    set_doctor = State()
    set_date = State()
    set_time = State()
    dont_know_set_time = State()
    add_appointment = State()


class ClientInfo(StatesGroup):
    ShowInfo = State()
    AcceptInfo = State()
    ChangeInfo = State()
    Name = State()
    ValidateName = State()
    Birthday = State()
    ValidateBirthday = State()
    PhoneNumber = State()
    ValidateNumber = State()
    OtherInfo = State()
    SwitchOtherInfo = State()
    FinallyChecker = State()
    GetInfo = State()


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [Keys.back, Keys.cancel]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda msg: msg.text == "Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await Menu.start_menu.set()
    await start_menu(message, state)


@dp.message_handler(lambda msg: msg.text == "Назад", state="*")
async def back(message: types.Message, state: FSMContext):
    dictionary: dict = await state.get_data()
    list_state: list = dictionary["list_state"]
    list_state.pop()
    settable_state = list_state.pop()
    await state.set_state(settable_state)
    await state.update_data(list_state=list_state)
    list_function: list = dictionary["list_function"]
    list_function.pop()
    called_function_name = list_function.pop()
    if "Menu:choice_search_method" in list_state:
        await state.update_data(tel_num="click on back button")
    await state.update_data(list_function=list_function)
    await called_function_name(message, state)


async def update_function_list(state: FSMContext, function_name: str):
    dictionary = await state.get_data()
    list_function = dictionary["list_function"]
    if function_name not in list_function:
        list_function.append(function_name)
    await state.update_data(list_function=list_function)


async def update_state_list(state: FSMContext):
    dictionary = await state.get_data()
    list_state: list = dictionary["list_state"]
    state_name = await state.get_state()
    if state_name not in list_state:
        list_state.append(await state.get_state())
    await state.update_data(list_state=list_state)


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в нашу клинику")
    await Menu.start_menu.set()
    await start_menu(message, state)


@dp.message_handler(state=Menu.start_menu)
async def start_menu(message: types.Message, state: FSMContext):
    await state.reset_data()
    await state.update_data(list_state=[])
    await state.update_data(list_function=[])
    name_current_function = start_menu
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [
        types.KeyboardButton("Записаться к врачу"),
        types.KeyboardButton("Посмотреть запись")
    ]
    keyboard.add(*buttons)
    await message.answer("Выберите действие", reply_markup=keyboard)
    await Menu.keyboard_menu.set()


@dp.message_handler(state=Menu.keyboard_menu)
async def switch_start_menu(message: types.Message, state: FSMContext):
    print(message.chat.id, datetime.datetime.now(), await state.get_data("list_state"))
    if message.text == "Записаться к врачу":
        await state.update_data(choice_start_menu="Записаться к врачу")
        await ClientInfo.PhoneNumber.set()
        await request_phone(message, state)
    elif message.text == "Посмотреть запись":
        await state.update_data(choice_start_menu="Посмотреть запись")
        # TODO провервка на админа
        if True:
            await Menu.choice_search_method.set()
            await choice_search_method(message, state)
            return
        else:
            await ClientInfo.PhoneNumber.set()
            await request_phone(message, state)


@dp.message_handler(state=Menu.choice_search_method)
async def choice_search_method(message: types.Message, state: FSMContext):
    print(message.chat.id, datetime.datetime.now(), await state.get_data("list_state"))
    name_current_function = choice_search_method
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [
        types.KeyboardButton("Поиск по номеру"),
        types.KeyboardButton("Поиск по дате"),
        types.KeyboardButton("Назад"),
        types.KeyboardButton("Отмена")
    ]
    keyboard.add(*buttons)
    await Menu.switch_choice_search_method.set()
    await message.answer("Выберите действие", reply_markup=keyboard)


@dp.message_handler(state=Menu.switch_choice_search_method)
async def switch_choice_search_method(message: types.Message, state: FSMContext):
    if message.text == "Поиск по номеру":
        await ClientInfo.PhoneNumber.set()
        await request_phone(message, state)
    else:
        await Menu.sign_up.set()
        await sign_up(message, state)


# Обработка телефонного номера
@dp.message_handler(state=ClientInfo.PhoneNumber)
async def request_phone(message: types.Message, state: FSMContext):
    name_current_function = request_phone
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    await message.answer("Введите номер телефона", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateNumber.set()


@dp.message_handler(lambda message: re.match(r'^(\+7|7|8)\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$',
                                             message.text) is None,
                    state=ClientInfo.ValidateNumber)
async def wrong_phone(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод номера телефона")
    await ClientInfo.PhoneNumber.set()
    await request_phone(message, state)


@dp.message_handler(lambda message: re.match(r'^(\+7|7|8)\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$',
                                             message.text) is not None,
                    state=ClientInfo.ValidateNumber)
async def correct_phone(message: types.Message, state: FSMContext):
    await state.update_data(tel_num=message.text)
    dictionary: dir = await state.get_data()
    if dictionary["choice_start_menu"] == "Записаться к врачу":
        await Menu.check_appointment.set()
        await check_appointment(message, state)
    else:
        await Menu.show_appointment.set()
        await show_appointment(message, state)


@dp.message_handler(state=Menu.show_appointment)
async def show_appointment(message: types.Message, state: FSMContext):
    name_current_function = show_appointment
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    dictionary: dict = await state.get_data()
    if not database.check_client_appointment(dictionary["tel_num"]):
        await message.answer("Вы не записывались в клинику")
        await Menu.start_menu.set()
        await start_menu(message, state)
        return
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="Удалить запись"),
        types.KeyboardButton(text=Keys.back)
    ]
    keyboard.add(*buttons)
    await message.answer(database.show_client_appointment(dictionary["tel_num"]), reply_markup=keyboard)
    await Menu.switch_show_appointment.set()


@dp.message_handler(state=Menu.switch_show_appointment)
async def switch_show_appointment(message: types.Message, state: FSMContext):
    print(message.chat.id, datetime.datetime.now(), await state.get_data("list_state"))
    dictionary: dict = await state.get_data()
    if message.text == "Удалить запись" and database.check_access(message.chat.id, dictionary["tel_num"]):
        database.del_appointment(dictionary["tel_num"])
        await message.answer("Запись успешно удалена")
    else:
        await message.answer("У вас недостаточно прав для удаления этой записи")
    await Menu.start_menu.set()
    await start_menu(message, state)


@dp.message_handler(state=Menu.check_appointment)
async def check_appointment(message: types.Message, state: FSMContext):
    dictionary: dict = await state.get_data()
    if not database.check_client_appointment(dictionary["tel_num"]):
        await Menu.sign_up.set()
        await sign_up(message, state)
    else:
        name_current_function = check_appointment
        await update_function_list(state, name_current_function)
        await update_state_list(state)
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = [
            types.KeyboardButton(text="Хочу перезаписаться"),
            types.KeyboardButton(text="Назад")
        ]
        keyboard.add(*buttons)
        await Menu.switch_check_appointment.set()
        await message.answer("Вы уже записаны", reply_markup=keyboard)


@dp.message_handler(state=Menu.switch_check_appointment)
async def switch_check_appointment(message: types.Message, state: FSMContext):
    dictionary: dict = await state.get_data()
    if message.text == "Хочу перезаписаться" and database.check_access(message.chat.id, dictionary["tel_num"]):
        await Menu.sign_up.set()
        await sign_up(message, state)
    else:
        await message.answer("У вас недостаточно прав для удаления этой записи")
        await Menu.start_menu.set()
        await start_menu(message, state)


@dp.message_handler(state=Menu.sign_up)
async def sign_up(message: types.Message, state: FSMContext):
    name_current_function = sign_up
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="Я знаю врача"),
        types.KeyboardButton(text="Я не знаю врача"),
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отмена")
    ]
    keyboard.add(*buttons)
    await Menu.switch_sign_up.set()
    await message.answer("Выберите вариант", reply_markup=keyboard)


@dp.message_handler(state=Menu.switch_sign_up)
async def switch_sign_up(message: types.Message, state: FSMContext):
    print(message.chat.id, datetime.datetime.now(), await state.get_data("list_state"))
    if message.text == "Я знаю врача":
        await Appointment.know_doctor.set()
        await choose_doctor(message, state)
    elif message.text == "Я не знаю врача":
        await Appointment.dont_know_doctor.set()
        await dont_know_choose_date(message, state)


@dp.message_handler(state=Appointment.dont_know_doctor)
async def dont_know_choose_date(message: types.Message, state: FSMContext):
    name_current_function = dont_know_choose_date
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="01.10", callback_data="01.10"),
        types.InlineKeyboardButton(text="02.10", callback_data="02.10"),
        types.InlineKeyboardButton(text="03.10", callback_data="03.10"),
        types.InlineKeyboardButton(text="04.10", callback_data="04.10"),
        types.InlineKeyboardButton(text="05.10", callback_data="05.10"),
        types.InlineKeyboardButton(text="06.10", callback_data="06.10")
    ]
    keyboard.add(*buttons)
    await message.answer("📅", reply_markup=cancel_keyboard())
    await message.answer("Выберите дату", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.dont_know_doctor)
async def dont_know_callback_choose_date(call: types.CallbackQuery, state: FSMContext):
    print(call.from_user.id, datetime.datetime.now(), await state.get_data("list_state"))
    if re.match(r'\d\d\.\d\d', call.data) is None:
        await call.answer()
        await dont_know_choose_date(call.message, state)
        return
    await call.message.delete_reply_markup()
    await call.message.edit_text("Дата записи: " + call.data)
    await call.answer()
    await state.update_data(date=call.data)
    await Appointment.dont_know_date.set()
    await dont_know_choose_time(call.message, state)


@dp.message_handler(state=Appointment.dont_know_date)
async def dont_know_choose_time(message: types.Message, state: FSMContext):
    name_current_function = dont_know_choose_time
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    time_keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="00:00", callback_data="00:00"),
        types.InlineKeyboardButton(text="01:00", callback_data="01:00"),
        types.InlineKeyboardButton(text="02:00", callback_data="02:00"),
        types.InlineKeyboardButton(text="03:00", callback_data="03:00"),
        types.InlineKeyboardButton(text="04:00", callback_data="04:00"),
    ]
    time_keyboard.add(*buttons)
    await message.answer("🕒", reply_markup=cancel_keyboard())
    await message.answer("Выберите время", reply_markup=time_keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.dont_know_date)
async def dont_know_callback_choose_time(call: types.CallbackQuery, state: FSMContext):
    print(call.from_user.id, datetime.datetime.now(), await state.get_data("list_state"))
    await call.message.delete_reply_markup()
    if re.match(r'\d\d:\d\d', call.data) is None:
        await call.answer()
        await dont_know_choose_time(call.message, state)
        return
    await call.message.edit_text("Выбранное время: " + call.data)
    await call.answer()
    await state.update_data(time=call.data)
    await Appointment.dont_know_set_time.set()
    await dont_know_choose_doctor(call.message, state)


@dp.message_handler(state=Appointment.dont_know_set_time)
async def dont_know_choose_doctor(message: types.Message, state: FSMContext):
    name_current_function = dont_know_choose_doctor
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    doctors_list = database.show_doctors()
    buttons = []
    for doctor in doctors_list:
        buttons.append(types.InlineKeyboardButton(text=doctor, callback_data=doctor))
    keyboard.add(*buttons)
    await message.answer("👨‍⚕👩‍⚕", reply_markup=cancel_keyboard())
    await message.answer("Выберите одного из доступных врачей", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.dont_know_set_time)
async def dont_know_callback_choose_doctor(call: types.CallbackQuery, state: FSMContext):
    print(call.from_user.id, datetime.datetime.now(), await state.get_data("list_state"))
    if re.match(r'\w*\s\w\.\w\.', call.data) is None:
        await call.answer()
        await dont_know_choose_doctor(call.message, state)
        return
    await call.message.delete_reply_markup()
    await call.message.edit_text("Врач: " + call.data)
    await call.answer()
    await state.update_data(chat_id=call.from_user.id)
    await state.update_data(doctor=call.data)
    await Appointment.set_time.set()
    await send_appointment(call.message, state)


@dp.message_handler(state=Appointment.know_doctor)
async def choose_doctor(message: types.Message, state: FSMContext):
    name_current_function = choose_doctor
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    doctors_list = database.show_doctors()
    buttons = []
    for doctor in doctors_list:
        buttons.append(types.InlineKeyboardButton(text=doctor, callback_data=doctor))
    keyboard.add(*buttons)
    await message.answer("👨‍⚕👩‍⚕", reply_markup=cancel_keyboard())
    await message.answer("Выберите врача", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.know_doctor)
async def callback_choose_doctor(call: types.CallbackQuery, state: FSMContext):
    print(call.from_user.id, datetime.datetime.now(), await state.get_data("list_state"))
    if re.match(r'\w*\s\w\.\w\.', call.data) is None:
        await call.answer()
        await choose_doctor(call.message, state)
        return
    await call.message.delete_reply_markup()
    await call.message.edit_text("Врач: " + call.data)
    await call.answer()
    await state.update_data(chat_id=call.from_user.id)
    await state.update_data(doctor=call.data)
    await Appointment.set_doctor.set()
    await choose_date(call.message, state)


@dp.message_handler(state=Appointment.set_doctor)
async def choose_date(message: types.Message, state: FSMContext):
    name_current_function = choose_date
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="01.10", callback_data="01.10"),
        types.InlineKeyboardButton(text="02.10", callback_data="02.10"),
        types.InlineKeyboardButton(text="03.10", callback_data="03.10"),
        types.InlineKeyboardButton(text="04.10", callback_data="04.10"),
        types.InlineKeyboardButton(text="05.10", callback_data="05.10"),
        types.InlineKeyboardButton(text="06.10", callback_data="06.10")
    ]
    keyboard.add(*buttons)
    await message.answer("📅", reply_markup=cancel_keyboard())
    await message.answer("Выберите дату", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.set_doctor)
async def callback_choose_date(call: types.CallbackQuery, state: FSMContext):
    print(call.from_user.id, datetime.datetime.now(), await state.get_data("list_state"))
    if re.match(r'\d\d\.\d\d', call.data) is None:
        await call.answer()
        await dont_know_choose_date(call.message, state)
        return
    await call.message.delete_reply_markup()
    await call.message.edit_text("Дата записи: " + call.data)
    await call.answer()
    await state.update_data(date=call.data)
    await Appointment.set_date.set()
    await choose_time(call.message, state)


@dp.message_handler(state=Appointment.set_date)
async def choose_time(message: types.Message, state: FSMContext):
    name_current_function = choose_time
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    time_keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="00:00", callback_data="00:00"),
        types.InlineKeyboardButton(text="01:00", callback_data="01:00"),
        types.InlineKeyboardButton(text="02:00", callback_data="02:00"),
        types.InlineKeyboardButton(text="03:00", callback_data="03:00"),
        types.InlineKeyboardButton(text="04:00", callback_data="04:00"),
    ]
    time_keyboard.add(*buttons)
    await message.answer("🕒", reply_markup=cancel_keyboard())
    await message.answer("Выберите время", reply_markup=time_keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.set_date)
async def callback_choose_time(call: types.CallbackQuery, state: FSMContext):
    print(call.from_user.id, datetime.datetime.now(), await state.get_data("list_state"))
    if re.match(r'\d\d:\d\d', call.data) is None:
        await call.answer()
        await choose_time(call.message, state)
        return
    await call.message.delete_reply_markup()
    await call.message.edit_text("Выбранное время: " + call.data)
    await call.answer()
    await state.update_data(time=call.data)
    await Appointment.set_time.set()
    await send_appointment(call.message, state)


@dp.message_handler(state=Appointment.set_time)
async def send_appointment(message: types.Message, state: FSMContext):
    # TODO функционал для бронирования времени
    await Appointment.add_appointment.set()
    await ClientInfo.ShowInfo.set()
    await show_client_info(message, state)


@dp.message_handler(state=ClientInfo.ShowInfo)
async def show_client_info(message: types.Message, state: FSMContext):
    dictionary: dict = await state.get_data()
    try:
        tel_num = dictionary["tel_num"]
        if tel_num == "click on back button":
            raise KeyError
    except KeyError:
        tel_num = database.get_number_by_date_time(dictionary["date"], dictionary["time"], dictionary["doctor"])
        await state.update_data(tel_num=tel_num)

    if tel_num is not None and database.check_client_info(tel_num):
        name_current_function = show_client_info
        await update_function_list(state, name_current_function)
        await update_state_list(state)
        show_info_keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text="Изменить", callback_data="change_info"),
            types.InlineKeyboardButton(text="Принять", callback_data="accept_info")
        ]
        if "Menu:choice_search_method" in dictionary["list_state"]:
            buttons = [
                types.InlineKeyboardButton(text="Удалить", callback_data="delete_info")
            ]
        show_info_keyboard.add(*buttons)
        await message.answer("Персональные данные уже были введены ранее, проверьте их правильность")
        await message.answer(database.show_client_info(tel_num), reply_markup=show_info_keyboard)
    else:
        if "Menu:choice_search_method" in dictionary["list_state"]:
            name_current_function = show_client_info
            await update_function_list(state, name_current_function)
            await update_state_list(state)
            await message.answer("Запись не найдена, попробуйте еще раз")
            await Menu.choice_search_method.set()
            await choice_search_method(message, state)
            return
        await ClientInfo.Name.set()
        await request_name(message, state)


@dp.callback_query_handler(lambda call: True, state=ClientInfo.ShowInfo)
async def switch_callback_client_info(call: types.CallbackQuery, state: FSMContext):
    dictionary: dict = await state.get_data()
    await call.message.delete_reply_markup()
    if call.data == "accept_info":
        await ClientInfo.AcceptInfo.set()
        await accept_client_info(call, state)
    elif call.data == "change_info":
        await call.message.delete()
        await ClientInfo.ChangeInfo.set()
        await change_client_info(call, state)
    elif call.data == "delete_info":
        tel_num = database.get_number_by_date_time(dictionary["date"], dictionary["time"], dictionary["doctor"])
        if tel_num is not None:
            database.del_appointment(tel_num)
            await call.message.answer("Запись удалена")
        else:
            await call.message.answer("Не удалось удалить, попробуйте еще раз")
        await Menu.start_menu.set()
        await start_menu(call.message, state)


async def accept_client_info(call: types.CallbackQuery, state: FSMContext):
    database.add_appointment(await state.get_data())
    await call.message.answer("Запись в клинику прошла успешно\nВсего доброго!")
    await call.answer()
    await state.reset_data()
    await Menu.start_menu.set()
    await start_menu(call.message, state)


async def change_client_info(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Давайте обновим данные📝")
    await call.answer()
    await ClientInfo.Name.set()
    await request_name(call.message, state)


# Обработка ФИО
@dp.message_handler(state=ClientInfo.Name)
async def request_name(message: types.Message, state: FSMContext):
    name_current_function = request_name
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    await message.answer("Введите свое ФИО на русском языке", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateName.set()


@dp.message_handler(lambda message: re.match(r'^[а-яА-Я]+((\s|-)?[а-яА-Я]+)*$', message.text) is None,
                    state=ClientInfo.ValidateName)
async def wrong_name(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод ФИО")
    await ClientInfo.Name.set()
    await request_name(message, state)


@dp.message_handler(lambda message: re.match(r'^[а-яА-Я]+((\s|-)?[а-яА-Я]+)*$', message.text) is not None,
                    state=ClientInfo.ValidateName)
async def correct_name(message: types.Message, state: FSMContext):
    await state.update_data(chat_id=message.from_user.id, name=message.text)
    await ClientInfo.Birthday.set()
    await request_birthday(message, state)


# Обработка даты рождения
@dp.message_handler(state=ClientInfo.Birthday)
async def request_birthday(message: types.Message, state: FSMContext):
    name_current_function = request_birthday
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    await message.answer("Введите дату своего рождения (дд.мм.гггг)", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateBirthday.set()


@dp.callback_query_handler(lambda call: True, state=ClientInfo.ValidateBirthday)
async def callback_request_birthday(call: types.CallbackQuery, state: FSMContext):
    await ClientInfo.Name.set()
    await call.message.delete()
    await request_name(call.message, state)


@dp.message_handler(lambda message: re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text) is None,
                    state=ClientInfo.ValidateBirthday)
async def wrong_format_birthday(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод даты рождения")
    await ClientInfo.Birthday.set()
    await request_birthday(message, state)


@dp.message_handler(lambda message: re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text) is not None,
                    state=ClientInfo.ValidateBirthday)
async def correct_format_birthday(message: types.Message, state: FSMContext):
    res = re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text)
    day, month, year = int(res[1]), int(res[2]), int(res[3])

    # Если дата некорректная (30 февраля, 46 марта etc)
    try:
        py_date = date(year, month, day)
        wrong_data = date.today() < py_date
    except ValueError:
        wrong_data = True

    if wrong_data:
        await wrong_format_birthday(message, state)
        return

    await state.update_data(birthday=message.text)
    await ClientInfo.OtherInfo.set()
    await request_info(message, state)


@dp.message_handler(state=ClientInfo.OtherInfo)
async def request_info(message: types.Message, state: FSMContext):
    name_current_function = request_info
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    await message.answer("Введите доп. информацию", reply_markup=cancel_keyboard())
    await ClientInfo.FinallyChecker.set()


@dp.message_handler(state=ClientInfo.FinallyChecker)
async def previously_request_info(message: types.Message, state: FSMContext):
    name_current_function = previously_request_info
    await update_function_list(state, name_current_function)
    await update_state_list(state)
    await state.update_data(other_info=message.text)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="Подтвердить"),
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отмена")
    ]
    keyboard.add(*buttons)
    dictionary = await state.get_data()
    await ClientInfo.SwitchOtherInfo.set()
    await message.answer(f"ФИО: {dictionary['name']}\n"
                         f"День рождения: {dictionary['birthday']}\n"
                         f"Телефонный номер: {dictionary['tel_num']}\n"
                         f"Дополнительная информация: {dictionary['other_info']}\n", reply_markup=keyboard)


@dp.message_handler(state=ClientInfo.SwitchOtherInfo)
async def switch_request_info(message: types.Message, state: FSMContext):
    if message.text == "Подтвердить":
        await ClientInfo.GetInfo.set()
        await get_info(message, state)


@dp.message_handler(state=ClientInfo.GetInfo)
async def get_info(message: types.Message, state: FSMContext):
    await message.answer("Запись в клинику прошла успешно\n"
                         "Всего доброго!")
    dictionary: dict = await state.get_data()
    database.del_client(dictionary["tel_num"])
    database.del_appointment(dictionary["tel_num"])
    database.add_client(await state.get_data())
    database.add_appointment(await state.get_data())
    await state.reset_data()
    await Menu.start_menu.set()
    await start_menu(message, state)


executor.start_polling(dp)
