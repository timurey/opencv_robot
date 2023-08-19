# import serial
import json

# параметры робота
speedScale = 0.65  # определяет скорость в процентах (0.50 = 50%) от максимальной абсолютной
maxAbsSpeed = 100  # максимальное абсолютное отправляемое значение скорости

msgPrev = {}

# serialPort = serial.Serial(args.serial, 9600)   # открываем uart

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
    if sorted(msg.items()) != sorted(msgPrev.items()):
        # serialPort.write(json.dumps(msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        print(json.dumps(msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
    msgPrev = msg
    return True
