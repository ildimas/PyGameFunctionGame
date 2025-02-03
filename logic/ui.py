from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.core.window import Window
from logic.utils import create_connection, authenticate_user, register_user
import sys
import gc
import os

def get_bg_image_path():
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    project_root = os.path.dirname(base_dir)  
    return os.path.join(project_root, "assets", "cobelstone.jpg")

# Screen for Login
class LoginScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
         # Add a background image using canvas.before
        with self.canvas.before:
            self.bg_rect = Rectangle(source=get_bg_image_path(), pos=self.pos, size=self.size)
        # Bind the screen's position and size to the update_bg method.
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text='Имя пользователя'))
        self.username = TextInput(multiline=False, font_size=60)
        layout.add_widget(self.username)

        layout.add_widget(Label(text='Пароль'))
        self.password = TextInput(password=True, multiline=False, font_size=60)
        layout.add_widget(self.password)

        login_button = Button(text='Войти', size_hint=(1, 0.5))
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)

        register_button = Button(text='Перейти к регистрации', size_hint=(1, 0.5))
        register_button.bind(on_press=self.go_to_register)
        layout.add_widget(register_button)

        self.add_widget(layout)
        
    def update_bg(self, *args):
        # Update the background rectangle's position and size.
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        close_button = Button(text='Close')
        content.add_widget(close_button)
    
    def login(self, instance):
        # Store login data in the app instance
        self.app.user_action = 'login'
        if (self.username.text != "" and self.password.text != "") and ((res:=authenticate_user(self.app.conn, self.username.text, self.password.text)) != None):
            self.app.username = res
            self.app.stop()  
        else:
            self.show_error_popup("Ошбика: Необходимо ввести имя пользователя и пароль k!")
            
    def go_to_register(self, instance):
        self.manager.current = 'register'

# Screen for Registration
class RegisterScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        with self.canvas.before:
            self.bg_rect = Rectangle(source=get_bg_image_path(), pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text='Придумайте имя пользователя'))
        self.new_username = TextInput(multiline=False, font_size=60)
        layout.add_widget(self.new_username)

        layout.add_widget(Label(text='Придумайте пароль'))
        self.new_password = TextInput(password=True, multiline=False, font_size=60)
        layout.add_widget(self.new_password)

        register_button = Button(text='Зарегистрироваться', size_hint=(1, 0.5))
        register_button.bind(on_press=self.register)
        layout.add_widget(register_button)

        back_button = Button(text='Перейти ко входу', size_hint=(1, 0.5))
        back_button.bind(on_press=self.go_to_login)
        layout.add_widget(back_button)

        self.add_widget(layout)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        close_button = Button(text='Close')
        content.add_widget(close_button)

        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


    def register(self, instance):
        # Store registration data in the app instance
        self.app.user_action = 'register'
        if (self.new_username.text != "" and self.new_password.text != "") and ((res:= register_user(self.app.conn, self.new_username.text, self.new_password.text)) != None):
            self.app.username = res
            self.app.stop()  
        else:
            self.show_error_popup("Ошбика: Необходимо ввести имя пользователя и пароль либо пользователь уже существует!")
            
    def go_to_login(self, instance):
        self.manager.current = 'login'

class LoginApp(App):
    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn
        self.username = None
        self.user_action = None  # Store whether the user logged in or registered
        self.user_data = None  # Store the user's input data

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login', app=self))
        sm.add_widget(RegisterScreen(name='register', app=self))
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
    app = LoginApp(conn=create_connection())
    app.run()
