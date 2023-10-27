// Constante con el código ok
const OkTranscr = "OKTRANSCR"
// Constante con el código error
const errorTranscr = "ERRORTRANSCR"
// Variable global con la URL del servidor y puerto donde esta desplegada la API-Trancriptor
let URLServidor;
// Variable global para almacenar el contexto del audio
let contextoAudio;
// Variable global para almacenar la cadena de audio blob
let audioStream;
// Variable global para almacenar el analizador
let analizador;
// Variable global para almacenar la grabador creada a partir de la librería recorder.js
let recorder;
// Variable global para almacenar el formato del tipo de archivo de audio
let formatoAudio = "wav";
// Variable global para almacenar el Id de la conexión del cliente
let socketId;
// Variable global para almacenar el contador de segmentos o divisiones de los audios
let segmento = 0;
// Variable global para almacenar el indicador de stop
let IndStop = false;
// Variable global para almacenar la data almacenada en el área de texto
let dataAntigua;
// Variable global para almacenar el número de canales
let numCanales = 1;
// Variable global para almacenar la frecuencia de muestreo
let freMuestreo = 16000;
// Variable global para almacenar la tasa mínimo de decibeles [-30 a ]
let minDecibeles = -70;
// Variable global para almacenar el tiempo en milisegundos para los silencios
let retrasoSilencio = 50;
// Variable global para almacenar la funcionalidad de repetir
let repetir;
// Variable global para el identificador de silencio
let IndSilencio = false;
// Variable global para identificar el tiempo de inicio del silencio
let silencioInicio;
// Variable global para almacenar la data de la frecuencia del audio
let data;
// Variable para almacenar Id del área de texto donde ser reflejara la transcripción
let IdAreaTranscripcion;
let canSilencioDetener;
let canSilencioAcumulado;
let funSilencioDetener;
// Indicador que marca el inicio de grabación
let IndGrabando = false;

/**
 * @description Función que permite identificar si el AudioContext, getUserMedia y URL son compatibles con el navegador, 
 * en caso de no ser compatible genera un mensaje en consola.
 * @returns {string} Código de respuesta de la función.
 */
function validarCompatibilidad() {
    try {
        // Interfaz para representar un gráfico de procesamiento de audio
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        // Permisos para acceder a los recursos de video (cámara) y audio (micrófono)
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        // Almacena un objeto con la información de la URL
        window.URL = window.URL || window.webkitURL;
        // Enviá código de ok si el navegador es compatible con la aplicación
        return OkTranscr;
    } catch (error) {
        // Enviá código de error si el no navegador es compatible con la aplicación
        return errorTranscr;
    };

};

/**
 * @description Establece la conexión del Socket IO a partir de la URL que recibe
 * @param {string} url La URL donde esta desplegada la API-Transcriptor
 * @returns {object} Objeto con la conexión establecida
 */
const iniciarSocket = ((url) => {
    // Crear constante para instanciar la conexión con socket IO
    const socketTranscriptor = io(url, { path: '/socket.io' });
    // Almacena la url del servidor
    URLServidor = url;

    /**
     * @description Después de establecer la conexión cliente – servidor, ejecuta la función que almacena el Id de la conexión
     */
    socketTranscriptor.on('connect', function () {
        // Almacena en la variable global el Id de la conexión del socket io
        socketId = socketTranscriptor.id;
    });

    /**
     * @description Después de identificar el mensaje “message”, ejecuta la función que almacena la transcripción en el Id de la caja de texto
     */
    socketTranscriptor.on('message', function (transcripcion) {
        // Valida si la transcripción no viene vacío o no esta definida
        if (transcripcion !== undefined && transcripcion !== "") {
            // Valida que la caja de texto no tenga información antigua
            if (dataAntigua !== "") {
                IdAreaTranscripcion.value = dataAntigua + ' ' + transcripcion;
            } else {
                IdAreaTranscripcion.value = transcripcion;
            };
        };
    });

    /**
     * @description Después de identificar el mensaje “messageFinal”, ejecuta la función que almacena la transcripción en el Id de la caja de texto e indica en consola que termino la transcripción
     */
    socketTranscriptor.on('messageFinal', function (transcripcion) {
        // Valida si la transcripción no viene vacío o no esta definida
        if (transcripcion !== undefined && transcripcion !== "") {
            // Valida que la caja de texto no tenga información antigua
            if (dataAntigua !== "") {
                IdAreaTranscripcion.value = dataAntigua + ' ' + transcripcion + '.';
            } else {
                IdAreaTranscripcion.value = transcripcion + '.';
            };
            // Genera un mensaje de alerta con la finalización del proceso
            console.log("Finalizo la trascripción!");
        };
    });

    /**
     * @description Después de identificar el mensaje “messageFinal”, imprime en consola el error.
     */
    socketTranscriptor.on('messageError', function (mensaje) {
        // Valida si el mensaje no viene vacío o no esta definida
        if (transcripcion !== undefined && transcripcion !== "") {
            // Imprime en consola el mensaje de error
            console.log(mensaje);
        };
    });

    return socketTranscriptor
})

/**
 * @description Función encargada de validar los permisos para acceder al micrófono, en caso de no detectar el micrófono
 * se genera un mensaje en consola. En caso de aceptar los permisos e identificar el micrófono ejecuta el método de iniciar la grabación.
 * @param {String} IdAreaTranscripcion Id de la caja de texto donde se reflejara la transcripción
 * @param {Integer} segundosSilencio Cantidad de segundos de silencio para detener el proceso de transcripción
 * @param {callback} funcionSilencio Función que se ejecuta cuando se detecta el silencio y detiene la transcripción
 */
function iniciarTranscripcion(IdElemento, segundosSilencio = 0, funcionSilencio = null) {
    // Almacena en la variable global el Id del elemento donde se escribira la transcripción.
    IdAreaTranscripcion = document.getElementById(IdElemento);
    // Almacena y convierte los segundos a milisegundo que detiene la transcripción por silencios
    canSilencioDetener = segundosSilencio * 1000;
    // Almacena la función que se ejecutara cuando se detenga la transcripción por silencios
    funSilencioDetener = funcionSilencio;
    // Control de errores durante el proceso de iniciar transcripción
    try {
        // Solicita los permisos para acceder al micrófono
        navigator.mediaDevices.getUserMedia({ audio: true, video: false })
            .then((stream) => {
                // Indicador que marca el inicio de grabación 
                IndGrabando = true;
                // Ejecuta la función de iniciar grabación
                iniciarGrabacion(stream);
            })
            .catch((error) => { console.log(error); });
    } catch (error) {
        // Imprime en consola el error cuando se presenta fallas al solicitar permisos al micrófono
        console.log(error);
    };
}

/**
 * @description Función encargada de detener la transcripción.
 */
function detenerTranscripcion() {
    if (IndGrabando) {
        // Ejecuta la función para detener y almacenar el blob de audio, con el fin de enviarlo al servidor
        detenerGrabacion(function (AudioBLOB) {
            // Ejecuta la función que enviá el blob de audio al servidor
            enviarBlob(socketId, segmento, AudioBLOB, IndStop);
        }, "audio/" + formatoAudio);
        IndGrabando = false;
    }
}

/**
 * @description Función que se ejecutar 60 veces por segundo, con el fin de analizar la data e identificar si hay silencios. 
 * Si la duración del tiempo es mayor al valor configurado en la variable retrasoSilencio, segmenta el audio y lo envía al servidor.
 * @param {Integer} time Tiempo en milisegundos para detectar silencias
 */
function identificarSilencios(time) {
    // Mantiene en ejecución la función y almacena el Id en la variable
    repetir = requestAnimationFrame(identificarSilencios);
    // Almacena en la frecuencia en byte del audio
    analizador.getByteFrequencyData(data);

    if (data.some(v => v)) {
        if (IndSilencio) {
            IndSilencio = false;
        };
        silencioInicio = time;
        // Reinicia la cantidad de milisegundos acumulados cuando detecta que están hablando
        canSilencioAcumulado = 0;
    };
    if (!IndSilencio && (time - silencioInicio) > retrasoSilencio) {
        IndSilencio = true;
        canSilencioAcumulado = canSilencioAcumulado + (time - silencioInicio);
        if (typeof (canSilencioDetener) == "number" && canSilencioDetener > 0) {
            if (canSilencioAcumulado >= canSilencioDetener) {
                if (typeof (funSilencioDetener) == "function") {
                    funSilencioDetener();
                };
                detenerTranscripcion();
            } else {
                segmentarAudio();
            }
        } else {
            segmentarAudio();
        };
    };
};

/**
 * @description Función encargada de enviar la configuración, iniciar el proceso de grabación 
 * e iniciar el proceso de identificación de silencios.
 * @param {object} stream Objeto con el flujo de audio
 */
function iniciarGrabacion(stream) {

    // Instanciar el AudioContexto
    contextoAudio = new AudioContext();
    // Almacenar el audio stream
    audioStream = stream;
    // Almacena el flujo de audio
    var fuenteFlujo = contextoAudio.createMediaStreamSource(stream);

    // Crea y configura el analizador, y por ultimo conectarlo con el flujo de audio
    analizador = contextoAudio.createAnalyser();
    fuenteFlujo.connect(analizador);
    analizador.minDecibels = minDecibeles;

    // Crea el array para almacenar la data para el analizador
    data = new Uint8Array(analizador.frequencyBinCount);

    // Almacena el tiempo de inicio de los silencios
    silencioInicio = performance.now();
    // Reinicia el indicador de silencio
    IndSilencio = false;
    // Reinicia la cantidad de milisegundos acumulados
    canSilencioAcumulado = 0;

    // Reinicio el contador de segmentos
    segmento = 0;
    // Cambia a falso la variable de stop
    IndStop = false;
    // Almacena la data registrada en el área de texto
    dataAntigua = IdAreaTranscripcion.value;

    // Inicializa la libreria de Recorder
    recorder = new Recorder(fuenteFlujo, { numChannels: numCanales, sampleRate: freMuestreo });
    // Inicia la grabación
    recorder && recorder.record();

    // Ejecutar la función para identificar los silencios
    identificarSilencios();
};

/**
 * @description Recibe como parámetro una función y el formato del audio. La función espera una devolución 
 * de llamada como primera argumento (función) y una vez ejecutada se genera el AudioBlob y se
 * recibe el mismo Blob que el primer argumento. El segundo argumento es opcional y especifica 
 * el formato para exportar el blob, ya sea wav o mp3
 * @param {Function} callback Función encargada de detener la grabación y enviar el audio al servidor
 * @param {String} formatoAudio Tipo de audio
 */
function detenerGrabacion(callback, formatoAudio) {
    // Cambia el indicador de stop a verdadero
    IndStop = true;
    // Cancela el ciclo de repetición del analizador
    cancelAnimationFrame(repetir);

    // Detiene la instancia de la grabadora
    recorder && recorder.stop();
    // Detiene la transmisión de audio del getUserMedia
    audioStream.getAudioTracks()[0].stop();

    // Identifica si la variable callback es una funcion, y si es asi exporta el audio grabado como un archivo .wav o .mp3
    // La devolución de llamada proporcionada en la función detener grabación recibe el blob
    if (typeof (callback) == "function") {
        // Exporta el AudioBLOB usando el método exportWAV
        recorder && recorder.exportWAV(function (blob) {
            callback(blob);
            // Borra la grabadora para comenzar de nuevo
            recorder.clear();
        }, formatoAudio);
    };
};

/**
 * @description Función encargada de detener la grabación, almacenar el blob con el audio y enviarlo al servidor.
 */
function segmentarAudio() {
    /**
     * @description Recibe como parámetro una función y el formato del audio. La función espera una devolución 
     * de llamada como primera argumento (función) y una vez ejecutada se genera el AudioBlob y se
     * recibe el mismo Blob que el primer argumento. El segundo argumento es opcional y especifica 
     * el formato para exportar el blob, ya sea wav o mp3
     * @param {Function} callback 
     * @param {String} formatoAudio 
     */
    function detenerSegmento(callback, formatoAudio) {
        // Detiene la instancia de la grabadora
        recorder && recorder.stop();
        // Identifica si la variable callback es una funcion, y si es asi exporta el audio grabado como un archivo .wav o .mp3
        // La devolución de llamada proporcionada en la función detener grabación recibe el blob
        if (typeof (callback) == "function") {
            // Exporta el AudioBLOB usando el método exportWAV
            recorder && recorder.exportWAV(function (blob) {
                callback(blob);
                // Borra la grabadora para comenzar de nuevo
                recorder.clear();
            }, formatoAudio);
        };
    };

    // Ejecuta la función para detener y almacenar el blob de audio, con el fin de enviarlo al servidor
    detenerSegmento(function (AudioBLOB) {
        // // Ejecuta la función que enviá el blob de audio al servidor
        enviarBlob(socketId, segmento, AudioBLOB, IndStop);
        // Aumenta el contador de segmentos
        segmento++;
    }, "audio/" + formatoAudio);
    // Inicia la grabación de nuevo
    recorder && recorder.record();
};

/**
 * @description Recibe como parámetro el Id de la conexión del socket, el número de segmento, 
 * el blob del audio y el indicador de stop. La función se encarga de estructurar 
 * los datos en un formData y lo envía al servidor.
 * @param {String} socketId Id de la conexión socket del cliente
 * @param {Number} segmento Numero de segmento del audio
 * @param {Blob} AudioBLOB Blob del audio grabado
 * @param {Boolean} IndStop Valor del indicador de detener
 */
function enviarBlob(socketId, segmento, AudioBLOB, IndStop) {
    // Crea el objeto de formData
    var formData = new FormData();
    //  Crea el objeto de XMLHttpRequest
    var xhr = new XMLHttpRequest();
    // Variable para el nombre del audio
    var socketIdSegmento = socketId + '_' + segmento;

    // Almacena los datos en el objeto
    formData.append("socketId", socketId);
    formData.append("segmento", segmento);
    formData.append("AudioBLOB", AudioBLOB, socketIdSegmento + '.' + formatoAudio);
    formData.append("IndStop", IndStop);

    // Imprime en consola en nombre del audio a enviar
    // console.log("Se envió el audio: " + socketIdSegmento);

    // Asigna el método de envió y abre la URL
    xhr.open("POST", URLServidor + "/transcribir/whisper-inlive");
    // Envía el objeto
    xhr.send(formData);
};