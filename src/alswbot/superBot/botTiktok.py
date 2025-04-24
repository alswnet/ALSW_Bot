# https://github.com/isaackogan/TikTokLive
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, ConnectEvent, LikeEvent

from alswbot.superBot.botBase import botBase
from alswbot.superBot.mensajeBot import mensajeBot


class BotTiktok(botBase):
    def __init__(self):
        super().__init__()
        

    def empezar(self):
        
        self.chatID = "castordie"
        self.url: str = f"https://www.tiktok.com/@{self.chatID}/live"

        print(f"Empezando Monitor de Chat - {self.url}")
        super().empezar()
        
        self.chat: TikTokLiveClient = TikTokLiveClient(unique_id=self.chatID)
        
        self.chat.add_listener(ConnectEvent, self.conectarTiktok)
        self.chat.add_listener(CommentEvent, self.comentarTiktok)
        self.chat.add_listener(LikeEvent, self.likeTiktok)
        self.chat.run()
        
    def conectarTiktok(self, event: ConnectEvent):
        print(f"Connected to @{event.unique_id}!")
        
    def comentarTiktok(self, event: CommentEvent):
        
        urlImagen: str = event.user_info.avatar_thumb.m_urls[0]

        mensaje = mensajeBot()
        
        mensaje.nombre = event.user.nickname
        mensaje.id = event.user.id
        mensaje.texto = event.comment
        mensaje.imagen = urlImagen
        mensaje.canal = "tiktok"
        
        # mensaje = {
        #     "nombre": event.user.nickname,
        #     "id": event.user.id,
        #     "texto": event.comment,
        #     "imagen": urlImagen,
        #     "canal": "tiktok"
        # }

        self.procesarMensaje(mensaje)
        
    def likeTiktok(self, event: LikeEvent):

        print(f"Like de {event.user.nickname} Total: {event.count}")
        print(f"Like Total : {event.total}")
