from flask import Blueprint, jsonify, request
from datetime import datetime
from src.services.Archivos import guardarAudio
from src.services.ModelosTranscriptor import *
from src.models.whisperConfig import whisperConfig

import traceback
import time

# Logger
from src.utils.Logger import Logger

main = Blueprint('index_blueprint', __name__)


@main.route('/transcribir/<modeloTranscriptor>', methods=['POST'])
def transcribir(modeloTranscriptor):
    try:
        Logger.add_to_log("info", "{} {}".format(request.method, request.path))

        #Guardar archivo en sistema de archivos - deberia descomprimir a futuro
        if 'audio' not in request.files:
            return 'Archivo no encontrado'#error
        archivo = request.files['audio']
        if archivo.filename == '':
            return 'Archivo no seleccionado'#error
        nomArchivo = guardarAudio(request.remote_addr, archivo)
        #Procesar audio según el modelo
        if modeloTranscriptor == "whisper":
            #Configuración del modelo
            modelo = request.form['modelo']
            dispositivo = request.form['dispositivo']
            tamLote = int(request.form['tamLote'])
            tipoComputo = request.form['tipoComputo']
            config = whisperConfig(modelo, dispositivo, tamLote, tipoComputo)
            #Proceso de transcripción
            start_time = time.time()
            transcripcion = transcribirWhisper(nomArchivo, config)
            end_time = time.time()
            tiempo_transcurrido = end_time - start_time
            return jsonify({'texto':transcripcion, 'tiempo':tiempo_transcurrido, 'success': True})
        elif modeloTranscriptor == "sphinx":
            #Proceso de transcripción
            start_time = time.time()
            transcripcion = transcribirSphinx(nomArchivo)
            end_time = time.time()
            tiempo_transcurrido = end_time - start_time
            return jsonify({'texto':transcripcion, 'tiempo':tiempo_transcurrido, 'success': True})
        else:
            return 'Modelo no encontrado'# Error
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())

        response = jsonify({'message': "Internal Server Error", 'success': False})
        return response, 500