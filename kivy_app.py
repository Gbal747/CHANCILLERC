# kivy_app.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from interfaz import SetupScreen, GameScreen

class CardGameApp(App):
    def build(self):
        # Configuración de la ventana (color de fondo, etc.) se puede definir aquí
        from kivy.core.window import Window
        Window.clearcolor = (0.95, 0.9, 0.8, 1)  # Color pergamino

        sm = ScreenManager()
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    CardGameApp().run()
