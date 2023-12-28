#!/usr/bin/env python
# turing-smart-screen-python - a Python system monitor and library for 3.5" USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This file is a simple Python test program using the library code to display custom content on screen (see README)

import os
import signal
import time
import sys
from datetime import datetime
import random
# Import only the modules for LCD communication

from library.log import logger

from objects.screen import screen

import win32api
import win32con
import win32gui

stop = False
drawing = True

if __name__ == "__main__":

    index = 0

    lcd = screen()

    def sighandler(signum, frame):
        global stop
        stop = True

    # Set the signal handlers, to send a complete frame to the LCD before exit


    def on_win32_ctrl_event(event):
        """Handle Windows console control events (like Ctrl-C)."""
        global stop
        if event in (win32con.CTRL_C_EVENT, win32con.CTRL_BREAK_EVENT, win32con.CTRL_CLOSE_EVENT):
            logger.debug("Caught Windows control event %s, exiting" % event)
            stop = True
        return 0


    def on_win32_wm_event(hWnd, msg, wParam, lParam):
        global drawing
        """Handle Windows window message events (like ENDSESSION, CLOSE, DESTROY)."""
        logger.debug("Caught Windows window message event %s" % msg)
        logger.debug("Info %s" % wParam)
        if msg == win32con.WM_POWERBROADCAST:
            # WM_POWERBROADCAST is used to detect computer going to/resuming from sleep
            if wParam == win32con.PBT_APMSUSPEND:
                logger.info("Computer is going to sleep, display will turn off")
                drawing = False
                lcd.off()
                time.sleep(1)
            elif wParam == win32con.PBT_APMRESUMEAUTOMATIC:
                logger.info("Computer is resuming from sleep, display will turn on")
                lcd.on()
                drawing = True
        else:
            # For any other events, the program will stop
            logger.info("Program will now exit")
            stop = True
        return 0

    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    win32api.SetConsoleCtrlHandler(on_win32_ctrl_event, True)

    lcd.on()
    # Define background picture
    background_paths = []

    for file in os.listdir("res/backgrounds/"):
        background_paths.append("res/backgrounds/" + file)
    #"res/backgrounds/backgroundff14.png"

    current_background = background_paths[index]

    lcd.setBackground(current_background)
    lcd.setTime(datetime.now().strftime('%H:%M'), 161, 30,
                            font="roboto/Roboto-Bold.ttf",
                            font_size=60,
                            font_color=(255, 255, 255),
                            align = 'center')
    lcd.setDate(datetime.now().strftime('%d/%m'), 161, 260,
                        font="roboto/Roboto-Bold.ttf",
                        font_size=60,
                        font_color=(255, 255, 255),
                        align = 'center')
    lcd.draw()

    # Display the current time and some progress bars as fast as possible

    # Create a hidden window just to be able to receive window message events (for shutdown/logoff clean stop)
    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "turingEventWndClass"
    messageMap = {win32con.WM_QUERYENDSESSION: on_win32_wm_event,
                    win32con.WM_ENDSESSION: on_win32_wm_event,
                    win32con.WM_QUIT: on_win32_wm_event,
                    win32con.WM_DESTROY: on_win32_wm_event,
                    win32con.WM_CLOSE: on_win32_wm_event,
                    win32con.WM_POWERBROADCAST: on_win32_wm_event}

    wndclass.lpfnWndProc = messageMap

    try:
        myWindowClass = win32gui.RegisterClass(wndclass)
        hwnd = win32gui.CreateWindowEx(win32con.WS_EX_LEFT,
                                        myWindowClass,
                                        "turingEventWnd",
                                        0,
                                        0,
                                        0,
                                        win32con.CW_USEDEFAULT,
                                        win32con.CW_USEDEFAULT,
                                        0,
                                        0,
                                        hinst,
                                        None)
    except Exception as e:
        logger.error("Exception while creating event window: %s" % str(e))

    old_time = datetime.now()
    current_index = 0
    while not stop:
        current_time = datetime.now()
        difference = current_time - old_time
        difference_in_seconds = difference.total_seconds()

        if(difference_in_seconds > 30):
            index = index + 1
            if not (index < len(background_paths)):
                index = 0
            old_time = current_time
            current_background = background_paths[index]
            lcd.setBackground(current_background)
        
        lcd.setTime(current_time.strftime('%H:%M'), 161, 30,
                             font="roboto/Roboto-Bold.ttf",
                             font_size=60,
                             font_color=(255, 255, 255),
                             align = 'center')

        if drawing:
            lcd.draw()
        win32gui.PumpWaitingMessages()
        time.sleep(0.5)

    lcd.clean_stop()

    time.sleep(5)
    # Close serial connection at exit
    lcd.close()
