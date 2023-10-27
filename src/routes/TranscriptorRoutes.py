from flask import Blueprint, jsonify, request
from datetime import datetime
from src.services.Archivos import guardarAudio
from src.services.ModelosTranscriptor import *
from src.models.whisperConfig import whisperConfig
from src import app
from src.routes.SocketIO import *

import traceback
import time

# Logger
from src.utils.Logger import Logger

#Ruta POST para recibir un archivo y transcribirlo
@app.route('/transcribir/<modeloTranscriptor>', methods=['POST'])
def transcribirArchivo(modeloTranscriptor):
    try:
        Logger.add_to_log("info", "{} {}".format(request.method, request.path))
        #Guardar archivo en sistema de archivos - deberia descomprimir a futuro
        if 'audio' not in request.files:
            return jsonify({'message': "Archivo no encontrado", 'success': False})#error
        archivo = request.files['audio']
        if archivo.filename == '':
            return jsonify({'message': "Archivo no seleccionado", 'success': False})#error
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
            return jsonify({'texto':transcripcion, 'tiempo':tiempo_transcurrido, 'success': True, 'modelo': modeloTranscriptor})
        elif modeloTranscriptor == "sphinx":
            #Proceso de transcripción
            start_time = time.time()
            transcripcion = transcribirSphinx(nomArchivo)
            end_time = time.time()
            tiempo_transcurrido = end_time - start_time
            return jsonify({'texto':transcripcion, 'tiempo':tiempo_transcurrido, 'success': True, 'modelo': modeloTranscriptor})
        else:
            return jsonify({'message': "Modelo no encontrado", 'success': False})# Error
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())

        response = jsonify({'message': "Internal Server Error", 'success': False})
        return response, 500

# Ruta para recibir por método POST el Id Socket, blob de audio y el indicador de stop    
@app.route('/transcribir/whisper-inlive', methods=['POST'])
def transcribirTiempoReal():
    try:
        Logger.add_to_log("info", "{} {}".format(request.method, request.path))
        # Variables de la solicitud
        IdSocket = request.form['socketId'] #Id de la conexión de socket
        # Variable para el número de segmento del audio
        segmento = request.form['segmento']
        # Variable para el nombre del audio
        nomAudio = request.files['AudioBLOB'].filename
        # Variable para el blob de audio
        AudioBLOB = request.files['AudioBLOB']
        # Variable para el indicador de stop
        IndStop = request.form['IndStop'].lower()

        # Valida si el nombre de la conexión esta almacenadas en el dict de conexiones
        if IdSocket in dictConexiones:
            pass
        else:
            # Inserta la conexión en el dict de conexiones
            dictConexiones[IdSocket] = {}

        # Inserta el nombre del audio en el dict de la conexión correspondiente
        dictConexiones[IdSocket][nomAudio] = {
            'segmento': int(segmento), 'IndStop': IndStop}

        # Enviar los datos a la función de transcribir
        transcribirInLive(IdSocket, nomAudio, AudioBLOB)

        return "Exito!"
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())

        response = jsonify({'message': "Internal Server Error", 'success': False})
        return response, 500