from musica import MusicPlayer
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.floatlayout import FloatLayout
from interfaz import SetupScreen, GameScreen, GuardiaScreen, ChancillerScreen

class CardGameApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.95, 0.9, 0.8, 1)  # Color pergamino

        # Iniciar reproductor de música
        self.music_player = MusicPlayer()
        self.music_player.play_music("assets/music/love_letters_theme.mp3")  # Ajusta la ruta

        # Crear el gestor de pantallas
        sm = ScreenManager()
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(GuardiaScreen(name='guardia'))
        sm.add_widget(ChancillerScreen(name='chanciller'))

        # Agregar el botón de volumen en la capa superior
        root_layout = FloatLayout()
        root_layout.add_widget(sm)
        root_layout.add_widget(self.music_player.create_volume_button())  # Agrega el botón mejorado

        return root_layout  # Retorna el layout con el botón agregado

if __name__ == '__main__':
    CardGameApp().run()
