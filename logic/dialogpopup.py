from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.window import Window
import gc

# Screen for Login
class FuncScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        layout.add_widget(Label(text='Введите функцию'))
        self.function = TextInput(multiline=False, font_size=30)
        #! Data retrive
        self.app.function = self.function.text
        layout.add_widget(self.function)
        
        faq_button = Button(text='Какие функции принимаются ?', size_hint=(1, 0.5))
        faq_button.bind(on_press=self.pop_up)
        layout.add_widget(faq_button)
        self.add_widget(layout)

    def show_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        close_button = Button(text='Close')
        content.add_widget(close_button)
        popup = Popup(title='FAQ', content=content, size_hint=(None, None), size=(400, 200))
        close_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def pop_up(self, instance):
        self.show_popup("Привет мир")
    
class FuncApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.function = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(FuncScreen(name='login', app=self))
        return sm
    
    def terminate(self):
        """Ensure the app and window are fully closed."""
        print("Terminating the app instance...")
        self.stop()  # Stop the Kivy event loop
        Window.close()  # Forcefully close the Kivy window
        del self  # Remove the app instance
        gc.collect()  # Force garbage collection
        print("App instance terminated. Returning to main program.")


if __name__ == '__main__':
    app = FuncApp()
    app.run()
