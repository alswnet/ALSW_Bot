import csv

from alswbot.MiLibrerias import ConfigurarLogging, SalvarArchivo, SalvarValor

logger = ConfigurarLogging(__name__)


def SalvarMensaje(Archivo, Tiempo, Usuario, Mensaje):
    Campos = ["tiempo", "usuario", "mensaje"]
    Data = {"tiempo": Tiempo, "usuario": Usuario, "mensaje": Mensaje}
    salvarCSV(Archivo, Campos, Data)


def SalvarDonaciones(Archivo, Tiempo, Usuario, Monto):
    Campos = ["tiempo", "usuario", "monto"]
    Data = {"tiempo": Tiempo, "usuario": Usuario, "monto": Monto}
    salvarCSV(Archivo, Campos, Data)


def SalvarComando(Archivo, Tiempo, Usuario, Comando, Valor):
    Campos = ["tiempo", "usuario", "comando", "valor"]
    Data = {"tiempo": Tiempo, "usuario": Usuario, "comando": Comando, "valor": Valor}
    # SalvarCSV(Archivo, Campos, Data)
    salvarCSV(Archivo, Data.keys())


def salvarCSV(Archivo, Data):
    with open(Archivo, "a") as MiArchivo:
        escribir = csv.DictWriter(MiArchivo, fieldnames=Data.keys())
        escribir.writerow(Data)
