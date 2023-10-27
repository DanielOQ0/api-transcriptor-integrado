import os
from src import app
from flask_socketio import SocketIO, emit, send
from src.services.ModelosTranscriptor import transcribirSphinxInlive, transcribirWhisperInLive
from shutil import rmtree
from src.models.whisperConfig import whisperConfig

socketio = SocketIO(app)

# Variable
dictConexiones = {} # Diccionario con las conexiones, audios y transcripción
rutaAudios = os.path.join('src', 'uploads')

#Funciones Principales
def transcribirInLive(IdSocket, nomAudio, AudioBLOB):
    '''Recibe como parámetro el Id de la conexión, nombre del audio,
    blob del audio y el indicador de stop. Esta función se encarga de organizar y
    ejecutar todo el proceso de transcripción. Además envía vía socket la transcripción resultante.'''

    # Crea el audio y almacena la ruta del audio en una variable
    rutaArchivoAudio = crearAudio(IdSocket, nomAudio, AudioBLOB)

    #configuracion de whisper
    config = whisperConfig('small','cuda',16, 'float16')
    # Transcribe el audio y almacena la transcripción en una variable
    #transcripcion = transcribirSphinxInlive(rutaArchivoAudio)
    print('Nombre del audio: ',nomAudio)
    print('Ruta Archivo: ', rutaArchivoAudio)
    transcripcion = transcribirWhisperInLive(rutaArchivoAudio, config)

    # Almacena la transcripción en el nombre del audio almacenado en el diccionario de conexiones
    dictConexiones[IdSocket][nomAudio]['transcripcion'] = transcripcion

    # Almacena la transcripción que genera la función unir transcripción
    transcripcionUnida = unirTranscripcion(IdSocket)

    # Elimina la ruta con su contenido
    termino, IndStop = borrarAudio(IdSocket)

    # Valida si el indicador de unir audio y stop son verdaderos
    if (termino) and (IndStop):
        # Emite el mensaje al cliente correspondiente
        socketio.emit('messageFinal', transcripcionUnida, to=IdSocket)
    else:
        # Envía el mensaje al cliente correspondiente
        socketio.send(transcripcionUnida, to=IdSocket)

    return

def crearAudio(IdSocket, nomAudio, AudioBLOB):
    
    '''Recibe como parámetro el Id de la conexión, nombre del audio, el blob de audio e indicador de stop.
    Esta función permite crear audios a partir de un blob, en el caso que el indicador de unir audio y stop sea verdadero
     llama a la función de unir audios, de lo contrario retorna la ruta donde quedo el audio creado.'''

    # Variable con la ruta de la conexion
    rutaAudiosSocket = os.path.join(rutaAudios, IdSocket)
    # Variable con la ruta y nombre del audio
    rutaAudio = os.path.join(rutaAudiosSocket, nomAudio)

    # Crea la ruta para almacenar los audios
    crearDirectorio(rutaAudios)
    # Crea la ruta para los audio del IdSocket
    crearDirectorio(rutaAudiosSocket)

    # Configuración y creación del audio
    with open(rutaAudio, "wb") as audio:
        flujoAudio = AudioBLOB.read()
        audio.write(flujoAudio)

    return rutaAudio

def unirTranscripcion(IdSocket):
    '''Recibe como parámetro el Id de la conexión del socket. Esta función se encargar se ordenar 
    los audios en relación al número de segmento, después concatena las transcripciones ignorando 
    los vacíos y None. Finalmente retorna el texto final.'''

    # Variable para almacenar la transcripción
    transcripcionFinal = ''

    # Ordena el dict por el número de segmento
    dictConexiones[IdSocket] = dict(sorted(dictConexiones[IdSocket].items(),
                                           key=lambda x: x[1]['segmento']))

    # Itera los audios de la conexión almacenado la transcripción, ignorando los valores vacíos o None
    for audio in dictConexiones[IdSocket]:
        if 'transcripcion' in dictConexiones[IdSocket][audio] and dictConexiones[IdSocket][audio]['transcripcion'] != None:
            # Valida si es la primera transcripción para no dejar espacios al inicio
            if len(transcripcionFinal) > 0:
                transcripcionFinal = transcripcionFinal + ' ' + \
                    dictConexiones[IdSocket][audio]['transcripcion']
            else:
                transcripcionFinal = dictConexiones[IdSocket][audio]['transcripcion']

    return transcripcionFinal.capitalize()

def borrarAudio(IdSocket):
    '''Recibe como parámetro el Id de la conexión y el indicador de stop.
    Esta función permite identificar si hay algún audio pendiente por transcribir de no ser así, 
    y si el indicador de stop es verdadero, en caso de cumplir estas dos condiciones elimina la 
    carpeta de conexión con los audios y elimina el dict de conexión. Retorna una variable que 
    indica que ya se terminó la transcripción.'''

    termino = True
    IndStop = False
    CanAudio = 0

    # Valida el segmento mayor y lo amacena en la variable, si hay algún audio pendiente de transcripción y si ya se recibió el stop de cliente, y retorna una variable bandera
    for audio in dictConexiones[IdSocket]:

        if dictConexiones[IdSocket][audio]['segmento'] > CanAudio:
            CanAudio = dictConexiones[IdSocket][audio]['segmento']

        if not 'transcripcion' in dictConexiones[IdSocket][audio]:
            termino = False

        if dictConexiones[IdSocket][audio]['IndStop'] == 'true':
            IndStop = True

    # Valida si ya se recibieron todos los audios
    if (CanAudio + 1) > len(dictConexiones[IdSocket]):
        termino = False

    # Valida si termino la transcripción y si el indicador de stop es verdadero
    if (termino) and (IndStop):
        # Elimina el directorio con su contenido
        rmtree(os.path.join(rutaAudios, IdSocket))
        # Eliminar el dict de la conexión
        del dictConexiones[IdSocket]

    return termino, IndStop

#Funciones secundarias
def crearDirectorio(ruta):
    '''Recibe como parámetro la ruta que incluye el nombre del directorio, y la función permite crear el
    directorio en caso de que no exista de lo contrario no realiza ninguna actividad.'''

    # Valida si no existe el directorio
    if not os.path.isdir(ruta):
        # Crea el directorio
        os.mkdir(ruta)