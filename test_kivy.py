from kivy.clock import Clock
from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
import time

from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
import binascii
pn532 = Pn532_i2c()
pn532.SAMconfigure()
import requests

last_card_data_str = ''

class IncrediblyCrudeClock(Label):
    def update(self, *args):
        self.text = time.asctime()

class CardReader(Label):
    def update(self, *args):
        global status
        resource = 'main_door'
        card_data = pn532.read_mifare().get_data()
        card_data_str = str(binascii.hexlify(card_data)[14:].decode("utf-8"))
        url = "http://eblab.acaia.ca/rfid/?uid=" + card_data_str + "&resource=" + resource
        try:
            r = requests.get(url)
            if r.status_code == 200:
                self.text = "AUTHORIZED: " + card_data_str
            if r.status_code == 405:
                self.text = "DENIED: " + card_data_str
        except:
            self.text = "ERROR! .-= better call greg =-."
#        time.sleep(5)

class ScreenApp(GridLayout):
    def __init__(self, **kwargs):
        super(ScreenApp, self).__init__(**kwargs)
        self.cols = 1
        self.l = Label(text='WELCOME TO THE LASER THING')
        self.l.font_size = '30px'
        self.add_widget(self.l)

#        crudeclock = IncrediblyCrudeClock()
#        crudeclock.font_size = '20px'
#        Clock.schedule_interval(crudeclock.update, 1)
#        self.add_widget(crudeclock)

        reader = CardReader()
        reader.font_size = '30px'
        Clock.schedule_interval(reader.update, 3)
        self.add_widget(reader)

class MyApp(App):
    def build(self):
        return ScreenApp()

if __name__ == '__main__':
    Config.set("graphics", "show_cursor", 0)
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()
    MyApp().run()
