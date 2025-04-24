from chat_downloader import ChatDownloader
from alswbot.superBot.botBase import botBase
from alswbot.superBot.mensajeBot import mensajeBot
from datetime import datetime 

class BotYoutube(botBase):
    def __init__(self):
        super().__init__()
        self.tiposMensajes: dict =  ["messages", "superchat", "tickers"]

    def empezar(self):
        
        self.chatID = "LofiGirl"
        
        self.url: str = f"https://www.youtube.com/@{self.chatID}/live"

        print(f"Empezando Monitor de Chat - {self.url}")
        
        self.chat = ChatDownloader().get_chat(self.url, message_groups=self.tiposMensajes)
        
        for mensajeYoutube in self.chat:
            
            if mensajeYoutube["message_type"] == "text_message":
                
                mensaje = mensajeBot()
                
                mensaje.nombre = mensajeYoutube["author"]["name"]
                mensaje.id = mensajeYoutube["author"]["id"]
                mensaje.texto = mensajeYoutube.get("message")
                mensaje.imagen = mensajeYoutube["author"]["images"][0]["url"]
                mensaje.canal = "youtube"
                
                # urlImagen = mensajeYoutube["author"]["images"][0]["url"]
                
            
                # mensaje = {
                #     "nombre": mensajeYoutube["author"]["name"],
                #     "imagen": urlImagen,
                #     "id": mensajeYoutube["author"]["id"],
                #     "texto": mensajeYoutube.get("message"),
                #     "canal": "youtube"
                # }

                self.procesarMensaje(mensaje)
