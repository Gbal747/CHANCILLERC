# cartas.py
import random

class Carta:
    def __init__(self, nombre, valor, descripcion, image_source):
        self.nombre = nombre
        self.valor = valor
        self.descripcion = descripcion
        self.image_source = image_source

    def __str__(self):
        return f"{self.nombre} (Valor: {self.valor})"

    def __repr__(self):
        return self.__str__()

# Definición de las cartas
CARTAS_DEFINICION = {
    "Espía": {
        "cantidad": 2,
        "valor": 0,
        "descripcion": "Efecto del Espía",
        "imagen": "images/Espia.png"
    },
    "Guardia": {
        "cantidad": 6,
        "valor": 1,
        "descripcion": "Adivinar la mano de otro jugador",
        "imagen": "images/Guardia.png"
    },
    "Sacerdote": {
        "cantidad": 2,
        "valor": 2,
        "descripcion": "Mirar la mano de otro jugador",
        "imagen": "images/Sacerdote.png"
    },
    "Baron": {
        "cantidad": 2,
        "valor": 3,
        "descripcion": "Comparar cartas con otro jugador",
        "imagen": "images/Baron.png"
    },
    "Doncella": {
        "cantidad": 2,
        "valor": 4,
        "descripcion": "Protección hasta el siguiente turno",
        "imagen": "images/Doncella.png"
    },
    "Príncipe": {
        "cantidad": 2,
        "valor": 5,
        "descripcion": "Obliga a otro jugador a descartar su mano",
        "imagen": "images/Principe.png"
    },
    "Chanciller": {
        "cantidad": 2,
        "valor": 6,
        "descripcion": "Roba dos cartas y elige una"
        # Si no se especifica imagen se usará la imagen default.
    },
    "Rey": {
        "cantidad": 1,
        "valor": 7,
        "descripcion": "Intercambia mano con otro jugador",
        "imagen": "images/Rey.png"
    },
    "Condesa": {
        "cantidad": 1,
        "valor": 8,
        "descripcion": "Sin efecto adicional",
        "imagen": "images/Condesa.png"
    },
    "Princesa": {
        "cantidad": 1,
        "valor": 9,
        "descripcion": "Si se juega, el jugador queda eliminado",
        "imagen": "images/Princesa.png"
    }
}

def crear_baraja():
    baraja = []
    for nombre, info in CARTAS_DEFINICION.items():
        for _ in range(info["cantidad"]):
            # Si no se define imagen se usa "images/default.png"
            image_source = info.get("imagen", "images/default.png")
            carta = Carta(nombre, info["valor"], info["descripcion"], image_source)
            baraja.append(carta)
    return baraja

def barajar(baraja):
    random.shuffle(baraja)
    return baraja
