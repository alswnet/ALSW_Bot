# https://github.com/isaackogan/TikTokLive
import multiprocessing
import asyncio
import time

from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    CommentEvent,
    ConnectEvent,
    LikeEvent,
    GiftEvent,
)
from TikTokLive.client.errors import UserOfflineError

from alswbot.superBot.botBase import botBase
from alswbot.superBot.mensajeBot import mensajeBot


class BotTiktok(botBase):
    def __init__(self):
        super().__init__()

    def empezar(self):

        self.url: str = f"https://www.tiktok.com/@{self.chatID}/live"

        print(f"Empezando Monitor de Chat - {self.url}")
        super().empezar()

        procesoBot = multiprocessing.Process(target=self.empezarBot)
        procesoBot.start()

    def empezarBot(self):
        """
        Iniciar el bot
        """

        self.chat: TikTokLiveClient = TikTokLiveClient(unique_id=self.chatID)
        estado = self.chat.is_live()
        print(f"Conectado {estado}")

        self.chat.add_listener(ConnectEvent, self.conectarTiktok)
        self.chat.add_listener(DisconnectEvent, self.desconectarTiktok)
        self.chat.add_listener(CommentEvent, self.comentarTiktok)
        self.chat.add_listener(LikeEvent, self.likeTiktok)
        self.chat.add_listener(GiftEvent, self.giftTiktok)

        while True:

            if not self.conectado:
                try:
                    self.chat.run()
                except UserOfflineError:
                    print("El usuario está offline")
                except Exception as e:
                    print(f"Error al conectar: {e}")
                except KeyboardInterrupt:
                    print("Interrupción del usuario, cerrando el bot...")
                    self.chat.stop()
                    exit(0)
                print("Reintentando en 10 segundos...")
                time.sleep(10)

    def conectarTiktok(self, event: ConnectEvent):
        print(f"Conectado a @{event.unique_id}")
        self.conectado = True

    def desconectarTiktok(self, event: DisconnectEvent):
        print(f"Desconectado de @{event.unique_id}")
        self.conectado = False

    def comentarTiktok(self, event: CommentEvent):

        urlImagen: str = event.user_info.avatar_thumb.m_urls[0]

        mensaje = mensajeBot()

        mensaje.nombre = event.user.nickname
        mensaje.id = event.user.id
        mensaje.texto = event.comment
        mensaje.imagen = urlImagen
        mensaje.canal = "tiktok"

        self.procesarMensaje(mensaje)

    def likeTiktok(self, event: LikeEvent):

        print(f"Like de {event.user.nickname} Total: {event.count}")
        print(f"Like Total : {event.total}")

    def giftTiktok(self, event: GiftEvent):

        urlImagen: str = event.gift.image.m_urls[0]

        mensaje = mensajeBot()

        mensaje.nombre = event.user.unique_id
        mensaje.id = event.user.id
        mensaje.texto = f"{event.gift.name}-{event.gift.diamond_count}"
        mensaje.imagen = urlImagen
        mensaje.canal = "tiktok"

        if event.gift.streakable and not event.streaking:
            if event.repeat_count > 1:
                mensaje.texto = f"{event.repeat_count} x {mensaje.texto}"

        self.procesarDonacion(mensaje)
