import os
from config import config
from src import init_app
from src.routes.SocketIO import *
from src.routes.TemplateRoutes import *
from src.routes.TranscriptorRoutes import *

configuration = config['development']
app = init_app(configuration)

def page_not_found(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__ == '__main__':
    socketio.init_app(app, cors_allowed_origins="*",ping_timeout=100, ping_interval=60)
    socketio.run(app, debug=True)

    app.register_error_handler(404, page_not_found)
    app.run(host='0.0.0.0', port=5000) 