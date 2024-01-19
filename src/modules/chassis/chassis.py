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

class Chassis:
    def __init__(self, serial_port, baudrate, chassistype):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.chassistype = chassistype
        self.controlX = 0
        self.controlY = 0
        self.speedScale = 1
        self.maxAbsSpeed = 100  # максимальное абсолютное отправляемое значение скорости
        self.running = False
        self.sendFreq = 10
        self.lock = threading.Lock()
        self.tread = threading.Thread(target=self.sender,  daemon=True)
        self.answer = {}
        print("Connecting to chassis type: ", self.chassistype, " on serial: ", self.serial_port, " with baudrate: ", self.baudrate)
        self.serialPort = serial.Serial(self.serial_port, self.baudrate)
        # пакет, посылаемый на робота
        if self.chassistype == "tank":
            self.msgPrev = self.msg = {
                "speedA": 0,  # в пакете посылается скорость на левый и правый борт тележки для танкового хода
                "speedB": 0,  #

            }
        elif self.chassistype == "steer":
            self.msgPrev = self.msg = {
                "speed": 0,  # для hoverBot передается скорость и направление
                "steer": 0
            }
        else:
            self.msgPrev = self.msg = {}

    def setSendFreq(self, send_freq):
        self.sendFreq = send_freq

    def setMaxAbsSpeed(self, max_speed):
        self.maxAbsSpeed = int(max_speed)

    def setSpeedScale (self, speed_scale):
        self.speedScale = speed_scale

    def setControl(self, x, y):
        self.controlX = x
        self.controlY = y

    def moving(self):  # ожидаем значения в интервале (-1..1)
        speedA = self.maxAbsSpeed * (self.controlY + self.controlX)  # преобразуем скорость робота,
        speedB = self.maxAbsSpeed * (self.controlY - self.controlX)  # в зависимости от положения джойстика

        speedA = max(-self.maxAbsSpeed, min(speedA, self.maxAbsSpeed))  # функция аналогичная constrain в arduino
        speedB = max(-self.maxAbsSpeed, min(speedB, self.maxAbsSpeed))  # функция аналогичная constrain в arduino

        if self.chassistype == "tank":
            self.msg["speedA"], self.msg[
                "speedB"] = self.speedScale * speedA, self.speedScale * speedB  # урезаем скорость и упаковываем

        elif self.chassistype == "steer":
            self.msg["speed"], self.msg["steer"] = int(self.controlY * 1000), int(
                self.controlX * 1000)  # для roverfocserial нужны значения в интервале (-1000... 1000)

        else:
            self.msg = {}

        self.serialPort.write(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        # print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg
        return True

    def start(self):
        with self.lock:
            self.running = True
        self.tread = threading.Thread(target=self.sender, daemon=True).start()

    def stop(self):
        with self.lock:
            self.running = False

    def sender(self):
        with self.lock:
            while self.running:
                self.moving()

                answer = self.serialPort.readline()
                if is_json(answer):
                    self.answer = json.loads(answer)
                    # print(self.answer)
                    # todo: сделать остановку по тайм-ауту
                    #
                    # controlX = 0  # failsafe: останавливаемся в случае обрыва связи
                    # controlY = 0  # failsafe: останавливаемся в случае обрыва связи
                    #
                time.sleep(1 / self.sendFreq)

    def getAnswer(self):
        return self.answer
