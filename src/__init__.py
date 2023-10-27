import os

from flask import Flask
from flask_cors import CORS


app = Flask(__name__)


def init_app(config):
    # Configuración
    app.config.from_object(config)

    #Configuración sistema de archivos
    app.config['UPLOAD_FOLDER'] = 'src/uploads'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.config['STATIC_URL_PATH'] = '/src/static'

    CORS(app)

    return app