import csv
import json
import multiprocessing
from alswbot.superBot.mensajeBot import mensajeBot
from alswbot.MiLibrerias.FuncionesMQTT import EnviarMensajeMQTT
from datetime import datetime


class botBase:

    salvarChat: bool = True
    # Salvar la información del chat en un Archivo csv
    chatID: str = None
    # ID del chat
    conectado: bool = False
    # Indica si el bot está conectado al chat

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

        self.chatMQTT(mensaje)
        self.mensajePresente(mensaje)

    def procesarDonacion(self, mensaje: mensajeBot) -> None:
        """
        Procesar la donación del chat
        """
        print(f"Donación {mensaje.nombre} a {mensaje.texto}")

        if self.salvarChat:
            self.salvarMensaje(mensaje, "donacion")

        self.chatMQTT(mensaje, "donar")

    def salvarMensaje(self, mensaje: mensajeBot, prefijo: str = None) -> None:
        """
        Salvar el mensaje en un archivo CSV
        """

        dataMensaje = {
            "nombre": mensaje.nombre,
            "id": mensaje.id,
            "texto": mensaje.texto,
            "canal": mensaje.canal,
            "imagen": mensaje.imagen,
        }

        fechaActual = datetime.now().strftime("%d-%m-%Y")
        nombreArchivo = f"chat_base_{fechaActual}.csv"

        if prefijo:
            nombreArchivo = f"{prefijo}_{nombreArchivo}"

        self.salvarCSV(dataMensaje, nombreArchivo)

    def salvarCSV(self, data: dict, nombreArchivo: str) -> None:
        """
        Salvar el mensaje en un archivo CSV
        """

        with open(nombreArchivo, "a") as MiArchivo:

            fieldnames = data.keys()

            escribir = csv.DictWriter(MiArchivo, fieldnames=fieldnames)

            if MiArchivo.tell() == 0:
                escribir.writeheader()

            escribir.writerow(data)

    def chatMQTT(self, mensaje: mensajeBot, topic: str = "mensajes") -> None:

        self.mensajeMqttTablero(f"alsw/chat/{topic}", mensaje.toJson())

    def mensajeMqttTablero(self, topic, mensaje):
        procesoMQTT = multiprocessing.Process(
            target=EnviarMensajeMQTT, args=(topic, mensaje)
        )
        procesoMQTT.start()

    def mensajePresente(self, mensaje: mensajeBot):

        if not self.filtranChat(mensaje.texto, "!presente"):
            return

        if self.salvarChat:
            dataMensaje = {
                "nombre": mensaje.nombre,
                "id": mensaje.id,
                "canal": mensaje.canal,
                "texto": mensaje.texto,
                "imagen": mensaje.imagen,
            }

            fechaActual = datetime.now().strftime("%d-%m-%Y")
            nombreArchivo = f"presente_{fechaActual}.csv"

            self.salvarCSV(dataMensaje, nombreArchivo)

        mensajeJson = {
            "nombre": mensaje.nombre,
            "texto": "Presente",
            "imagen": mensaje.imagen,
            "miembro": mensaje.miembro,
        }

        mensajeMQTT = json.dumps(mensajeJson)

        self.mensajeMqttTablero("alsw/chat/comando", mensajeMQTT)

        mensajeJson = {
            "nombre": mensaje.nombre,
            "id_youtube": mensaje.id,
            "imagen": mensaje.imagen,
            "miembro": mensaje.miembro,
        }

        mensajeMQTT = json.dumps(mensajeJson)

        self.mensajeMqttTablero("alsw/notificacion/presente", mensajeMQTT)

    def filtranChat(self, textMensaje, Palabra):
        if not textMensaje or not Palabra:
            return False

        if Palabra.lower() in textMensaje.lower():
            return True

        return False
