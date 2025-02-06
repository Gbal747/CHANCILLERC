# partida.py

from cartas import crear_baraja, barajar
from juego import Jugador  # Usamos la clase Jugador definida en juego.py
import random

def aplicar_efecto(carta, jugador_actual, jugadores, baraja):
    """
    Aplica el efecto de la carta jugada por el jugador actual.
    Se solicitan objetivos y entradas según el efecto.
    """
    if carta.nombre == "Guardia":
        # Efecto: Adivinar la carta de otro jugador.
        print(f"{jugador_actual.nombre} juega {carta.nombre}")
        # Se muestran solo los jugadores activos (no eliminados) y que no estén protegidos.
        objetivos = [j for j in jugadores if j != jugador_actual and not j.eliminado and not j.protegido]
        if not objetivos:
            print("No hay objetivos disponibles para el Guardia.")
            return
        print("Selecciona el jugador al que deseas adivinar su carta:")
        for idx, obj in enumerate(objetivos):
            print(f"  {idx + 1}. {obj.nombre}")
        eleccion = int(input("Elige el número del jugador: "))
        objetivo = objetivos[eleccion - 1]
        adivinanza = input("¿Qué carta crees que tiene? (escribe el nombre): ")
        if any(c.nombre.lower() == adivinanza for c in objetivo.mano):
          if adivinanza == "guardia":  # 💡 Aquí evitamos que se elimine si es un Guardia
            print(f"{objetivo.nombre} tenía un Guardia, no puede ser eliminado.")
        else:
          print(f"¡Correcto! {objetivo.nombre} tenía {adivinanza} y queda eliminado.")
        objetivo.eliminado = True
        print("Adivinaste mal. No ocurre nada.")
    
    elif carta.nombre == "Sacerdote":
        # Efecto: Mirar la mano de otro jugador.
        print(f"{jugador_actual.nombre} juega {carta.nombre}")
        objetivos = [j for j in jugadores if j != jugador_actual and not j.eliminado]
        if not objetivos:
            print("No hay objetivos disponibles para el Sacerdote.")
            return
        print("Selecciona el jugador cuya mano deseas ver:")
        for idx, obj in enumerate(objetivos):
            print(f"  {idx + 1}. {obj.nombre}")
        eleccion = int(input("Elige el número del jugador: "))
        objetivo = objetivos[eleccion - 1]
        print(f"La mano de {objetivo.nombre} es: {objetivo.mostrar_mano()}")
    
    elif carta.nombre == "Baron":
        # Efecto: Comparar la carta en mano con la de otro jugador.
        print(f"{jugador_actual.nombre} juega {carta.nombre}")
        objetivos = [j for j in jugadores if j != jugador_actual and not j.eliminado and not j.protegido]
        if not objetivos:
            print("No hay objetivos disponibles para el Baron.")
            return
        print("Selecciona el jugador contra el que deseas comparar cartas:")
        for idx, obj in enumerate(objetivos):
            print(f"  {idx + 1}. {obj.nombre}")
        eleccion = int(input("Elige el número del jugador: "))
        objetivo = objetivos[eleccion - 1]
        # Se compara la carta que quedó en mano de cada uno.
        carta_objetivo = objetivo.mano[0]
        carta_jugador = jugador_actual.mano[0]
        print(f"{jugador_actual.nombre} tiene {carta_jugador} y {objetivo.nombre} tiene {carta_objetivo}")
        if carta_jugador.valor > carta_objetivo.valor:
            print(f"{objetivo.nombre} es eliminado.")
            objetivo.eliminado = True
        elif carta_objetivo.valor > carta_jugador.valor:
            print(f"{jugador_actual.nombre} es eliminado.")
            jugador_actual.eliminado = True
        else:
            print("Empate. Nadie es eliminado.")
    
    elif carta.nombre == "Doncella":
        # Efecto: Protección hasta el siguiente turno.
        print(f"{jugador_actual.nombre} juega {carta.nombre} y queda protegido hasta su próximo turno.")
        jugador_actual.protegido = True

    elif carta.nombre == "Príncipe":
        # Efecto: Forzar a otro jugador a descartar su mano.
        print(f"{jugador_actual.nombre} juega {carta.nombre}")
        objetivos = [j for j in jugadores if not j.eliminado]
        print("Selecciona el jugador que debe descartar su mano:")
        for idx, obj in enumerate(objetivos):
            print(f"  {idx + 1}. {obj.nombre}")
        eleccion = int(input("Elige el número del jugador: "))
        objetivo = objetivos[eleccion - 1]
        print(f"{objetivo.nombre} descarta {objetivo.mano[0]}")
        descartada = objetivo.mano.pop(0)
        if descartada.nombre == "Princesa":
            print(f"{objetivo.nombre} descartó la Princesa y queda eliminado.")
            objetivo.eliminado = True
        else:
            if baraja:
                nueva = baraja.pop(0)
                objetivo.mano.append(nueva)
                print(f"{objetivo.nombre} roba una nueva carta: {nueva}")
            else:
                print("La baraja está vacía. No se puede robar una nueva carta.")

    elif carta.nombre == "Chanciller":
    # Efecto: Robar dos cartas y elegir una para conservar.
        print(f"{jugador_actual.nombre} juega {carta.nombre}")

    if len(baraja) >= 2:
        cartas_robadas = [baraja.pop(0) for _ in range(2)]  # Roba dos cartas de la baraja
        cartas_totales = jugador_actual.mano + cartas_robadas  # Incluye su carta actual

        print("Tienes las siguientes cartas:")
        for idx, c in enumerate(cartas_totales):
            print(f"  {idx + 1}. {c.nombre}")  # Muestra todas las cartas disponibles

        try:
            eleccion = int(input("Elige la carta que deseas conservar (1, 2 o 3): ")) - 1
            if eleccion < 0 or eleccion >= len(cartas_totales):
                print("Selección inválida.")
                return
        except ValueError:
            print("Debes ingresar un número válido.")
            return

        # Se queda con la carta elegida
        jugador_actual.mano = [cartas_totales[eleccion]]

        # Las dos restantes deben colocarse en el orden que el jugador elija
        cartas_restantes = [c for i, c in enumerate(cartas_totales) if i != eleccion]

        print("Debes colocar las dos cartas restantes al final del mazo en el orden que quieras.")
        print("Elige el orden de las siguientes cartas:")
        print(f"  1. {cartas_restantes[0].nombre}")
        print(f"  2. {cartas_restantes[1].nombre}")

        try:
            orden = int(input("Elige qué carta irá primero en el mazo (1 o 2): ")) - 1
            if orden not in [0, 1]:
                print("Selección inválida.")
                return
        except ValueError:
            print("Debes ingresar un número válido.")
            return
        # Coloca las cartas en el mazo en el orden elegido
        baraja.append(cartas_restantes[orden])  # La primera seleccionada va al final
        baraja.append(cartas_restantes[1 - orden])  # La segunda seleccionada después
        print("No hay suficientes cartas en la baraja para el efecto del Chanciller.")
    
    elif carta.nombre == "Rey":
        # Efecto: Intercambiar la mano con la de otro jugador.
        print(f"{jugador_actual.nombre} juega {carta.nombre}")
        objetivos = [j for j in jugadores if j != jugador_actual and not j.eliminado and not j.protegido]
        if not objetivos:
            print("No hay objetivos disponibles para el Rey.")
            return
        print("Selecciona el jugador con quien intercambiar tu mano:")
        for idx, obj in enumerate(objetivos):
            print(f"  {idx + 1}. {obj.nombre}")
        eleccion = int(input("Elige el número del jugador: "))
        objetivo = objetivos[eleccion - 1]
        # Intercambio de la carta en mano (ya que se tiene una sola carta después de jugar).
        jugador_actual.mano[0], objetivo.mano[0] = objetivo.mano[0], jugador_actual.mano[0]
        print(f"{jugador_actual.nombre} y {objetivo.nombre} han intercambiado sus manos.")
    
    elif carta.nombre == "Condesa":
        # La Condesa no tiene efecto, pero se debe jugar obligatoriamente en ciertas condiciones.
        print(f"{jugador_actual.nombre} juega {carta.nombre}. Sin efecto adicional.")
    
    elif carta.nombre == "Princesa":
        # Efecto: Si se juega la Princesa, el jugador queda eliminado.
        print(f"{jugador_actual.nombre} juega {carta.nombre} y queda eliminado.")
        jugador_actual.eliminado = True

    elif carta.nombre == "Espía":
        # Para el Espía, si no se define un efecto concreto, se deja un mensaje.
        print(f"{jugador_actual.nombre} juega {carta.nombre}.")
        print("El efecto del Espía aún no se ha implementado.")
    
    else:
        print(f"{carta.nombre} no tiene un efecto implementado.")

def jugar_turno(jugador_actual, jugadores, baraja):
    """
    Ejecuta un turno para el jugador actual:
      - Resetea su protección.
      - El jugador roba una carta (si la baraja no está vacía).
      - Se muestra la mano y se solicita que elija la carta a jugar.
      - Se verifica la regla obligatoria de la Condesa.
      - Se aplica el efecto de la carta jugada.
    """
    # Al iniciar el turno se quita la protección (excepto si se desea conservarla solo durante el turno)
    jugador_actual.protegido = False

    # Robar una carta si es posible
    if baraja:
        nueva_carta = baraja.pop(0)
        jugador_actual.mano.append(nueva_carta)
        print(f"{jugador_actual.nombre} roba: {nueva_carta}")
    else:
        print("La baraja se ha agotado.")

    # Mostrar la mano (deberá tener 2 cartas)
    print(f"Mano de {jugador_actual.nombre}:")
    for idx, carta in enumerate(jugador_actual.mano):
        print(f"  {idx + 1}. {carta}")

    # Si se tiene la Condesa junto con el Rey o el Príncipe, se debe jugar la Condesa.
    jugar_condesa = False
    if any(c.nombre == "Condesa" for c in jugador_actual.mano) and \
       any(c.nombre in ["Rey", "Príncipe"] for c in jugador_actual.mano):
        print("Debes jugar la Condesa, ya que la tienes junto con el Rey o el Príncipe.")
        jugar_condesa = True

    if jugar_condesa:
        # Se selecciona automáticamente la Condesa.
        for idx, carta in enumerate(jugador_actual.mano):
            if carta.nombre == "Condesa":
                eleccion = idx + 1
                break
    else:
        eleccion = int(input("Elige la carta a jugar (ingresa el número): "))

    # Remover la carta jugada de la mano.
    carta_jugada = jugador_actual.mano.pop(eleccion - 1)
    print(f"{jugador_actual.nombre} juega {carta_jugada}")
    # Aplicar el efecto de la carta.
    aplicar_efecto(carta_jugada, jugador_actual, jugadores, baraja)

def determinar_ganador(jugadores, baraja):
    """
    Determina si hay un ganador.
      - Si solo queda un jugador sin eliminar, ese es el ganador.
      - Si la baraja se ha agotado, se determina el ganador por el valor de la carta en mano.
      - En otro caso, devuelve None.
    """
    activos = [j for j in jugadores if not j.eliminado]
    if len(activos) == 1:
        return activos[0]
    if not baraja:
        print("La baraja se ha agotado. Se determina el ganador por el valor de la carta en mano.")
        ganador = max(activos, key=lambda j: j.mano[0].valor)
        return ganador
    return None

def main():
    # Solicitar número de jugadores.
    try:
        num = int(input("Ingrese el número de jugadores (mínimo 2): "))
        if num < 2:
            print("Se necesita al menos 2 jugadores para jugar.")
            return
    except ValueError:
        print("Ingrese un número válido.")
        return

    # Crear jugadores solicitando su nombre.
    jugadores = []
    for i in range(num):
        nombre = input(f"Ingrese el nombre del Jugador {i + 1}: ").strip()
        # Si el usuario no ingresa un nombre, se asigna un nombre por defecto.
        if not nombre:
            nombre = f"Jugador {i + 1}"
        jugador = Jugador(nombre)
        jugador.eliminado = False  # Propiedad para marcar eliminación.
        jugador.protegido = False  # Propiedad para la protección (por efecto de la Doncella, por ejemplo).
        jugadores.append(jugador)

    # Crear y barajar la baraja.
    baraja = crear_baraja()
    barajar(baraja)

    # Repartir una carta inicial a cada jugador.
    for jugador in jugadores:
        if baraja:
            jugador.mano.append(baraja.pop(0))

    turno = 0
    ganador = None

    # Bucle principal del juego.
    while not ganador:
        # Seleccionar el jugador actual (omitiendo a los eliminados).
        jugador_actual = jugadores[turno % len(jugadores)]
        if jugador_actual.eliminado:
            turno += 1
            continue

        print(f"\n--- Turno de {jugador_actual.nombre} ---")
        jugar_turno(jugador_actual, jugadores, baraja)
        
        # Mostrar el estado actual de los jugadores tras cada turno.
        print("\nEstado actual de los jugadores:")
        for j in jugadores:
            estado = "Eliminado" if j.eliminado else "Activo"
            print(f"  {j.nombre}: {estado}")

        ganador = determinar_ganador(jugadores, baraja)
        turno += 1

    print(f"\n¡El ganador es {ganador.nombre} con {ganador.mano[0]} en mano!")

if __name__ == "__main__":
    main()
