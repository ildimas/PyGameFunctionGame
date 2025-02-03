from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Rectangle
import os
import sys
import gc
from logic.utils import create_connection, get_all_users_scores# Ensure this function retrieves scores from a database

# -----------------------------
# Function to Get Background Image Path
# -----------------------------
def get_bg_image_path():
    """Returns the path of the background image stored in the 'assets' folder."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    return os.path.join(project_root, "assets", "gold.jpeg")  # Ensure this file exists!

# -----------------------------
# Scores Screen with Texture Background
# -----------------------------
class ScoresScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        # Apply background image
        with self.canvas.before:
            self.bg_rect = Rectangle(source=get_bg_image_path(), pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Main Layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title Label
        layout.add_widget(Label(text='Таблица результатов', font_size=30, bold=True))

        # Scrollable Score List
        scroll_view = ScrollView(size_hint=(1, 0.8), do_scroll_x=False)  # Only vertical scrolling
        self.scores_layout = GridLayout(cols=1, spacing=20, size_hint_y=None)  # Increase spacing
        self.scores_layout.bind(minimum_height=self.scores_layout.setter('height'))  # Make it scrollable
        scroll_view.add_widget(self.scores_layout)
        layout.add_widget(scroll_view)

        # Close Button (instead of "Back")
        close_button = Button(text='Выйти', size_hint=(1, 0.2))
        close_button.bind(on_press=self.close_program)
        layout.add_widget(close_button)

        self.add_widget(layout)

    def update_bg(self, *args):
        """Updates background size and position when the screen is resized."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_scores(self, scores):
        """Updates the displayed scores dynamically with black text and spacing."""
        self.scores_layout.clear_widgets()
        for player, score in scores.items():
            label = Label(
                text=f'{player}: {score}',
                font_size=22,  # Slightly larger font
                bold=True,
                color=(0, 0, 0, 1),  # Black color
                size_hint_y=None,
                height=40  # More space between lines
            )
            self.scores_layout.add_widget(label)

    def close_program(self, instance):
        """Closes the Kivy application."""
        print("Closing the application...")
        App.get_running_app().stop()  # Properly stop Kivy app
        sys.exit()  # Force exit the script


# -----------------------------
# Main ScoreApp Class
# -----------------------------
class ScoreApp(App):
    def __init__(self, conn, scores, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn
        self.scores_screen = None
        self.scores_data = scores  # Store the scores passed during initialization

    def build(self):
        sm = ScreenManager()
        self.scores_screen = ScoresScreen(name='scores', app=self)
        sm.add_widget(self.scores_screen)
        return sm

    def on_start(self):
        """Updates the scores when the app starts."""
        if self.scores_data:
            self.scores_screen.update_scores(self.scores_data)

    def terminate(self):
        """Ensure the app and window are fully closed."""
        print("Terminating the app instance...")
        self.stop()
        Window.close()
        del self
        gc.collect()
        print("App instance terminated. Returning to main program.")


# -----------------------------
# Example Usage
# -----------------------------
if __name__ == '__main__':
    conn = create_connection()  # Establish database connection

    # Example: Simulating score retrieval from a database (many scores to test scrolling)
    # Start the Kivy application with scores
    app = ScoreApp(conn, get_all_users_scores(conn))
    app.run()
    sys.exit()
