from config import config
from src import init_app

configuration = config['development']
app = init_app(configuration)

def page_not_found(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__ == '__main__':
    app.register_error_handler(404, page_not_found)
    app.run()
