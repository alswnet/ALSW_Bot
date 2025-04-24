# https://pypi.org/project/pytchat/

# Nueva libreria a estudiar
# https://github.com/xenova/chat-downloader

import json
import re
import signal
import sys
import time

import pytchat
from alswbot.MiLibrerias import ConfigurarLogging, EnviarMensajeMQTT, SalvarValor

from .funcionesbot import SalvarComando, SalvarDonaciones, SalvarMensaje

logger = ConfigurarLogging(__name__)

ExprecionColores = (
    "\#[a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9][a-fA-f0-9]"
)
ComandosColor = ["base", "linea", "fondo"]
ComandosPremium = ["apagar"]
Colores = [
    "rojo",
    "azul",
    "verde",
    "blanco",
    "gris",
    "aqua",
    "amarillo",
    "naranja",
    "morado",
    "rosado",
]


def sigint_handler(signal, frame):
    print("Interrupted")
    sys.exit(0)


def ChatYoutube(IdVideo, Salvar=False):
    # TODO: que se pueda matar jajaja
    signal.signal(signal.SIGINT, sigint_handler)
    # try:
    espera = 3
    intentos = 3
    while intentos > 0:
        # chat = None
        # try:
        chat = pytchat.create(video_id=IdVideo)
        while chat.is_alive():
            for Mensaje in chat.get().sync_items():
                print(Mensaje)
                Mensaje.IdVideo = IdVideo
                # Mensaje.texto = Mensaje.message.lower()
                # Mensaje.texto = Mensaje.message
                FiltrarPreguntas(Mensaje, Salvar)

                if not (Mensaje.author.isChatModerator or Mensaje.author.isChatOwner):
                    FiltrarMods(Mensaje, Salvar)

                if (
                    Mensaje.author.isChatSponsor
                    or Mensaje.type == "superChat"
                    or Mensaje.author.isChatModerator
                    or Mensaje.author.isChatOwner
                ):
                    FiltrarComandoPremium(Mensaje)

                esPresente = FiltrarPresente(Mensaje, Salvar)
                esColor = FiltrarColor(Mensaje, Salvar)
                if not esColor and not esPresente:
                    chatMQTT(Mensaje)

                SalvarMensajes(Mensaje.IdVideo, Mensaje, Salvar)
            # except KeyboardInterrupt:
            #     logger.info("Saliendo del Chat")
            #     exit()
            #     if chat is not None:
            #         chat.terminate()
        intentos = intentos - 1
        logger.info(f"Reintegrando vigila chat {IdVideo}")
        print("-" * 100)
        time.sleep(espera)
    print("terminando el programa")
    # except KeyboardInterrupt:
    #     logger.info("Saliendo del Chat")
    #     exit()
    # if chat is not None:
    #     chat.terminate()


def chatMQTT(mensaje):
    miembro: str= "no"
    if mensaje.author.isChatSponsor:
        miembro = "si"

    mensaje = {
        "nombre": mensaje.author.name,
        "texto": mensaje.message,
        "imagen": mensaje.author.imageUrl,
        "miembro": miembro,
    }

    mensaje = json.dumps(mensaje)

    EnviarMensajeMQTT("alsw/chat/mensajes", mensaje)


def SalvarMensajes(IdVideo, mensaje, Salvar):
    if mensaje.type == "superChat":
        logger.info(f"SuperChat [{mensaje.author.name}]{mensaje.amountString}")
        if Salvar:
            SalvarDonaciones(
                f"{IdVideo}_SuperChat.csv",
                mensaje.datetime,
                mensaje.author.name,
                mensaje.amountString,
            )

        mienbro = "no"
        if mensaje.author.isChatSponsor:
            mienbro = "si"

        mensaje = {
            "nombre": mensaje.author.name,
            "texto": f"{mensaje.amountString}",
            "imagen": mensaje.author.imageUrl,
            "miembro": mienbro,
        }

        mensaje = json.dumps(mensaje)

        EnviarMensajeMQTT("alsw/chat/donar", mensaje)

    if mensaje.author.isChatSponsor:
        logger.info(f"Miembro >>>>{mensaje.author.name}<<<<")
        if Salvar:
            SalvarMensaje(
                f"{IdVideo}_Miembros.csv",
                mensaje.datetime,
                mensaje.author.name,
                mensaje.message,
            )
    else:
        if Salvar:
            SalvarMensaje(
                f"{IdVideo}_YT.csv",
                mensaje.datetime,
                mensaje.author.name,
                mensaje.message,
            )

    logger.info(
        f"{mensaje.datetime} - [{mensaje.type}] [{mensaje.author.name}]- {mensaje.message}"
    )

    print(mensaje)


def FiltrarColor(mensaje, Salvar):
    if not FiltranChat(mensaje.message, "color"):
        return False

    Comando = FiltrarChatComando(mensaje.message, ComandosColor)
    if Comando is None:
        Comando = ComandosColor[0]

    Color = BuscarColor(mensaje.message)
    if Color is None:
        return False

    if Salvar:
        SalvarComando(
            f"{mensaje.IdVideo}_Color.csv",
            mensaje.datetime,
            mensaje.author.name,
            Comando,
            Color,
        )

    logger.info(f"Comando [{Comando}]{Color} por {mensaje.author.name}")
    EnviarMensajeMQTT(f"/fondo/color/{Comando}", Color)

    mienbro = "no"
    if mensaje.author.isChatSponsor:
        mienbro = "si"

    mensaje = {
        "nombre": mensaje.author.name,
        "texto": f"color/{Comando}-{Color}",
        "imagen": mensaje.author.imageUrl,
        "miembro": mienbro,
    }

    mensaje = json.dumps(mensaje)

    EnviarMensajeMQTT("alsw/chat/comando", mensaje)

    return True


def FiltrarPresente(mensaje, salvar):
    if not FiltranChat(mensaje.message, "presente"):
        return False

    nombre = mensaje.author.name
    canal = mensaje.author.channelId
    miembro = mensaje.author.isChatSponsor

    if miembro:
        logger.info(
            f"Presente Patrocinador {nombre} - https://www.youtube.com/channel/{canal}"
        )
    else:
        logger.info(f"Presente {nombre} - https://www.youtube.com/channel/{canal}")

    if salvar:
        SalvarValor(f"{mensaje.IdVideo}_Presente.json", canal, nombre, False)

    mienbro = "no"
    if mensaje.author.isChatSponsor:
        mienbro = "si"

    mensaje = {
        "nombre": mensaje.author.name,
        "texto": "Presente",
        "imagen": mensaje.author.imageUrl,
        "miembro": mienbro,
    }

    mensaje = json.dumps(mensaje)

    EnviarMensajeMQTT("alsw/chat/comando", mensaje)

    return True


def FiltrarPreguntas(Mensaje, Salvar):
    if FiltranChat(Mensaje.message, "pregunta") or FiltranChat(Mensaje.message, "?"):
        logger.info(f"Pregunta de {Mensaje.author.name} {Mensaje.message}")
        if Salvar:
            SalvarComando(
                f"{Mensaje.IdVideo}_Pregunta.csv",
                Mensaje.datetime,
                Mensaje.author.name,
                "Pregunta",
                Mensaje.message,
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
                    "opciones": {
                        "mensaje": f"{Mensaje.author.name} pregunta, si estan grabando, Gracias"
                    },
                },
            ],
        }
        Comando = json.dumps(Comando)
        EnviarMensajeMQTT("/alsw/evento/ryuk", Comando)


def FiltranChat(Mensaje, Palabra):
    if not Mensaje or not Palabra:
        return False

    if Palabra.lower() in Mensaje.lower():
        return True

    return False


def FiltrarChatComando(Mensaje, Comandos):
    if not Mensaje or not Comandos:
        return None

    for Comando in Comandos:
        if Comando.lower() in Mensaje.lower():
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


def FiltrarComandoPremium(Mensaje):

    if FiltranChat(Mensaje.message, "apagar"):

        print(f"Comando apagar estudio {mensaje.author.name}")

        EnviarMensajeMQTT("alsw/estudio/estado/t", "c")

        mensaje = {
            "nombre": mensaje.author.name,
            "texto": "apagar",
            "imagen": mensaje.author.imageUrl,
        }

        mensaje = json.dumps(mensaje)

        EnviarMensajeMQTT("alsw/chat/comando", mensaje)
