# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import json
import protocol
import socket

from pynput import keyboard
from pynput import mouse

mouse_control = mouse.Controller()
keyboard_control = keyboard.Controller()


def mmove(x, y):
    mouse_control.position = (x, y)
    print(mouse_control.position)
    # print(time.time())


def mpress():
    mouse_control.press(mouse.Button.left)
    print('mouse has press')
    # print(time.time())


def mrelease():
    mouse_control.release(mouse.Button.left)
    print('mouse has release')
    # print(time.time())
    # exit(1)


def mscroll(x, y):
    mouse_control.scroll(x, y)
    print('mouse scroll')
    # print(time.time())


def kpress(a):
    # keyboard.press(a)
    keyboard_control.press(a)
    print('keyboard press', a)

    # pressing(a)


def krelease(a):
    keyboard_control.release(a)
    print('keyboard release', a)


# start the main
# socket connect


HOST = '192.168.0.101'
PORT = 8000
print("connecting")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)
conn, addr = server.accept()
print("connect success")

while True:

    try:
        clientMessage = (conn.recv(1024))
        signal = json.loads(clientMessage)
        # print (clientMessage)
        print(signal)
        if signal['0'] == 'mm':
            mmove(int(signal['1']), int(signal['2']))
        elif signal['0'] == 'mp':
            mpress()
        elif signal['0'] == 'mr':
            mrelease()
        elif signal['0'] == 'ms':
            mscroll(int(signal['1']), int(signal['2']))
        elif signal['0'] == 'kp':
            if signal['1'] == 'up':
                keyboard_control.press(keyboard.Key.up)
            elif signal['1'] == 'down':
                keyboard_control.press(keyboard.Key.down)
            elif signal['1'] == 'left':
                keyboard_control.press(keyboard.Key.left)
                # pressing('left')
            elif signal['1'] == 'right':
                keyboard_control.press(keyboard.Key.right)
                # pressing('right')
            elif signal['1'] == 'enter':
                keyboard_control.press(keyboard.Key.enter)
                # pressing('enter')
            else:
                kpress(signal['1'])
            # kpress(signal['1'])
        elif signal['0'] == 'kr':
            if signal['1'] == 'up':
                keyboard_control.release(keyboard.Key.up)
                # check_if_press.remove('up')
            elif signal['1'] == 'down':
                keyboard_control.release(keyboard.Key.down)
                # check_if_press.remove('down')
            elif signal['1'] == 'left':
                keyboard_control.release(keyboard.Key.left)
                # check_if_press.remove('left')
            elif signal['1'] == 'right':
                keyboard_control.release(keyboard.Key.right)
                # check_if_press.remove('right')
            elif signal['1'] == 'enter':
                keyboard_control.release(keyboard.Key.enter)
                # check_if_press.remove('enter')
            else:
                krelease((signal['1']))
    except:
        pass