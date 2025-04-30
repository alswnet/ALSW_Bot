import argparse

import alswbot.MiLibrerias as MiLibrerias
from alswbot.bot.monitorChat import monitorChat
from alswbot.bot.twitchbot import twithbot
from alswbot.superBot.botYoutube import BotYoutube
from alswbot.superBot.botTiktok import BotTiktok

logger = MiLibrerias.ConfigurarLogging(__name__)


def ArgumentosCLI():
    parser = argparse.ArgumentParser(prog="alswbot", description="Bot para chat de ALSW")
    parser.add_argument("--twitch", "-t", help="Activar Bot Twitch", action="store_true")
    parser.add_argument("--youtube", "-y", type=str, help="Activar Bot Youtube")
    parser.add_argument("--youtube2", help="Activar Bot Youtube V2", action="store_true")
    parser.add_argument("--tiktok", help="Activar Bot Tiktok", action="store_true")
    parser.add_argument("--ambos", help="Activar Ambos Bot Youtube y Tiktok", action="store_true")
    
    parser.add_argument("--youtube_id", help="ID de depuración para Youtube", type=str)
    parser.add_argument("--tiktok_id", help="ID de depuración para Tiktok", type=str)

    parser.add_argument("--noSalvar", "-no_s", help="No Salvar Chat en Archivo", action="store_true")
    return parser.parse_args()


def main():
    logger.info("Iniciando el bot")
    args = ArgumentosCLI()
    salvarChar = True
    if args.noSalvar:
        salvarChar = False

    if args.youtube:
        Youtube = monitorChat(args.youtube)
        Youtube.salvarChat = salvarChar
        # Youtube.duennoMiembro = True
        Youtube.empezar()
    if args.twitch:
        bot = twithbot()
        bot.conectar()

    if args.tiktok:
        logger.info("Activando Bot Tiktok")
        botTiktok = BotTiktok()
        if args.tiktok_id:
            botTiktok.chatID = args.tiktok_id
        botTiktok.empezar()
    elif args.youtube2:
        logger.info("Activando Bot youtube V2")
        botYoutube = BotYoutube()
        if args.youtube_id:
            botYoutube.chatID = args.youtube_id
        botYoutube.empezar()
    elif args.ambos:
        logger.info("Activando Bot Youtube y Tiktok")
        botYoutube = BotYoutube()
        if args.youtube_id:
            botYoutube.chatID = args.youtube_id
        botYoutube.empezar()
        botTiktok = BotTiktok()
        if args.tiktok_id:
            botTiktok.chatID = args.tiktok_id
        botTiktok.empezar()


if __name__ == "__main__":
    main()
