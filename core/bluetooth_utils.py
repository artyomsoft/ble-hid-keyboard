import dbus
import logging


def disconnect(bus, path):
    device = bus.get_object("org.bluez", path)
    interface = dbus.Interface(device, "org.bluez.Device1")
    interface.Disconnect()


def turn_off(bus):
    controller = bus.get_object("org.bluez", "/org/bluez/hci0")
    props = dbus.Interface(controller, "org.freedesktop.DBus.Properties")
    props.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(False))


def turn_on(bus):
    controller = bus.get_object("org.bluez", "/org/bluez/hci0")
    props = dbus.Interface(controller, "org.freedesktop.DBus.Properties")
    props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))


def enable_discovering(bus):
    logging.info("Enabling discovering")
    controller = bus.get_object("org.bluez", "/org/bluez/hci0")
    props = dbus.Interface(controller, "org.freedesktop.DBus.Properties")
    props.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(True))


def disable_discovering(bus):
    controller = bus.get_object("org.bluez", "/org/bluez/hci0")
    props = dbus.Interface(controller, "org.freedesktop.DBus.Properties")
    props.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(False))


def is_discovering(bus):
    controller = bus.get_object("org.bluez", "/org/bluez/hci0")
    props = dbus.Interface(controller, 'org.freedesktop.DBus.Properties')
    return bool(props.Get('org.bluez.Adapter1', 'Discoverable'))


def properties_changed_callback(*args):
    logging.info(f"PROPERTIES CHANGED: {args}")


def listen_to_device(bus):
    controller = bus.get_object("org.bluez", "/org/bluez/hci0")
    props = dbus.Interface(controller, "org.freedesktop.DBus.Properties")
    props.connect_to_signal("PropertiesChanged", properties_changed_callback)

