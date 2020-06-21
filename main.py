from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config

Window.set_icon('res/images/hscc_logo.png')

# kivymd imports
from kivymd.theming import ThemeManager
from kivymd.button import MDIconButton, MDFlatButton
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel


from userinterface import BubbledTextInput
from userinterface.screens import RootScrMgr
from userinterface.screens.splashscreen import SplashScreen
from userinterface.screens.homescreen import HomeScreen 


Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy','window_icon','icon.ico')
Config.window_icon = "icon.ico"

class MainApp(App):
    icon = "icon.png"
    theme_cls = ThemeManager()
    title = 'HSCC Media Lyrics Finder'
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Green'
        self.theme_cls.primary_hue = '600'
        self.icon = 'icon.ico'
        return RootScrMgr()
    
    def on_start(*args):  
        width, height = Window.width, Window.height
        Window.minimum_width = width
        Window.minimum_height = height


MainApp().run()