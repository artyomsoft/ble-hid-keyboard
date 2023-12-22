import logging

import dbus
import keyboard

from core.ble_dbus import BLUEZ_SERVICE_NAME

from core.config import config

AGENT_IFACE = "org.bluez.Agent1"
AGENT_MANAGER_IFACE = "org.bluez.AgentManager1"


class Agent(dbus.service.Object):
    def __init__(self, bus, capability):
        self.path = "/org/bluez/BLEHidKeyBoard/Agent"
        self.capability = capability
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method(AGENT_IFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        logging.info(f"Requesting passkey {device}")
        passkey = get_passkey()
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_IFACE, in_signature="", out_signature="")
    def Cancel(self):
        logging.info("Cancel")

    def get_path(self):
        return self.path

    def get_capability(self):
        return self.capability


class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"


def get_passkey():
    recorded = keyboard.record(until="enter")
    passkey = ''
    for i in range(len(recorded) - 2):
        event = recorded[i]
        if event.event_type == "down":
            passkey = passkey + event.name
    return passkey


def register_agent(adapter, bus):
    bluez = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")
    manager = dbus.Interface(bluez, "org.bluez.AgentManager1")

#    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), AGENT_MANAGER_IFACE)
    agent = Agent(bus, "KeyboardOnly")
    manager.RegisterAgent(agent, agent.get_capability())
    logging.info("Agent registered")
    manager.RequestDefaultAgent(agent)
    logging.info("Default Agent is Registered")
