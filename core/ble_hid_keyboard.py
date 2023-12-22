import logging
import signal

import dbus

from core.ble_dbus import Service, Characteristic, Application, BLUEZ_SERVICE_NAME, GATT_MANAGER_IFACE, Descriptor
from core.bluetooth_utils import turn_off
from core.hidraw_keyboard import keyboards

#HID_REPORT_DESCRIPTOR = '05010906a1018501050719e029e71500250175019508810295017508810395057501050819012905910295017503910395067508150025ff0507190029ff8100c0'
#HID_REPORT_DESCRIPTOR = '05010906a101050719e029e715002501750195088102750895018101050875019505190129059102750395019101050719002aff00150026ff00750895068100c0'
HID_REPORT_DESCRIPTOR = "05010906a1018501050719e029e715002501750195088102750895018101050875019505190129059102750395019101050719002aff00150026ff00750895068100c0"
#HID_REPORT_DESCRIPTOR = "05010906a101050719e029e715002501750195088102750895018101050875019505190129059102750395019101050719002aff00150026ff00750895068100c0"

BATTERY_SERVICE_UUID = '180f'
BATTERY_LVL_UUID = '2a19'
DEVICE_INFO_SERVICE_UUID = '180A'
VENDOR_CHARACTERISTIC_UUID = '2A29'
PRODUCT_CHARACTERISTIC_UUID = '2A24'
VERSION_CHARACTERISTIC_UUID = '2A28'
PNP_CHARACTERISTIC_UUID = '2A50'
HID_SERVICE_UUID = '1812'
PROTOCOL_MODE_CHARACTERISTIC_UUID = '2A4E'
HID_INFO_CHARACTERISTIC_UUID = '2A4A'
CONTROL_POINT_CHARACTERISTIC_UUID = '2A4C'
REPORT_MAP_CHARACTERISTIC_UUID = '2A4B'
REPORT_CHARACTERISTIC_UUID = '2A4D'


class BleHidKeyboardApplication(Application):
    def __init__(self, bus, mainloop):
        Application.__init__(self, bus)
#        self.services = [HIDService(bus), DeviceInfoService(bus), BatteryService(bus)]
        self.services = [HIDService(bus), DeviceInfoService(bus), BatteryService(bus)]

        self.mainloop = mainloop
        self.bus = bus

    def register_callback(self):
        logging.info('GATT application registered')

    def error_callback(self, error):
        logging.error('Failed to register application: ' + str(error))
        self.mainloop.quit()

    def sigint_handler(self, sig, frame):
        logging.info("Signal Handler")
        if sig != signal.SIGINT:
            raise ValueError("Undefined handler for '{sig}'")
        else:
            logging.info('SIGINT RECEIVED')
            turn_off(self.bus)
            self.mainloop.quit()


class BatteryService(Service):
    def __init__(self, bus):
        Service.__init__(self, bus, BATTERY_SERVICE_UUID, True)
        self.characteristics = [BatteryLevelCharacteristic(self)]


class BatteryLevelCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(self, self.__class__.__name__, service, BATTERY_LVL_UUID, ["read", "notify"])
        self.battery_lvl = 100

    def ReadValue(self, options):
        logging.info("Battery Level read: " + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]

    def StartNotify(self):
        logging.info("Start Battery Notify")

    def StopNotify(self):
        logging.info("Stop Battery Notify")


class DeviceInfoService(Service):
    def __init__(self, bus):
        Service.__init__(self, bus, DEVICE_INFO_SERVICE_UUID, True)
        self.characteristics = [self.ro_charateristic("PnP", PNP_CHARACTERISTIC_UUID, hex_2_dbus_array("02C41001000100")),
                                self.ro_charateristic("Vendor", VENDOR_CHARACTERISTIC_UUID, str_2_dbus_array("artyomsoft")),
                                self.ro_charateristic("Product", PRODUCT_CHARACTERISTIC_UUID, str_2_dbus_array("BLE Keyboard")),
                                self.ro_charateristic("Version", VERSION_CHARACTERISTIC_UUID, str_2_dbus_array("1.0.0"))
                                ]


class HIDService(Service):

    def __init__(self, bus):
        Service.__init__(self, bus, HID_SERVICE_UUID, True)
        self.characteristics = [
            ProtocolModeCharacteristic(self),
            HIDInfoCharacteristic(self),
            ControlPointCharacteristic(self),
            ReportMapCharacteristic(self),
            ReportCharacteristic(self)
        ]


class ProtocolModeCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(self, self.__class__.__name__,
                                service, PROTOCOL_MODE_CHARACTERISTIC_UUID, ["read", "write-without-response"])
        self.value = hex_2_dbus_array("01")
        logging.info(f"Created {self.name}: {self.value}")

    def ReadValue(self, options):
        logging.info(f"Read {self.value}: {self.value}")
        return self.value

    def WriteValue(self, value, options):
        logging.info(f"Write {self.value}: {value}")
        self.value = value


class HIDInfoCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(self, self.__class__.__name__,
                                service, HID_INFO_CHARACTERISTIC_UUID, ['secure-read'])
        self.value = hex_2_dbus_array("01110002")
        logging.info(f"Created {self.name} value: {self.value}")

    def ReadValue(self, options):
        logging.info(f"Read {self.name}: {self.value}")
        return self.value


class ControlPointCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(self, self.__class__.__name__, service,
                                CONTROL_POINT_CHARACTERISTIC_UUID, ["write-without-response"])
        self.value = hex_2_dbus_array("00")
        logging.info(f"Created {self.name}: {self.value}")

    def WriteValue(self, value, options):
        logging.info(f"Write {self.name} {value}")
        self.value = value


class ReportMapCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(self, self.__class__.__name__, service, REPORT_MAP_CHARACTERISTIC_UUID, ['read'])
        # USB HID Report Descriptor
        self.value = hex_2_dbus_array(HID_REPORT_DESCRIPTOR)
        logging.info(f"Created {self.name}: {self.value}")

    def ReadValue(self, options):
        logging.info(f"Read {self.name}: {self.value}")
        return self.value


class ReportCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(self, self.__class__.__name__, service,
                                REPORT_CHARACTERISTIC_UUID, ["secure-read", "notify"])
        self.value = hex_2_dbus_array("000000000000")
        self.descriptors = [Report1ReferenceDescriptor(service.bus, 1, self)]
        logging.info(f"Created ReportCharacteristic: {self.value}")

    def send(self, data):
        logging.info(f"Send key")
        super().properties_changed({"Value": dbus.Array(data, signature=dbus.Signature("y"))})
        return True

    def ReadValue(self, options):
        logging.info(f"Read {self.name}: {self.value}")
        return self.value

    def WriteValue(self, value, options):
        logging.info(f"Write {self.name}: {value}")
        self.value = value

    def StartNotify(self):
        logging.info(f"Started ReportCharacteristic notifying")
        keyboards.watch(self.send)
        logging.info(f"Started HID keyboard watching")

    def StopNotify(self):
        logging.info(f"Stop Report Keyboard Input")


class Report1ReferenceDescriptor(Descriptor):
    DESCRIPTOR_UUID = '2908'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self, bus, index,
            self.DESCRIPTOR_UUID,
            ['read'],
            characteristic)

        self.value = dbus.Array(bytearray.fromhex('0101'), signature=dbus.Signature('y'))
        print(f'***ReportReference***: {self.value}')

    def ReadValue(self, options):
        print(f'Read ReportReference: {self.value}')
        return self.value


def hex_2_dbus_array(value):
    return dbus.Array(bytearray.fromhex(value))


def str_2_dbus_array(value):
    return dbus.Array(value.encode(), signature=dbus.Signature("y"))


def register_application(adapter, bus, mainloop):
    logging.info("Registering GATT application...")
    app = BleHidKeyboardApplication(bus, mainloop)
    signal.signal(signal.SIGINT, app.sigint_handler)

    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=app.register_callback,
                                        error_handler=app.error_callback)
