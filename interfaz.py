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
from kivy.uix.gridlayout import GridLayout

from jugadores import Jugador
from partida import Partida

# Nueva pantalla para el efecto del Guardia
class GuardiaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jugador_actual = None
        self.carta = None
        self.game_screen = None
        
        # Layout principal con más padding arriba
        self.layout = BoxLayout(orientation='vertical', padding=[20, 30, 20, 10], spacing=10)
        self.add_widget(self.layout)
        
        # Sección de selección de jugador (aún más compacta)
        self.player_section = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.15))
        self.instruction_label = Label(
            text="Selecciona un jugador objetivo:",
            size_hint=(1, 0.4),
            font_size='18sp',
            color=(0.2, 0.1, 0, 1)
        )
        self.player_section.add_widget(self.instruction_label)
        
        # Layout horizontal para los jugadores aún más compacto
        self.target_buttons_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(0.7, 0.6),  # Reducido a 70% del ancho
            pos_hint={'center_x': 0.5}
        )
        self.player_section.add_widget(self.target_buttons_layout)
        self.layout.add_widget(self.player_section)
        
        # Sección de selección de carta (más compacta)
        self.card_section = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.6))
        self.instruction_label2 = Label(
            text="Elige la carta que crees que tiene:",
            size_hint=(1, 0.1),
            font_size='18sp',
            color=(0.2, 0.1, 0, 1)
        )
        self.card_section.add_widget(self.instruction_label2)
        
        # Grid layout para las cartas más compacto
        self.guess_buttons_layout = GridLayout(
            cols=2,
            spacing=8,
            size_hint=(0.8, 0.9),  # 80% del ancho
            pos_hint={'center_x': 0.5}
        )
        self.card_section.add_widget(self.guess_buttons_layout)
        self.layout.add_widget(self.card_section)
        
        # Botón de confirmar (más pequeño y con padding abajo)
        button_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.15),
            padding=[0, 0, 0, 10]  # Padding abajo
        )
        self.confirm_btn = Button(
            text="Confirmar",
            size_hint=(0.3, 0.7),
            pos_hint={'center_x': 0.5},
            background_color=(0.6, 0.4, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        button_layout.add_widget(self.confirm_btn)
        self.layout.add_widget(button_layout)
        
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
            
        # Botones de jugadores aún más pequeños
        button_width = 1.0 / len(targets) if targets else 1
        for target in targets:
            btn = Button(
                text=target.nombre,
                size_hint=(button_width, 0.7),  # Altura reducida al 70%
                pos_hint={'center_y': 0.5},
                background_color=(0.6, 0.4, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda instance, t=target: self.select_target(instance, t))
            self.target_buttons_layout.add_widget(btn)
            
        # Construir botones para la selección de carta
        available_cards = ["Sacerdote", "Barón", "Doncella", "Príncipe", "Rey", 
                         "Condesa", "Princesa", "Chanceller", "Espía"]
        for card_name in available_cards:
            btn = Button(
                text=card_name,
                size_hint=(1, None),
                height=45,  # Altura reducida
                background_color=(0.6, 0.4, 0.2, 1),
                color=(1, 1, 1, 1)
            )
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
            
        # Descartar la carta del Guardia
        self.game_screen.complete_card_play(self.carta)
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
        self.is_processing_effect = False  # Variable para controlar el estado de procesamiento

        # Layout principal (vertical)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Contenedor superior (Texto del turno)
        turno_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=50)  # Fijamos la altura
        self.info_label = Label(
            text="Turno de: Jugador 1",
            font_size='24sp',
            color=(0.2, 0.1, 0, 1),
            size_hint_y=None,  # Fijamos la altura para que no se sobreponga
            height=40
        )
        turno_layout.add_widget(self.info_label)
        self.layout.add_widget(turno_layout)

        # Contenedor para los mazos (Deck y DiscardPile)
        mazo_layout = BoxLayout(
            orientation='horizontal', 
            size_hint=(None, None), 
            width=430,  # Ajustado para que el centro quede bien
            height=280,  
            spacing=50  # Espacio entre los mazos
        )
        mazo_layout.pos_hint = {'center_x': 0.5}  # Centramos el contenedor de mazos

        # Mazo de robo
        self.deck_widget = DeckWidget(callback=self.show_remaining_deck, size_hint=(None, None), size=(120, 150))
        mazo_layout.add_widget(self.deck_widget)

        # Mazo de descartes
        self.discard_pile = DiscardPile(size_hint=(None, None), size=(120, 150))
        mazo_layout.add_widget(self.discard_pile)

        # Agregar el layout de mazos al layout principal
        self.layout.add_widget(mazo_layout)

        # Layout de la mano del jugador
        self.hand_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        self.layout.add_widget(self.hand_layout)

        # Log del juego
        self.log_label = Label(text="Log del juego:", size_hint=(1, 0.4), font_size='18sp', color=(0.2, 0.1, 0, 1))
        self.layout.add_widget(self.log_label)


        # Botón de siguiente turno
        self.next_button = Button(
            text="Siguiente Turno",
            size_hint=(1, 0.1),
            background_color=(0.6, 0.4, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.next_button.bind(on_press=self.next_turn)
        self.layout.add_widget(self.next_button)

        self.add_widget(self.layout)

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

    def show_remaining_deck(self):
        if self.partida and self.partida.deck:
            count = len(self.partida.deck)
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text=f"Cartas restantes en el mazo: {count}", font_size="20sp"))
            popup = Popup(title="Mazo", content=content, size_hint=(None, None), size=(400, 200))
            popup.open()
        else:
            popup = Popup(title="Mazo", content=Label(text="El mazo está vacío."), size_hint=(None, None), size=(300, 200))
            popup.open()

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
        # Limpiar el log del juego al cambiar de turno  
        self.log_label.text = "Log del juego:\n"

        # Si se presionó el botón y aún no se jugó una carta, se impide avanzar
        if instance is not None and self.partida and self.partida.current_player and not self.card_played:
            popup = Popup(title="Alerta",
                          content=Label(text="Debes jugar una carta antes de pasar al siguiente turno.", color=(1, 0, 0, 1)),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        if self.partida:
            jugador = self.partida.siguiente_jugador()
            self.card_played = False
            # Se elimina la protección al inicio del turno
            jugador.protegido = False
            carta_roba = self.partida.robar_carta(jugador)
            if carta_roba:
                self.log(f"{jugador.nombre} roba: {carta_roba}")
            else:
                self.log("La baraja se ha agotado.")

            # Regla de la Condesa: si en la mano hay Condesa junto a Rey o Príncipe, se debe jugar la Condesa
            if any(carta.nombre == "Condesa" for carta in jugador.mano) and \
               any(carta.nombre in ["Rey", "Príncipe"] for carta in jugador.mano):
                for carta in jugador.mano:
                    if carta.nombre == "Condesa":
                        self.log(f"{jugador.nombre} debe jugar la Condesa obligatoriamente.")
                        self.play_card(carta)
                        return

            # Actualizar la UI
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
        # Si ya se ha jugado una carta, no permitir jugar otra
        if self.card_played:
            popup = Popup(title='Aviso',
                        content=Label(text='Ya has jugado una carta en este turno.',
                                    color=(0.2,0.1,0,1)),
                        size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        # Verificar la regla de la Condesa
        tiene_condesa = any(c.nombre == "Condesa" for c in self.partida.current_player.mano)
        tiene_rey_o_principe = any(c.nombre in ["Rey", "Príncipe"] for c in self.partida.current_player.mano)
        
        if tiene_condesa and tiene_rey_o_principe and carta.nombre != "Condesa":
            popup = Popup(title="Regla de la Condesa",
                        content=Label(text="Si tienes la Condesa y el Rey o el Príncipe,\ndebes jugar la Condesa.",
                                    color=(0.2,0.1,0,1)),
                        size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Imagen y descripción
        card_image = Image(source=carta.image_source, size_hint=(1, 0.6))
        layout.add_widget(card_image)
        info_text = f"Nombre: {carta.nombre}\nValor: {carta.valor}\nDescripción: {carta.descripcion}"
        layout.add_widget(Label(text=info_text, color=(0.2,0.1,0,1)))
        
        # Layout para botones
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        # Botón de retroceso
        back_btn = Button(
            text="Volver",
            background_color=(0.8, 0.3, 0.2, 1),
            color=(1,1,1,1)
        )
        btn_layout.add_widget(back_btn)
        
        # Botón de jugar
        play_btn = Button(
            text="Jugar",
            background_color=(0.6, 0.4, 0.2, 1),
            color=(1,1,1,1)
        )
        btn_layout.add_widget(play_btn)
        
        layout.add_widget(btn_layout)
        popup = Popup(
            title="Detalles de la carta",
            content=layout,
            size_hint=(None, None),
            size=(400, 300),
            auto_dismiss=False
        )
        
        # Vincular botones
        back_btn.bind(on_press=popup.dismiss)
        play_btn.bind(on_press=lambda inst: self.confirm_play_card(carta, popup))
        
        popup.open()

    def confirm_play_card(self, carta, popup):
        # Verificar la regla de la Condesa
        tiene_condesa = any(c.nombre == "Condesa" for c in self.partida.current_player.mano)
        tiene_rey_o_principe = any(c.nombre in ["Rey", "Príncipe"] for c in self.partida.current_player.mano)
        
        if tiene_condesa and tiene_rey_o_principe and carta.nombre != "Condesa":
            error_popup = Popup(title="Regla de la Condesa",
                            content=Label(text="Si tienes la Condesa y el Rey o el Príncipe,\ndebes jugar la Condesa.",
                                        color=(0.2,0.1,0,1)),
                            size_hint=(None, None), size=(400, 200))
            error_popup.open()
            return

        popup.dismiss()
        self.play_card(carta)

    def play_card(self, carta):
        if self.partida and carta in self.partida.current_player.mano:
            self.card_played = True
            
            # Si la carta requiere selección de jugador, esperar a que se complete la acción
            if carta.nombre in ["Guardia", "Sacerdote", "Barón", "Príncipe", "Rey"]:
                self.elegir_jugador(carta)
                return  # Se espera la interacción del usuario
            
            # Si no requiere selección, proceder con el descarte
            self.complete_card_play(carta)
        else:
            self.log("Carta no encontrada en la mano.")

    def complete_card_play(self, carta):
        # Eliminar la carta de la mano
        if carta in self.partida.current_player.mano:
            self.partida.current_player.mano.remove(carta)
            self.discard_pile.update_card(carta)
            self.log(f"{self.partida.current_player.nombre} juega: {carta}")

            # Animación para quitar la carta jugada de la mano
            for child in self.hand_layout.children[:]:
                if hasattr(child, 'carta') and child.carta == carta:
                    anim = Animation(opacity=0, duration=0.3)
                    def remove_widget_after_anim(animation, widget):
                        if widget in self.hand_layout.children:
                            self.hand_layout.remove_widget(widget)
                    anim.bind(on_complete=remove_widget_after_anim)
                    anim.start(child)
                    break

            # Aplicar el efecto de la carta
            self.apply_effect(carta, self.partida.current_player)

            # Verificar si hay ganador
            ganador = self.partida.determinar_ganador()
            if ganador:
                popup = Popup(title="Juego Terminado",
                            content=Label(text=f"¡El ganador es {ganador.nombre} con {ganador.mostrar_mano()}!", color=(0, 0, 0, 1)),
                            size_hint=(None, None), size=(400, 300))
                popup.open()
                self.log(f"¡El ganador es {ganador.nombre}!")
                return

            self.next_button.disabled = False

    def apply_effect(self, carta, jugador):
        if carta.nombre == "Espía":
            self.log(f"El efecto del Espía aún no está implementado")
            self.next_button.disabled = False
        elif carta.nombre == "Guardia":
            self.show_guardia_popup(jugador, carta)
        elif carta.nombre == "Sacerdote":
            self.show_sacerdote_popup(jugador, carta)
        elif carta.nombre == "Barón":
            self.show_baron_popup(jugador, carta)
        elif carta.nombre == "Doncella":
            jugador.protegido = True
            self.log(f"{jugador.nombre} está protegido hasta su próximo turno")
            self.next_button.disabled = False
        elif carta.nombre == "Príncipe":
            self.show_principe_popup(jugador, carta)
        elif carta.nombre == "Chanceller":
            self.show_chanceller_popup(jugador, carta)
        elif carta.nombre == "Rey":
            self.show_rey_popup(jugador, carta)
        elif carta.nombre == "Condesa":
            pass  # La Condesa no tiene efecto
            self.next_button.disabled = False
        elif carta.nombre == "Princesa":
            self.log(f"{jugador.nombre} ha jugado la Princesa y pierde")
            jugador.eliminado = True
            jugador.mano.clear()
            self.next_button.disabled = False
        else:
            self.log(f"{carta.nombre} no tiene efecto implementado.")
            self.next_button.disabled = False

    def show_guardia_popup(self, jugador, carta):
        if self.is_processing_effect:  # Si ya estamos procesando un efecto, no hacer nada
            return
            
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Guardia.")
            self.complete_card_play(carta)  # Descartar la carta incluso si no hay objetivos
            return
            
        # Crear un nuevo BoxLayout para cada popup
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador objetivo:", color=(0.2,0.1,0,1)))
        
        # Crear un nuevo BoxLayout para los botones
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target: self.show_guardia_screen(jugador, carta))
            target_buttons.add_widget(btn)
            
        content.add_widget(target_buttons)
        
        popup = Popup(title="Efecto Guardia", 
                     content=content,
                     size_hint=(None, None), 
                     size=(400, 300))
        popup.open()

    def show_guardia_screen(self, jugador, carta):
        guardia_screen = self.manager.get_screen('guardia')
        guardia_screen.set_context(jugador, carta, self)
        self.manager.current = 'guardia'

    def show_sacerdote_popup(self, jugador, carta):
        if self.is_processing_effect:  # Si ya estamos procesando un efecto, no hacer nada
            return
            
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Sacerdote.")
            self.complete_card_play(carta)  # Descartar la carta incluso si no hay objetivos
            return
            
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador para ver su mano:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Sacerdote", content=content,
                      size_hint=(None, None), size=(400, 300))
        
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target: self.sacerdote_selected(t, carta, popup))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def sacerdote_selected(self, target, carta, popup):
        if self.is_processing_effect:  # Si ya estamos procesando un efecto, no hacer nada
            return
            
        self.is_processing_effect = True  # Marcar que estamos procesando
        
        # Mostrar la mano del jugador objetivo
        if target.mano:
            cartas_mano = [carta.nombre for carta in target.mano]
            self.log(f"La mano de {target.nombre} es: {', '.join(cartas_mano)}")
        else:
            self.log(f"{target.nombre} no tiene cartas en la mano.")
        popup.dismiss()  # Cerrar el popup después de mostrar la información
        self.complete_card_play(carta)
        
        self.is_processing_effect = False  # Resetear el estado

    def show_baron_popup(self, jugador, carta):
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Barón.")
            self.complete_card_play(carta)
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona el jugador para comparar cartas:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Barón", content=content,
                      size_hint=(None, None), size=(400,300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, c=carta, p=popup: self.baron_selected(jugador, t, c, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def baron_selected(self, jugador, target, carta, popup):
        if target.mano:
            carta_jugador = [c for c in jugador.mano if c != carta][0]  # La otra carta en la mano
            carta_objetivo = target.mano[0]
            self.log(f"Comparando cartas: {jugador.nombre}({carta_jugador.nombre}) vs {target.nombre}({carta_objetivo.nombre})")
            if carta_jugador.valor > carta_objetivo.valor:
                self.log(f"{target.nombre} es eliminado")
                target.eliminado = True
            elif carta_jugador.valor < carta_objetivo.valor:
                self.log(f"{jugador.nombre} es eliminado")
                jugador.eliminado = True
            else:
                self.log("Empate, nadie es eliminado")
        else:
            self.log(f"{target.nombre} no tiene cartas para comparar")
        popup.dismiss()
        self.complete_card_play(carta)

    def show_principe_popup(self, jugador, carta):
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        targets.append(jugador)  # El Príncipe puede afectar al jugador que lo usa
        if not targets:
            self.log("No hay objetivos disponibles para el Príncipe.")
            self.complete_card_play(carta)
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador para descartar su mano:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Príncipe", content=content,
                      size_hint=(None, None), size=(400, 300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, c=carta, p=popup: self.principe_selected(t, c, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def principe_selected(self, target, carta, popup):
        if target.mano:
            carta_descartada = target.mano[0]
            if carta_descartada.nombre == "Princesa":
                self.log(f"{target.nombre} descartó la Princesa y queda eliminado")
                target.eliminado = True
            else:
                self.log(f"{target.nombre} descarta: {carta_descartada.nombre}")
                target.mano.remove(carta_descartada)
                self.discard_pile.update_card(carta_descartada)
                # Robar nueva carta si quedan en el mazo
                if self.partida.hay_baraja():
                    nueva_carta = self.partida.robar_carta(target)
                    self.log(f"{target.nombre} roba una nueva carta")
                else:
                    self.log("No quedan cartas en el mazo")
        else:
            self.log(f"{target.nombre} no tiene cartas para descartar")
        popup.dismiss()  # Cerrar el popup
        self.complete_card_play(carta)  # Completar el juego de la carta

    def show_rey_popup(self, jugador, carta):
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Rey.")
            self.complete_card_play(carta)
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador para intercambiar manos:", color=(0.2,0.1,0,1)))
        target_buttons = BoxLayout(orientation='vertical', spacing=5)
        popup = Popup(title="Efecto Rey", content=content,
                      size_hint=(None, None), size=(400, 300))
        for target in targets:
            btn = Button(text=target.nombre, size_hint_y=None, height=40,
                         background_color=(0.6, 0.4, 0.2, 1), color=(1,1,1,1))
            btn.bind(on_press=lambda inst, t=target, c=carta, p=popup: self.rey_selected(jugador, t, c, p))
            target_buttons.add_widget(btn)
        content.add_widget(target_buttons)
        popup.open()

    def rey_selected(self, jugador, target, carta, popup):
        if target.mano and jugador.mano:
            # Intercambiar solo la carta que tienen en mano (siempre debería ser una)
            carta_jugador = jugador.mano[0] if jugador.mano else None
            carta_target = target.mano[0] if target.mano else None
            
            if carta_jugador and carta_target:
                jugador.mano = [carta_target]
                target.mano = [carta_jugador]
                self.log(f"{jugador.nombre} y {target.nombre} intercambian sus cartas")
                self.update_ui()  # Actualizar la interfaz para mostrar la nueva mano
            else:
                self.log("Error: Algún jugador no tiene carta para intercambiar")
        else:
            self.log("No se puede realizar el intercambio porque algún jugador no tiene cartas")
        popup.dismiss()
        self.next_button.disabled = False
        self.complete_card_play(carta)

    def show_chanceller_popup(self, jugador, carta):
        if len(self.partida.mazo) < 2:
            self.log("No hay suficientes cartas en el mazo para usar el Chanceller")
            self.complete_card_play(carta)
            return
        
        # Robar dos cartas
        cartas_robadas = [self.partida.mazo.pop(0) for _ in range(2)]
        
        content = BoxLayout(orientation='vertical')
        label = Label(text="Selecciona una carta para conservar")
        button_box = BoxLayout(orientation='horizontal')
        
        popup = Popup(title='Efecto del Chanceller',
                     content=content,
                     size_hint=(0.8, 0.4))
        
        def on_select(carta_elegida):
            # Conservar la carta elegida
            jugador.mano.append(carta_elegida)
            # Devolver la otra carta al mazo
            carta_devuelta = next(c for c in cartas_robadas if c != carta_elegida)
            self.partida.mazo.append(carta_devuelta)
            # Barajar el mazo
            random.shuffle(self.partida.mazo)
            self.log(f"{jugador.nombre} ha usado el Chanceller y ha elegido una carta")
            popup.dismiss()
            self.complete_card_play(carta)
        
        for c in cartas_robadas:
            btn = Button(text=c.nombre)
            btn.bind(on_press=lambda btn, c=c: on_select(c))
            button_box.add_widget(btn)
        
        content.add_widget(label)
        content.add_widget(button_box)
        popup.open()

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
        
        # Crear un widget de imagen con una imagen por defecto
        self.image = Image(source='images/default_card.png', size_hint=(1, 1))
        self.image.bind(on_error=self.on_image_error)
        self.add_widget(self.image)
        
        # Añadir una etiqueta para el nombre de la carta
        self.label = Label(
            text='',
            size_hint=(1, 0.2),
            color=(0.2, 0.1, 0, 1)
        )
        self.add_widget(self.label)

    def on_image_error(self, instance, *args):
        # Si la imagen no se puede cargar, usar la imagen por defecto
        instance.source = 'images/default_card.png'
        
    def update_card(self, carta):
        if carta:
            self.image.source = carta.image_source
            self.label.text = carta.nombre
        else:
            self.image.source = 'images/default_card.png'
            self.label.text = ''

# Mazo que se baraja y del que se reparten las cartas
class DeckWidget(ButtonBehavior, BoxLayout):
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback  # Función que se llamará al tocar el widget
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (200, 300)  # Ajustado para que el centro quede bien
        self.padding = 5
        self.spacing = 5
        
        # Usar la imagen del dorso de la carta
        self.image = Image(source='images/deck_back.png', size_hint=(1, 1))
        self.image.bind(on_error=self.on_image_error)
        self.add_widget(self.image)
        
        # Añadir una etiqueta para indicar que es el mazo
        self.label = Label(
            text='Mazo',
            size_hint=(1, 0.2),
            color=(0.2, 0.1, 0, 1)
        )
        self.add_widget(self.label)

    def on_image_error(self, instance, *args):
        # Si la imagen no se puede cargar, usar la imagen por defecto
        instance.source = 'images/default_card.png'

    def on_press(self):
        if self.callback:
            self.callback()
