from tables import Client, Employee


def check_employee(identify: str) -> bool:
    return Employee.select().where(Employee.id == identify).exists()


def check_client(identify: str) -> bool:
    return Client.select().where(Client.id == identify).exists()

