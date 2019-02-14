#!/usr/bin/python3
# -*- coding: utf-8 -*-

from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
import binascii
pn532 = Pn532_i2c()
pn532.SAMconfigure()
import time
import requests

#resource = "laser_cutter"
resource = "main_door"

while 1:
    card_data = pn532.read_mifare().get_data()
    card_data_str = str(binascii.hexlify(card_data)[14:].decode("utf-8"))
    url = "http://192.168.2.32:8000/rfid/?uid=" + card_data_str + "&resource=" + resource
    try:
        r = requests.get(url)
        if r.status_code == 200:
            print("AUTHORIZED:", card_data_str, resource)
        if r.status_code == 405:
            print("DENIED:", card_data_str, resource)
        time.sleep(2)
    except:
        print("ERROR")
        continue

