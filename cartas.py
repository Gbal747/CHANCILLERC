# cartas.py
import random

class Carta:
    def __init__(self, nombre, valor, descripcion):
        """
        Inicializa una carta.
        
        :param nombre: Nombre de la carta (str).
        :param valor: Valor numérico de la carta (int) que se puede usar para desempates o lógica interna.
        :param descripcion: Descripción del efecto de la carta (str).
        """
        self.nombre = nombre
        self.valor = valor
        self.descripcion = descripcion

    def __str__(self):
        return f"{self.nombre} (Valor: {self.valor})"

    def __repr__(self):
        return self.__str__()

# Definición de las cartas según las reglas del juego.
# Puedes ajustar los valores y descripciones de acuerdo a las reglas que decidas implementar.
CARTAS_DEFINICION = {
    "Espía": {
        "cantidad": 2,
        "valor": 0,
        "descripcion": "Efecto del Espía ()"
    },
    "Guardia": {
        "cantidad": 6,
        "valor": 1,
        "descripcion": "Efecto del Guardia (La Guardia tiene la misión de adivinar la mano de otro jugador, si lo adivina el otro jugador queda eliminado)"
    },
    "Sacerdote": {
        "cantidad": 2,
        "valor": 2,
        "descripcion": "Efecto del Sacerdote (El Sacerdote puede mirar la mano de otro jugador en secreto)"
    },
    "Baron": {
        "cantidad": 2,
        "valor": 3,
        "descripcion": "Efecto del Baron (El Barón puede comparar su mano con la de otro jugador, para ello debe descartarse la carta del Barón y hacer la comparación con la otra carta que tenga en mano. El jugador que tenga la carta mayor gana el duelo y el que tenga la carta menos quedará eliminado. En caso de empate se sigue jugando)"
    },
    "Doncella": {
        "cantidad": 2,
        "valor": 4,
        "descripcion": "Efecto de la Doncella (La Doncella, debido a su discreción, tiene absoluta protección hasta el siguiente turno, queda protegida de los ataques del resto )"
    },
    "Príncipe": {
        "cantidad": 2,
        "valor": 5,
        "descripcion": "Efecto del Príncipe (El Príncipe puede hacer descartar a otro jugador, el cual deberá descartarse la carta de su mano y robar la carta superior del mazo)"
    },
    "Chanciller": {
        "cantidad": 2,
        "valor": 6,
        "descripcion": "Efecto del Chanciller (El Chanciller puede robar dos cartas del mazo de las cuales debera quedarse con una y colocar las dos restantes al final del mazo en el oden que quiera)"
    },
    "Rey": {
        "cantidad": 1,
        "valor": 7,
        "descripcion": "Efecto del Rey (El Rey puede intercambiar su mano con la de otro jugador)"
    },
    "Condesa": {
        "cantidad": 1,
        "valor": 8,
        "descripcion": "Efecto de la Condesa (La Condesa no tiene efecto, pero deberá ser descartada si tuvieras en tu mano el Rey o el Príncipe)"
    },
    "Princesa": {
        "cantidad": 1,
        "valor": 9,
        "descripcion": "Efecto de la Princesa (La Princesa quedará eliminda si es descartada)"
    }
}

def crear_baraja():
    """
    Crea la baraja completa del juego a partir de la definición de cartas.
    
    :return: Lista de objetos Carta representando la baraja.
    """
    baraja = []
    for nombre, info in CARTAS_DEFINICION.items():
        for _ in range(info["cantidad"]):
            carta = Carta(nombre, info["valor"], info["descripcion"])
            baraja.append(carta)
    return baraja

def barajar(baraja):
    """
    Recibe una baraja (lista de cartas) y la baraja aleatoriamente.
    
    :param baraja: Lista de objetos Carta.
    :return: La misma lista barajada.
    """
    random.shuffle(baraja)
    return baraja

if __name__ == "__main__":
    # Código de prueba para ver que se crea y baraja la baraja correctamente.
    baraja = crear_baraja()
    print("Baraja sin barajar:")
    print(baraja)
    
    barajar(baraja)
    print("\nBaraja barajada:")
    print(baraja)
