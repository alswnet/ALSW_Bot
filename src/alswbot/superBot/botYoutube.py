# https://chat-downloader.readthedocs.io/en/latest/index.html

import multiprocessing

from chat_downloader import ChatDownloader
from alswbot.superBot.botBase import botBase
from alswbot.superBot.mensajeBot import mensajeBot
from datetime import datetime 

class BotYoutube(botBase):
    def __init__(self):
        super().__init__()
        self.tiposMensajes: dict =  ["messages", "superchat", "tickers"]

    def empezar(self):
        
        self.url: str = f"https://www.youtube.com/@{self.chatID}/live"

        print(f"Empezando Monitor de Chat - {self.url}")
        
        procesoBot = multiprocessing.Process(target=self.empezarBot)
        procesoBot.start()

    def empezarBot(self):
        """
        Iniciar el bot
        """
        
        self.chat = ChatDownloader().get_chat(self.url, message_groups=self.tiposMensajes)
        
        for mensajeYoutube in self.chat:
            
            if mensajeYoutube["message_type"] == "text_message":
                
                mensaje = mensajeBot()
                
                mensaje.nombre = mensajeYoutube["author"]["name"]
                mensaje.id = mensajeYoutube["author"]["id"]
                mensaje.texto = mensajeYoutube.get("message")
                mensaje.imagen = mensajeYoutube["author"]["images"][0]["url"]
                mensaje.canal = "youtube"
                
                self.procesarMensaje(mensaje)