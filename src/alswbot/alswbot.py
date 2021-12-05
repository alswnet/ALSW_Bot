
import argparse
from bot.twitchbot import twithbot
from bot.youtubebot import ChatYoutube

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)

def ArgumentosCLI():
    parser = argparse.ArgumentParser(prog="alswbot", description='Bot para chat de ALSW')
    parser.add_argument("--twitch", '-t', help="Activar Bot Twitch", action="store_true")
    parser.add_argument("--youtube", '-y', help="Activar Bot Youtube")

    parser.add_argument("--salvar", '-s', help="Salvar Chat en Archivo", action="store_true")
    return parser.parse_args()
    

def main():
    logger.info("Iniciando el bot")
    args = ArgumentosCLI()
    if args.youtube:
        print(f"valor de youtube {args.youtube}")
        ChatYoutube(args.youtube, args.salvar)
    if args.twitch:
        bot = twithbot()
        bot.conectar()


if __name__ == '__main__':
    main()