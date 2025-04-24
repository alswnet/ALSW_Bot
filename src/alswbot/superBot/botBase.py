import csv

class botBase:

    salvarChat: bool = True
    # Salvar la información del chat en un Archivo csv
    chatID: str = None
    # ID del chat

    def __init__(self) -> None:
        self.salvarChat = True
        self.chatID = "chepecarlo"

    def empezar(self) -> None:
        """
        Iniciar el bot
        """
        print("Iniciando el Bot")

    def procesarMensaje(self, mensaje) -> None:
        """
        Procesar el mensaje del chat
        """
        print(f"Mensaje: {mensaje}")
        
        if self.salvarChat:
            self.salvarMensaje(mensaje)
        
    def salvarMensaje(self, mensaje) -> None:
        """
        Salvar el mensaje en un archivo CSV
        """
        with open(f"chat_Base.csv", "a") as MiArchivo:
            escribir = csv.DictWriter(MiArchivo, fieldnames=mensaje.keys())
            escribir.writeheader()
            escribir.writerow(mensaje)