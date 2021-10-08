import logging
import json


class Properties:
    OUTPUT_ERROR = "Ошибка записи в файл"

    def __init__(self, property_file_name: str):
        self._PROPERTY_FILE = property_file_name

    def get_property(self, property_name: str) -> str:
        with open(self._PROPERTY_FILE, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is None:
                logging.error("Свойство не существует")
                raise Exception
            else:
                return value

    def set_property(self, property_name: str, property_value: str) -> str:
        with open(self._PROPERTY_FILE, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is None:
                data[property_name] = property_value
            else:
                logging.error("Свойство с таким именем уже существует")
                raise Exception
        with open(self._PROPERTY_FILE, 'w') as file_property:
            try:
                file_property.writelines(json.dumps(data, sort_keys=True, indent=4))
                return property_value
            except Exception:
                logging.error(Properties.OUTPUT_ERROR)

    def change_property(self, property_name: str, property_value: str) -> str:
        with open(self._PROPERTY_FILE, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is None:
                logging.error("Свойство не существует")
                raise Exception
            else:
                data[property_name] = property_value
                if value == property_value:
                    logging.warning("Вы пытаетесь записать в файл то же самое значение")
        with open(self._PROPERTY_FILE, 'w') as file_property:
            try:
                file_property.writelines(json.dumps(data, sort_keys=True, indent=4))
                return property_value
            except Exception:
                logging.error(Properties.OUTPUT_ERROR)

    def delete_property(self, property_name: str) -> None:
        with open(self._PROPERTY_FILE, 'r') as file_property:
            data: dict = json.load(file_property)
            value: str = data.get(property_name)
            if value is None:
                return
            else:
                data.pop(property_name)
        with open(self._PROPERTY_FILE, 'w') as file_property:
            try:
                file_property.writelines(json.dumps(data, sort_keys=True, indent=4))
            except Exception:
                logging.error(Properties.OUTPUT_ERROR)
