# Librería o modulo para usar funciones del sistema operativo
import os
# Librería o modulo que proporciona una interfaz para formato de sonido wav
import wave
# Librería o modulo para reconocimiento de voz
import speech_recognition as speRec
# Librería o modulo que importa Flask
from flask import Flask, render_template, request
# Librería o modulo que permite acceder a comunicaciones bidireccionales
from flask_socketio import SocketIO, emit, send
# Librería o modulo que permite manipular archivos o colecciones de archivos
from shutil import rmtree
# Importar la configuración de los ambiente de desarrollo, pruebas y producción
from config import DevelopmentConfig, ProductionConfig, TestingConfig
# Librería para intercambiar recursos de origen cruzado
from flask_cors import CORS


# Inicializar servidor web – Flask y asigno el nombre de la carpeta con los archivos estáticos
app = Flask(__name__, static_folder='ApiTranscriptor')
# Activa CORS en la app
CORS(app)
# Permite asignar la configuración del ambiente a utilizar
app.config.from_object(ProductionConfig)
# Instanciar SocketIO
socketio = SocketIO()

# Variable con el nombre de la carpeta donde están los modelos que hacen parte del motor de reconocimiento de voz
lenguaje = "es-CO"
# Variable con la ruta del proyecto
rutaProyecto = os.path.dirname(__file__)
# Ruta del modelo de lenguaje
directorioLenguaje = os.path.join(rutaProyecto, "modelo", lenguaje)
# Directorio y los nombres de los archivos que contiene el modelo de lenguaje
directorioParametrosAcusticos = os.path.join(
    directorioLenguaje, "acoustic-model")
archivoModeloLenguaje = os.path.join(
    directorioLenguaje, "language-model.lm.bin")
archivoDiccionarioFonemas = os.path.join(
    directorioLenguaje, "pronounciation-dictionary.dict")
# Tupla con el directorio y archivos del modelo
modeloLenguaje = (directorioParametrosAcusticos,
                  archivoModeloLenguaje, archivoDiccionarioFonemas)
# Variable para el nombre de la carpeta donde se almacenaran los audios
nomCarAudios = "audios"
# Variable para el tipo de archivo de audio
tipArcAudio = ".wav"
# Variable con la ruta donde se almacenara los audios
rutaAudios = os.path.join(rutaProyecto, nomCarAudios)
# Diccionario con las conexiones, audios y transcripción
dictConexiones = {}
# Variable con activar o desactivar proceso de unir audios
IndUnirAudio = False


# Crea la instancia para representar una colección de configuraciones y funciones de reconocimiento de voz
escucharAudio = speRec.Recognizer()



def unirAudios(IdSocket, rutaAudiosSocket):
    '''Recibe como parámetro el Id de la conexión y la ruta donde están almacenado los audios.
    Esta función permite unir los audios almacenado en una determina ruta, teniendo en cuenta de
    ordenarlos por fecha de creación previamente. El audio resultante o final tendrá los parámetros del audio inicial.
    Retorna la ruta donde quedo almacenado el audio final.'''

    # Lista para almacenar los parámetros y data de todos los audios
    data = []
    # Variable con la ruta para el audio final
    rutaAudioFinal = os.path.join(
        rutaAudiosSocket, IdSocket + "_final" + tipArcAudio)

    # Crea una lista con los audios almacenado en la ruta, validando que existan y cumplan con la extensión del tipo de archivo de audio
    with os.scandir(rutaAudiosSocket) as listaAudios:
        listaAudios = [audio.name for audio in listaAudios if audio.is_file(
        ) and audio.name.endswith(tipArcAudio)]

    # Ordenar la lista por la fecha de creación
    listaAudios.sort(key=lambda x: os.path.getmtime(
        os.join(rutaAudiosSocket, x)))

    # Recorre audio por audio, almacenado los parámetros y data
    for audio in listaAudios:
        w = wave.open(os.path.join(rutaAudiosSocket, audio), 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    # Crea el audio final
    audioFinal = wave.open(rutaAudioFinal, 'wb')
    # Asigna los parámetros al audio final
    audioFinal.setparams(data[0][0])

    # Une la data de cada audio y la almacena en el audio final
    for x in range(len(listaAudios)):
        audioFinal.writeframes(data[x][1])

    # Cierra el audio final
    audioFinal.close()
    # Limpia la lista de audios
    listaAudios.clear()

    return rutaAudioFinal


def transcribirAudio(IdSocket, nomAudio, rutaAudio):
    '''Recibe como parámetro la ruta con el nombre del audio a transcribir.
    Esta función recibe le audio, lo envía al objeto speech_recognition utilizando el método de AudioFile
    para así posteriormente pasarlo por el transcriptor con su respectivo lenguaje. Retorna la transcripción
    resultante, en caso de no entender el audio o enviar un audio no compatible genera un mensaje en consola.'''

    # Crear la variable global
    global escucharAudio
    # Variable para almacenar la transcripción
    transcripcion = ''

    # Usar el archivo de audio como fuente de audio
    with speRec.AudioFile(rutaAudio) as source:
        audio = escucharAudio.record(source)

    # Reconocer el audio usando el motor de Sphinx
    try:
        # Almacena la transcripción
        transcripcion = escucharAudio.recognize_sphinx(
            audio, language=modeloLenguaje)

    # Control de excepción cuando no entiende el audio
    except speRec.UnknownValueError:
        print("Sphinx no puede entener el audio")
    # Control de excepción cuando audio no es compatible
    except speRec.RequestError as e:
        print("Error de esfinge; {0}".format(e))

    # Si no se logra identificar la transcripción enviar valor None
    transcripcion = None if len(transcripcion) < 1 else transcripcion

    # Almacena la transcripción en el nombre del audio almacenado en el diccionario de conexiones
    dictConexiones[IdSocket][nomAudio]['transcripcion'] = transcripcion

    # Imprime la transcripción
    # print('Se Transcribio: ' + nomAudio, transcripcion, datetime.now())


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

