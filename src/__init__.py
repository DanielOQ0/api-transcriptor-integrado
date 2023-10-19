from flask import Flask
import os
# Routes
from .routes import TranscriptorRoutes

app = Flask(__name__)


def init_app(config):
    # Configuración
    app.config.from_object(config)

    #Configuración sistema de archivos
    app.config['UPLOAD_FOLDER'] = 'src/uploads'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # plantillas
    app.register_blueprint(TranscriptorRoutes.main, url_prefix='/')

    return app
