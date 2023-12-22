import configparser
import logging
import os.path

CONFIG_FILE = "/etc/ble-hid-keyboard.conf"


class Config:

    def __init__(self):
        self.config = configparser.ConfigParser()

        if not os.path.exists(CONFIG_FILE):
            logging.info(f"Config {CONFIG_FILE} is not exists. Creating new one.")
            self.config["Bluetooth"] = {"paired": False,
                                        "name": "BLE Keyboard"}
        else:
            logging.info(f"Loading {CONFIG_FILE}")
            self.config.read(CONFIG_FILE)
            logging.info(self.config["Bluetooth"]["paired"])
            logging.info(self.config["Bluetooth"]["name"])

    def get(self, section, option):
        return self.config[section][option]

    def get_boolean(self, section, option):
        value = self.config[section].getboolean(option)
        logging.info(f"Type: {type(value)}")
        logging.info(f"Get boolean {section}.{option} = {value}")
        return value

    def set(self, section, option, value):
        logging.info("setting")
#        self.config.set(section, option, value)
        logging.info("is set")

    def save(self):
        with open(CONFIG_FILE) as configfile:
            self.config.write(configfile)


config = Config()
