import traceback

from flask import Blueprint, render_template, jsonify
from src import app
# Logger
from src.utils.Logger import Logger


@app.route('/plantilla/cargar-audio')
def cargarArchivo():
    '''Función que se encarga de direccionar a la plantilla de prueba de inicio o principal'''
    try:
        return render_template('transcribir-archivo.html')
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())

        response = jsonify({'message': "Internal Server Error", 'success': False})
        return response, 500

@app.route('/plantilla/grabar-audio')
def grabarAudio():
    '''Función que se encarga de direccionar a la plantilla de prueba de inicio o principal'''
    try:
        return render_template('transcribir-tiempo-real.html')
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())

        response = jsonify({'message': "Internal Server Error", 'success': False})
        return response, 500