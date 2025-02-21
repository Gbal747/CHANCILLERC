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
from kivy.uix.relativelayout import RelativeLayout
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
                         "Condesa", "Princesa", "Chanciller", "Espía"]
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

# Nueva pantalla para el efecto del Barón
class BaronScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jugador_actual = None
        self.carta = None
        self.game_screen = None
        
        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=[20, 30, 20, 10], spacing=10)
        self.add_widget(self.layout)
        
        # Sección de selección de jugador
        self.player_section = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.4))
        self.instruction_label = Label(
            text="Selecciona un jugador para comparar cartas:",
            size_hint=(1, 0.4),
            font_size='18sp',
            color=(0.2, 0.1, 0, 1)
        )
        self.player_section.add_widget(self.instruction_label)
        
        # Layout para los botones de jugadores
        self.target_buttons_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(0.7, 0.6),
            pos_hint={'center_x': 0.5}
        )
        self.player_section.add_widget(self.target_buttons_layout)
        self.layout.add_widget(self.player_section)
        
        # Botón de confirmar
        button_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.15),
            padding=[0, 0, 0, 10]
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

    def set_context(self, jugador_actual, carta, game_screen):
        self.jugador_actual = jugador_actual
        self.carta = carta
        self.game_screen = game_screen
        self.selected_target = None
        self.build_ui()

    def build_ui(self):
        self.target_buttons_layout.clear_widgets()
        
        # Construir botones para la selección de jugador objetivo
        targets = [j for j in self.game_screen.partida.jugadores 
                   if j != self.jugador_actual and not j.eliminado and not j.protegido]
        
        if not targets:
            self.game_screen.log("No hay objetivos disponibles para el Barón.")
            self.game_screen.complete_card_play(self.carta)
            self.game_screen.next_button.disabled = False
            self.game_screen.manager.current = 'game'
            return
            
        # Botones de jugadores
        button_width = 1.0 / len(targets) if targets else 1
        for target in targets:
            btn = Button(
                text=target.nombre,
                size_hint=(button_width, 0.7),
                pos_hint={'center_y': 0.5},
                background_color=(0.6, 0.4, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda instance, t=target: self.select_target(instance, t))
            self.target_buttons_layout.add_widget(btn)
            
        self.confirm_btn.bind(on_press=self.on_confirm)

    def select_target(self, instance, target):
        self.selected_target = target
        for child in self.target_buttons_layout.children:
            child.background_color = (0.6, 0.4, 0.2, 1)
        instance.background_color = (0, 1, 0, 1)

    def on_confirm(self, instance):
        if self.selected_target is None:
            self.game_screen.log("Debes seleccionar un objetivo.")
            return
            
        target = self.selected_target
        if target.mano:
            carta_jugador = [c for c in self.jugador_actual.mano if c != self.carta][0]
            carta_objetivo = target.mano[0]
            self.game_screen.log(f"Comparando cartas: {self.jugador_actual.nombre}({carta_jugador.nombre}) vs {target.nombre}({carta_objetivo.nombre})")
            
            if carta_jugador.valor > carta_objetivo.valor:
                self.game_screen.log(f"{target.nombre} es eliminado")
                target.eliminado = True
            elif carta_jugador.valor < carta_objetivo.valor:
                self.game_screen.log(f"{self.jugador_actual.nombre} es eliminado")
                self.jugador_actual.eliminado = True
            else:
                self.game_screen.log("Empate, nadie es eliminado")
        
        # Descartar la carta del Barón
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
class ChancillerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jugador_actual = None
        self.carta = None
        self.game_screen = None
        
        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=[20, 30, 20, 10], spacing=10)
        self.add_widget(self.layout)
        
        # Instrucción
        self.instruction_label = Label(
            text="Elige una carta para quedártela y devuelve dos al final del mazo en el orden que quieras:",
            size_hint=(1, 0.2),
            font_size='18sp',
            color=(0.2, 0.1, 0, 1)
        )
        self.layout.add_widget(self.instruction_label)
        
        # Layout para las cartas en posiciones específicas
        self.card_section = RelativeLayout(size_hint=(1, 0.6))
        self.layout.add_widget(self.card_section)
        
        # Botón de confirmar
        self.confirm_btn = Button(
            text="Confirmar",
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0.6, 0.4, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.confirm_btn)
        self.confirm_btn.bind(on_press=self.on_confirm)
        
        self.selected_card = None
        self.cards_drawn = []
    
    def set_context(self, jugador_actual, carta, game_screen):
        self.jugador_actual = jugador_actual
        self.carta = carta
        self.game_screen = game_screen
        self.selected_card = None
        self.cards_drawn = self.draw_two_cards()
        self.cards_drawn.append(self.jugador_actual.mano.pop())  # Agregar la carta que ya tenía
        self.build_ui()
    
    def draw_two_cards(self):
        """Robar dos cartas del mazo."""
        if len(self.game_screen.partida.deck) < 2:
            return self.game_screen.partida.deck[:]
        return [self.game_screen.partida.deck.pop(0) for _ in range(2)]
    
    def build_ui(self):
        self.card_section.clear_widgets()
        
        positions = [{'center_x': 0.5, 'center_y': 0.5}, {'center_x': 0.2, 'center_y': 0.5}, {'center_x': 0.8, 'center_y': 0.5}]
        
        for i, card in enumerate(self.cards_drawn):
            card_btn = Image(
                source=card.image_source,
                size_hint=(None, None),
                size=(150, 200),
                pos_hint=positions[i]
            )
            card_btn.bind(
                on_touch_down=lambda instance, touch, c=card: self.select_card(c) if instance.collide_point(*touch.pos) else None
            )
            card_btn.bind(
                on_touch_move=lambda instance, touch, c=card: self.highlight_card(instance, touch, c) if instance.collide_point(*touch.pos) else None
            )
            card_btn.bind(
                on_touch_up=lambda instance, touch, c=card: self.remove_highlight(instance, touch, c) if instance.collide_point(*touch.pos) else None
            )
            self.card_section.add_widget(card_btn)
    
    def highlight_card(self, instance, touch, card):
        """Resalta la carta cuando el ratón pasa sobre ella."""
        if self.selected_card != card:
            instance.size = (170, 220)  # Aumentar tamaño
            instance.opacity = 0.8  # Hacerla ligeramente transparente
    
    def remove_highlight(self, instance, touch, card):
        """Elimina el resaltado cuando el ratón ya no está sobre la carta."""
        if self.selected_card != card:
            instance.size = (150, 200)  # Tamaño original
            instance.opacity = 1  # Opacidad normal
    
    def select_card(self, card):
        """Método para seleccionar la carta al hacer click sobre ella"""
        if self.selected_card == card:
            return  # Si la carta ya está seleccionada, no hacer nada
        self.selected_card = card
        print(f"Carta seleccionada: {card.nombre}")  # Para depurar
        
        # Al seleccionar la carta, podemos cambiar su estilo visual (por ejemplo, bordes)
        for child in self.card_section.children:
            if isinstance(child, Image):
                if child.source == card.image_source:
                    child.opacity = 1  # Asegurarse de que la carta seleccionada esté completamente visible
                    child.size = (170, 220)  # Tamaño resaltado
                else:
                    child.opacity = 0.6  # Deja las demás cartas menos opacas (no seleccionadas)
    
    def on_confirm(self, instance):
        if self.selected_card is None:
            popup = Popup(title="Error", content=Label(text="Debes seleccionar una carta para quedártela."),
                          size_hint=(None, None), size=(300, 200))
            popup.open()
            return
        
        self.jugador_actual.mano.append(self.selected_card)
        self.cards_drawn.remove(self.selected_card)
        
        self.ask_card_order()
    
    def ask_card_order(self):
        """Permite al jugador elegir el orden de las cartas restantes en el mazo."""
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)  # Aumentar espaciado y padding
        instruction_label = Label(
            text="Selecciona la carta que irá en la última posición:",
            size_hint=(1, None),
            height=50,  # Ajustar la altura del texto
            font_size='14sp',  # Reducir el tamaño del texto
            color=(1, 1, 1, 1),  # Texto en blanco
            valign='top',
            halign='center'  # Centrar el texto horizontalmente
        )
        content.add_widget(instruction_label)
    
        # Layout para las cartas (centradas en el centro)
        card_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, None), height=200, pos_hint={'center_x': 0.5})
    
        # Crear botones de las cartas
        for card in self.cards_drawn:
            card_btn = Image(
                source=card.image_source,
                size_hint=(None, None),
                size=(150, 200),  # Tamaño de las cartas
                pos_hint={'center_y': 0.5}
            )
            # Asegurarnos de que `self` se pase correctamente dentro del lambda
            card_btn.bind(
                on_touch_down=lambda instance, touch, c=card: self.select_last_card(c) if instance.collide_point(*touch.pos) else None
            )
            card_btn.bind(
                on_touch_move=lambda instance, touch, c=card: self.highlight_last_card(instance, touch, c) if instance.collide_point(*touch.pos) else None
            )
            card_btn.bind(
                on_touch_up=lambda instance, touch, c=card: self.remove_highlight_last_card(instance, touch, c) if instance.collide_point(*touch.pos) else None
            )
            card_layout.add_widget(card_btn)
        content.add_widget(card_layout)

        # Crear la ventana emergente
        self.order_popup = Popup(
            title="Orden de cartas",
            content=content,
            size_hint=(None, None),
            size=(500, 300)  # Aumentar tamaño de la ventana emergente
        )
        self.order_popup.open()

    def highlight_last_card(self, instance, touch, card):
        """Resalta la carta de la última posición cuando el ratón pasa sobre ella."""
        instance.opacity = 0.8  # Hacerla un poco más transparente para resaltar
    
    def remove_highlight_last_card(self, instance, touch, card):
        """Elimina el resaltado de la carta de la última posición."""
        instance.opacity = 1  # Restablecer opacidad a su valor original
    
    def select_last_card(self, card):
        """Seleccionar la carta que irá en la última posición."""
        self.cards_drawn.remove(card)
        self.game_screen.partida.deck.append(card)
        self.select_second_last_card()
    
    def select_second_last_card(self):
        remaining_card = self.cards_drawn[0]
        self.game_screen.partida.deck.append(remaining_card)
        self.order_popup.dismiss()
        self.game_screen.log(f"{self.jugador_actual.nombre} ha devuelto las cartas al final del mazo.")
        self.game_screen.complete_card_play(self.carta)
        self.game_screen.next_button.disabled = False
        self.game_screen.manager.current = 'game'
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
        self.card_played = False  # Variable para controlar si se ha jugado una carta
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

        # Reiniciar el estado de la carta jugada para el siguiente turno
        self.card_played = False

    def elegir_jugador(self, carta):
        """
        Maneja la selección de un objetivo para el efecto de una carta
        """
        self.next_button.disabled = True
        if carta.nombre == "Guardia":
            self.show_guardia_screen(self.partida.current_player, carta)
        elif carta.nombre == "Sacerdote":
            # Obtener jugadores válidos como objetivo
            targets = [j for j in self.partida.jugadores if j != self.partida.current_player and not j.eliminado and not j.protegido]
            
            if not targets:
                self.log("No hay objetivos válidos para el Sacerdote")
                self.card_played = True
                self.next_button.disabled = False
                self.complete_card_play(carta)
                return
                
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text="Selecciona un jugador para ver su carta:", font_size='18sp'))
            
            # Layout para los botones
            buttons_layout = GridLayout(cols=2, spacing=10, padding=10)

            # Crear el popup antes de los botones para poder referenciarlo
            selection_popup = Popup(
                title='Efecto del Sacerdote',
                content=content,
                size_hint=(0.8, 0.8),
                auto_dismiss=False
            )
            
            for target in targets:
                btn = Button(
                    text=target.nombre,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.6, 0.4, 0.2, 1),
                    color=(1,1,1,1)
                )
                def create_callback(t=target, p=selection_popup):
                    def on_press(instance):
                        p.dismiss()  # Cerrar el popup usando la referencia correcta
                        # Mostrar la carta del objetivo
                        self.show_target_card(self.partida.current_player, t, carta)
                    return on_press
                btn.bind(on_press=create_callback())
                buttons_layout.add_widget(btn)
            
            content.add_widget(buttons_layout)
            selection_popup.open()
        elif carta.nombre == "Barón":
            # Mostrar popup para seleccionar objetivo para el Barón
            targets = [j for j in self.partida.jugadores if j != self.partida.current_player and not j.eliminado and not j.protegido]
            if not targets:
                self.log("No hay objetivos válidos para el Barón")
                self.card_played = True
                self.next_button.disabled = False
                self.complete_card_play(carta)
                return
            
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text="Selecciona un jugador para comparar cartas:", font_size='18sp'))
            
            # Layout para los botones
            buttons_layout = GridLayout(cols=2, spacing=10, padding=10)

            # Crear el popup antes de los botones para poder referenciarlo
            baron_popup = Popup(
                title='Efecto del Barón',
                content=content,
                size_hint=(0.8, 0.8),
                auto_dismiss=False
            )
            
            for target in targets:
                btn = Button(
                    text=target.nombre,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.6, 0.4, 0.2, 1),
                    color=(1,1,1,1)
                )
                def create_callback(t=target, p=baron_popup):
                    def on_press(instance):
                        p.dismiss()  # Cerrar el popup usando la referencia correcta
                        self.compare_hands(self.partida.current_player, t, carta)
                    return on_press
                btn.bind(on_press=create_callback())
                buttons_layout.add_widget(btn)
            
            content.add_widget(buttons_layout)
            baron_popup.open()
        elif carta.nombre == "Príncipe":
            self.show_principe_popup(self.partida.current_player, carta)
        elif carta.nombre == "Rey":
            self.show_rey_popup(self.partida.current_player, carta)
        else:
            # Para cartas sin efecto que requieren selección de objetivo
            self.complete_card_play(carta)
        
        # Marcar que se jugó una carta
        self.card_played = True

    def on_target_selected(self, jugador, carta, target):
        """
        Maneja la selección de un objetivo para el efecto de una carta
        """
        if target:
            if carta.nombre == "Guardia":
                self.show_guardia_screen(jugador, carta)
            elif carta.nombre == "Sacerdote":
                self.show_target_card(self.partida.current_player, target, carta)
                self.complete_card_play(carta)
            elif carta.nombre == "Barón":
                self.compare_hands(jugador, target, carta)
            elif carta.nombre == "Príncipe":
                self.discard_and_draw(target, carta)
            elif carta.nombre == "Rey":
                self.swap_hands(jugador, target, carta)
            
            # Marcar que se jugó una carta
            self.card_played = True
            
        else:
            self.log("Debes seleccionar un objetivo.")

    def show_guardia_screen(self, jugador, carta):
        guardia_screen = self.manager.get_screen('guardia')
        guardia_screen.set_context(jugador, carta, self)
        self.manager.current = 'guardia'

    def show_sacerdote_popup(self, jugador, carta):
        """
        Muestra el popup para seleccionar el objetivo del Sacerdote
        """
        content = BoxLayout(orientation='vertical')
        label = Label(text="Selecciona un jugador para ver su carta:")
        content.add_widget(label)
        
        # Marcar que se jugó una carta inmediatamente
        self.card_played = True
        
        # Crear botones para cada jugador que no sea el actual y no esté eliminado o protegido
        target_buttons = GridLayout(cols=2, spacing=10, padding=10)
        for target in self.partida.jugadores:
            if target != jugador and not target.eliminado and not target.protegido:
                btn = Button(
                    text=target.nombre,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.6, 0.4, 0.2, 1),
                    color=(1,1,1,1)
                )
                def create_callback(t=target, p=popup):
                    def on_press(instance):
                        p.dismiss()
                        self.show_target_card(jugador, t, carta)
                    return on_press
                btn.bind(on_press=create_callback())
                target_buttons.add_widget(btn)
        
        content.add_widget(target_buttons)
        
        # Si no hay objetivos válidos
        if not target_buttons.children:
            self.log("No hay objetivos válidos para el Sacerdote")
            self.complete_card_play(carta)
            return
        
        popup = Popup(
            title='Efecto del Sacerdote',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.open()

    def show_target_card(self, jugador, target, carta):
        """Muestra la carta del jugador objetivo en un popup con imagen y efectos visuales."""
        if not target.mano:
            self.log(f"{target.nombre} no tiene cartas en la mano")
            self.complete_card_play(carta)
            return
        
        carta_objetivo = target.mano[0]
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Fondo semitransparente
        with content.canvas.before:
            Color(0, 0, 0, 0.5)
            content.rect = Rectangle(size=content.size, pos=content.pos)
        content.bind(size=lambda instance, value: setattr(content.rect, 'size', value))
        content.bind(pos=lambda instance, value: setattr(content.rect, 'pos', value))
        
        # Imagen de la carta centrada
        card_image = Image(source=carta_objetivo.image_source, size_hint=(None, None), size=(200, 300), pos_hint={'center_x': 0.5})
        content.add_widget(card_image)
        
        # Solo mostrar el nombre del jugador
        info_label = Label(text=target.nombre, color=(1, 1, 1, 1), font_size='20sp', bold=True)
        content.add_widget(info_label)
        
        # Botón de cerrar con efectos visuales
        close_btn = Button(
            text="Continuar",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        def on_press_effect(instance):
            instance.background_color = (1, 0.5, 0.5, 1)
        
        def on_release_effect(instance):
            instance.background_color = (0.8, 0.2, 0.2, 1)
        
        close_btn.bind(on_press=on_press_effect)
        close_btn.bind(on_release=on_release_effect)
        content.add_widget(close_btn)
        
        popup = Popup(title=f'Carta de {target.nombre}', content=content, size_hint=(0.8, 0.8), auto_dismiss=False, background_color=(0, 0, 0, 0))
        
        def on_close(instance):
            popup.dismiss()
            self.log(f"{jugador.nombre} vio la carta de {target.nombre}")
            self.manager.current = 'game'
            self.complete_card_play(carta)
        
        close_btn.bind(on_press=on_close)
        popup.open()

    # Nueva función para mostrar el popup de victoria con animaciones
    def show_winner_popup(self, ganador):
        """Muestra una animación con el ganador y un botón para reiniciar la partida."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Fondo semitransparente para mejorar visibilidad
        with content.canvas.before:
            Color(0.95, 0.9, 0.8, 1)
            content.rect = Rectangle(size=content.size, pos=content.pos)
        content.bind(size=lambda instance, value: setattr(content.rect, 'size', value))
        content.bind(pos=lambda instance, value: setattr(content.rect, 'pos', value))
        
        # Animación del nombre del ganador
        winner_label = Label(text=f"¡{ganador.nombre} ha ganado!", font_size='24sp', bold=True, color=(1, 1, 0, 1))
        anim = Animation(font_size=30, duration=0.5) + Animation(font_size=24, duration=0.5)
        anim.repeat = True
        anim.start(winner_label)
        content.add_widget(winner_label)
    
        # Botón para reiniciar la partida
        restart_btn = Button(
            text="Jugar de nuevo",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        def restart_game(instance):
            popup.dismiss()
            setup_screen = self.manager.get_screen('setup')
            setup_screen.build_initial_ui()  # Reiniciar la interfaz de selección de jugadores
            self.manager.current = 'setup'
        
        restart_btn.bind(on_press=restart_game)
        content.add_widget(restart_btn)
        
        popup = Popup(title='¡Victoria!', content=content, size_hint=(0.8, 0.8), auto_dismiss=False, background_color=(0, 0, 0, 0))
        popup.open()


    def show_baron_popup(self, jugador, carta):
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Barón.")
            self.complete_card_play(carta)
            return
        
        content = BoxLayout(orientation='vertical')
        label = Label(text="Selecciona un jugador para comparar cartas:")
        content.add_widget(label)
        
        # Crear botones para cada jugador que no sea el actual y no esté eliminado o protegido
        target_buttons = GridLayout(cols=2, spacing=10, padding=10)
        for target in targets:
            btn = Button(
                text=target.nombre,
                size_hint_y=None,
                height=40,
                background_color=(0.6, 0.4, 0.2, 1),
                color=(1,1,1,1)
            )
            def create_callback(t=target, p=popup):
                def on_press(instance):
                    p.dismiss()  # Cerrar el popup usando la referencia correcta
                    self.compare_hands(jugador, t, carta)
                return on_press
            btn.bind(on_press=create_callback())
            target_buttons.add_widget(btn)
        
        content.add_widget(target_buttons)
        
        # Si no hay objetivos válidos
        if not target_buttons.children:
            self.log("No hay objetivos válidos para el Barón")
            self.card_played = True  # Marcar que se jugó la carta aunque no haya efecto
            self.complete_card_play(carta)
            return
        
        popup = Popup(
            title='Efecto del Barón',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.open()

    def baron_selected(self, jugador, target, carta):
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
        self.card_played = True
        self.complete_card_play(carta)

    def show_principe_popup(self, jugador, carta):
        """
        Muestra el popup para seleccionar el objetivo del Príncipe
        """
        # Obtener todos los jugadores no eliminados como objetivos válidos (incluyendo al jugador actual)
        targets = [j for j in self.partida.jugadores if not j.eliminado and not j.protegido]
        
        if not targets:
            self.log("No hay objetivos válidos para el Príncipe")
            self.card_played = True
            self.next_button.disabled = False
            self.complete_card_play(carta)
            return
            
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador para descartar su carta:", font_size='18sp'))
        
        # Layout para los botones
        buttons_layout = GridLayout(cols=2, spacing=10, padding=10)

        # Crear el popup antes de los botones para poder referenciarlo
        principe_popup = Popup(
            title='Efecto del Príncipe',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )

        for target in targets:
            btn = Button(
                text=target.nombre,
                size_hint_y=None,
                height=40,
                background_color=(0.6, 0.4, 0.2, 1),
                color=(1,1,1,1)
            )
            def create_callback(t=target, p=principe_popup):
                def on_press(instance):
                    p.dismiss()  # Cerrar el popup usando la referencia correcta
                    self.descartar_y_robar(t, carta)
                return on_press
            btn.bind(on_press=create_callback())
            buttons_layout.add_widget(btn)
        
        content.add_widget(buttons_layout)
        principe_popup.open()

    def descartar_y_robar(self, target, carta):
        """
        Descarta la carta del objetivo y le hace robar una nueva
        """
        if not target.mano:
            self.log(f"{target.nombre} no tiene cartas para descartar")
            self.complete_card_play(carta)
            return
            
        # Obtener la carta a descartar
        carta_descartada = target.mano[0]
        
        # Si descarta la Princesa, el jugador es eliminado
        if carta_descartada.nombre == "Princesa":
            self.log(f"{target.nombre} descartó la Princesa y queda eliminado")
            target.eliminado = True
            target.mano = []
            self.complete_card_play(carta)
            return
            
        # Descartar la carta actual
        target.mano = []
        self.discard_pile.update_card(carta_descartada)
        
        # Robar una nueva carta si quedan en el mazo
        if self.partida.deck:
            nueva_carta = self.partida.deck.pop(0)
            target.mano = [nueva_carta]
            self.log(f"{target.nombre} descartó {carta_descartada.nombre} y robó una nueva carta")
        else:
            self.log(f"{target.nombre} descartó {carta_descartada.nombre} pero no quedan cartas para robar")
            
        self.complete_card_play(carta)

    def show_rey_popup(self, jugador, carta):
        targets = [j for j in self.partida.jugadores if j != jugador and not j.eliminado and not j.protegido]
        if not targets:
            self.log("No hay objetivos disponibles para el Rey.")
            self.complete_card_play(carta)
            return
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Selecciona un jugador para intercambiar cartas:", font_size='18sp'))
        
        # Layout para los botones
        target_buttons = GridLayout(cols=2, spacing=10, padding=10)

        # Crear el popup antes de los botones para poder referenciarlo
        rey_popup = Popup(
            title='Efecto del Rey',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        for target in targets:
            btn = Button(
                text=target.nombre,
                size_hint_y=None,
                height=40,
                background_color=(0.6, 0.4, 0.2, 1),
                color=(1,1,1,1)
            )
            def create_callback(t=target, p=rey_popup):
                def on_press(instance):
                    p.dismiss()  # Cerrar el popup usando la referencia correcta
                    self.intercambiar_cartas(jugador, t, carta)
                return on_press
            btn.bind(on_press=create_callback())
            target_buttons.add_widget(btn)
        
        content.add_widget(target_buttons)
        rey_popup.open()

    def intercambiar_cartas(self, jugador, target, carta):
        """
        Intercambia las cartas entre dos jugadores
        """
        if not target.mano:
            self.log(f"{target.nombre} no tiene cartas para intercambiar")
            self.complete_card_play(carta)
            return
            
        # Obtener las cartas a intercambiar (excluyendo la carta Rey que se está jugando)
        carta_jugador = [c for c in jugador.mano if c != carta][0] if jugador.mano else None
        carta_target = target.mano[0] if target.mano else None
        
        if not carta_jugador or not carta_target:
            self.log("No hay suficientes cartas para intercambiar")
            self.complete_card_play(carta)
            return
            
        # Realizar el intercambio
        jugador.mano = [carta_target]
        target.mano = [carta_jugador]
        
        self.log(f"{jugador.nombre} intercambió cartas con {target.nombre}")
        self.complete_card_play(carta)

    def show_baron_screen(self, jugador, carta):
        content = BoxLayout(orientation='vertical')
        label = Label(text="Selecciona un jugador para comparar manos:")
        content.add_widget(label)
        
        # Crear botones para cada jugador que no sea el actual y no esté eliminado o protegido
        target_buttons = GridLayout(cols=2, spacing=10, padding=10)
        for target in self.partida.jugadores:
            if target != jugador and not target.eliminado and not target.protegido:
                btn = Button(
                    text=target.nombre,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.6, 0.4, 0.2, 1),
                    color=(1,1,1,1)
                )
                def create_callback(t=target, p=popup):
                    def on_press(instance):
                        p.dismiss()  # Cerrar el popup usando la referencia correcta
                        self.on_target_selected(jugador, carta, t)
                    return on_press
                btn.bind(on_press=create_callback())
                target_buttons.add_widget(btn)
        
        content.add_widget(target_buttons)
        
        # Si no hay objetivos válidos
        if not target_buttons.children:
            self.log("No hay objetivos válidos para el Barón")
            self.card_played = True  # Marcar que se jugó la carta aunque no haya efecto
            self.complete_card_play(carta)
            return
        
        popup = Popup(
            title='Efecto del Barón',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.open()

    def compare_hands(self, jugador, target, carta):
        """
        Compara las cartas de dos jugadores para el efecto del Barón
        """
        # Obtener las cartas de ambos jugadores
        carta_jugador = jugador.mano[0] if jugador.mano else None
        carta_target = target.mano[0] if target.mano else None
        
        if not carta_jugador or not carta_target:
            self.log("Uno de los jugadores no tiene cartas para comparar")
            return
        
        # Mostrar las cartas
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Carta de {jugador.nombre}: {carta_jugador.nombre} ({carta_jugador.valor})", font_size='18sp'))
        content.add_widget(Label(text=f"Carta de {target.nombre}: {carta_target.nombre} ({carta_target.valor})", font_size='18sp'))
        
        # Determinar el ganador
        if carta_jugador.valor > carta_target.valor:
            content.add_widget(Label(text=f"{target.nombre} es eliminado del juego", font_size='20sp', color=(1, 0, 0, 1)))
            target.eliminado = True
        elif carta_jugador.valor < carta_target.valor:
            content.add_widget(Label(text=f"{jugador.nombre} es eliminado del juego", font_size='20sp', color=(1, 0, 0, 1)))
            jugador.eliminado = True
        else:
            content.add_widget(Label(text="¡Empate! Nadie es eliminado", font_size='20sp'))
        
        # Crear y mostrar el popup
        popup = Popup(
            title='Resultado de la comparación',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        # Botón para cerrar
        close_button = Button(
            text="Cerrar",
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.5}
        )
        
        def on_close(instance):
            popup.dismiss()
            self.card_played = True
            self.next_button.disabled = False
            self.complete_card_play(carta)
        
        close_button.bind(on_press=on_close)
        content.add_widget(close_button)
        
        popup.open()

    def remove_widget_after_anim(self, animation, widget):
        """
        Callback para remover un widget después de que termine su animación
        """
        if widget in self.hand_layout.children:
            self.hand_layout.remove_widget(widget)

    def play_card(self, carta):
        """
        Juega una carta de la mano del jugador actual
        """
        if self.card_played:
            return
        
        self.card_played = True
        jugador = self.partida.current_player
        
        # Remover la carta de la mano del jugador
        if carta in jugador.mano:
            jugador.mano.remove(carta)
        
        # Animar la carta hacia el mazo de descartes
        card_widget = None
        for widget in self.hand_layout.children:
            if isinstance(widget, CardWidget) and widget.carta == carta:
                card_widget = widget
                break
        
        if card_widget:
            # Obtener la posición del mazo de descartes
            discard_pos = self.discard_pile.pos
            
            # Crear la animación
            anim = Animation(opacity=0, duration=0.3)
            anim.bind(on_complete=self.remove_widget_after_anim)
            anim.start(card_widget)
        
        # Agregar la carta al mazo de descartes
        self.partida.discard_pile.append(carta)
        self.discard_pile.update_card(carta)
        
        # Manejar el efecto de la carta
        if carta.nombre in ["Guardia", "Sacerdote", "Barón", "Príncipe", "Rey"]:
            self.elegir_jugador(carta)
        elif carta.nombre == "Chanciller":
            chanciller_screen = self.manager.get_screen('chanciller')
            chanciller_screen.set_context(self.partida.current_player, carta, self)
            self.manager.current = 'chanciller'
        else:
            self.complete_card_play(carta)

    def confirm_play_card(self, carta, popup):
        """
        Confirma jugar una carta después de ver sus detalles
        """
        # Verificar la regla de la Condesa
        tiene_condesa = any(carta.nombre == "Condesa" for carta in self.partida.current_player.mano)
        tiene_rey_o_principe = any(carta.nombre in ["Rey", "Príncipe"] for carta in self.partida.current_player.mano)
        
        if tiene_condesa and tiene_rey_o_principe and carta.nombre != "Condesa":
            error_popup = Popup(title="Regla de la Condesa",
                            content=Label(text="Si tienes la Condesa y el Rey o el Príncipe,\ndebes jugar la Condesa.",
                                        color=(0.2,0.1,0,1)),
                            size_hint=(None, None), size=(400, 200))
            error_popup.open()
            return

        popup.dismiss()
        self.play_card(carta)

    def show_card_details(self, carta):
        """
        Muestra los detalles de una carta y permite jugarla
        """
        # Si ya se ha jugado una carta, no permitir jugar otra
        if self.card_played:
            popup = Popup(title='Aviso',
                        content=Label(text='Ya has jugado una carta.',
                                    color=(0.2,0.1,0,1)),
                        size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        # Verificar la regla de la Condesa
        tiene_condesa = any(carta.nombre == "Condesa" for carta in self.partida.current_player.mano)
        tiene_rey_o_principe = any(carta.nombre in ["Rey", "Príncipe"] for carta in self.partida.current_player.mano)
        
        if tiene_condesa and tiene_rey_o_principe and carta.nombre != "Condesa":
            popup = Popup(title="Regla de la Condesa",
                        content=Label(text="Si tienes la Condesa y el Rey o el Príncipe,\ndebes jugar la Condesa.",
                                    color=(0.2,0.1,0,1)),
                        size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        content = BoxLayout(orientation='vertical', spacing=5, padding=5)
        
        # Layout principal
        card_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
        card_image = Image(
            source=carta.image_source,
            size_hint=(None, None),
            size=(180, 270),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        card_layout.add_widget(card_image)
        content.add_widget(card_layout)
        
        # Solo la descripción
        content.add_widget(Label(
            text=carta.descripcion,
            font_size='16sp',
            color=(0.2,0.1,0,1),
            size_hint=(1, 0.2)
        ))
        
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
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title="Detalles de la carta",
            content=content,
            size_hint=(None, None),
            size=(300, 450),
            auto_dismiss=False
        )
        
        # Vincular botones
        back_btn.bind(on_press=popup.dismiss)
        play_btn.bind(on_press=lambda inst: self.confirm_play_card(carta, popup))
        
        popup.open()

    def complete_card_play(self, carta):
        """
        Completa el efecto de una carta y actualiza el estado del juego
        """
        # Asegurarse de que la carta se marque como jugada
        self.card_played = True
        
        # Si es la princesa, el jugador queda eliminado
        if carta.nombre == "Princesa":
            jugador = self.partida.current_player
            jugador.eliminado = True
            self.log(f"{jugador.nombre} jugó la Princesa y queda eliminado")
            
            # Descartar las cartas restantes del jugador eliminado
            for carta_restante in jugador.mano:
                self.partida.discard_pile.append(carta_restante)
                self.discard_pile.update_card(carta_restante)
            jugador.mano.clear()
        
        # Habilitar el botón de siguiente turno
        self.next_button.disabled = False
        
        # Actualizar la interfaz
        self.update_ui()
        
        # Verificar si hay ganador
        ganador = self.partida.determinar_ganador()
        if ganador:
            self.show_winner_popup(ganador)

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