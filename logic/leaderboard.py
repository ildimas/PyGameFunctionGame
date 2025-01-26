from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.window import Window
from logic.utils import create_connection
import sys
import gc

# Screen for displaying player scores
class ScoresScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Add a title
        layout.add_widget(Label(text='Таблица результатов', font_size=30))

        # Create a scrollable list of scores
        scroll_view = ScrollView()
        self.scores_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scores_layout.bind(minimum_height=self.scores_layout.setter('height'))
        scroll_view.add_widget(self.scores_layout)

        layout.add_widget(scroll_view)

        # Add a back button
        back_button = Button(text='Назад', size_hint=(1, 0.2))
        layout.add_widget(back_button)

        self.add_widget(layout)

    def update_scores(self, scores):
        # Clear existing scores
        self.scores_layout.clear_widgets()
        for player, score in scores.items():
            self.scores_layout.add_widget(Label(text=f'{player}: {score}', font_size=20))

class ScoreApp(App):
    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn

    def build(self):
        sm = ScreenManager()
        self.scores_screen = ScoresScreen(name='scores', app=self)
        sm.add_widget(self.scores_screen)
        return sm

    def show_scores(self):
        # Simulate scores for demonstration purposes
        scores = {
            'Игрок1': 100,
            'Игрок2': 85,
            'Игрок3': 78,
            'Игрок4': 92,
        }
        self.scores_screen.update_scores(scores)
        self.root.current = 'scores'
        
    def terminate(self):
        """Ensure the app and window are fully closed."""
        print("Terminating the app instance...")
        self.stop()  # Stop the Kivy event loop
        Window.close()  # Forcefully close the Kivy window
        del self  # Remove the app instance
        gc.collect()  # Force garbage collection
        print("App instance terminated. Returning to main program.")


if __name__ == '__main__':
    app = ScoreApp(conn=create_connection())
    app.run()
