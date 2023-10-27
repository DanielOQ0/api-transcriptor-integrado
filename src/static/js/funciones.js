// Constantes
const btnTranscribir = document.querySelector('#btnTranscribir');
const areaTextTranscripcion = 'areaTextTranscripcion';

/**
 * Ejecuta las funciones al cargar el navegador
 */
window.onload = function () {
    // Ejecuta la función encargado de validar la compatibilidad del navegador con la aplicación.
    var rtaValCom = validarCompatibilidad();
    // Valida la respuesta del metodo
    if (rtaValCom === "ERRORTRANSCR") {
        // Deshabilita el botón de transcribir
        btnTranscribir.disabled = true;
        alert("El navegador no es compatible con la aplicación");
    } else {
        // Iniciar la conexión  con socket IO
        iniciarSocket('https://xq3d8bbg-5000.use2.devtunnels.ms');
    }
};

/**
 * @description Función encargada de cambiar el estado a transcribir del botón que permite iniciar el proceso de transcripción.
 */
function cambiarEstadoBtnTranscribir() {
    // Cambia el texto a Transcribir
    btnTranscribir.innerText = "Transcribir";
    // Cambia el titulo a Transcribir
    btnTranscribir.title = "Transcribir";
    // Cambiar la clase
    btnTranscribir.classList.remove('btn-danger')
    btnTranscribir.classList.add('btn-primary')
}

/**
 * Ejecuta una serie de funciones al realizar clic sobre el botón de transcribir
 */
btnTranscribir.addEventListener("click", () => {

    // Valida el texto del botón
    if (btnTranscribir.innerHTML === "Transcribir") {
        // Cambia el texto a Detener
        btnTranscribir.innerText = "Detener";
        // Cambia el titulo a Detener
        btnTranscribir.title = "Detener";
        // Cambiar la clase
        btnTranscribir.classList.remove('btn-primary')
        btnTranscribir.classList.add('btn-danger')
        // Ejecuta la función para iniciar el proceso de transcripción
        iniciarTranscripcion(areaTextTranscripcion);
    } else if (btnTranscribir.innerHTML === "Detener") {
        // Cambia el texto a Transcribir
        btnTranscribir.innerText = "Transcribir";
        // Cambia el titulo a Transcribir
        btnTranscribir.title = "Transcribir";
        // Cambiar la clase
        btnTranscribir.classList.remove('btn-danger')
        btnTranscribir.classList.add('btn-primary')
        // Ejecuta la función que detiene el proceso de transcripción
        detenerTranscripcion();
    } else {
        // Alerta en caso de no reconocer el boton
        alert("No se reconoce boton!");
    };

    // Valida si el usuario esta ingresando desde protocolo seguro (https)
    /* if (location.protocol === 'https:') {
        // Permite validar si existe dispositivo de video y audio
        navigator.mediaDevices.enumerateDevices()
            .then((dispositivos) => {
                // Crea lista vaciá para almacenar los dispositivos de audio
                var dispositivosAudio = []
                // Recorrer el Array de dispositivos
                dispositivos.forEach((dispositivo) => {
                    // Valida si hay un micrófono para almacenar su información en la lista de dispositivos de audio
                    if (dispositivo.kind === 'audioinput') {
                        dispositivosAudio.push(dispositivo.kind + ": " + dispositivo.label + " id = " + dispositivo.deviceId);
                    };
                });
                // Valida si la cantidad de dispositivos de audio es mayor a cero (0)
                if (dispositivosAudio.length > 0) {

                } else {
                    btnTranscribir.disabled = true;
                    // Genera alerta cuando la computador no cuenta o no se reconoce el micrófono
                    alert("El computador no cuenta o no se reconoce el micrófono.");
                }
            })
            .catch((error) => { console.log(error); });
    } else {
        btnTranscribir.disabled = true;
        // Genera alerta indicando que la función se ejecuto en protocolo no seguro
        alert("Navegando en protocolo no seguro.");
    }; */
});

/* btnTranscribir.addEventListener("mouseover", () => {
    // Valida si el usuario esta ingresando desde protocolo seguro (https)
    if (location.protocol === 'https:') {
        // Permite validar si existe dispositivo de video y audio
        navigator.mediaDevices.enumerateDevices()
            .then((dispositivos) => {
                // Crea lista vaciá para almacenar los dispositivos de audio
                var dispositivosAudio = []
                // Recorrer el Array de dispositivos
                dispositivos.forEach((dispositivo) => {
                    // Valida si hay un micrófono para almacenar su información en la lista de dispositivos de audio
                    if (dispositivo.kind === 'audioinput') {
                        dispositivosAudio.push(dispositivo.kind + ": " + dispositivo.label + " id = " + dispositivo.deviceId);
                    };
                });
                // Valida si la cantidad de dispositivos de audio es mayor a cero (0)
                if (dispositivosAudio.length > 0) {
                    btnTranscribir.disabled = true;
                    // Solicita los permisos para acceder al micrófono
                    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
                        .then(() => {
                            btnTranscribir.disabled = false;
                            console.log("Usuario acepto los permisos");
                        })
                        .catch(() => {
                            btnTranscribir.disabled = true;
                            console.log("Usuario no acepto los permisos");
                        });
                } else {
                    btnTranscribir.disabled = true;
                    // Genera alerta cuando la computador no cuenta o no se reconoce el micrófono
                    alert("El computador no cuenta o no se reconoce el micrófono.");
                }
            })
            .catch((error) => { console.log(error); });
    } else {
        btnTranscribir.disabled = true;
        // Genera alerta indicando que la función se ejecuto en protocolo no seguro
        alert("Navegando en protocolo no seguro.");
    };
}); */