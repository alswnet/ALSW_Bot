
import socket
from collections import namedtuple

from MiLibrerias import ConfigurarLogging

logger = ConfigurarLogging(__name__)


from MiLibrerias import ObtenerValor
from MiLibrerias import EnviarMensajeMQTT

colores = ["rojo", "azul", "verde", "blanco", "gris",
           "aqua", "amarillo", "naranja", "morado", "rosado"]

Mensaje = namedtuple(
    'Message',
    'prefix user channel irc_command irc_args text text_command text_args',
)

COMANDOS_BASAS = {
    '!discord': 'Unete {mensaje.user} a nuestro discord https://nocheprogramacion.com/discord',
    '!youtube': 'Subcribete a Canal de Youtube https://youtube.com/alswnet?sub_confirmation=1, {mensaje.user}'
}



def holabot(mensaje):
    print(f"el {mensaje}")

class twithbot:
    
    def __init__(self):
        logger.info("Creando Bot de Twitch")
        self.irc_server = 'irc.twitch.tv'
        self.irc_port = 6667
        self.oauth_token =  ObtenerValor("data/twitch.json", 'token')
        self.usuario =  ObtenerValor("data/twitch.json", 'usuario')
        self.canales = ObtenerValor("data/twitch.json", 'canales')
        self.comandos_extras = {
            '!ping': self.responder_ping,
            '!colorlinea': self.funcion_color_linea
        }

    def conectar(self):
        self.irc = socket.socket()
        self.irc.connect((self.irc_server, self.irc_port))
        self.enviar_commando(f'PASS {self.oauth_token}')
        self.enviar_commando(f'NICK {self.usuario}')
        for canal in self.canales:
            self.enviar_commando(f'JOIN #{canal}')
            self.enviar_privado(canal, "ALSWbot Activo")
        self.loop_mensajes()
    
    def enviar_privado(self, canal, texto):
        self.enviar_commando(f'PRIVMSG #{canal} :{texto}')

    def enviar_commando(self, comando):
        if 'PASS' not in comando:
            print(f'< {comando}')
        self.irc.send((comando + '\r\n').encode())

    def obtener_usuario_prefix(self, prefix):
        dominio = prefix.split('!')[0]
        if dominio.endswith('.tmi.twitch.tv'):
            return dominio.replace('.tmi.twitch.tv', '')
        elif '.tmi.twitch.tv' not in dominio:
            return dominio
        return None

    def responder_ping(self, mensaje):
        text = f'hola {mensaje.user}, Pong!!'
        self.enviar_privado(mensaje.channel, text)

    

    def funcion_color_linea(self, mensaje):
        # for mensaje_actual in mensaje.text_args:
        Color = self.Es_color(mensaje.text_args)
        if Color is None:
            texto = f'Ese color no estas en la lista'
        else:
            texto = f'Es un color - {Color}'
            logger.info(f"Cambiar a Clor {Color}")
            EnviarMensajeMQTT("fondo/color/linea", Color)
            # Enviar por mqtt

        self.enviar_privado(mensaje.channel, texto)

    def Es_color(self, MensajeColor):
        for mensaje in MensajeColor:
            if mensaje in colores:
                return mensaje
        return None

    def FiltranChat(Mensaje, Palabra):
        if Mensaje:
            Palabra = Palabra.lower()
            Mensaje = Mensaje.lower()
            if Palabra in Mensaje:
                return True
        return False

    def procesar_mensaje(self, mensaje_recivido):
        partes = mensaje_recivido.split(' ')

        prefix = None
        user = None
        channel = None
        text = None
        text_command = None
        text_args = None
        irc_command = None
        irc_args = None

        if partes[0].startswith(":"):
            prefix = partes[0][1:]
            user = self.obtener_usuario_prefix(prefix)
            partes = partes[1:]

        text_start = next(
            (idx for idx, parte in enumerate(partes) if parte.startswith(':')),
            None
        )
        if text_start is not None:
            text_parts = partes[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = ' '.join(text_parts)
            text_command = text_parts[0]
            text_args = text_parts[1:]
            partes = partes[:text_start]

        irc_command = partes[0]
        irc_args = partes[1:]

        hast_star = next(
            (idx for idx, parte in enumerate(irc_args) if parte.startswith('#')),
            None
        )
        if hast_star is not None:
            channel = irc_args[hast_star][1:]

        mensaje = Mensaje(
            prefix=prefix,
            user=user,
            channel=channel,
            text=text,
            text_command=text_command,
            text_args=text_args,
            irc_command=irc_command,
            irc_args=irc_args
        )

        return mensaje

    def manejar_comandos_base(self, mensaje, text_command, template):
        text = template.format(**{'mensaje': mensaje})
        self.enviar_privado(mensaje.channel, text)

    def manejar_mensaje(self, mensaje_recivido):
        # print(mensaje_recivido)

        if len(mensaje_recivido) == 0:
            return

        mensaje = self.procesar_mensaje(mensaje_recivido)

        if mensaje.irc_command == 'PING':
            self.enviar_commando('PONG :tmi.twitch.tv')
        elif mensaje.irc_command == 'PRIVMSG':
            # print(f"Comando {mensaje.text_command}")
            if mensaje.text_command in COMANDOS_BASAS:
                self.manejar_comandos_base(
                    mensaje,
                    mensaje.text_command,
                    COMANDOS_BASAS[mensaje.text_command]
                )
            if mensaje.text_command in self.comandos_extras:
                self.comandos_extras[mensaje.text_command](mensaje)

        print(f'> {mensaje}')

    def loop_mensajes(self):
        while True:
            mensajes_nuevos = self.irc.recv(2048).decode()
            for Mensaje_nuevo in mensajes_nuevos.split('\r\n'):
                self.manejar_mensaje(Mensaje_nuevo)
