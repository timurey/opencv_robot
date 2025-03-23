import configparser
import argparse

# модуль конфигурации устройства
# конфигурация читается из файла "opencvbot.cfg"
# затем, при наличии параметров, переданных аргументами при запуске, эти параметры перезаписываются

DEFAULTS = "opencvbot.cfg"

parser = argparse.ArgumentParser()
config = configparser.ConfigParser()

parser.add_argument('-p', '--port', type=int, help="Running port")
parser.add_argument("-i", "--ip", type=str, help="Ip address")
parser.add_argument('-s', '--serial', type=str, help="Serial port")
args = parser.parse_args()

config.read(DEFAULTS)

# описывается структура, каким параметрам соответствуют аргументы запуска
args_ = {
    'webserver': {
        'port': args.port,
        'ip': args.ip
    },
    'chassis': {
        'serial': args.serial
    },
    'manipulator': {

    },
    'radsens': {

    },
    "camera": {

    }}


def read_config(section, key, _type="string"):
    x = args_.get(section).get(key) or config[section][key] or None
    if isinstance(x, str):
        if x.lower() in ['true', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
            x = True
        elif x.lower() in ['false', 'no', 'nope', 'oh-no']:
            x = False

    # print('Getting params: \'{0}\' \'{1}\', args is: \'{2}\', config file is: \'{3}\', returned value: \'{4}\''
    #       .format(section, key, args_.get(section).get(key), config[section][key], x))
    if _type == 'int':
        return int(x)
    if _type == 'float':
        return float(x)
    return x
