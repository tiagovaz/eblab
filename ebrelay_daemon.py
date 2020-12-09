import time
from datetime import datetime
import json

from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
import binascii
import requests
from subprocess import Popen, PIPE

from gpiozero import OutputDevice

pn532 = Pn532_i2c()
pn532.SAMconfigure()

#TODO: check if status is busy before checking the authentication
class CardReader():
    def __init__(self):
        self.relay_pinout = OutputDevice(17)
        self.relay_pinout.off()
        self.card_data = None
        self.current_id = None
        self.person = None
        self.fortune = ""
        self.resource_time_daily = "00:00:00"
        self.timestamp = None
        self.is_free = True
        self.text = 'RFID PLEASE'
        self.output_json = {}
        self.update_json()
        self.headers = {'Authorization': 'Token YYY'}

    def read_card(self):
        self.card_data = pn532.read_mifare().get_data()
        pn532.reset_i2c()

        resource = 'laser_cutter'
        if self.card_data != None:
            card_data_str = None
            card_data_str = str(binascii.hexlify(self.card_data)[14:].decode("utf-8"))
            url_base = "https://eblab.acaia.ca/rfid/?uid=" + card_data_str + "&resource=" + resource
            url = url_base + "&action=NON"
            try:
                r = requests.get(url, headers=self.headers)
                print(url)
                self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
                if r.status_code == 406:
                    self.text = "UNKNOWN ID: " + card_data_str
                    self.relay_pinout.off()
                    # Update json file and keep the auth_text for a few seconds
                    self.update_json()
                    time.sleep(1)
                    self.text = "RFID PLEASE"

                if r.status_code == 405 and self.is_free is True:
                    self.text = "DENIED: " + card_data_str
                    self.relay_pinout.off()
                    # Update json file and keep the auth_text for a few seconds
                    self.update_json()
                    time.sleep(1)
                    self.text = "RFID PLEASE"
    
                elif r.status_code == 200:
                    if self.is_free is True:
                        self.text = "AUTHORIZED: " + card_data_str
                        url = url_base + "&action=LOI"
                        r = requests.get(url, headers=self.headers)
                        self.set_person_by_rfid(card_data_str)
                        self.set_resource_time_daily_by_rfid(card_data_str)
                        self.relay_pinout.on()
                        self.update_json()
                        time.sleep(1)
                        self.text = "Hi " + self.person + "!"
                        f = self.get_fortune()
                        self.fortune = str(f).strip()
                        self.is_free = False
                        self.current_id = card_data_str
                        
                    elif self.is_free is False:
                        if card_data_str == self.current_id:
                            self.text = "bye, " + self.person
                            url = url_base + "&action=LOO"
                            r = requests.get(url, headers=self.headers)
                            self.set_person_by_rfid(None)
                            self.relay_pinout.off()
                            self.update_json()
                            time.sleep(1)
                            self.text = "RFID PLEASE"
                            self.is_free = True
                            self.current_id = None
                        else:
                            self.text = 'Use id ' + self.current_id + " to log out" 
                            self.update_json()
                            time.sleep(1)
                            self.text = card_data_str + " LOGGED IN"
                            #self.relay_pinout.off()
            except:
                self.text = "ERROR! .-= better call greg =-."
                self.relay_pinout.off()

            # Update json file
            self.update_json()

            # Reset stuff
            r.status_code = None
            self.card_data = None

    def get_fortune(self):
        pipe = Popen("/usr/games/fortune -n 30 -s", shell=True, stdout=PIPE).stdout
        return pipe.read().decode('UTF-8')

    def set_person_by_rfid(self, rfid):
        if rfid == None:
            self.person = None
        else:
            url = "https://eblab.acaia.ca/person/" + rfid
            response = requests.get(url, headers=self.headers)
            jsonResponse = response.json()
            self.person = jsonResponse["first_name"]

    def set_resource_time_daily_by_rfid(self, rfid):
        if rfid == None:
            self.daily_usage = "00:00:00"
        else:
            url = "https://eblab.acaia.ca/daily_usage/" + rfid
            response = requests.get(url, headers=self.headers)
            jsonResponse = response.json()
            print(jsonResponse)
            if jsonResponse["laser_usage_time"] == None:
                self.resource_time_daily = "00:00:00"
            else:
                self.resource_time_daily = jsonResponse["laser_usage_time"]

    def update_json(self):
        json_output = {'current_id': self.current_id,
                       'person': self.person,
                       'is_free': self.is_free,
                       'fortune': self.fortune,
                       'resource_time_daily': self.resource_time_daily,
                       'timestamp': self.timestamp,
                       'text': self.text
                      }
        print(json_output)

        with open('/tmp/ebrelay_data.json', 'w') as outfile:
                json.dump(json_output, outfile)

if __name__ == '__main__':
    reader = CardReader()
    while True:
        reader.read_card()
        time.sleep(0.1)
