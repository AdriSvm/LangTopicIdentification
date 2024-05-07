"""
Main class for managing the configuration files
Steps to use it:
    1. Create a file with the configuration data in JSON format.
    2. Create an instance of Config with the path to the file.
    3. Use the attributes of the instance to access the data. If the attribute does not exist, returns None.
    4. Use the data as needed.
    5. Profit.
Example:
    config = Config('config.json')
    print(config.api_key)
    print(config.api_secret)
    print(config.api_url)
    print(config.api_version)
    print(config.non_existent_attribute)  # Returns None

"""

import json

class Config:
    def __init__(self, filepath):
        self._data = {}
        self.filepath = filepath
        try:
            with open(filepath, 'r') as file:
                self._data = json.load(file,)
        except FileNotFoundError:
            print(f"El archivo {filepath} no fue encontrado.")
        except json.JSONDecodeError:
            print(f"Error al decodificar JSON en el archivo {filepath}.")

    def attrs(self):
        return self._data.keys()

    def super_save(self,f):
        try:
            with open(f, 'w') as file:
                json.dump(self._data, file, indent=4)
        except TypeError:
            print(f"Error al guardar el archivo {f}.")
    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data.get(key,None)
    def __getattr__(self, name):
        # Este método se llama si no se encuentra el atributo de manera regular.
        # Buscamos el nombre del atributo en los datos cargados.
        # Si el atributo no existe, se devuelve None.
        return self._data.get(name, None)

    def __setattr__(self, key, value):
        # Verifica si el atributo a establecer es uno de los atributos internos.
        if key == '_data':
            # Llama al __setattr__ de la superclase para evitar la recursión.
            object.__setattr__(self, key, value)
        else:
            # Maneja todos los otros atributos a través del diccionario _data.
            self._data[key] = value

    def __str__(self):
        return str(self._data)
