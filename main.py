from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

class MainWindow(Screen):
    pass

class ResultsWindow(Screen):
    def change_text(self):
        self.manager.get_screen('results').ids.label_res.text = self.manager.thetext


class WindowManager(ScreenManager):
    thetext = StringProperty('Mvi123: 0.28\nMvi321: 0.77\nMvi333: 0.99')
    direction = StringProperty(None)

kv = Builder.load_file("my.kv")


class Satellite(App):
    def build(self):
        return kv


if __name__ == "__main__":
    Satellite().run()
