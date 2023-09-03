import serial
import json

# параметры робота
speedScale = 0.65  # определяет скорость в процентах (0.50 = 50%) от максимальной абсолютной
lightScale = 1  # определяет скорость в процентах (0.50 = 50%) от максимальной абсолютной

maxAbsSpeed = 100  # максимальное абсолютное отправляемое значение скорости
maxAbsLighting = 100

msgPrev = {}
ledMsgPrev = {}

# serialPort = serial.Serial(args.serial, 9600)   # открываем uart
ledSerialPort = serial.Serial("/dev/tty.usbmodem101", 9600)  # открываем uart


def moving(controlX, controlY):
    # пакет, посылаемый на робота
    msg = {
        "speedA": 0,  # в пакете посылается скорость на левый и правый борт тележки
        "speedB": 0  #
    }
    global msgPrev
    speedA = maxAbsSpeed * (controlY + controlX)  # преобразуем скорость робота,
    speedB = maxAbsSpeed * (controlY - controlX)  # в зависимости от положения джойстика

    speedA = max(-maxAbsSpeed, min(speedA, maxAbsSpeed))  # функция аналогичная constrain в arduino
    speedB = max(-maxAbsSpeed, min(speedB, maxAbsSpeed))  # функция аналогичная constrain в arduino

    msg["speedA"], msg["speedB"] = speedScale * speedA, speedScale * speedB  # урезаем скорость и упаковываем
    # if sorted(msg.items()) != sorted(msgPrev.items()):
        # ledSerialPort.write(json.dumps(msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
    msgPrev = msg
    return True

def lighting(controlX, controlY):
    # пакет, посылаемый на робота
    ledMsg = {
        "ledA": 0,  # в пакете посылается скорость на левый и правый борт тележки
        "ledB": 0  #
    }
    global ledMsgPrev

    if (controlX > 0):
        ledB = controlX * maxAbsLighting
        ledA = 0.0
    else:
        ledA = abs(controlX) * maxAbsLighting
        ledB = 0.0

    ledA = max(0, min(ledA, maxAbsLighting))  # функция аналогичная constrain в arduino
    ledB = max(0, min(ledB, maxAbsLighting))  # функция аналогичная constrain в arduino

    ledMsg["ledA"], ledMsg["ledB"] = lightScale * ledA, lightScale * ledB  # урезаем скорость и упаковываем
    if sorted(ledMsg.items()) != sorted(ledMsgPrev.items()):
        ledSerialPort.write(json.dumps(ledMsg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        print(json.dumps(ledMsg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
    ledMsgPrev = ledMsg
    return True