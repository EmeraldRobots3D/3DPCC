from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window

from gui.PCC import PCC


class CustomInput(Widget):
    pass


class PCCApp(MDApp):
    def __init__(self):
        MDApp.__init__(self)
        Window.minimum_height = 600
        Window.minimum_width = 800

    def build(self):
        # Builder.load_file("gui/PCC.kv")
        self.theme_cls.theme_style = "Dark"
        program = PCC()
        Clock.schedule_interval(program.update, 1.0 / 60.0)
        self.title = "3D Printer Controller Controller"
        return program

    def on_start(self, **kwargs):
        self.root.start()

    def on_stop(self):
        self.root.stop()

