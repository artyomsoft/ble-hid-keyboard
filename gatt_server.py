#! /usr/bin/python3

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s][%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler()])

import dbus.mainloop.glib
import dbus.service

import time

from gi.repository import GLib

from core.advertisement import register_advertisement
from core.agent import register_agent
from core.ble_dbus import find_adapter
from core.ble_hid_keyboard import register_application
from core.bluetooth_utils import listen_to_device, enable_discovering, turn_on
from core.config import config


def main():
#    time.sleep(5)
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    adapter = find_adapter(bus)
    if not adapter:
        logging.error('GattManager1 interface not found')
        exit(-1)

    mainloop = GLib.MainLoop()
    turn_on(bus)
    listen_to_device(bus)

    discoverable = not config.get_boolean("Bluetooth", "paired")
    if discoverable:
        register_agent(adapter, bus)

    register_advertisement(adapter, bus, discoverable)
    register_application(adapter, bus, mainloop)

    mainloop.run()


if __name__ == '__main__':
    main()
