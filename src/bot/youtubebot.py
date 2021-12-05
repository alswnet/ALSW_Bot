# https://pypi.org/project/pytchat/
import pytchat
import re

from MiLibrerias import ConfigurarLogging
from MiLibrerias import EnviarMensajeMQTT
from .funcionesbot import SalvarMensaje, SalvarDonaciones, SalvarComando

logger = ConfigurarLogging(__name__)

ExprecionColores = "\#[a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9]"
ComandosColor = ["base", "linea" "fondo"]
Colores = ["rojo", "azul", "verde", "blanco", "gris", "aqua", "amarillo", "naranja", "morado", "rosado"]


def ChatYoutube(IdVideo, Salvar=False):
    chat = pytchat.create(video_id=IdVideo)
    while chat.is_alive():
        try:
            for Mensaje in chat.get().sync_items():
                Mensaje.IdVideo = IdVideo
                Mensaje.message = Mensaje.message.lower()
                SalvarMensajes(Mensaje.IdVideo, Mensaje, Salvar)
                FiltrarColor(Mensaje, Salvar)
        except KeyboardInterrupt:
            logger.info("Saliendo del Chat")
            chat.terminate()


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
        return

    Comando = FiltrarChatComando(Mensaje.message, ComandosColor)
    if Comando is None:
        Comando = ComandosColor[0]

    Color = BuscarColor(Mensaje.message)
    if Color is None:
        return

    if Salvar:
        SalvarComando(f"{Mensaje.IdVideo}_Color.csv", Mensaje.datetime, Mensaje.author.name, Comando, Color)

    logger.info(f"Comando [{Comando}]{Color} por {Mensaje.author.name}")
    EnviarMensajeMQTT(f"/fondo/color/{Comando}", Color)


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
