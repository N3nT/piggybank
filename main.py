from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import re
Builder.load_file('style.kv')


def delete_dig(text):
    del_small_le = re.sub('[a-z]', '', text)
    del_big_le = re.sub('[A-Z]', '', del_small_le)
    value = re.sub('[!@#`~$%^&*()+=}{|:;,<>/?]', '', del_big_le)
    return value


def delete_all_minus(text):
    value = re.sub('-', '', text)
    return value


class WindowManager(ScreenManager):
    pass


class MainWindow(Screen):
    goal_name_top = ObjectProperty(None)

    def add_goal(self):
        sm.current = "add_goal"

    def take_data(self):
        goal_name_top = self.goal_name_ons.text

    def add_to_value(self):
        second = sm.get_screen('add_goal')
        value = self.add_to_bar.text
        value = delete_dig(value)

        if value == '':
            value = '0'
        if value.__contains__("-"):
            without_minus = delete_all_minus(value)
            value = "-" + without_minus

        self.add_to_bar.text = value
        value = float(value)

        if self.progress_bar.max == 0:
            self.goal_progress.text = "NaN %"
        else:
            self.progress_bar.value += value
            self.goal_progress.text = str(round((self.progress_bar.value / self.progress_bar.max)*100, 2)) + " %"
        new_value = float(second.actual_value.text)
        new_value += value
        if int(new_value) < 0:
            new_value = 0
        second.actual_value.text = str(round(new_value, 2))

        if new_value >= self.progress_bar.max:
            self.goal_progress.text = f'Goal complete, actual value: {new_value}'
            self.progress_bar.value = new_value
        else:
            self.progress_bar.value = new_value

    def write_in_file_mn(self):
        sc = sm.get_screen("add_goal")
        f = open("database.txt", "r+")
        db = f.readline().split(";")
        f.close()

        file_goal_name = db[0]
        file_actual_value = sc.actual_value.text
        file_end_value = float(db[3])
        file_p_value = str(round(float(sc.actual_value.text)/float(db[3])*100, 2))

        f = open("database.txt", "r+")
        f.truncate(0)
        f.write(f'{file_goal_name};{file_p_value} %;{file_actual_value};{file_end_value};')
        f.close()

    def read_database(self):
        f = open("database.txt", "r+")
        db = f.readline().split(";")
        self.goal_name_ons.text = db[0]
        self.goal_progress.text = db[1]
        self.goal_progress.max = db[2]

        sc = sm.get_screen('add_goal')
        sc.goal_name.text = db[0]
        sc.goal_value.text = db[3]
        sc.actual_value.text = db[2]


class AddGoalWindow(Screen):
    goal = ObjectProperty(None)
    end_value = ObjectProperty(None)
    start = ObjectProperty(None)
    actual = ObjectProperty(None)
    Window.clearcolor = (151/255, 190/255, 195/255, 1)

    def back_to_main(self):
        sm.current = "main"

    def done(self):
        global goal
        goal = self.goal_name.text

        global end_value
        self.goal_value.text = delete_dig(self.goal_value.text)
        self.goal_value.text = delete_all_minus(self.goal_value.text)
        end_value = self.goal_value.text

        global actual
        self.actual_value.text = delete_dig(self.actual_value.text)
        self.actual_value.text = delete_all_minus(self.actual_value.text)
        actual = self.actual_value.text

        main = sm.get_screen('main')
        if self.actual_value.text == '':
            self.actual_value.text = '0'
        if self.goal_value.text == '':
            self.goal_value.text = '0'
        if float(delete_dig(self.actual_value.text)) == float(delete_dig(self.goal_value.text)) and self.goal_value.text != '0':
            main.goal_progress.text = f'Goal complete, actual value: {float(self.actual_value.text)}'

    def reset(self):
        self.goal_name.text = 'No goal'
        self.goal_value.text = '100'
        self.actual_value.text = '0'

    def change(self):
        main = sm.get_screen('main')
        global file_goal_name
        file_goal_name = self.goal_name.text
        global file_actual_value
        self.actual_value.text = delete_dig(self.actual_value.text)
        file_actual_value = self.actual_value.text
        global file_end_value
        file_end_value = float(self.goal_value.text)
        main.goal_name_ons.text = self.goal_name.text
        main.progress_bar.max = float(self.goal_value.text)
        main.progress_bar.value = float(self.actual_value.text)

        if main.progress_bar.max == 0:
            main.goal_progress.text = "NaN %"
        if float(self.actual_value.text) >= float(self.goal_value.text):
            main.goal_progress.text = f'Goal complete, actual value: {float(self.actual_value.text)}'
        else:
            main.goal_progress.text = str(round((main.progress_bar.value / main.progress_bar.max)*100, 2)) + " %"

        global file_p_value
        file_p_value = main.goal_progress.text

    def write_in_file_sc(self):
        f = open("database.txt", "r+")
        f.truncate(0)
        f.write(f'{file_goal_name};{file_p_value};{file_actual_value};{file_end_value};')
        f.close()


class MyApp(App):
    def build(self):
        Window.size = (700, 800)
        mn = sm.get_screen('main')
        mn.read_database()
        f = open("database.txt", "r+")
        db = f.readline().split(";")
        if float(db[2]) >= float(db[3]):
            mn.goal_progress.text = f'Goal complete, actual value: {float(db[2])}'
            mn.progress_bar.max = float(db[3])
            mn.progress_bar.value = float(db[2])
        else:
            mn.progress_bar.max = float(db[3])
            mn.progress_bar.value = float(db[2])
        f.close()
        return sm


sm = WindowManager()
screens = [MainWindow(name='main'), AddGoalWindow(name='add_goal')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'main'
if __name__ == "__main__":
    MyApp().run()
