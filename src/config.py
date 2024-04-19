from configparser import ConfigParser


def GetConfig():
    config = ConfigParser()
    config.read('config.ini')
    return config
