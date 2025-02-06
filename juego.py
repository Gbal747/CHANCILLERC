# juego.py

from cartas import crear_baraja, barajar
import sys

class Jugador:
    def __init__(self, nombre):
        """
        Inicializa un jugador con un nombre y una mano (lista de cartas).
        """
        self.nombre = nombre
        self.mano = []  # Lista para almacenar las cartas del jugador

    def recibir_carta(self, carta):
        """
        Añade una carta a la mano del jugador.
        :param carta: Objeto Carta.
        """
        self.mano.append(carta)

    def mostrar_mano(self):
        """
        Retorna un string que muestra las cartas en la mano del jugador.
        """
        return ', '.join(str(carta) for carta in self.mano)

def crear_jugadores(numero):
    """
    Crea una lista de jugadores.
    :param numero: Número de jugadores (int)
    :return: Lista de objetos Jugador.
    """
    jugadores = []
    for i in range(numero):
        # Puedes pedir un nombre personalizado o utilizar un nombre por defecto
        nombre = f"Jugador {i + 1}"
        jugadores.append(Jugador(nombre))
    return jugadores

def repartir_cartas(jugadores, baraja, numero_cartas=1):
    """
    Reparte un número de cartas a cada jugador.
    :param jugadores: Lista de objetos Jugador.
    :param baraja: Lista de objetos Carta (baraja ya barajada).
    :param numero_cartas: Número de cartas a repartir a cada jugador (por defecto 1).
    """
    for jugador in jugadores:
        for _ in range(numero_cartas):
            if not baraja:
                print("La baraja se ha quedado sin cartas.")
                sys.exit(1)
            carta = baraja.pop(0)  # Se saca la carta de la parte superior
            jugador.recibir_carta(carta)

def main():
    try:
        numero_jugadores = int(input("Ingrese el número de jugadores: "))
        if numero_jugadores < 2:
            print("Se necesita al menos 2 jugadores para jugar.")
            return
    except ValueError:
        print("Por favor ingrese un número válido.")
        return

    # Crear jugadores
    jugadores = crear_jugadores(numero_jugadores)

    # Crear y barajar la baraja
    baraja = crear_baraja()
    barajar(baraja)

    # Repartir 1 carta a cada jugador
    repartir_cartas(jugadores, baraja, numero_cartas=1)

    # Mostrar las cartas que recibió cada jugador
    print("\nCartas repartidas:")
    for jugador in jugadores:
        print(f"{jugador.nombre}: {jugador.mostrar_mano()}")

if __name__ == "__main__":
    main()
