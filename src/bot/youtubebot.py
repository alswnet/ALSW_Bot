# https://pypi.org/project/pytchat/
import json
import re

import pytchat
from MiLibrerias import ConfigurarLogging, EnviarMensajeMQTT, SalvarValor

from .funcionesbot import SalvarComando, SalvarDonaciones, SalvarMensaje

logger = ConfigurarLogging(__name__)

ExprecionColores = "\#[a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9]"
ComandosColor = ["base", "linea", "fondo"]
Colores = ["rojo", "azul", "verde", "blanco", "gris", "aqua", "amarillo", "naranja", "morado", "rosado"]


def ChatYoutube(IdVideo, Salvar=False):
    chat = pytchat.create(video_id=IdVideo)
    while chat.is_alive():
        try:
            for Mensaje in chat.get().sync_items():
                Mensaje.IdVideo = IdVideo
                Mensaje.message = Mensaje.message.lower()
                SalvarMensajes(Mensaje.IdVideo, Mensaje, Salvar)
                esColor = FiltrarColor(Mensaje, Salvar)
                FiltrarPresente(Mensaje, Salvar)
                FiltrarPreguntas(Mensaje, Salvar)
                if not (Mensaje.author.isChatModerator or Mensaje.author.isChatOwner):
                    FiltrarMods(Mensaje, Salvar)
                if not esColor:
                    chatMQTT(Mensaje)
                    pass
        except KeyboardInterrupt:
            logger.info("Saliendo del Chat")
            chat.terminate()


def chatMQTT(mensaje):
    mensaje = {"nombre": mensaje.author.name, "texto": mensaje.message, "imagen": mensaje.author.imageUrl}

    mensaje = json.dumps(mensaje)

    EnviarMensajeMQTT("alsw/chat/mensajes", mensaje)


def SalvarMensajes(IdVideo, mensaje, Salvar):
    if mensaje.type == "superChat":
        logger.info(f"SuperChat [{mensaje.author.name}]{mensaje.amountString}")
        if Salvar:
            SalvarDonaciones(f"{IdVideo}_SuperChat.csv", mensaje.datetime, mensaje.author.name, mensaje.amountString)

    if mensaje.author.isChatSponsor:
        logger.info(f"Miembro >>>>{mensaje.author.name}<<<<")
        if Salvar:
            SalvarMensaje(f"{IdVideo}_Miembros.csv", mensaje.datetime, mensaje.author.name, mensaje.message)
    else:
        if Salvar:
            SalvarMensaje(f"{IdVideo}_YT.csv", mensaje.datetime, mensaje.author.name, mensaje.message)

    logger.info(f"{mensaje.datetime} - [{mensaje.type}] [{mensaje.author.name}]- {mensaje.message}")


def FiltrarColor(Mensaje, Salvar):
    if not FiltranChat(Mensaje.message, "color"):
        return False

    Comando = FiltrarChatComando(Mensaje.message, ComandosColor)
    if Comando is None:
        Comando = ComandosColor[0]

    Color = BuscarColor(Mensaje.message)
    if Color is None:
        return False

    if Salvar:
        SalvarComando(f"{Mensaje.IdVideo}_Color.csv", Mensaje.datetime, Mensaje.author.name, Comando, Color)

    logger.info(f"Comando [{Comando}]{Color} por {Mensaje.author.name}")
    EnviarMensajeMQTT(f"/fondo/color/{Comando}", Color)

    return True


def FiltrarPresente(Mensaje, salvar):
    if not FiltranChat(Mensaje.message, "presente"):
        return

    nombre = Mensaje.author.name
    canal = Mensaje.author.channelId
    miembro = Mensaje.author.isChatSponsor

    if miembro:
        logger.info(f"Presente Patrocinador {nombre} - https://www.youtube.com/channel/{canal}")
    else:
        logger.info(f"Presente {nombre} - https://www.youtube.com/channel/{canal}")

    if salvar:

        SalvarValor(f"{Mensaje.IdVideo}_Presente.json", canal, nombre, False)
        print(f"Salvando {nombre}")


def FiltrarPreguntas(Mensaje, Salvar):
    if FiltranChat(Mensaje.message, "pregunta") or FiltranChat(Mensaje.message, "?"):
        logger.info(f"Pregunta de {Mensaje.author.name} {Mensaje.message}")
        if Salvar:
            SalvarComando(
                f"{Mensaje.IdVideo}_Pregunta.csv", Mensaje.datetime, Mensaje.author.name, "Pregunta", Mensaje.message
            )


def FiltrarMods(Mensaje, Salvar):

    if FiltranChat(Mensaje.message, "grabando"):
        Comando = {
            "nombre": "Pregunta Grabando",
            "accion": "macro",
            "opciones": [
                {"accion": "notificacion", "opciones": {"texto": "Pregunta si Grabas"}},
                {
                    "nombre": "Sonido",
                    "accion": "textovoz",
                    "opciones": {"mensaje": f"{Mensaje.author.name} pregunta, si estan grabando, Gracias"},
                },
            ],
        }
        Comando = json.dumps(Comando)
        EnviarMensajeMQTT("/alsw/evento/ryuk", Comando)


def FiltranChat(Mensaje, Palabra):
    if not Mensaje or not Palabra:
        return False

    if Palabra in Mensaje:
        return True

    return False


def FiltrarChatComando(Mensaje, Comandos):
    if not Mensaje or not Comandos:
        return None

    for Comando in Comandos:
        if Comando in Mensaje:
            return Comando

    return None


def BuscarColor(Mensaje):
    Color = FiltrarChatComando(Mensaje, Colores)
    if Color is None:
        return FiltrarExprecion(Mensaje, ExprecionColores)
    return Color


def FiltrarExprecion(Mensaje, Expresion):
    valor = re.findall(Expresion, Mensaje)
    if valor:
        return valor[0]
    return None
