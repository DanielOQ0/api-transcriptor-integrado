class whisperConfig():

    def __init__(self, modelo, dispositivo, tamLote, tipoComputo) -> None:
        self.modelo = modelo
        self.dispositivo = dispositivo
        self.tamLote = tamLote
        self.tipoComputo = tipoComputo

    def to_json(self):
        return {
            'modelo': self.modelo,
            'dispositivo': self.dispositivo,
            'tamLote': self.tamLote,
            'tipoComputo': self.tipoComputo
        }
