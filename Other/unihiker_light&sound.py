#!/usr/bin/env python
# coding: utf-8

import time
from pinpong.board import *
from pinpong.extension.unihiker import *
from unihiker import GUI, Audio
gui = GUI()
audio = Audio()
Board().begin()

light_max = 4095
sound_max = 100
green_bar = (122, 222, 44)
yellow_bar = (222, 222, 44)
red_bar = (222, 88, 44)

info_text1 = gui.draw_text(x=120, y=40, text='Ambiant Lighting', font_size=18, origin='top')
light_bar_bg = gui.draw_line(x0=20, y0=80, x1=220, y1=80, width=5, color=(150,150,150))
light_bar = gui.draw_line(x0=20, y0=80, x1=20, y1=80, width=5, color=red_bar)
light_text = gui.draw_text(x=120, y=90, text='0', font_size=18, origin='top')

info_text2 = gui.draw_text(x=120, y=180, text='Ambiant Sound', font_size=18, origin='top')
sound_bar_bg = gui.draw_line(x0=20, y0=220, x1=220, y1=220, width=5, color=(150,150,150))
sound_bar = gui.draw_line(x0=20, y0=220, x1=20, y1=220, width=5, color=red_bar)
sound_text = gui.draw_text(x=120, y=240, text='0', font_size=18, origin='top')

gui.draw_qr_code(x=0, y=320, w=60, text="https://github.com/Bananzarama", origin="bottom_left")

def lighting_change():
    light_level = light.read() 
    light_perc = int(light_level/light_max * 100)
    light_text.config(text=str(light_perc) + "%") 
    light_bar.config(x0=20, x1=20+(light_perc/100 * 200))
    #print("light level:", str(light_perc) + "%")
    if 0 <= light_level < light_max/4:
        light_bar.config(color=red_bar) 
    elif light_max/4 <= light_level < light_max/2:
        light_bar.config(color=yellow_bar) 
    else:
        light_bar.config(color=green_bar) 

def sound_change():
    sound_db = int(audio.sound_level())
    sound_text.config(text=str(sound_db) + "db")
    sound_bar.config(x0=20, x1=20+(sound_db/sound_max * 200))
    #print("sound level:", str(sound_db) + "db")
    if 0 <= sound_db < sound_max/4:
        sound_bar.config(color=red_bar) 
    elif sound_max/4 <= sound_db < sound_max/2:
        sound_bar.config(color=yellow_bar) 
    else:
        sound_bar.config(color=green_bar) 

while True:
    lighting_change()
    sound_change()
    time.sleep(.1) 
