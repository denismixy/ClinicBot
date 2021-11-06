import logging
import json


class Properties:
    
    def __init__(self, property_file_name: str):
        self._filename = property_file_name

    def get_property(self, property_name: str) -> str:
        with open(self._filename, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is not None:
                return value
            logging.error("Свойство не существует")
            raise KeyError

    def set_property(self, property_name: str, property_value: str) -> str:
        with open(self._filename, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is None:
                data[property_name] = property_value
            else:
                logging.error("Свойство с таким именем уже существует")
                raise KeyError
            try:
                file_property.writelines(json.dumps(data, sort_keys=True, indent=4))
                return property_value
            except OSError as exc:
                logging.error(f"Ошибка записи в файл {exc.errno}")

    def change_property(self, property_name: str, property_value: str) -> str:
        with open(self._filename, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is None:
                logging.error("Свойство не существует")
                raise KeyError
            else:
                data[property_name] = property_value

            try:
                file_property.writelines(json.dumps(data, sort_keys=True, indent=4))
                return property_value
            except OSError as exc:
                logging.error(f"Ошибка записи в файл {exc.errno}")

    def delete_property(self, property_name: str) -> None:
        with open(self._filename, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is not None:
                data.pop(property_name)
            try:
                file_property.writelines(json.dumps(data, sort_keys=True, indent=4))
            except OSError as exc:
                logging.error(f"Ошибка записи в файл {exc.errno}")
