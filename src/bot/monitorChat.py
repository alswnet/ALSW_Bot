import json
import multiprocessing
import re

from chat_downloader import ChatDownloader
from MiLibrerias import ConfigurarLogging, EnviarMensajeMQTT, FuncionesArchivos, SalvarValor

from .funcionesbot import salvarCSV

logger = ConfigurarLogging(__name__)


class monitorChat:
    def __init__(self, chatID):
        self.salvarChat = False
        self.chatID = chatID
        self.listaColores = FuncionesArchivos.ObtenerArchivo("data/color.json")
        self.exprecionColores = "\#[a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9]"
        self.comandoColor = ["base", "linea", "fondo"]

    def empezar(self):
        self.url = f"https://www.youtube.com/watch?v={self.chatID}"
        logger.info(f"Empezando Monitor de Chat - {self.url}")

        self.grupos = ["messages", "superchat", "tickers"]
        self.chat = ChatDownloader().get_chat(self.url, message_groups=self.grupos)

        for mensaje in self.chat:
            # chat.print_formatted(mensaje)
            if "author" in mensaje:
                autor = mensaje["author"]

                if mensaje["message_type"] == "text_message":
                    self.filtrasMensajes(mensaje)
                # elif mensaje["message_type"] == "paid_message":
                #     print(f"Super Chat")
                # elif mensaje["message_type"] == "paid_sticker":
                #     print(f"Super strikers")
                # elif mensaje["message_type"] == "membership_item":
                #     print(f"Nuevo miembro")
                else:
                    print(f"Nombre: {mensaje['author']['name']} Tipo: {mensaje['message_type']}")

    def filtrasMensajes(self, mensaje):

        if mensaje["message"] is None:
            return

        esColor = self.filtrarColor(mensaje)

        if not esColor:
            self.chatMQTT(mensaje)
            # self.chat.print_formatted(mensaje)

        data = {
            "tiempo": mensaje["time_text"],
            "nombre": mensaje["author"]["name"],
            "mensaje": mensaje["message"],
        }
        salvarCSV(self.chatID + ".cvs", data)

    def filtranChat(self, Mensaje, Palabra):
        if not Mensaje or not Palabra:
            return False

        if Palabra.lower() in Mensaje.lower():
            return True

        return False

    def filtrarChatComando(self, mensaje, comandos):
        if not mensaje or not comandos:
            return None

        for comando in comandos:
            if comando.lower() in mensaje.lower():
                return comando

        return None

    def FiltrarExprecion(self, mensaje, expresion):
        valor = re.findall(expresion, mensaje)
        if valor:
            return valor[0]
        return None

    def buscarColor(self, mensaje):
        Color = self.filtrarChatComando(mensaje, self.listaColores)
        if Color is None:
            return self.FiltrarExprecion(mensaje, self.exprecionColores)
        return Color

    def filtrarColor(self, mensaje):
        texto = mensaje["message"]
        if not self.filtranChat(texto, "!color"):
            return False

        comando = self.filtrarChatComando(texto, self.comandoColor)
        if comando is None:
            comando = self.comandoColor[0]

        color = self.buscarColor(texto)
        if color is None:
            return False

        nombre = mensaje["author"]["name"]

        if self.salvarChat:
            data = {
                "tiempo": mensaje["time_text"],
                "nombre": nombre,
                "comando": comando,
                "color": color,
            }
            salvarCSV(self.chatID + "_Color.csv", data)

        logger.info(f"Comando [{comando}]{color} por {nombre}")
        self.mensajeMQTT(f"/fondo/color/{comando}", color)

        mienbro = self.esMiembro(mensaje)

        mensaje = {
            "nombre": nombre,
            "texto": f"color/{comando}-{color}",
            "imagen": mensaje["author"]["images"][0]["url"],
            "miembro": mienbro,
        }

        mensaje = json.dumps(mensaje)

        self.mensajeMQTT("alsw/chat/comando", mensaje)

        return True

    def chatMQTT(self, mensaje):

        mienbro = self.esMiembro(mensaje)

        mensaje = {
            "nombre": mensaje["author"]["name"],
            "texto": mensaje["message"],
            "imagen": mensaje["author"]["images"][0]["url"],
            "miembro": mienbro,
        }

        mensaje = json.dumps(mensaje)

        self.mensajeMQTT("alsw/chat/mensajes", mensaje)

    def esMiembro(self, mensaje):
        mienbro = False
        if "badges" in mensaje["author"]:
            for badges in mensaje["author"]["badges"]:
                if "Member" in badges["title"]:
                    mienbro = True
        return mienbro

    def mensajeMQTT(self, topic, mensaje):
        procesoMQTT = multiprocessing.Process(target=EnviarMensajeMQTT, args=(topic, mensaje))
        procesoMQTT.start()
