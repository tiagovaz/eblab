from kivy.clock import Clock
from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
import time
from datetime import datetime
from datetime import timedelta
import json
import requests

from gpiozero import Button, OutputDevice, InputDevice

# Input from laser when it's in function
laser_status = InputDevice(19)

# Relay
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
        self.laser_time_start = 0
        self.laser_time_end = 0
        self.laser_time_total = 0
        self.laser_flag = True
        self.laser_flag_do_not_log = True
        self.p_laser_state = 0
        self.cols = 1
        self.status = 'free'
        self.event = Clock.schedule_once(self.start, 2)

    def read_gpio(self, *args):
        # FIXME: try/exception + method for url request
        if self.rfid:
            if laser_status.is_active is False: # opposite, fine => laser on
                if self.laser_flag == False:
                    # start counting time
                    self.laser_time_start = time.time()
                    self.laser_flag = True
                    self.laser_text.text = "Laser is ON"
                    url = "http://eblab.acaia.ca/rfid/?uid=" + self.rfid + "&resource=laser_cutter" + "&action=LAS"
                    r = requests.get(url)
            # If laser becomes OFF and lastest ON was minimum 8s before, then turn it OFF for real
            # otherwise it is just pulses from engraving activity
            elif laser_status.is_active is True and int(timedelta(seconds=(time.time() - self.laser_time_start)).total_seconds()) > 7:
                if self.laser_flag == True:
                    self.laser_flag = False
                    if self.laser_flag_do_not_log == False: # do not log the first loop interaction
                        ### laser time counter ###
                        self.laser_time_end = time.time()
                        self.laser_time_total = self.laser_time_total + (self.laser_time_end - self.laser_time_start)
                        self.laser_time_start = 0
                        self.laser_time_end = 0
                        ##########################
                        url = "http://eblab.acaia.ca/rfid/?uid=" + self.rfid + "&resource=laser_cutter" + "&action=LAE" + "&usage_time=" + str(round(self.laser_time_total))
                        r = requests.get(url)
                        self.laser_text.text = "Laser is OFF"
                    self.laser_flag_do_not_log = False

    def start(self, *args):
        self.main_text = Label()
        self.main_text.font_size = "50px"
        self.add_widget(self.main_text)

        self.laser_time_text = Label()
        self.laser_time_text.font_size = "40px"
        self.add_widget(self.laser_time_text)

        self.laser_text = Label(text="Laser is OFF")
        self.laser_text.font_size = "25px"
        self.add_widget(self.laser_text)

        self.gpio_event = Clock.schedule_interval(self.read_gpio, 0.05)
        self.event = Clock.schedule_interval(self.update, 0.05)

    def load_json(self):
        with open('/tmp/eblaser_data.json') as json_file:
            self.data = json.load(json_file)

    def update(self, *args):
        self.load_json()
        self.main_text.text = self.data['text']
        self.rfid = self.data['current_id']
        # reset total laser time each time we have a logoff
        if self.data['is_free'] == True:
            self.laser_time_total = 0
        self.laser_time_text.text = "Session usage: " + str(timedelta(seconds=round(self.laser_time_total)))

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

