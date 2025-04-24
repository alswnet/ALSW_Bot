
class mensajeBot:
    nombre: str = None
    id: str = None
    texto: str = None
    imagen: str = None
    canal: str = None
    miembro: bool = False
    # Apoya en canal con una contribución monetaria
    
    def __str__(self):
        return (
            f"MensajeBot(\n"
            f"nombre='{self.nombre}', "
            f"id='{self.id}', "
            f"texto='{self.texto}', "
            f"imagen='{self.imagen}', "
            f"canal='{self.canal}'"
            f"\n)"
        )