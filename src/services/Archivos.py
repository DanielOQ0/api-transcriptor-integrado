from datetime import datetime

import os


def guardarAudio(ip, archivo):
    # Guardar el archivo en tu sistema de archivos
    nomArchivo = f'{ip}({datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}).wav'
    archivo.save(os.path.join("src/uploads",nomArchivo))
    return nomArchivo