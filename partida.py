# partida.py
from cartas import crear_baraja, barajar

class Partida:
    def __init__(self, jugadores):
        self.jugadores = jugadores
        self.deck = crear_baraja()
        barajar(self.deck)
        self.turn = 0
        self.current_player = None

    def repartir_inicial(self):
        for jugador in self.jugadores:
            if self.deck:
                jugador.mano.append(self.deck.pop(0))

    def siguiente_jugador(self):
        # Selecciona al siguiente jugador que no esté eliminado
        while True:
            self.current_player = self.jugadores[self.turn % len(self.jugadores)]
            self.turn += 1
            if not self.current_player.eliminado:
                break
        return self.current_player

    def robar_carta(self, jugador):
        if self.deck:
            carta = self.deck.pop(0)
            jugador.mano.append(carta)
            return carta
        return None

    def hay_baraja(self):
        return bool(self.deck)

    def determinar_ganador(self):
        activos = [j for j in self.jugadores if not j.eliminado]
        if len(activos) == 1:
            return activos[0]
        if not self.deck and activos:
            # Se determina el ganador por el valor de la carta en mano
            winner = max(activos, key=lambda j: j.mano[0].valor if j.mano else 0)
            return winner
        return None
