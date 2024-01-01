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

import signal
import time
from datetime import datetime
from threading import Thread, Lock
# Import only the modules for LCD communication

from library.log import logger
from PIL import Image
from objects.screen import screen
from objects.app import app
from objects.bg_handler import background_handler

try:
    import pystray
except:
    pass

import win32api
import win32con
import win32gui

stop = False
drawing = True

def sighandler(signum, frame):
    global stop
    stop = True


def on_win32_ctrl_event(event):
    """Handle Windows console control events (like Ctrl-C)."""
    global stop
    if event in (win32con.CTRL_C_EVENT, win32con.CTRL_BREAK_EVENT, win32con.CTRL_CLOSE_EVENT):
        logger.debug("Caught Windows control event %s, exiting" % event)
        stop = True
    return 0


def on_win32_wm_event(hWnd, msg, wParam, lParam):
    global drawing
    global stop
    """Handle Windows window message events (like ENDSESSION, CLOSE, DESTROY)."""
    logger.debug("Caught Windows window message event %s" % msg)
    logger.debug("Info %s" % wParam)
    if msg == win32con.WM_POWERBROADCAST:
        # WM_POWERBROADCAST is used to detect computer going to/resuming from sleep
        if wParam == win32con.PBT_APMSUSPEND:
            logger.info("Computer is going to sleep, display will turn off")
            drawing = False
            time.sleep(1)
        elif wParam == win32con.PBT_APMRESUMEAUTOMATIC:
            logger.info("Computer is resuming from sleep, display will turn on")
            drawing = True
    else:
        # For any other events, the program will stop
        logger.info("Program will now exit")
        stop = True
    return 0


def lcdThread(background_handler,mutex):
    global drawing
    global stop
    lcd = screen()

    lcd.on()

    # Display the current time and some progress bars as fast as possible
    old_time = datetime.now()

    text_x = 161
    time_y = 30
    date_y = 260
    old_drawing = True
    redraw = False
    while not stop:
        current_time = datetime.now()
        difference = current_time - old_time
        difference_in_seconds = difference.total_seconds()

        with mutex:
            redraw = background_handler.check_redraw()

        if(difference_in_seconds > 30 or redraw):
            old_time = current_time
            with mutex:
                current_background = background_handler.get_current_item()
                background_handler.clear_redraw()
            lcd.setBackground(current_background)
            temp = date_y
            date_y = time_y
            time_y = temp
        
        lcd.setTime(current_time.strftime('%H:%M'), text_x, time_y,
                             font="roboto/Roboto-Bold.ttf",
                             font_size=60,
                             font_color=(255, 255, 255),
                             align = 'center')

        lcd.setDate(datetime.now().strftime('%d/%m'), text_x, date_y,
                    font="roboto/Roboto-Bold.ttf",
                    font_size=60,
                    font_color=(255, 255, 255),
                    align = 'center')

        if drawing:
            if old_drawing != drawing:
                logger.info("Turning Display on")
                lcd.on()
                old_drawing = drawing
            lcd.draw()
        else:
            if old_drawing != drawing:
                logger.info("Turning Display Off")
                lcd.off()
                old_drawing = drawing

        
        win32gui.PumpWaitingMessages()
        time.sleep(0.02)

    lcd.clean_stop()

    time.sleep(1)
    # Close serial connection at exit
    lcd.close()

if __name__ == "__main__":
    # Define background picture
    mutex = Lock()
    bg_handler = background_handler()
    bg_handler.load_backgrounds("res/backgrounds/FF14/")
    gui = app(bg_handler,mutex)

    def on_exit_tray(tray_icon, item):
        global stop
        global gui
        logger.info("Exit from tray icon")
        if tray_icon:
            tray_icon.visible = False
            stop = True
            time.sleep(1)
            tray_icon.stop()
            gui.stop_event()
            logger.info("Exitting")

    try:
        tray_icon = pystray.Icon(
            name='Keyboard Screen',
            title='Keyboard Screen',
            icon=Image.open("res/icons/monitor-icon-17865/64.png"),
            menu=pystray.Menu(
                pystray.MenuItem(
                text='Open',
                action=gui.resume_window_event),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    text='Exit',
                    action=on_exit_tray)
            )
        )
    except:
        tray_icon = None
        logger.warning("Tray icon is not supported on your platform")


    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    win32api.SetConsoleCtrlHandler(on_win32_ctrl_event, True)

    

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


    t1 = Thread(target=lcdThread, args=(bg_handler,mutex,))
    t1.start()

    t2 = Thread(target=tray_icon.run)
    t2.start()

    gui.run()

    logger.debug("Program End")




