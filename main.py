from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, DictProperty, ObjectProperty
import pandas as pd
import xlsxwriter


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
            return True
        except:
            self.manager.get_screen('main').ids.hello_label.color = "red"
            self.manager.get_screen('main').ids.hello_label.text = "Error during loading file. Try again."
            self.manager.get_screen('main').ids.results_button.disabled = True
            return False

    def get_basic(self):
        try:
            self.col_names = [col.split("_", 1)[0] for col in self.df.columns[::2]]
            self.ncolumns = int(len(self.df.columns) / 2)
            self.nrows_gene = len(self.df)
            self.nrows_allel = self.nrows_gene * 2
            return True
        except:
            self.manager.get_screen('main').ids.hello_label.color = "red"
            self.manager.get_screen('main').ids.hello_label.text = "Something wrong with file format. Please check it."
            return False

    def get_allel_freq(self):
        allel_freq_dict = {}
        o = 0
        p = 1
        for i in range(self.ncolumns):
            x = list(self.df[self.df.columns[o]])
            y = list(self.df[self.df.columns[p]])
            xy = x + y
            my_dict = {i: xy.count(i) for i in xy}
            res = {key: (my_dict[key] / self.nrows_allel) for key in my_dict.keys()}
            allel_freq_dict[self.col_names[i]] = res
            o += 2
            p += 2

        return allel_freq_dict

    def get_hetero_exp(self):
        hetero_exp_dict = {}
        res_list = []
        for key in self.manager.af:
            for a in self.manager.af[key]:
                res_list.append(self.manager.af[key][a] ** 2)
            hetero_exp = 1 - sum(res_list)
            hetero_exp_dict[key] = hetero_exp
            res_list.clear()

        return hetero_exp_dict

    def get_gene_freq(self):
        gene_freq_dict = {}
        o = 0
        p = 1
        for i in range(self.ncolumns):
            self.df[self.df.columns[o]] = self.df[self.df.columns[o]].astype("string")
            self.df[self.df.columns[p]] = self.df[self.df.columns[p]].astype("string")
            series = self.df[self.df.columns[o]].str.cat(self.df[self.df.columns[p]].astype(str), sep='/')
            ll = list(series)
            my_dict2 = {i: ll.count(i) for i in ll}
            res = {key: (my_dict2[key] / self.nrows_gene) for key in my_dict2.keys()}
            gene_freq_dict[self.col_names[i]] = res
            o += 2
            p += 2
        return gene_freq_dict

    def get_hetero_obs(self):
        hetero_obs_dict = {}
        res_list = []
        for key in self.manager.gf:
            for a in self.manager.gf[key]:
                gene_check = a.split("/")
                if gene_check[0] != gene_check[1]:
                    res_list.append(self.manager.gf[key][a])
                hetero_obs = sum(res_list)
                hetero_obs_dict[key] = hetero_obs
            res_list.clear()
        return hetero_obs_dict

    def pop_hetero(self, hetero):
        return sum(hetero.values()) / self.ncolumns

    def f_stats(self):
        sub = [a - b for a, b in zip(self.manager.h_exp.values(), self.manager.h_obs.values())]
        f_statistics = [a / b for a, b in zip(sub, self.manager.h_exp.values())]
        f_dict = dict(zip(self.col_names, f_statistics))
        return f_dict

    def f_statistic(self):
        return (self.manager.phexp - self.manager.phobs) / self.manager.phexp

    def calculate(self):
        if self.create_df():
            if self.get_basic():
                try:
                    self.manager.af = self.get_allel_freq()
                    self.manager.gf = self.get_gene_freq()
                    self.manager.h_obs = self.get_hetero_obs()
                    self.manager.h_exp = self.get_hetero_exp()
                    self.manager.phobs = self.pop_hetero(self.manager.h_obs)
                    self.manager.phexp = self.pop_hetero(self.manager.h_exp)
                    self.manager.small_f = self.f_stats()
                    self.manager.big_f = self.f_statistic()
                    # return communicate
                    self.manager.get_screen('main').ids.hello_label.color = "green"
                    self.manager.get_screen('main').ids.hello_label.text = "File calculated."
                    self.manager.get_screen('main').ids.results_button.disabled = False
                except:
                    self.manager.get_screen('main').ids.hello_label.color = "red"
                    self.manager.get_screen('main').ids.hello_label.text = "Something went wrong. Check your file and "\
                                                                           "try again"
                    self.manager.get_screen('main').ids.results_button.disabled = True


class ResultsWindow(Screen):

    def to_str(self, thedict):
        converted = ""
        try:
            for key in thedict:
                for a in thedict[key]:
                    log_sum = str(key) + " | " + str(a) + " | " + str(round(thedict[key][a], 6)) + "\n"
                    converted = converted + log_sum
            return converted
        except:
            for k in thedict:
                log_sum = str(k) + " | "  + str(round(thedict[k], 6)) + "\n"
                converted = converted + log_sum
            return converted

    def show_allel(self):
        self.manager.af_str = self.to_str(self.manager.af)
        self.manager.get_screen('results').ids.label_res.text = self.manager.af_str

    def show_gene(self):
        self.manager.gf_str = self.to_str(self.manager.gf)
        self.manager.get_screen('results').ids.label_res.text = self.manager.gf_str

    def show_hetero(self):
        self.manager.h_str = "*** Heterozigosity observed:\n" + self.to_str(self.manager.h_obs) \
                             + "*** Heterozigosity expected:\n" + self.to_str(self.manager.h_exp) \
                             + "*** Heterozigosity observed for population:\n" + str(self.manager.phobs) + "\n" \
                             + "*** Heterozigosity expected for population:\n" + str(self.manager.phexp)
        self.manager.get_screen('results').ids.label_res.text = self.manager.h_str

    def show_f(self):
        self.manager.f_str = "*** F statistics:\n" + self.to_str(self.manager.small_f) + "*** Fst statistic:\n" \
                             + str(round(self.manager.big_f, 6))
        self.manager.get_screen('results').ids.label_res.text = self.manager.f_str


class WindowManager(ScreenManager):
    # Properties for calculations
    af = DictProperty(None)
    gf = DictProperty(None)
    h_obs = DictProperty(None)
    h_exp = DictProperty(None)
    phobs = ObjectProperty(None)
    phexp = ObjectProperty(None)
    small_f = DictProperty(None)
    big_f = ObjectProperty(None)
    # Strings to show results
    f_str = StringProperty(None)
    af_str = StringProperty(None)
    gf_str = StringProperty(None)
    h_str = StringProperty(None)


kv = Builder.load_file("my.kv")


class Satellite(App):
    def build(self):
        return kv


if __name__ == "__main__":
    Satellite().run()
