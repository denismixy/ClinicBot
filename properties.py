"""
Записи в PROPERTY_FILE должны иметь вид 'property_name = "property_value"', каждая запись находится на отдельной строке.

Пример:
id = "123"
token = "abc123"

Пример создания объекта для использования:
property_file = Properties("config.txt")

"""
import re


class Properties:

    def __init__(self, property_file_name: str):
        self._PROPERTY_FILE = property_file_name
        self._PATTERN_FOR_VALUE = r' = "(.*)"'

    def get_property(self, property_name: str) -> str:
        pattern = property_name + self._PATTERN_FOR_VALUE
        with open(self._PROPERTY_FILE, "r") as file_property:
            for string in file_property.readlines():
                if re.search(pattern, string):
                    search_result = re.search(pattern, string)
                    result = search_result.group(1)
                    return result

    def set_property(self, property_name: str, property_value: str) -> str:
        with open(self._PROPERTY_FILE, 'a') as file_property:
            file_property.write("\n{0} = \"{1}\"".format(property_name, property_value))
        return property_value

    def change_property(self, property_name: str, property_value: str) -> str:
        with open(self._PROPERTY_FILE, 'r') as file_property:
            pattern = property_name + self._PATTERN_FOR_VALUE
            list_properties = file_property.readlines()
            for index, string in enumerate(list_properties):
                if re.search(pattern, string):
                    list_properties[index] = "{0} = \"{1}\"\n".format(property_name, property_value)
                    break
        with open(self._PROPERTY_FILE, 'w') as file_property:
            file_property.writelines(list_properties)
            return property_value

    def delete_property(self, property_name: str) -> None:
        with open(self._PROPERTY_FILE, 'r') as file_property:
            pattern = property_name + self._PATTERN_FOR_VALUE
            list_properties = file_property.readlines()
            for index, string in enumerate(list_properties):
                if re.search(pattern, string):
                    del list_properties[index]
                    break
        with open(self._PROPERTY_FILE, 'w') as file_property:
            file_property.writelines(list_properties)
