import argparse

import MiLibrerias
from bot.monitorChat import monitorChat
from bot.twitchbot import twithbot

logger = MiLibrerias.ConfigurarLogging(__name__)


def ArgumentosCLI():
    parser = argparse.ArgumentParser(prog="alswbot", description="Bot para chat de ALSW")
    parser.add_argument("--twitch", "-t", help="Activar Bot Twitch", action="store_true")
    parser.add_argument("--youtube", "-y", type=str, help="Activar Bot Youtube")

    parser.add_argument("--noSalvar", "-no_s", help="No Salvar Chat en Archivo", action="store_true")
    return parser.parse_args()


def main():
    logger.info("Iniciando el bot")
    args = ArgumentosCLI()
    salvarChar = True
    if args.noSalvar is None or args.noSalvar:
        salvar = False

    if args.youtube:
        Youtube = monitorChat(args.youtube)
        Youtube.salvarChat = salvarChar
        # Youtube.duennoMiembro = True
        Youtube.empezar()
    if args.twitch:
        bot = twithbot()
        bot.conectar()


if __name__ == "__main__":
    main()
