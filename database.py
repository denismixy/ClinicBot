import logging
import peewee as pw

db = pw.SqliteDatabase("clinic.db")


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
    date_and_time = pw.DateField()

    class Meta:
        database = db


class Holidays(pw.Model):
    date = pw.DateField()
    type = pw.CharField()

    class Meta:
        database = db


class WeekSchedule(pw.Model):
    day = pw.CharField()
    time = pw.CharField()

    class Meta:
        database = db


db.connect()


db.drop_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])
db.create_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])


# add client into DB
def add_client(person) -> None:
    Clients.create(tel_num=person["tel_num"],
                   chat_id=person["chat_id"],
                   name=person["name"],
                   birthday=person["birthday"],
                   other_info=person["other_info"])


def del_client(tel_num) -> None:
    Clients.delete_by_id(tel_num)


#TODO: сделать изменение значения в поле клиента
def update_client(person_id, field, value) -> None:
    Clients.update(field = value).where(Clients.client_id == person_id)


def add_appointment(note) -> None:
    AppointmentsList.create(tel_num=note["tel_num"],
                            doctor_id=Doctors.get(Doctors.name == note["doctor"]),
                            date_and_time=note["date"] + " " + note["time"])


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
    output = ""
    output += f"Ваше имя: {client.name}\n"
    output += f"Ваша дата рождения: {client.birthday}\n"
    output += f"Ваш телефон: {client.tel_num}\n"
    output += f"Доп. инфо: {client.other_info}"
    return output


def show_client_appointment(tel_num: int) -> str:
    try:
        note = AppointmentsList.get(AppointmentsList.tel_num == tel_num)
        client = Clients.get(Clients.tel_num == note.tel_num)
        doctor = Doctors.get(Doctors.doctor_id == note.doctor_id)
        output = ""
        output += f"Ваше имя: {client.name}\n"
        output += f"Ваш врач: {doctor.name}\n"
        output += f"Ваше время: {note.date_and_time}"
        return output
    except Exception:
        return ''


def show_doctors() -> list:
    output = []
    try:
        for doctor in Doctors.select():
            output.append(doctor.name)
        return output

    except Exception:
        logging.error("Упало обращение к таблице докторов")
