
import argparse
from bot.twitchbot import twithbot

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)

def ArgumentosCLI():
    parser = argparse.ArgumentParser(prog="alswbot", description='Bot para chat de ALSW')
    parser.add_argument("--twitch", '-t', help="Activar Bot Twitch", action="store_true")

    return parser.parse_args()
    

def main():
    logger.info("Iniciando el bot")
    args = ArgumentosCLI()
    bot = twithbot()
    bot.conectar()


if __name__ == '__main__':
    main()