from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label 
from kivy.uix.button import Button 
from kivy.uix.textinput import TextInput 
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

from jugadores import Jugador
from partida import Partida
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

# Nueva pantalla para el efecto del Guardia
class GuardiaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jugador_actual = None
        self.carta = None
        self.game_screen = None
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.layout)
        
        self.instruction_label = Label(text="Selecciona un jugador objetivo:", size_hint=(1, 0.1))
        self.layout.add_widget(self.instruction_label)
        
        self.target_buttons_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.3))
        self.layout.add_widget(self.target_buttons_layout)
        
        self.instruction_label2 = Label(text="Elige la carta que crees que tiene:", size_hint=(1, 0.1))
        self.layout.add_widget(self.instruction_label2)
        
        self.guess_buttons_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.3))
        self.layout.add_widget(self.guess_buttons_layout)
        
        self.confirm_btn = Button(text="Confirmar", size_hint=(1, 0.1), background_color=(0.6, 0.4, 0.2, 1))
        self.layout.add_widget(self.confirm_btn)
        
        self.selected_target = None
        self.selected_guess = None

    def set_context(self, jugador_actual, carta, game_screen):
        self.jugador_actual = jugador_actual
        self.carta = carta
        self.game_screen = game_screen
        self.selected_target = None
        self.selected_guess = None
        self.build_ui()

    def build_ui(self):
        self.target_buttons_layout.clear_widgets()
        self.guess_buttons_layout.clear_widgets()
        # Construir botones para la selección de jugador objetivo
        targets = [j for j in self.game_screen.partida.jugadores 
                   if j != self.jugador_actual and not j.eliminado and not j.protegido]
        if not targets:
            self.game_screen.log("No hay objetivos disponibles para el Guardia.")
            self.game_screen.next_button.disabled = False
            self.game_screen.manager.current = 'game'
            return
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1))
            btn.bind(on_press=lambda instance, t=target: self.select_target(instance, t))
            self.target_buttons_layout.add_widget(btn)
        # Construir botones para la selección de carta a adivinar (excluyendo "Guardia")
        available_cards = ["Sacerdote", "Barón", "Doncella", "Príncipe", "Rey", 
                           "Condesa", "Princesa", "Chanciller", "Espía"]
        for card_name in available_cards:
            btn = Button(text=card_name, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1))
            btn.bind(on_press=lambda instance, guess=card_name: self.select_guess(instance, guess))
            self.guess_buttons_layout.add_widget(btn)
        self.confirm_btn.unbind(on_press=self.on_confirm)
        self.confirm_btn.bind(on_press=self.on_confirm)

    def select_target(self, instance, target):
        self.selected_target = target
        for child in self.target_buttons_layout.children:
            child.background_color = (0.6, 0.4, 0.2, 1)
        instance.background_color = (0, 1, 0, 1)

    def select_guess(self, instance, guess):
        self.selected_guess = guess
        for child in self.guess_buttons_layout.children:
            child.background_color = (0.6, 0.4, 0.2, 1)
        instance.background_color = (0, 1, 0, 1)

    def on_confirm(self, instance):
        if self.selected_target is None:
            self.game_screen.log("Debes seleccionar un objetivo.")
            return
        if self.selected_guess is None:
            self.game_screen.log("Debes seleccionar una carta para adivinar.")
            return
        guess = self.selected_guess.lower()
        target = self.selected_target
        if any(carta.nombre.lower() == guess for carta in target.mano):
            if any(carta.nombre.lower() == "guardia" for carta in target.mano):
                self.game_screen.log(f"{target.nombre} tiene un Guardia, no puede ser eliminado.")
            else:
                self.game_screen.log(f"¡Correcto! {target.nombre} tenía {guess} y queda eliminado.")
                target.eliminado = True
                target.mano.clear()
        else:
            self.game_screen.log("Adivinaste mal. No ocurre nada.")
        self.game_screen.next_button.disabled = False
        self.game_screen.manager.current = 'game'

# -----------------------------
# Widget para representar una carta
# -----------------------------
class CardWidget(ButtonBehavior, BoxLayout):
    def __init__(self, carta, **kwargs):
        super().__init__(**kwargs)
        self.carta = carta
        self.orientation = 'vertical'
        self.size_hint = (None, 1)
        self.width = 400
        self.padding = 10
        self.spacing = 10
        with self.canvas.before:
            Color(rgba=(0.8, 0.7, 0.6, 1))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        card_image = Image(source=carta.image_source, size_hint=(1, 0.7))
        card_label = Label(text=carta.nombre, size_hint=(1, 0.3), font_size='18sp', color=(0.2, 0.1, 0, 1))
        self.add_widget(card_image)
        self.add_widget(card_label)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# -----------------------------
# Pantalla de configuración (SetupScreen)
# Ahora se pide primero el número de jugadores y luego, en el mismo layout, se
# solicitan los nombres de cada uno.
# -----------------------------
class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.names_inputs = []
        with self.canvas.before:
            Color(rgba=(0.95, 0.9, 0.8, 1))
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.add_widget(self.layout)
        self.build_initial_ui()

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def build_initial_ui(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Bienvenido al Juego de Cartas", font_size='30sp', color=(0.2,0.1,0,1)))
        self.layout.add_widget(Label(text="Ingresa el número de jugadores (mínimo 2):", color=(0.2,0.1,0,1)))
        self.num_input = TextInput(text='', multiline=False, input_filter='int', hint_text="Número de jugadores")
        self.layout.add_widget(self.num_input)
        start_button = Button(text="Siguiente", size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5},
                              background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
        start_button.bind(on_press=self.create_name_inputs)
        self.layout.add_widget(start_button)

    def create_name_inputs(self, instance):
        num_str = self.num_input.text.strip()
        if not num_str.isdigit() or int(num_str) < 2:
            popup = Popup(title="Error",
                          content=Label(text="Ingrese un número válido (mínimo 2).", color=(1,0,0,1)),
                          size_hint=(None, None), size=(300, 200))
            popup.open()
            return
        num = int(num_str)
        self.layout.clear_widgets()
        self.names_inputs = []
        self.layout.add_widget(Label(text="Ingresa el nombre de cada jugador:", font_size='24sp', color=(0.2,0.1,0,1)))
        for i in range(num):
            ti = TextInput(text=f"Jugador {i+1}", multiline=False, size_hint=(1, None), height=40)
            self.names_inputs.append(ti)
            self.layout.add_widget(ti)
        confirm_button = Button(text="Iniciar Juego", size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5},
                                  background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
        confirm_button.bind(on_press=self.start_game)
        self.layout.add_widget(confirm_button)

    def start_game(self, instance):
        names = [ti.text.strip() for ti in self.names_inputs if ti.text.strip()]
        if len(names) < 2:
            popup = Popup(title="Error",
                          content=Label(text="Debe haber al menos 2 nombres.", color=(1,0,0,1)),
                          size_hint=(None, None), size=(300, 200))
            popup.open()
            return
        players = [Jugador(name) for name in names]
        game_screen = self.manager.get_screen('game')
        game_screen.start_game(players)
        self.manager.current = 'game'

# -----------------------------
# Pantalla del juego (GameScreen)
# -----------------------------
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=(0.95, 0.9, 0.8, 1))
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.partida = None
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.info_label = Label(text="Información del juego", size_hint=(1, 0.1),
                                font_size='24sp', color=(0.2,0.1,0,1))
        self.layout.add_widget(self.info_label)
        self.discard_pile = DiscardPile()
        self.layout.add_widget(self.discard_pile)
        self.hand_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        self.layout.add_widget(self.hand_layout)
        self.log_label = Label(text="Log del juego:", size_hint=(1, 0.5),
                                font_size='18sp', color=(0.2,0.1,0,1))
        self.layout.add_widget(self.log_label)
        self.next_button = Button(text="Siguiente Turn", size_hint=(1, 0.1),
                                  background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
        self.next_button.bind(on_press=self.next_turn)
        self.layout.add_widget(self.next_button)
        self.add_widget(self.layout)
        self.card_played = False

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def start_game(self, players):
        self.partida = Partida(players)
        self.partida.repartir_inicial()
        self.log_label.text = "Juego iniciado.\n"
        self.next_turn()

    def log(self, message):
        self.log_label.text += message + "\n"

    def update_ui(self):
        self.hand_layout.clear_widgets()
        if self.partida and self.partida.current_player and not self.partida.current_player.eliminado:
            self.info_label.text = f"Turno de: {self.partida.current_player.nombre}"
            for carta in self.partida.current_player.mano:
                card_widget = CardWidget(carta)
                card_widget.opacity = 0
                anim = Animation(opacity=1, duration=0.5)
                anim.start(card_widget)
                card_widget.bind(on_press=lambda instance, c=carta: self.show_card_details(c))
                self.hand_layout.add_widget(card_widget)

    def next_turn(self, instance=None):
        self.log_label.text = "Log del juego:\n"
        if instance is not None and self.partida and self.partida.current_player and not self.card_played:
            popup = Popup(title="Alerta",
                          content=Label(text="Debes jugar una carta antes de pasar al siguiente turno.",
                                        color=(1, 0, 0, 1)),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return
        if self.partida:
            jugador = self.partida.siguiente_jugador()
            self.card_played = False
            jugador.protegido = False
            if not jugador.eliminado:
                carta_roba = self.partida.robar_carta(jugador)
                if carta_roba:
                    self.log(f"{jugador.nombre} roba: {carta_roba}")
                else:
                    self.log("La baraja se ha agotado.")
            if any(carta.nombre == "Condesa" for carta in jugador.mano) and \
               any(carta.nombre in ["Rey", "Príncipe"] for carta in jugador.mano):
                for carta in jugador.mano:
                    if carta.nombre == "Condesa":
                        self.log(f"{jugador.nombre} debe jugar la Condesa obligatoriamente.")
                        self.play_card(carta)
                        return
            self.update_ui()

    def elegir_jugador(self, carta):
        self.next_button.disabled = True
        if carta.nombre == "Guardia":
            self.show_guardia_screen(self.partida.current_player, carta)
        elif carta.nombre == "Sacerdote":
            self.show_sacerdote_popup(self.partida.current_player, carta)
        elif carta.nombre == "Barón":
            self.show_baron_popup(self.partida.current_player, carta)
        elif carta.nombre == "Príncipe":
            self.show_principe_popup(self.partida.current_player, carta)
        elif carta.nombre == "Rey":
            self.show_rey_popup(self.partida.current_player, carta)
        else:
            self.apply_effect(carta, self.partida.current_player)
            self.next_button.disabled = False
            self.next_turn()

    def show_card_details(self, carta):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        card_image = Image(source=carta.image_source, size_hint=(1, 0.6))
        layout.add_widget(card_image)
        info_text = f"Nombre: {carta.nombre}\nValor: {carta.valor}\nDescripción: {carta.descripcion}"
        layout.add_widget(Label(text=info_text, color=(0.2,0.1,0,1)))
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        play_btn = Button(text="Jugar", background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
        btn_layout.add_widget(play_btn)
        layout.add_widget(btn_layout)
        popup = Popup(title="Detalles de la carta", content=layout,
                      size_hint=(None, None), size=(400, 300), auto_dismiss=False)
        play_btn.bind(on_press=lambda inst: self.confirm_play_card(carta, popup))
        popup.open()

    def confirm_play_card(self, carta, popup):
        popup.dismiss()
        self.play_card(carta)

    def play_card(self, carta):
        if self.partida and carta in self.partida.current_player.mano:
            self.card_played = True
        self.partida.current_player.mano.remove(carta)
        self.discard_pile.update_card(carta)
        self.log(f"{self.partida.current_player.nombre} juega: {carta}")
        if carta.nombre in ["Guardia", "Sacerdote", "Barón", "Príncipe", "Rey"]:
            self.elegir_jugador(carta)
            return
        else:
            self.apply_effect(carta, self.partida.current_player)
        ganador = self.partida.determinar_ganador()
        if ganador:
            popup = Popup(title="Juego Terminado",
                          content=Label(text=f"¡El ganador es {ganador.nombre} con {ganador.mostrar_mano()}!",
                                        color=(0, 0, 0, 1)),
                          size_hint=(None, None), size=(400, 300))
            popup.open()
            self.log(f"¡El ganador es {ganador.nombre}!")
            return
        for child in self.hand_layout.children:
            if hasattr(child, 'carta') and child.carta == carta:
                anim = Animation(opacity=0, duration=0.3)
                anim.start(child)
                break
        self.next_turn()
        self.log("Carta no encontrada en la mano.")

    def show_interaction_popup(self, carta):
        if carta.nombre == "Guardia":
            self.show_guardia_screen(self.partida.current_player, carta)
        elif carta.nombre == "Sacerdote":
            self.show_sacerdote_popup(self.partida.current_player, carta)
        elif carta.nombre == "Barón":
            self.show_baron_popup(self.partida.current_player, carta)
        elif carta.nombre == "Príncipe":
            self.show_principe_popup(self.partida.current_player, carta)
        elif carta.nombre == "Rey":
            self.show_rey_popup(self.partida.current_player, carta)

    def apply_effect(self, carta, jugador_actual):
        if carta.nombre == "Guardia":
            self.show_guardia_screen(jugador_actual, carta)
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
            jugador_actual.mano.clear()
        elif carta.nombre == "Espía":
            self.log("Efecto del Espía no implementado.")
        else:
            self.log(f"{carta.nombre} no tiene efecto implementado.")

    def show_guardia_screen(self, jugador_actual, carta):
        guardia_screen = self.manager.get_screen('guardia')
        guardia_screen.set_context(jugador_actual, carta, self)
        self.manager.current = 'guardia'

    def show_sacerdote_popup(self, jugador_actual, carta):
        targets = [j for j in self.partida.jugadores if j != jugador_actual and not j.eliminado]
        if not targets:
            self.log("No hay objetivos disponibles para el Sacerdote.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador cuya mano deseas ver:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Sacerdote", content=content,
                      size_hint=(None, None), size=(400,300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6,0.4,0.2,1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, p=popup: self.sacerdote_selected(t, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def sacerdote_selected(self, target, popup):
        self.log(f"La mano de {target.nombre} es: {target.mostrar_mano()}")
        popup.dismiss()
        self.next_button.disabled = False
        self.next_turn()

    def show_baron_popup(self, jugador_actual, carta):
        targets = [j for j in self.partida.jugadores if j != jugador_actual and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Baron.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador para comparar cartas:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Baron", content=content,
                      size_hint=(None, None), size=(400,300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6,0.4,0.2,1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, p=popup: self.baron_selected(jugador_actual, t, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
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
                    target.mano.clear()
                elif carta_target.valor > carta_jugador.valor:
                    self.log(f"{jugador_actual.nombre} es eliminado.")
                    jugador_actual.eliminado = True
                    jugador_actual.mano.clear()
                else:
                    self.log("Empate. Nadie es eliminado.")
        else:
            self.log(f"{target.nombre} no tiene cartas para comparar.")
        popup.dismiss()
        self.next_button.disabled = False
        self.next_turn()

    def show_principe_popup(self, jugador_actual, carta):
        targets = [j for j in self.partida.jugadores if not j.eliminado]
        if not targets:
            self.log("No hay objetivos disponibles para el Príncipe.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador que debe descartar su mano:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Príncipe", content=content,
                      size_hint=(None, None), size=(400,300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6,0.4,0.2,1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, p=popup: self.principe_selected(t, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def principe_selected(self, target, popup):
        if target.mano:
            discarded = target.mano.pop(0)
            self.log(f"{target.nombre} descarta {discarded}")
            if discarded.nombre == "Princesa":
                self.log(f"{target.nombre} descartó la Princesa y queda eliminado.")
                target.eliminado = True
                target.mano.clear()
            else:
                if self.partida and self.partida.deck:
                    new_card = self.partida.robar_carta(target)
                    self.log(f"{target.nombre} roba una nueva carta: {new_card}")
                else:
                    self.log("La baraja está vacía. No se puede robar una nueva carta.")
        popup.dismiss()
        self.next_button.disabled = False
        self.next_turn()

    def show_rey_popup(self, jugador_actual, carta):
        targets = [j for j in self.partida.jugadores if j != jugador_actual and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Rey.")
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador para intercambiar manos:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Rey", content=content,
                      size_hint=(None, None), size=(400,300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6,0.4,0.2,1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, p=popup: self.rey_selected(jugador_actual, t, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def rey_selected(self, jugador_actual, target, popup):
        if jugador_actual.mano and target.mano:
            jugador_actual.mano[0], target.mano[0] = target.mano[0], jugador_actual.mano[0]
            self.log(f"{jugador_actual.nombre} y {target.nombre} han intercambiado sus manos.")
        else:
            self.log("Intercambio no posible.")
        popup.dismiss()
        self.next_button.disabled = False
        self.next_turn()

# -----------------------------
# Widget para el mazo de descartes
# -----------------------------
class DiscardPile(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (200, 300)
        self.orientation = 'vertical'
        self.padding = 5
        self.spacing = 5
        self.image = Image(source='images/card_back.png', size_hint=(1, 1))
        self.add_widget(self.image)

    def update_card(self, carta):
        self.image.source = carta.image_source
        self.image.reload()

# -----------------------------
# Clase principal de la aplicación
# -----------------------------
class CardGameApp(App):
    def build(self):
        self.title = "Juego de Cartas"
        sm = ScreenManager()
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(GuardiaScreen(name='guardia'))
        return sm

if __name__ == '__main__':
    CardGameApp().run()
