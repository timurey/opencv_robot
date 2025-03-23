import serial
import json
import time
import threading


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


class Radsens:
    def __init__(self, serial_port, baudrate):
        self.serial_port = serial_port
        self.baudrate = baudrate

        self.minSensitivity = 0
        self.maxSensitivity = 105
# максимальное абсолютное отправляемое значение скорости
        self.running = False
        self.sendFreq = 1
        self.lock = threading.Lock()
        self.tread = threading.Thread(target=self.sender, daemon=True)
        self.answer = {}
        print("Connecting to radsens sensor on serial: ", self.serial_port, " with baudrate: ", self.baudrate)
        self.serialPort = serial.Serial(self.serial_port, self.baudrate)
        # пакет, посылаемый на сенсор

        self.msgPrev = self.msg = {}

    def config(self):  # ожидаем значения в интервале (-1..1)
        # speedA = self.maxAbsSpeed * (self.controlY + self.controlX)  # преобразуем скорость робота,
        # speedB = self.maxAbsSpeed * (self.controlY - self.controlX)  # в зависимости от положения джойстика
        #
        # speedA = max(-self.maxAbsSpeed, min(speedA, self.maxAbsSpeed))  # функция аналогичная constrain в arduino
        # speedB = max(-self.maxAbsSpeed, min(speedB, self.maxAbsSpeed))  # функция аналогичная constrain в arduino
        #
        # if self.chassistype == "tank":
        #     self.msg["speedA"], self.msg[
        #         "speedB"] = self.speedScale * speedA, self.speedScale * speedB  # урезаем скорость и упаковываем
        #
        # elif self.chassistype == "steer":
        #     self.msg["speed"], self.msg["steer"] = int(self.controlY * 1000), int(
        #         self.controlX * 1000)  # для roverfocserial нужны значения в интервале (-1000... 1000)
        #
        # else:
        #     self.msg = {}
        #
        # self.serialPort.write(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        # self.msgPrev = self.msg
        return True

    def start(self):
        with self.lock:
            self.running = True
        self.tread = threading.Thread(target=self.sender, daemon=True).start()

    def hvGeneratorStart(self):
        self.msg = {"configure": {"setHVGeneratorState": "true"}}
        self.serialPort.write(
            json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg

    def hvGeneratorStop(self):
        self.msg = {"configure": {"setHVGeneratorState": "false"}}
        self.serialPort.write(
            json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg

    def setLedOn(self):
        self.msg = {"configure": {"setLed": "true"}}
        self.serialPort.write(
            json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg

    def setLedOff(self):
        self.msg = {"configure": {"setLed": "false"}}
        self.serialPort.write(
            json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg

    def setSensitivity(self, sensitivity):
        # todo: add checking for minimum/maximum value
        self.msg = {"configure": {"setSensitivity": sensitivity}}
        self.serialPort.write(
            json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg
    def stop(self):
        with self.lock:
            self.running = False

    def sender(self):
        with self.lock:
            while self.running:
                # self.moving()

                answer = self.serialPort.readline()
                if is_json(answer):
                    self.answer = json.loads(answer)
                    print(self.answer)
                    # todo: сделать остановку по тайм-ауту
                    #
                    # controlX = 0  # failsafe: останавливаемся в случае обрыва связи
                    # controlY = 0  # failsafe: останавливаемся в случае обрыва связи
                    #
                time.sleep(1 / self.sendFreq)

    def getAnswer(self):
        return self.answer
