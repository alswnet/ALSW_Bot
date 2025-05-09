# https://github.com/xenova/chat-downloader

import json
import multiprocessing
import re

from chat_downloader import ChatDownloader

from alswbot.MiLibrerias import ConfigurarLogging, FuncionesArchivos, SalvarValor
from alswbot.MiLibrerias.FuncionesMQTT import EnviarMensajeMQTT

from .funcionesbot import salvarCSV

logger = ConfigurarLogging(__name__)


class monitorChat:
    def __init__(self, chatID):
        self.salvarChat = False
        self.chatID = chatID
        self.listaColores = FuncionesArchivos.ObtenerArchivo("data/color.json")
        self.listaAlgoritmo = FuncionesArchivos.ObtenerArchivo(
            "data/algoritmo.json")
        self.exprecionColores = "\#[a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9]"
        self.comandoColor = ["base", "linea", "fondo"]
        self.comandoTroll = {
            "arriba": "up",
            "abajo": "down",
            "derecha": "left",
            "izquierda": "right",
        }
        self.duennoMiembro = True

    def empezar(self):
        self.url = f"https://www.youtube.com/watch?v={self.chatID}"
        logger.info(f"Empezando Monitor de Chat - {self.url}")

        self.grupos = ["messages", "superchat", "tickers"]
        self.chat = ChatDownloader().get_chat(self.url, message_groups=self.grupos)

        for mensaje in self.chat:
            self.chat.print_formatted(mensaje)
            print(mensaje["author"])
            if "author" in mensaje:
                autor = mensaje["author"]

                if not "time_text" in mensaje:
                    mensaje["time_text"] = None

                if mensaje["message_type"] == "text_message":
                    self.filtrasMensajes(mensaje)
                elif mensaje["message_type"] == "paid_message":
                    self.filtroDonacion("Super Chat", mensaje)
                    self.filtrasMensajes(mensaje)
                elif mensaje["message_type"] == "paid_sticker":
                    self.filtroDonacion("Super strikers", mensaje)
                elif mensaje["message_type"] == "membership_item":
                    self.filtroDonacion("Nuevo Miembro", mensaje)
                else:
                    print(
                        f"Nombre: {mensaje['author']['name']} Tipo: {mensaje['message_type']}")

    def filtrasMensajes(self, mensaje):

        if mensaje["message"] is None:
            return

        esColor = self.filtrarColor(mensaje)
        esPresente = self.filtrarPresente(mensaje)
        self.filtrarMiembros(mensaje)

        if not esColor and not esPresente:
            self.chatMQTT(mensaje)

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

    def filtroTroll(self, mensaje):
        texto = mensaje["message"].lower()

        for troll in self.comandoTroll.keys():
            if "!" + troll in texto:
                print(f"Troleo de {mensaje['author']['name']} - {troll}")
                data = {
                    "nombre": f"Troleo de {mensaje['author']['name']} - {troll}",
                    "accion": "teclas",
                    "opciones": {"teclas": [self.comandoTroll[troll]]},
                }
                self.mensajeMqttTablero(f"alsw/evento/ryuk", json.dumps(data))
                salvarCSV(self.chatID + "_Troll.csv", data)
                return

    def buscarColor(self, mensaje):
        Color = self.filtrarChatComando(mensaje, self.listaColores)
        if Color is None:
            return self.FiltrarExprecion(mensaje, self.exprecionColores)
        return Color

    def filtrarColor(self, mensaje):
        texto = mensaje["message"].lower()

        comando = None
        for comandoActual in self.comandoColor:
            if "!" + comandoActual in texto:
                comando = comandoActual
        if "!color" in texto:
            comando = self.comandoColor[0]

        if comando is None:
            return False

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
        self.mensajeMqttTablero(f"alsw/fondoOBS/color/{comando}", color)

        miembro = self.esMiembro(mensaje)

        mensaje = {
            "nombre": nombre,
            "texto": f"color/{comando}-{color}",
            "imagen": mensaje["author"]["images"][0]["url"],
            "miembro": miembro,
        }

        mensaje = json.dumps(mensaje)

        self.mensajeMqttTablero("alsw/chat/comando", mensaje)

        return True

    def filtrarPresente(self, mensaje):
        if not self.filtranChat(mensaje["message"], "!presente"):
            return False

        nombre = mensaje["author"]["name"]
        canal = mensaje["author"]["id"]
        imagen = mensaje["author"]["images"][0]["url"]
        miembro = self.esMiembro(mensaje)

        if self.salvarChat:
            FuncionesArchivos.SalvarValor(
                f"{self.chatID }_Presente.json", canal, nombre, False)

        mensaje = {
            "nombre": nombre,
            "texto": "Presente",
            "imagen": imagen,
            "miembro": miembro,
        }

        mensaje = json.dumps(mensaje)

        self.mensajeMqttTablero("alsw/chat/comando", mensaje)

        mensaje = {
            "nombre": nombre,
            "id_youtube": canal,
            "imagen": imagen,
            "miembro": miembro,
        }

        mensaje = json.dumps(mensaje)
        self.mensajeMqttTablero("alsw/notificacion/presente", mensaje)

        return True

    def filtrarMiembros(self, mensaje):
        miembro = self.esMiembro(mensaje)
        if miembro:
            self.filtrarAltoritmo(mensaje)
            self.filtrarApagar(mensaje)
        self.filtroTroll(mensaje)

    def filtrarAltoritmo(self, mensaje):
        texto = mensaje["message"]
        if not self.filtranChat(texto, "!algoritmo"):
            return False

        comando = self.filtrarChatComando(texto, self.listaAlgoritmo)
        if comando is None:
            comando = self.listaAlgoritmo[0]

        if self.salvarChat:
            data = {
                "tiempo": mensaje["time_text"],
                "nombre": mensaje["author"]["name"],
                "comando": "algoritmo",
                "opcion": comando,
            }
            salvarCSV(self.chatID + "_Comando.csv", data)

        self.mensajeMqttTablero("alsw/fondoOBS/animacion", comando)
        return False

    def filtrarApagar(self, mensaje: dict[str, any]) -> bool:
        
        texto : str = mensaje["message"].lower()
        
        if "!apagar" in texto:
            print("Apagar estudio")
            EnviarMensajeMQTT("alsw/estudio/estado/t", "c")
            return True
        
        return False

    def filtroDonacion(self, tipo, mensaje):
        print(f"Mensaje {tipo}")

        monto = None
        nombre = mensaje["author"]["name"]
        if "money" in mensaje:
            monto = mensaje["money"]["text"]
            print(f"Monto {monto}")

        if self.salvarChat:
            data = {
                "tiempo": mensaje["time_text"],
                "tipo": tipo,
                "nombre": nombre,
                "monto": monto,
            }
            salvarCSV(self.chatID + "_Donacion.csv", data)

        miembro = self.esMiembro(mensaje)

        mensaje = {
            "nombre": nombre,
            "texto": f"{tipo} {monto}",
            "imagen": mensaje["author"]["images"][0]["url"],
            "miembro": miembro,
        }

        mensaje = json.dumps(mensaje)

        self.mensajeMqttTablero("alsw/chat/donar", mensaje)

    def chatMQTT(self, mensaje):

        miembro = self.esMiembro(mensaje)

        mensaje = {
            "nombre": mensaje["author"]["name"],
            "texto": mensaje["message"],
            "imagen": mensaje["author"]["images"][0]["url"],
            "miembro": miembro,
        }

        mensaje = json.dumps(mensaje)

        self.mensajeMqttTablero("alsw/chat/mensajes", mensaje)

    def esMiembro(self, mensaje):
        """
        El Mensaje es de miembro del canal
        """

        if "badges" in mensaje["author"]:
            for badges in mensaje["author"]["badges"]:
                titulo = badges["title"].lower()

                if "member" in titulo:
                    return True

                if self.duennoMiembro:
                    if "owner" in titulo or "moderator" in titulo:
                        return True
        return False

    def mensajeMqttTablero(self, topic, mensaje):
        procesoMQTT = multiprocessing.Process(
            target=EnviarMensajeMQTT, args=(topic, mensaje, None, None, None, None))
        procesoMQTT.start()
