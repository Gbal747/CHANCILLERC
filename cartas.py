import random

class Carta:
    def __init__(self, nombre, valor, descripcion, image_source):
        self.nombre = nombre
        self.valor = valor
        self.descripcion = descripcion
        self.image_source = image_source

    def __str__(self):
        return f"{self.nombre} (Valor: {self.valor})"

def crear_baraja():
    cartas = []
    # Espía (2)
    for _ in range(2):
        cartas.append(Carta("Espía", 0, "Efecto del Espía", "images/Espia.png"))
    
    # Guardia (5)
    for _ in range(5):
        cartas.append(Carta("Guardia", 1, "Adivinar la mano de otro jugador", "images/Guardia.png"))
    
    # Sacerdote (2)
    for _ in range(2):
        cartas.append(Carta("Sacerdote", 2, "Mirar la mano de otro jugador", "images/Sacerdote.png"))
    
    # Barón (2)
    for _ in range(2):
        cartas.append(Carta("Barón", 3, "Comparar cartas con otro jugador", "images/Baron.png"))
    
    # Doncella (2)
    for _ in range(2):
        cartas.append(Carta("Doncella", 4, "Protección hasta el siguiente turno", "images/Doncella.png"))
    
    # Príncipe (2)
    for _ in range(2):
        cartas.append(Carta("Príncipe", 5, "Obliga a otro jugador a descartar su mano", "images/Principe.png"))
    
    # Chanciller (2)
    for _ in range(2):
        cartas.append(Carta("Chanciller", 6, "Roba dos cartas y elige una", "images/Chanciller.png"))

    # Rey (1)
    cartas.append(Carta("Rey", 7, "Intercambia mano con otro jugador", "images/Rey.png"))
    
    # Condesa (1)
    cartas.append(Carta("Condesa", 8, "Sin efecto adicional", "images/Condesa.png"))
    
    # Princesa (1)
    cartas.append(Carta("Princesa", 9, "Si se juega, el jugador queda eliminado", "images/Princesa.png"))
    
    return cartas

def barajar(baraja):
    random.shuffle(baraja)
    return baraja
