from kivy.clock import Clock
from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
import time
from datetime import datetime
import json
import requests

from gpiozero import Button, OutputDevice, InputDevice

laser_status = InputDevice(19)
oe_pinout = OutputDevice(13)
oe_pinout.on()

class myClock(Label):
    def update(self, *args):
        self.text = time.asctime()

#TODO: check if status is busy before checking the authentication
class CardReader(GridLayout):

    def __init__(self, **kwargs):
        super(CardReader, self).__init__(**kwargs)
        self.rfid = None
        self.laser_flag = True
        self.laser_flag_do_not_log = True
        self.p_laser_state = 0
        self.cols = 1
        self.status = 'free'
        self.event = Clock.schedule_once(self.start, 2)

    def read_gpio(self, *args):
        # FIXME: try/exception + method for url request
        if self.rfid:
            if laser_status.is_active is False: # opposite, fine
                if self.laser_flag == False:
                    self.laser_flag = True
                    self.laser_text.text = "Laser is on"
                    url = "http://eblab.acaia.ca/rfid/?uid=" + self.rfid + "&resource=laser_cutter" + "&action=LAS"
                    r = requests.get(url)
            elif laser_status.is_active is True:
                if self.laser_flag == True:
                    self.laser_flag = False
                    self.laser_text.text = "Laser is off"
                    url = "http://eblab.acaia.ca/rfid/?uid=" + self.rfid + "&resource=laser_cutter" + "&action=LAE"
                    if self.laser_flag_do_not_log == False: # do not log the first loop interaction
                        r = requests.get(url)
                    self.laser_flag_do_not_log = False

    def start(self, *args):
        self.main_text = Label()
        self.main_text.font_size = "50px"
        self.add_widget(self.main_text)
        
        self.laser_text = Label(text="Laser is off")
        self.laser_text.font_size = "25px"
        self.add_widget(self.laser_text)

        self.gpio_event = Clock.schedule_interval(self.read_gpio, 0.1)
        self.event = Clock.schedule_interval(self.update, 0.1)

    def load_json(self):
        with open('/tmp/eblaser_data.json') as json_file:
            self.data = json.load(json_file)

    def update(self, *args):
        self.load_json()
        self.main_text.text = self.data['text']
        self.rfid = self.data['current_id']

class ScreenApp(GridLayout):
    def __init__(self, **kwargs):
        super(ScreenApp, self).__init__(**kwargs)
        self.cols = 1
        self.l = Label(text='WELCOME TO THE LASER THING')
        self.l.font_size = '30px'
        self.add_widget(self.l)

        reader = CardReader()
        reader.font_size = '30px'
        self.add_widget(reader)

        clock = myClock()
        clock.font_size = '25px'
        Clock.schedule_interval(clock.update, 1)
        self.add_widget(clock)

class MyApp(App):
    def build(self):
        return ScreenApp()

if __name__ == '__main__':
    Config.set("graphics", "show_cursor", 0)
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()
    MyApp().run()
