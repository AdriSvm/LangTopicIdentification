import os
import re
from datetime import datetime, timedelta


def delete_old_files(directory:str, pattern:r"", days_ago:int) -> list[str]:
    # Convertir días en timedelta
    cutoff_date = datetime.now() - timedelta(days=days_ago)

    # Compilar la expresión regular
    regex = re.compile(pattern)

    # Recorrer los archivos en el directorio
    files_deleted = []
    for filename in os.listdir(directory):
        # Verificar si el archivo cumple con el patrón
        if regex.match(filename):
            # Obtener la ruta completa del archivo
            file_path = os.path.join(directory, filename)
            # Obtener la última fecha de modificación del archivo
            file_mod_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            # Si el archivo es más antiguo que la fecha límite, eliminarlo
            if file_mod_date < cutoff_date:
                os.remove(file_path)
                files_deleted.append(file_path)

    return files_deleted