from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.popup import Popup

class MusicPlayer:
    def __init__(self):
        self.sound = None
        self.volume = 1.0  # Volumen inicial

    def play_music(self, file_path, loop=True):
        """Reproduce música en bucle si loop=True."""
        self.sound = SoundLoader.load(file_path)
        if self.sound:
            self.sound.loop = loop
            self.sound.volume = self.volume
            self.sound.play()

    def stop_music(self):
        """Detiene la música si está en reproducción."""
        if self.sound:
            self.sound.stop()

    def set_volume(self, volume, slider=None, label=None, mute_button=None):
        """Ajusta el volumen de la música y actualiza la interfaz."""
        self.volume = volume
        if self.sound:
            self.sound.volume = volume

        # Actualizar la etiqueta con el porcentaje de volumen
        if label:
            label.text = f"Volumen: {int(volume * 100)}%"

        # Cambiar el color del botón de silenciar si el volumen es 0
        if mute_button:
            mute_button.background_color = (1, 0, 0, 1) if volume == 0 else (1, 1, 1, 1)  # Rojo si está silenciado

    def show_volume_control(self):
        """Muestra un popup con un control deslizante para ajustar el volumen."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        volume_label = Label(text=f"Volumen: {int(self.volume * 100)}%", size_hint=(1, None), height=30)

        slider = Slider(min=0, max=1, value=self.volume, size_hint=(1, None), height=50)
        mute_button = Button(text="🔇 Silenciar", size_hint=(1, None), height=50)

        # Actualizar volumen con el slider
        slider.bind(value=lambda instance, value: self.set_volume(value, slider, volume_label, mute_button))

        # Botón de silenciar que ajusta el volumen a 0
        mute_button.bind(on_press=lambda instance: self.set_volume(0, slider, volume_label, mute_button))

        # Agregar widgets
        content.add_widget(volume_label)
        content.add_widget(slider)
        content.add_widget(mute_button)

        popup = Popup(title="Control de Volumen", content=content, size_hint=(0.5, 0.3))
        popup.open()

    def create_volume_button(self):
        """Crea un botón en la esquina superior derecha con un icono de nota musical 🎵."""
        volume_button = Button(text="\U0001F3B5", size_hint=(None, None), size=(50, 50), 
                               pos_hint={'right': 1, 'top': 1})  # Esquina superior derecha
        volume_button.bind(on_press=lambda instance: self.show_volume_control())
        return volume_button
