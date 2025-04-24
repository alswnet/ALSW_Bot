import csv
from alswbot.superBot.mensajeBot import mensajeBot

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

    def procesarMensaje(self, mensaje: mensajeBot) -> None:
        """
        Procesar el mensaje del chat
        """
        print(f"{mensaje.nombre} - {mensaje.texto}")
        
        if self.salvarChat:
            self.salvarMensaje(mensaje)
        
    def salvarMensaje(self, mensaje: mensajeBot) -> None:
        """
        Salvar el mensaje en un archivo CSV
        """
        
        mensaje_dict = {
        "nombre": mensaje.nombre,
        "id": mensaje.id,
        "texto": mensaje.texto,
        "canal": mensaje.canal,
        "imagen": mensaje.imagen,
        }
        
        with open(f"chat_Base.csv", "a") as MiArchivo:
            
            fieldnames = mensaje_dict.keys()
            
            escribir = csv.DictWriter(MiArchivo, fieldnames=fieldnames)
            
            if MiArchivo.tell() == 0:
                escribir.writeheader()
            
            escribir.writerow(mensaje_dict)