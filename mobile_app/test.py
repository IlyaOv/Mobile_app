import json
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
import threading
from webview import WebView
from kivy.logger import Logger
from os import listdir, path

from android.permissions import Permission, request_permissions, check_permission
from android.storage import app_storage_path, primary_external_storage_path, secondary_external_storage_path


def log(msg):
    Logger.info(msg)


def check_permissions(perms):
    for perm in perms:
        if check_permission(perm) != True:
            return False
    return True


class BrowserApp(App):

    def build(self):
        self.filename = None
        self.label_host = Label(text='host: ', size_hint_x=None, width=250)
        self.label_port = Label(text='port: ', size_hint_x=None, width=250)
        self.label_block = Label(text='Название блока: ', size_hint_x=None, width=270)
        self.label_info = Label(text='')
        self.text_host = TextInput(text='192.168.0.2')
        self.text_port = TextInput(text='8080')
        self.text_block = TextInput(text='Новокуйбышевск')
        grid_layout = GridLayout(cols=2, row_force_default=True, row_default_height=60, spacing=20)
        grid_layout.add_widget(self.label_host)
        grid_layout.add_widget(self.text_host)
        grid_layout.add_widget(self.label_port)
        grid_layout.add_widget(self.text_port)
        grid_layout.add_widget(self.label_block)
        grid_layout.add_widget(self.text_block)
        box_main = BoxLayout(orientation='vertical', spacing=20)
        label_tb = Label(text='Выберите подложку:')
        box_tb = BoxLayout(orientation='horizontal')
        self.btn1 = ToggleButton(text='OpenStreetMap', group='map', state='down')
        self.btn2 = ToggleButton(text='Satellite', group='map')
        box_tb.add_widget(self.btn1)
        box_tb.add_widget(self.btn2)
        print(self.btn2.state)
        self.button_wf = Button(text='Получить ОАП', background_color=[0, 1, 0, 1],
                             size_hint=(.6, .6), pos_hint={'x': .2, 'y': .2}, on_press=self.get_oap)
        self.button_view = Button(text='Отобразить ОАП', background_color=[0, 1, 0, 1],
                                size_hint=(.6, .6), pos_hint={'x': .2, 'y': .2}, on_press=self.view_local_file)
        box_main.add_widget(grid_layout)
        box_main.add_widget(label_tb)
        box_main.add_widget(box_tb)
        box_main.add_widget(self.button_wf)
        box_main.add_widget(self.button_view)
        box_main.add_widget(self.label_info)
        return box_main

    def get_oap(self, e):
        perms = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
        if check_permissions(perms) != True:
            req_perm = request_permissions(perms)
            self.label_info.text = str(req_perm)
        else:
            try:
                host = self.text_host.text
                port = self.text_port.text
                block_name = self.text_block.text
                tiles = self.btn1.text
                print(block_name, tiles)
                if self.btn2.state == "down":
                    tiles = self.btn2.text
                if block_name != '':
                    threading.Thread(target=self.write_html, args=(host, port, block_name, tiles)).start()
                    self.button_wf.set_disabled(False)
                else:
                    self.label_info.text = "Введите название блока"
            except Exception as ex:
                self.label_info.text = str(ex)

    def write_html(self, host, port, block_name, tiles):
        try:
            self.button_wf.set_disabled(True)
            self.label_info.text = "Пожалуйста подождите"
            param = json.dumps({"block_name": block_name, "tiles": tiles})
            res = requests.post("http://{}:{}/test_json".format(host, port), json=param)
            fname = path.join(primary_external_storage_path(), 'index.html')
            with open(fname, 'wb') as f:
                f.write(res.content)
            self.label_info.text = 'Записан: %s' % fname
            self.filename = fname
            # self.label_info.text = ""
        except Exception as ex:
            self.label_info.text = str(ex)

    def view_local_file(self, e):
        if self.filename is not None:
            self.browser = WebView('file://' + self.filename,
                                   enable_javascript=True,
                                   enable_downloads=True,
                                   enable_zoom=True)
        else:
            self.label_info.text = "Файл не записан"


BrowserApp().run()