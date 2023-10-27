# Api de intragracion para modelo de transcriptor con whisper y CMUSphinx

La siguiente api integra dos modelos de IA para realizar transcripciones ya sea con whisper o un modelo propio entrenado a partir del CMUSphinx.

# Instalación

1) Instalar requirements.txt 

```python
    pip install -r requirements.txt
```
2) Instalar dependencias del hardware a usar

```python
    # Para GPU
    pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
    # Solo CPU
    pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
```
3) Instalar ffmpeg en el sistema operativo

https://ffmpeg.org/download.html

4) Extras
instalar sockey io en el server
pip install flask-socketio

En el cliente se usa libreria de socket.io y peerJS