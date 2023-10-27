import whisperx
import speech_recognition as speRec
import os

# Variable con el nombre de la carpeta donde están los modelos que hacen parte del motor de reconocimiento de voz
lenguaje = "es-CO"
# Ruta del modelo de lenguaje
directorioLenguaje = os.path.join("modelo-sphinx", lenguaje)
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


def transcribirWhisper(nomArchivo, config):
    '''Recibe como parámetro la ruta con el nombre del audio a transcribir y la configuración del whisper.
    Esta función recibe le audio, lo procesa con whisperx. Retorna la transcripción resultante.'''

    #Cargar modelo segun la configuración
    model = whisperx.load_model(config.modelo, config.dispositivo, compute_type=config.tipoComputo, language="es")
    #Cargar audio al modelo de whisper seleccionado
    audio = whisperx.load_audio(f'src/uploads/{nomArchivo}')
    result = model.transcribe(audio, batch_size=config.tamLote)
    texto_unificado = ""
    # Concatenamos los textos
    for resultado in result["segments"]:
        texto_unificado += resultado['text']
    return texto_unificado
def transcribirSphinx(nomArchivo):
    '''Recibe como parámetro la ruta con el nombre del audio a transcribir.
    Esta función recibe le audio, lo envía al objeto speech_recognition utilizando el método de AudioFile
    para así posteriormente pasarlo por el transcriptor con su respectivo lenguaje. Retorna la transcripción
    resultante, en caso de no entender el audio o enviar un audio no compatible genera un mensaje en consola.'''

    # Crear la variable reconizer
    escucharAudio = speRec.Recognizer()
    # Variable para almacenar la transcripción
    transcripcion = ''
    # Usar el archivo de audio como fuente de audio
    with speRec.AudioFile(f'src/uploads/{nomArchivo}') as source:
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
    return transcripcion

def transcribirSphinxInlive(rutaAudio):
    '''Recibe como parámetro la ruta con el nombre del audio a transcribir.
    Esta función recibe le audio, lo envía al objeto speech_recognition utilizando el método de AudioFile
    para así posteriormente pasarlo por el transcriptor con su respectivo lenguaje. Retorna la transcripción
    resultante, en caso de no entender el audio o enviar un audio no compatible genera un mensaje en consola.'''

    # Crear la variable reconizer
    escucharAudio = speRec.Recognizer()
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
    
    return transcripcion

def transcribirWhisperInLive(rutaArchivoAudio, config):
    '''Recibe como parámetro la ruta con el nombre del audio a transcribir y la configuración del whisper.
    Esta función recibe le audio, lo procesa con whisperx. Retorna la transcripción resultante.'''

    #Cargar modelo segun la configuración
    model = whisperx.load_model(config.modelo, config.dispositivo, compute_type=config.tipoComputo, language="es")
    #Cargar audio al modelo de whisper seleccionado
    audio = whisperx.load_audio(rutaArchivoAudio)
    result = model.transcribe(audio, batch_size=config.tamLote)
    texto_unificado = ""
    # Concatenamos los textos
    for resultado in result["segments"]:
        texto_unificado += resultado['text']
    return texto_unificado