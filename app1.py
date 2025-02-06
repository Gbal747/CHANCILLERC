import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label 
from kivy.uix.button import Button 
from kivy.uix.textinput import TextInput 
from kivy.uix.popup import Popup

# =====================================================
# LÓGICA DEL JUEGO (adaptada de tus archivos originales)
# =====================================================

class Carta:
    def __init__(self, nombre, valor, descripcion):
        self.nombre = nombre
        self.valor = valor
        self.descripcion = descripcion

    def __str__(self):
        return f"{self.nombre} (Valor: {self.valor})"

    def __repr__(self):
        return self.__str__()

CARTAS_DEFINICION = {
    "Espía": {
        "cantidad": 2,
        "valor": 0,
        "descripcion": "Efecto del Espía"
    },
    "Guardia": {
        "cantidad": 6,
        "valor": 1,
        "descripcion": "Adivinar la mano de otro jugador"
    },
    "Sacerdote": {
        "cantidad": 2,
        "valor": 2,
        "descripcion": "Mirar la mano de otro jugador"
    },
    "Baron": {
        "cantidad": 2,
        "valor": 3,
        "descripcion": "Comparar cartas con otro jugador"
    },
    "Doncella": {
        "cantidad": 2,
        "valor": 4,
        "descripcion": "Protección hasta el siguiente turno"
    },
    "Príncipe": {
        "cantidad": 2,
        "valor": 5,
        "descripcion": "Obliga a otro jugador a descartar su mano"
    },
    "Chanciller": {
        "cantidad": 2,
        "valor": 6,
        "descripcion": "Roba dos cartas y elige una"
    },
    "Rey": {
        "cantidad": 1,
        "valor": 7,
        "descripcion": "Intercambia mano con otro jugador"
    },
    "Condesa": {
        "cantidad": 1,
        "valor": 8,
        "descripcion": "Sin efecto adicional"
    },
    "Princesa": {
        "cantidad": 1,
        "valor": 9,
        "descripcion": "Si se juega, el jugador queda eliminado"
    }
}

def crear_baraja():
    baraja = []
    for nombre, info in CARTAS_DEFINICION.items():
        for _ in range(info["cantidad"]):
            carta = Carta(nombre, info["valor"], info["descripcion"])
            baraja.append(carta)
    return baraja

def barajar(baraja):
    random.shuffle(baraja)
    return baraja

class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mano = []      # Lista de cartas
        self.eliminado = False
        self.protegido = False

    def mostrar_mano(self):
        return ', '.join(str(carta) for carta in self.mano)

# =====================================================
# INTERFAZ CON KIVY
# =====================================================

# Pantalla de setup: pide el número de jugadores

class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Bienvenido al Juego de Cartas", font_size='30sp'))
        layout.add_widget(Label(text="Ingresa el número de jugadores (mínimo 2):"))
        self.num_input = TextInput(text='', multiline=False, input_filter='int', hint_text="Número de jugadores")
        layout.add_widget(self.num_input)
        start_button = Button(text="Comenzar Juego", size_hint=(0.5, 0.3), pos_hint={'center_x':0.5})
        start_button.bind(on_press=self.start_game)
        layout.add_widget(start_button)
        self.add_widget(layout)

    def start_game(self, instance):
        num_str = self.num_input.text.strip()
        if num_str.isdigit() and int(num_str) >= 2:
            num = int(num_str)
            # Para simplificar, usamos nombres por defecto (Jugador 1, Jugador 2, ...)
            players = [Jugador(f"Jugador {i+1}") for i in range(num)]
            # Pasamos los jugadores a la pantalla del juego y cambiamos de pantalla
            game_screen = self.manager.get_screen('game')
            game_screen.start_game(players)
            self.manager.current = 'game'
        else:
            popup = Popup(title="Error",
                          content=Label(text="Ingrese un número válido (mínimo 2)."),
                          size_hint=(None, None), size=(300, 200))
            popup.open()

# Pantalla del juego

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Variables de estado
        self.players = []
        self.deck = []
        self.turn = 0
        self.current_player = None

        # Layout principal (vertical)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # Etiqueta de información (turno actual, etc.)
        self.info_label = Label(text="Información del juego", size_hint=(1, 0.1))
        self.layout.add_widget(self.info_label)
        # Layout para la mano del jugador (se llenará con botones)
        self.hand_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)
        self.layout.add_widget(self.hand_layout)
        # Label para el “log” del juego (mensajes, resultados, etc.)
        self.log_label = Label(text="Log del juego:", size_hint=(1, 0.5))
        self.layout.add_widget(self.log_label)
        # Botón para avanzar el turno (si fuese necesario)
        self.next_button = Button(text="Siguiente Turno", size_hint=(1, 0.1))
        self.next_button.bind(on_press=self.next_turn)
        self.layout.add_widget(self.next_button)

        self.add_widget(self.layout)

    def start_game(self, players):
        self.players = players
        self.deck = crear_baraja()
        barajar(self.deck)
        self.turn = 0
        # Repartir una carta inicial a cada jugador
        for jugador in self.players:
            if self.deck:
                jugador.mano.append(self.deck.pop(0))
        self.log_label.text = "Juego iniciado.\n"
        self.next_turn()

    def log(self, message):
        self.log_label.text += message + "\n"

    def update_ui(self):
        self.hand_layout.clear_widgets()
        if self.current_player:
            self.info_label.text = f"Turno de: {self.current_player.nombre}"
            # Mostrar un botón por cada carta en la mano
            for carta in self.current_player.mano:
                btn = Button(text=str(carta), size_hint=(None, 1), width=150)
                # Al pulsar la carta se muestra un popup con sus detalles
                btn.bind(on_press=lambda instance, c=carta: self.show_card_details(c))
                self.hand_layout.add_widget(btn)

    def next_turn(self, instance=None):
        # Verificar si ya hay un ganador antes de continuar
        if self.check_winner():
            return
        # Seleccionar el siguiente jugador activo (no eliminado)
        while True:
            self.current_player = self.players[self.turn % len(self.players)]
            self.turn += 1
            if not self.current_player.eliminado:
                break
        # Al inicio del turno se elimina la protección
        self.current_player.protegido = False
        # Robar una carta si es posible
        if self.deck:
            drawn = self.deck.pop(0)
            self.current_player.mano.append(drawn)
            self.log(f"{self.current_player.nombre} roba: {drawn}")
        else:
            self.log("La baraja se ha agotado.")
        # Verificar la regla de la Condesa: si en la mano hay Condesa junto a Rey o Príncipe, se debe jugar la Condesa
        if any(carta.nombre == "Condesa" for carta in self.current_player.mano) and \
           any(carta.nombre in ["Rey", "Príncipe"] for carta in self.current_player.mano):
            for carta in self.current_player.mano:
                if carta.nombre == "Condesa":
                    self.log(f"{self.current_player.nombre} debe jugar la Condesa obligatoriamente.")
                    self.play_card(carta)
                    return
        self.update_ui()

    def show_card_details(self, carta):
        # Crea un popup que muestra los detalles de la carta y pregunta si se desea jugarla
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        info_text = f"Nombre: {carta.nombre}\nValor: {carta.valor}\nDescripción: {carta.descripcion}"
        layout.add_widget(Label(text=info_text))
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        play_btn = Button(text="Jugar")
        cancel_btn = Button(text="Cancelar")
        btn_layout.add_widget(play_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        popup = Popup(title="Detalles de la carta", content=layout, size_hint=(None, None), size=(400, 300))
        play_btn.bind(on_press=lambda inst: self.confirm_play_card(carta, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def confirm_play_card(self, carta, popup):
        popup.dismiss()
        self.play_card(carta)

    def play_card(self, carta):
        if carta in self.current_player.mano:
            self.current_player.mano.remove(carta)
            self.log(f"{self.current_player.nombre} juega: {carta}")
            self.apply_effect(carta, self.current_player)
            # Después de aplicar el efecto se verifica el estado del juego y se avanza el turno
            self.check_winner()
            self.next_turn()
        else:
            self.log("Carta no encontrada en la mano.")

    def apply_effect(self, carta, jugador_actual):
        # Se implementan algunos efectos de forma simplificada.
        if carta.nombre == "Guardia":
            self.show_guardia_popup(jugador_actual, carta)
        elif carta.nombre == "Sacerdote":
            self.show_sacerdote_popup(jugador_actual, carta)
        elif carta.nombre == "Baron":
            self.show_baron_popup(jugador_actual, carta)
        elif carta.nombre == "Doncella":
            self.log(f"{jugador_actual.nombre} queda protegida por la Doncella.")
            jugador_actual.protegido = True
        elif carta.nombre == "Príncipe":
            self.show_principe_popup(jugador_actual, carta)
        elif carta.nombre == "Chanciller":
            self.log("Efecto del Chanciller no implementado completamente.")
        elif carta.nombre == "Rey":
            self.show_rey_popup(jugador_actual, carta)
        elif carta.nombre == "Condesa":
            self.log("La Condesa no tiene efecto adicional.")
        elif carta.nombre == "Princesa":
            self.log(f"{jugador_actual.nombre} jugó la Princesa y queda eliminado.")
            jugador_actual.eliminado = True
        elif carta.nombre == "Espía":
            self.log("Efecto del Espía no implementado.")
        else:
            self.log(f"{carta.nombre} no tiene efecto implementado.")

    # -----------------------------
    # Ejemplos de popups para efectos
    # -----------------------------

    def show_guardia_popup(self, jugador_actual, carta):
        # Objetivos: jugadores distintos al actual que estén activos y no protegidos
        targets = [j for j in self.players if j != jugador_actual and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Guardia.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador objetivo:"))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        selected_target = {"target": None}
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40)
            btn.bind(on_press=lambda inst, t=target: self.select_guardia_target(selected_target, t))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        content.add_widget(Label(text="¿Qué carta crees que tiene?"))
        guess_input = TextInput(text='', multiline=False)
        content.add_widget(guess_input)
        confirm_btn = Button(text="Confirmar", size_hint_y=None, height=40)
        popup = Popup(title="Efecto Guardia", content=content, size_hint=(None, None), size=(400, 400))
        def on_confirm(instance):
            if selected_target["target"] is None:
                self.log("Debes seleccionar un objetivo.")
            else:
                guess = guess_input.text.strip().lower()
                target = selected_target["target"]
                if any(c.nombre.lower() == guess for c in target.mano):
                    if any(c.nombre.lower() == "guardia" for c in target.mano):
                        self.log(f"{target.nombre} tiene un Guardia, no puede ser eliminado.")
                    else:
                        self.log(f"¡Correcto! {target.nombre} tenía {guess} y queda eliminado.")
                        target.eliminado = True
                else:
                    self.log("Adivinaste mal. No ocurre nada.")
                popup.dismiss()
        confirm_btn.bind(on_press=on_confirm)
        content.add_widget(confirm_btn)
        popup.open()

    def select_guardia_target(self, selected_target, target):
        selected_target["target"] = target

    def show_sacerdote_popup(self, jugador_actual, carta):
        targets = [j for j in self.players if j != jugador_actual and not j.eliminado]
        if not targets:
            self.log("No hay objetivos disponibles para el Sacerdote.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador cuya mano deseas ver:"))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40)
            btn.bind(on_press=lambda inst, t=target: self.sacerdote_selected(t, popup))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup = Popup(title="Efecto Sacerdote", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def sacerdote_selected(self, target, popup):
        self.log(f"La mano de {target.nombre} es: {target.mostrar_mano()}")
        popup.dismiss()

    def show_baron_popup(self, jugador_actual, carta):
        targets = [j for j in self.players if j != jugador_actual and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Baron.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador para comparar cartas:"))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40)
            btn.bind(on_press=lambda inst, t=target: self.baron_selected(jugador_actual, t, popup))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup = Popup(title="Efecto Baron", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def baron_selected(self, jugador_actual, target, popup):
        if target.mano:
            if len(jugador_actual.mano) == 0:
                self.log(f"{jugador_actual.nombre} no tiene cartas para comparar.")
            else:
                carta_jugador = jugador_actual.mano[0]
                carta_target = target.mano[0]
                self.log(f"{jugador_actual.nombre} tiene {carta_jugador} y {target.nombre} tiene {carta_target}")
                if carta_jugador.valor > carta_target.valor:
                    self.log(f"{target.nombre} es eliminado.")
                    target.eliminado = True
                elif carta_target.valor > carta_jugador.valor:
                    self.log(f"{jugador_actual.nombre} es eliminado.")
                    jugador_actual.eliminado = True
                else:
                    self.log("Empate. Nadie es eliminado.")
        else:
            self.log(f"{target.nombre} no tiene cartas para comparar.")
        popup.dismiss()

    def show_principe_popup(self, jugador_actual, carta):
        targets = [j for j in self.players if not j.eliminado]
        if not targets:
            self.log("No hay objetivos disponibles para el Príncipe.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador que debe descartar su mano:"))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40)
            btn.bind(on_press=lambda inst, t=target: self.principe_selected(t, popup))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup = Popup(title="Efecto Príncipe", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def principe_selected(self, target, popup):
        if target.mano:
            discarded = target.mano.pop(0)
            self.log(f"{target.nombre} descarta {discarded}")
            if discarded.nombre == "Princesa":
                self.log(f"{target.nombre} descartó la Princesa y queda eliminado.")
                target.eliminado = True
            else:
                if self.deck:
                    new_card = self.deck.pop(0)
                    target.mano.append(new_card)
                    self.log(f"{target.nombre} roba una nueva carta: {new_card}")
                else:
                    self.log("La baraja está vacía. No se puede robar una nueva carta.")
        popup.dismiss()

    def show_rey_popup(self, jugador_actual, carta):
        targets = [j for j in self.players if j != jugador_actual and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Rey.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador para intercambiar manos:"))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40)
            btn.bind(on_press=lambda inst, t=target: self.rey_selected(jugador_actual, t, popup))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup = Popup(title="Efecto Rey", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def rey_selected(self, jugador_actual, target, popup):
        if jugador_actual.mano and target.mano:
            jugador_actual.mano[0], target.mano[0] = target.mano[0], jugador_actual.mano[0]
            self.log(f"{jugador_actual.nombre} y {target.nombre} han intercambiado sus manos.")
        else:
            self.log("Intercambio no posible.")
        popup.dismiss()

    def check_winner(self):
        activos = [j for j in self.players if not j.eliminado]
        if len(activos) == 1:
            winner = activos[0]
            popup = Popup(title="Juego Terminado",
                          content=Label(text=f"¡El ganador es {winner.nombre} con {winner.mostrar_mano()}!"),
                          size_hint=(None, None), size=(400, 300))
            popup.open()
            self.log(f"¡El ganador es {winner.nombre}!")
            return True
        if not self.deck:
            self.log("La baraja se ha agotado. Se determina el ganador por el valor de carta.")
            if activos:
                winner = max(activos, key=lambda j: j.mano[0].valor if j.mano else 0)
                popup = Popup(title="Juego Terminado",
                          content=Label(text=f"¡El ganador es {winner.nombre} con {winner.mostrar_mano()}!"),
                          size_hint=(None, None), size=(400, 300))
                popup.open()
                self.log(f"¡El ganador es {winner.nombre}!")
                return True
        return False

# =====================================================
# App y ScreenManager
# =====================================================

class CardGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    CardGameApp().run()
