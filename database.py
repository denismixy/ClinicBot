import logging
import peewee as pw

from datetime import date, datetime, timedelta

db = pw.SqliteDatabase("clinic.db")

class Admins(pw.Model):
    chat_id = pw.IntegerField()

    class Meta:
        database = db


class Clients(pw.Model):
    tel_num = pw.IntegerField(primary_key=True, unique=True)
    chat_id = pw.IntegerField()
    name = pw.CharField()
    birthday = pw.DateField()
    other_info = pw.CharField()

    class Meta:
        database = db


class Doctors(pw.Model):
    doctor_id = pw.IntegerField(primary_key=True, unique=True)
    name = pw.CharField()

    class Meta:
        database = db


class AppointmentsList(pw.Model):
    tel_num = pw.ForeignKeyField(Clients)
    doctor_id = pw.ForeignKeyField(Doctors)
    date = pw.DateField()
    time = pw.CharField()

    class Meta:
        database = db


class Holidays(pw.Model):
    date = pw.DateField()
    type = pw.CharField()

    class Meta:
        database = db


class WeekSchedule(pw.Model):
    # 0 - Понедельник и т. д.
    day = pw.CharField()
    time = pw.CharField()

    class Meta:
        database = db


db.connect()

# db.drop_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])
# db.create_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])


# add client into DB
def add_client(person) -> None:
    Clients.create(tel_num=person["tel_num"],
                   chat_id=person["chat_id"],
                   name=person["name"],
                   birthday=person["birthday"],
                   other_info=person["other_info"])


def del_client(tel_num) -> None:
    Clients.delete_by_id(tel_num)


# TODO: сделать изменение значения в поле клиента
# def update_client(person_id, field_bd, value) -> None:
#     Clients.update(field=value).where(Clients.client_id == person_id)


def add_appointment(note) -> None:
    AppointmentsList.create(tel_num=note["tel_num"],
                            doctor_id=Doctors.get(Doctors.name == note["doctor"]),
                            date=note["date"],
                            time=note["time"])


def del_appointment(tel_num) -> None:
    try:
        note_id = AppointmentsList.get(AppointmentsList.tel_num == tel_num)
        AppointmentsList.delete_by_id(note_id.id)
    except Exception:
        return


def check_client_info(tel_num: int) -> bool:
    try:
        Clients.get(Clients.tel_num == tel_num)
        return True
    except Exception:
        return False


def check_client_appointment(tel_num: int) -> bool:
    try:
        AppointmentsList.get(AppointmentsList.tel_num == tel_num)
        Clients.get(Clients.tel_num == tel_num)
        return True
    except Exception:
        del_appointment(tel_num)
        return False


# show client info
def show_client_info(tel_num: int) -> str:
    client = Clients.get(Clients.tel_num == tel_num)
    return  f"Ваше имя: {client.name}\n"\
            f"Ваша дата рождения: {client.birthday}\n" \
            f"Ваш телефон: {client.tel_num}\n" \
            f"Доп. инфо: {client.other_info}"


def show_client_appointment(tel_num: int) -> str:
    try:
        note = AppointmentsList.get(AppointmentsList.tel_num == tel_num)
        client = Clients.get(Clients.tel_num == note.tel_num)
        doctor = Doctors.get(Doctors.doctor_id == note.doctor_id)
        return f"ФИО: {client.name}\n" \
               f"Врач: {doctor.name}\n" \
               f"Выбранная время: {str(note.time) + ' ' + datetime.strftime(note.date, '%d.%m.%Y')}"
    except Exception as exc:
        return ''


def show_doctors() -> list:
    try:
        return [doctor.name for doctor in Doctors.select()]
    except Exception:
        logging.error("Упало обращение к таблице докторов")
        return []


def get_appointments(amount_weeks: int = 4) -> list:
    first_day: date = date.today()
    last_day: date = date.today() + timedelta(amount_weeks * 7)
    try:
        dates = [first_day + timedelta(i) for i in range(0, amount_weeks * 7 + 1)]
        weekdays_schedule = {datetime.strftime(i.day, "%d.%m.%Y"): i.time
                             for i in WeekSchedule.get()}
        holidays = {datetime.strftime(i.date, "%d.%m.%Y")
                    for i in Holidays.get(Holidays.date <= last_day.strftime("%d.%m.%Y"),
                                                 Holidays.date >= first_day.strftime("%d.%m.&Y"))}
        return [dt for dt in dates if dt not in holidays and weekdays_schedule[dt.strftime("%d.%m.%Y")]]
    except Exception as exc:
        return []


# TODO добавить админов
def check_access(chat_id, tel_num):
    try:
        print(chat_id, tel_num)
        print(Clients.get(tel_num).chat_id)
        if Clients.get(Clients.tel_num == tel_num).chat_id == chat_id:
            return True
        else:
            return False
    except Exception:
        return False

def check_admin(chat_id):
    try:
        Admins.get(Admins.chat_id == chat_id)
        return True
    except Exception as exc:
        return False

def get_number_by_date_time(date, time, doctor):
    date_time = date + " " + time
    try:
        return AppointmentsList.get(AppointmentsList.date_and_time == date_time,
                                    AppointmentsList.doctor_id == Doctors.get(Doctors.name == doctor)
                                    ).tel_num
    except Exception:
        return None
