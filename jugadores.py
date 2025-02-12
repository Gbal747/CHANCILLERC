# jugadores.py

class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mano = []      # Lista de cartas
        self.eliminado = False
        self.protegido = False

    def mostrar_mano(self):
        return ', '.join(str(carta) for carta in self.mano)
