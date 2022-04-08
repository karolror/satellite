from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
import pandas as pd


class MainWindow(Screen):
    def __init__(self, **kwargs):
        self.df = None
        self.col_names = None
        self.ncolumns = None
        self.nrows_gene = None
        self.nrows_allel = None
        super(Screen, self).__init__(**kwargs)

    def create_df(self):
        self.manager.csv_path = self.manager.get_screen('main').ids.path_input.text
        try:
            self.df = pd.read_csv(self.manager.csv_path, sep=";")
            print(self.df)
            return True
        except:
            self.manager.get_screen('main').ids.hello_label.color = "red"
            self.manager.get_screen('main').ids.hello_label.text = "Error during loading file. Try again."
            return False

    def get_basic(self):
        try:
            self.col_names = [col.split("_", 1)[0] for col in self.df.columns[::2]]
            self.ncolumns = int(len(self.df.columns) / 2)
            self.nrows_gene = len(self.df)
            self.nrows_allel = self.nrows_gene * 2
            return True
        except:
            return False

    def calculate(self):
        if self.create_df():
            if self.get_basic():
                self.manager.get_screen('main').ids.hello_label.color = "green"
                self.manager.get_screen('main').ids.hello_label.text = "File calculated."
                self.manager.get_screen('main').ids.results_button.disabled = False


class ResultsWindow(Screen):
    def change_text(self):
        self.manager.get_screen('results').ids.label_res.text = self.manager.thetext


class WindowManager(ScreenManager):
    thetext = StringProperty('Mvi123: 0.28\nMvi321: 0.77\nMvi333: 0.99')
    csv_path = StringProperty(None)


kv = Builder.load_file("my.kv")


class Satellite(App):
    def build(self):
        return kv


if __name__ == "__main__":
    Satellite().run()
