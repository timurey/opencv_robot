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


class SomeObject:
    def __init__(self, arg_1: str, arg_2: int) -> None:
        self._attr_1 = arg_1
        self._attr_2 = arg_2


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


class ManipulatorConfig:
    def __init__(
            self,
            serial_port: str,
            baudrate: int,
            resetCommand: json,

            a_joint_mode: str,
            a_joint_id: int,
            a_joint_name: str,
            a_joint_ratio: float,
            # a_limit_min: int,
            # a_limit_max: int,
            a_moving_speed: int,
            a_dynamixel_id: int,
            a_dynamixel_torque_limit: int,
            a_dynamixel_reverse: bool,

            q1_joint_mode: str,
            q1_joint_id: int,
            q1_joint_name: str,
            q1_joint_length: int,
            # q1_joint_ratio: float,
            q1_limit_min: int,
            q1_limit_max: int,
            q1_moving_speed: int,

            q1_1_dynamixel_id: int,
            q1_1_dynamixel_torque_limit: int,
            q1_1_dynamixel_min: int,
            # q1_1_dynamixel_max: int,
            q1_1_dynamixel_reverse: bool,
            q1_2_dynamixel_id: int,
            q1_2_dynamixel_torque_limit: int,
            q1_2_dynamixel_min: int,
            # q1_2_dynamixel_max: int,
            q1_2_dynamixel_reverse: bool,

            q2_joint_mode: str,
            q2_joint_id: int,
            q2_joint_name: str,
            q2_joint_length: int,
            # q2_joint_ratio: float,
            q2_limit_min: int,
            q2_limit_max: int,
            q2_moving_speed: int,

            q2_1_dynamixel_id: int,
            q2_1_dynamixel_torque_limit: int,
            q2_1_dynamixel_min: int,
            # q2_dynamixel_max: int,
            q2_1_dynamixel_reverse: bool,

            q2_2_dynamixel_id: int,
            q2_2_dynamixel_torque_limit: int,
            # q2_2_dynamixel_min: int,
            # q2_dynamixel_max: int,
            q2_2_dynamixel_reverse: bool,
            q2_2_slave: bool,
            q2_2_ratio: float,

            q3_joint_mode: str,
            q3_joint_id: int,
            q3_joint_name: str,
            q3_joint_length: int,
            # q3_joint_ratio: float,
            q3_limit_min: int,
            q3_limit_max: int,
            q3_moving_speed: int,

            q3_dynamixel_id: int,
            q3_dynamixel_torque_limit: int,
            q3_dynamixel_min: int,
            # q3_dynamixel_max: int,
            q3_dynamixel_reverse: bool,

            b_joint_mode: str,
            b_joint_id: int,
            b_joint_name: str,
            b_joint_ratio: float,
            b_limit_min: int,
            b_limit_max: int,
            b_moving_speed: int,

            b_dynamixel_id: int,
            b_dynamixel_torque_limit: int,
            b_dynamixel_reverse: bool,

            g_joint_mode: str,
            g_joint_id: int,
            g_joint_name: str,
            g_joint_length: int,
            # g_joint_ratio: float,
            g_limit_min: int,
            g_limit_max: int,
            g_moving_speed: int,

            g_dynamixel_id: int,
            g_dynamixel_torque_limit: int,
            g_dynamixel_min: int,
            # g_dynamixel_max: int,
            g_dynamixel_reverse: bool

    ) -> None:
        self.serial_port = serial_port
        self.baudrate = baudrate

        # joint a configuration
        self.a_joint_mode = a_joint_mode
        self.a_joint_id = a_joint_id
        self.a_joint_name = a_joint_name
        self.a_joint_ratio = float(a_joint_ratio)
        # self.a_limit_min = a_limit_min
        # self.a_limit_max = a_limit_max
        self.a_moving_speed = a_moving_speed

        # joint a dynamixel configuration
        self.a_dynamixel_id = a_dynamixel_id
        self.a_dynamixel_torque_limit = a_dynamixel_torque_limit
        self.a_dynamixel_reverse = a_dynamixel_reverse

        # joint q1 configuration
        self.q1_joint_mode = q1_joint_mode
        self.q1_joint_id = q1_joint_id
        self.q1_joint_name = q1_joint_name
        self.q1_joint_length = q1_joint_length
        # self.q1_joint_ratio =  float(q1_joint_ratio)
        self.q1_limit_min = q1_limit_min
        self.q1_limit_max = q1_limit_max
        self.q1_moving_speed = q1_moving_speed

        # joint q1 dynamixel 1 configuration
        self.q1_1_dynamixel_id = q1_1_dynamixel_id
        self.q1_1_dynamixel_min = q1_1_dynamixel_min
        # self.q1_1_dynamixel_max = q1_1_dynamixel_max
        self.q1_1_dynamixel_torque_limit = q1_1_dynamixel_torque_limit
        self.q1_1_dynamixel_reverse = q1_1_dynamixel_reverse
        # joint q1 dynamixel 2 configuration
        self.q1_2_dynamixel_id = q1_2_dynamixel_id
        self.q1_2_dynamixel_min = q1_2_dynamixel_min
        # self.q1_2_dynamixel_max = q1_2_dynamixel_max
        self.q1_2_dynamixel_torque_limit = q1_2_dynamixel_torque_limit
        self.q1_2_dynamixel_reverse = q1_2_dynamixel_reverse

        # joint q2 configuration
        self.q2_joint_mode = q2_joint_mode
        self.q2_joint_id = q2_joint_id
        self.q2_joint_name = q2_joint_name
        self.q2_joint_length = q2_joint_length
        # self.q2_joint_ratio =  float(q2_joint_ratio)
        self.q2_limit_min = q2_limit_min
        self.q2_limit_max = q2_limit_max
        self.q2_moving_speed = q2_moving_speed
        self.q2_2_slave = q2_2_slave
        self.q2_2_ratio = q2_2_ratio

        # joint q2 dynamixel 1 configuration
        self.q2_1_dynamixel_id = q2_1_dynamixel_id
        self.q2_1_dynamixel_min = q2_1_dynamixel_min
        # self.q2_dynamixel_max = q2_dynamixel_max
        self.q2_1_dynamixel_torque_limit = q2_1_dynamixel_torque_limit
        self.q2_1_dynamixel_reverse = q2_1_dynamixel_reverse
        # joint q2 dynamixel 2 configuration
        self.q2_2_dynamixel_id = q2_2_dynamixel_id
        # self.q2_2_dynamixel_min = q2_2_dynamixel_min
        # self.q2_dynamixel_max = q2_dynamixel_max
        self.q2_2_dynamixel_torque_limit = q2_2_dynamixel_torque_limit
        self.q2_2_dynamixel_reverse = q2_2_dynamixel_reverse

        # joint q3 configuration
        self.q3_joint_mode = q3_joint_mode
        self.q3_joint_id = q3_joint_id
        self.q3_joint_name = q3_joint_name
        self.q3_joint_length = q3_joint_length
        # self.q3_joint_ratio =  float(q3_joint_ratio)
        self.q3_limit_min = q3_limit_min
        self.q3_limit_max = q3_limit_max
        self.q3_moving_speed = q3_moving_speed

        # joint q3 dynamixel 1 configuration
        self.q3_dynamixel_id = q3_dynamixel_id
        self.q3_dynamixel_min = q3_dynamixel_min
        # self.q3_dynamixel_max = q3_dynamixel_max
        self.q3_dynamixel_torque_limit = q3_dynamixel_torque_limit
        self.q3_dynamixel_reverse = q3_dynamixel_reverse

        # joint b configuration
        self.b_joint_mode = b_joint_mode
        self.b_joint_id = b_joint_id
        self.b_joint_name = b_joint_name
        self.b_joint_ratio = float(b_joint_ratio)
        self.b_limit_min = b_limit_min
        self.b_limit_max = b_limit_max
        self.b_moving_speed = b_moving_speed

        # joint a dynamixel configuration
        self.b_dynamixel_id = b_dynamixel_id
        self.b_dynamixel_torque_limit = b_dynamixel_torque_limit
        self.b_dynamixel_reverse = b_dynamixel_reverse

        # joint g configuration
        self.g_joint_mode = g_joint_mode
        self.g_joint_id = g_joint_id
        self.g_joint_name = g_joint_name
        self.g_joint_length = g_joint_length
        # self.g_joint_ratio =  float(g_joint_ratio)
        self.g_limit_min = g_limit_min
        self.g_limit_max = g_limit_max
        self.g_moving_speed = g_moving_speed

        # joint g dynamixel 1 configuration
        self.g_dynamixel_id = g_dynamixel_id
        self.g_dynamixel_min = g_dynamixel_min
        # self.g_dynamixel_max = g_dynamixel_max
        self.g_dynamixel_torque_limit = g_dynamixel_torque_limit
        self.g_dynamixel_reverse = g_dynamixel_reverse

        self.resetCommand = {"reset": True}

class ManipulatorStatus:
    def __init__(self,
                 # l: float,
                 # t: float,
                 # z: float,
                 pos_a: float,
                 pos_q1: float,
                 pos_q2: float,
                 pos_q3: float,
                 pos_b: float,
                 pos_g: float,
                 speed_a: float,
                 speed_q1: float,
                 speed_q2: float,
                 speed_q3: float,
                 speed_b: float,
                 speed_g: float

                 ) -> None:
        # self.l = l
        # self.t = t
        # self.z = z
        self.pos_a = pos_a
        self.pos_q1 = pos_q1
        self.pos_q2 = pos_q2
        self.pos_q3 = pos_q3
        self.pos_b = pos_b
        self.pos_g = pos_g
        self.speed_a = speed_a
        self.speed_q1 = speed_q1
        self.speed_q2 = speed_q2
        self.speed_q3 = speed_q3
        self.speed_b = speed_b
        self.speed_g = speed_g


class ManipulatorControl:
    def __init__(self,
                 l: float,
                 t: float,
                 z: float,
                 c: float,
                 r: float,
                 pos_a: float,
                 pos_q1: float,
                 pos_q2: float,
                 pos_q3: float,
                 pos_b: float,
                 pos_g: float,
                 speed_a: float,
                 speed_q1: float,
                 speed_q2: float,
                 speed_q3: float,
                 speed_b: float,
                 speed_g: float

                 ) -> None:
        self.l = l | 0
        self.t = t | 0
        self.z = z | 0
        self.c = c | 0
        self.r = r | 0
        self.pos_a = pos_a
        self.pos_q1 = pos_q1
        self.pos_q2 = pos_q2
        self.pos_q3 = pos_q3
        self.pos_b = pos_b
        self.pos_g = pos_g
        self.speed_a = speed_a
        self.speed_q1 = speed_q1
        self.speed_q2 = speed_q2
        self.speed_q3 = speed_q3
        self.speed_b = speed_b
        self.speed_g = speed_g


class Manipulator:
    def __init__(self, config: ManipulatorConfig):
        self.config = config
        self.control = ManipulatorControl(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.status = {}
        self.is_configured = False
        # self.serial_port = config.serial_port
        # self.baudrate = config.baudrate
        # self.chassistype = chassistype
        # self.controlX = 0
        # self.controlY = 0
        # self.speedScale = 1
        # self.maxAbsSpeed = 100  # максимальное абсолютное отправляемое значение скорости
        self.running = False
        self.sendFreq = 10
        self.lockTX = threading.Lock()
        self.lockRX = threading.Lock()
        self.treadTX = threading.Thread(target=self.sender, daemon=True)
        self.treadRX = threading.Thread(target=self.receiver, daemon=True)
        self.answer = {}
        print("Connecting to manipulator on serial: ", self.config.serial_port, " with baudrate: ",
              self.config.baudrate)
        self.serialPort = serial.Serial(self.config.serial_port, self.config.baudrate, timeout=100)

        # configure opencm9
        self.currentConfigA = {
            "configure": {
                "joint": [{
                    "name": "a",
                    "id": self.config.a_joint_id,
                    "mode": "wheel",
                    # "limits": [
                    #     self.config.a_limit_min,
                    #     self.config.a_limit_max
                    # ],
                    "ratio": self.config.a_joint_ratio,
                    "dynamixels": [
                        {
                            "id": self.config.a_dynamixel_id,
                            "cw_angle_limit": 0,
                            "cww_angle_limit": 0,
                            "moving_speed": 0,
                            "torque_limit": self.config.a_dynamixel_torque_limit,
                            "reverse": self.config.a_dynamixel_reverse
                        }
                    ]
                }
                ]
            }
        }
        self.currentConfigQ1 = {
            "configure": {
                "joint": [{
                    "name": "q1",
                    "id": self.config.q1_joint_id,
                    "mode": "joint",
                    "limits": [
                        self.config.q1_limit_min,
                        self.config.q1_limit_max
                    ],
                    "moving_speed": self.config.q1_moving_speed,
                    "dynamixels": [
                        {
                            "id": self.config.q1_1_dynamixel_id,
                            "cw_angle_limit": self.config.q1_1_dynamixel_min,
                            # "cww_angle_limit": self.config.q1_1_dynamixel_max,
                            "torque_limit": self.config.q1_1_dynamixel_torque_limit,
                            "reverse": self.config.q1_1_dynamixel_reverse
                        },
                        {
                            "id": self.config.q1_2_dynamixel_id,
                            "cw_angle_limit": self.config.q1_2_dynamixel_min,
                            # "cww_angle_limit": self.config.q1_2_dynamixel_max,
                            "torque_limit": self.config.q1_2_dynamixel_torque_limit,
                            "reverse": self.config.q1_2_dynamixel_reverse
                        }
                    ]
                }
                ]
            }
        }
        self.currentConfigQ2 = {
            "configure": {
                "joint": [
                    {
                        "name": "q2",
                        "id": self.config.q2_joint_id,
                        "mode": "joint",
                        "limits": [
                            self.config.q2_limit_min,
                            self.config.q2_limit_max
                        ],
                        "moving_speed": self.config.q2_moving_speed,
                        "dynamixels": [
                            {
                                "id": self.config.q2_1_dynamixel_id,
                                "cw_angle_limit": self.config.q2_1_dynamixel_min,
                                # "cww_angle_limit": self.config.q2_dynamixel_max,
                                "torque_limit": self.config.q2_1_dynamixel_torque_limit,
                                "reverse": self.config.q2_1_dynamixel_reverse
                            },
                            {
                                "id": self.config.q2_2_dynamixel_id,
                                # "cw_angle_limit": self.config.q2_2_dynamixel_min,
                                # "cww_angle_limit": self.config.q2_dynamixel_max,
                                "torque_limit": self.config.q2_2_dynamixel_torque_limit,
                                "reverse": self.config.q2_2_dynamixel_reverse,
                                "slave": self.config.q2_2_slave,
                                "ratio": self.config.q2_2_ratio
                            }
                        ]
                    }

                ]
            }
        }
        self.currentConfigQ3 = {
            "configure": {
                "joint": [
                    {
                        "name": "q3",
                        "id": self.config.q3_joint_id,
                        "mode": "joint",
                        "limits": [
                            self.config.q3_limit_min,
                            self.config.q3_limit_max
                        ],
                        "moving_speed": self.config.q3_moving_speed,
                        "dynamixels": [
                            {
                                "id": self.config.q3_dynamixel_id,
                                "cw_angle_limit": self.config.q3_dynamixel_min,
                                # "cww_angle_limit": self.config.q3_dynamixel_max,
                                "torque_limit": self.config.q3_dynamixel_torque_limit,
                                "reverse": self.config.q3_dynamixel_reverse
                            }
                        ]
                    }
                ]
            }
        }
        self.currentConfigB = {
            "configure": {
                "joint": [{
                    "name": "b",
                    "id": self.config.b_joint_id,
                    "mode": "wheel",
                    "limits": [
                        self.config.b_limit_min,
                        self.config.b_limit_max
                    ],
                    "ratio": self.config.b_joint_ratio,
                    "moving_speed": 0,
                    "dynamixels": [
                        {
                            "id": self.config.b_dynamixel_id,
                            "cw_angle_limit": 0,
                            "cww_angle_limit": 0,
                            "torque_limit": self.config.b_dynamixel_torque_limit,
                            "reverse": self.config.b_dynamixel_reverse
                        }
                    ]
                }

                ]
            }
        }
        self.currentConfigG = {
            "configure": {
                "joint": [
                    {
                        "name": "g",
                        "id": self.config.g_joint_id,
                        "mode": "joint",
                        "limits": [
                            self.config.g_limit_min,
                            self.config.g_limit_max
                        ],
                        "moving_speed": self.config.g_moving_speed,
                        "dynamixels": [
                            {
                                "id": self.config.g_dynamixel_id,
                                "cw_angle_limit": self.config.g_dynamixel_min,
                                "torque_limit": self.config.g_dynamixel_torque_limit,
                                "reverse": self.config.g_dynamixel_reverse
                            }
                        ]
                    }
                ]
            }
        }
        # First reset controller
        self.serialPort.write(json.dumps(self.resetCommand, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.resetCommand, ensure_ascii=False).encode("utf8"))

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()

            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if self.answer['status'] == "Waiting for configuration":
                    break
        # Configure a
        self.serialPort.write(json.dumps(self.currentConfigA, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.currentConfigA, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'configured_joints' in self.answer['status']:
                    break
        print(self.answer)
        # Configure q1
        self.serialPort.write(json.dumps(self.currentConfigQ1, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.currentConfigQ1, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'configured_joints' in self.answer['status']:
                    break
        print(self.answer)
        # Configure q2
        self.serialPort.write(json.dumps(self.currentConfigQ2, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.currentConfigQ2, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'configured_joints' in self.answer['status']:
                    break
        print(self.answer)
        # Configure q3
        self.serialPort.write(json.dumps(self.currentConfigQ3, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.currentConfigQ3, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'configured_joints' in self.answer['status']:
                    break
        print(self.answer)

        # Configure B
        self.serialPort.write(json.dumps(self.currentConfigB, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.currentConfigB, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'configured_joints' in self.answer['status']:
                    break
        print(self.answer)

        # Configure G
        self.serialPort.write(json.dumps(self.currentConfigG, ensure_ascii=False).encode("utf8"))
        print(json.dumps(self.currentConfigG, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'configured_joints' in self.answer['status']:
                    break
        print(self.answer)

        # End configure
        self.serialPort.write(json.dumps({"end_configure": True}, ensure_ascii=False).encode("utf8"))
        print(json.dumps({"end_configure": True}, ensure_ascii=False).encode("utf8"))
        # пакет, посылаемый на робота

        while True:
            # Read a line of data from the serial port
            answer = self.serialPort.readline().decode().strip()
            if answer:
                print("Received:", answer)
            if is_json(answer):
                self.answer = json.loads(answer)
                if 'status' in self.answer and 'positions' in self.answer['status']:
                    break
        self.is_configured = True
        # todo: read current values from servos to avoid damage!!!
        self.status = ManipulatorStatus(
            pos_a=self.answer["status"]["positions"]["a"]["pos"],
            pos_q1=self.answer['status']['positions']['q1']['pos'],
            pos_q2=self.answer['status']['positions']['q2']['pos'],
            pos_q3=self.answer['status']['positions']['q3']['pos'],
            pos_b=self.answer['status']['positions']['b']['pos'],
            pos_g=self.answer['status']['positions']['g']['pos'],
            speed_a=self.answer["status"]["positions"]["a"]["speed"],
            speed_q1=self.answer['status']['positions']['q1']['speed'],
            speed_q2=self.answer['status']['positions']['q2']['speed'],
            speed_q3=self.answer['status']['positions']['q3']['speed'],
            speed_b=self.answer['status']['positions']['b']['speed'],
            speed_g=self.answer['status']['positions']['g']['speed']
        )

        # self.msgPrev = self.msg = {"move": [
        #     {"a": {"pos": self.status.pos_a, "speed": self.status.pos_a}},  # угол поворота платформы
        #     {"q1": {"pos": self.status.pos_q1, "speed": self.status.pos_q1}},  # угол поворота первого плеча
        #     {"q2": {"pos": self.status.pos_q2, "speed": self.status.pos_q2}},  # угол поворота второго плеча
        #     {"q3": {"pos": self.status.pos_q3, "speed": self.status.pos_q3}},  # угол наклона клешни
        #     {"b": {"pos": self.status.pos_b, "speed": self.status.pos_b}},  # угол вращения клешни
        #     {"g": {"pos": self.status.pos_g, "speed": self.status.pos_g}}  # угол зажима клешни
        # ]}

    # решаем прямую задачу. из имеющихся углов актуаторов, длин плеч находим положение манипулятора
    def doForward(self, a, q1, q2, q3, b, g):
        l = 0
        t = 6
        z = 6
        return l, t, z

    # решаем обратную задачу. из координат расчитываем углы положения актуаторов
    def doBackward(self, l, t, z, c, r):
        a_speed = self.config.a_moving_speed * t
        # abs(self.config.a_moving_speed * t)
        a = 0
        # self.status.pos_a + self.config.a_moving_speed * t / 10
        q1_speed = abs(self.config.q1_moving_speed * z)
        q1 = constrain(self.status.pos_q1 + (self.config.q1_moving_speed * z) / 10, self.config.q1_limit_min, self.config.q1_limit_max)
        # q2_speed = abs(self.config.q2_moving_speed * z)
        # q2 = self.status.pos_q2 + (self.config.q2_moving_speed * z) / 10
        q2_speed = q1_speed
        q2 = q1

        q3_speed = abs(self.config.q3_moving_speed * l)
        q3 = constrain(self.status.pos_q3 + (self.config.q3_moving_speed * l) / 10, self.config.q3_limit_min, self.config.q3_limit_max)

        b_speed = self.config.b_moving_speed * r
        b = 0

        g_speed = abs(self.config.g_moving_speed * c)
        g = constrain(self.status.pos_g + (self.config.g_moving_speed * c) / 10, self.config.g_limit_min, self.config.g_limit_max)
        return a_speed, a, q1_speed, q1, q2_speed, q2, q3_speed, q3, b_speed, b, g_speed, g

    def setSendFreq(self, send_freq):
        self.sendFreq = send_freq

    # def setMaxAbsSpeed(self, max_speed):
    #     self.maxAbsSpeed = int(max_speed)
    #
    # def setSpeedScale(self, speed_scale):
    #     self.speedScale = speed_scale

    def setControl(self, l, t, z, c, r):
        self.control.l = l
        self.control.t = t
        self.control.z = z
        self.control.g = c
        self.control.r = r
        a_speed, a, q1_speed, q1, q2_speed, q2, q3_speed, q3, b_speed, b, g_speed, g = self.doBackward(l, t, z, c, r)
        self.control.pos_a = a
        self.control.pos_q1 = q1
        self.control.pos_q2 = q2
        self.control.pos_q3 = q3
        self.control.pos_b = b
        self.control.pos_g = g
        self.control.speed_a = a_speed
        self.control.speed_q1 = q1_speed
        self.control.speed_q2 = q2_speed
        self.control.speed_q3 = q3_speed
        self.control.speed_b = b_speed
        self.control.speed_g = g_speed

    def moving(self):  # ожидаем значения в интервале (-1..1)
        if not self.is_configured:
            return False

        # self.msg = {"move": [
        #     {"a": {"pos": self.control.pos_a, "speed": self.control.speed_a}},  # угол поворота платформы
        #     {"q1": {"pos": self.control.pos_q1, "speed": self.control.speed_q1}},  # угол поворота первого плеча
        #     {"q2": {"pos": self.control.pos_q2, "speed": self.control.speed_q2}},  # угол поворота второго плеча
        #     {"q3": {"pos": self.control.pos_q3, "speed": self.control.speed_q3}},  # угол наклона клешни
        #     {"b": {"pos": self.control.pos_b, "speed": self.control.pos_b}},  # угол вращения клешни
        #     {"g": {"pos": self.control.pos_g, "speed": self.control.pos_g}}  # угол зажима клешни
        # ]}
        # self.msg = {}
        self.msg = {"move": []}

        # if self.control.speed_a or self.control.speed_q1 or self.control.speed_q2 or self.control.speed_q3 or self.control.speed_b or self.control.speed_g:
        #     self.msg = {"move": []}
        if self.control.speed_a or self.config.a_joint_mode != 'joint':
            self.msg["move"].append({"a": {"pos": self.control.pos_a, "speed": self.control.speed_a}})
            self.status.pos_a = self.control.pos_a
        if self.control.speed_q1 or self.config.q1_joint_mode != 'joint':
            self.msg["move"].append({"q1": {"pos": self.control.pos_q1, "speed": self.control.speed_q1}})
            self.status.pos_q1 = self.control.pos_q1
        if self.control.speed_q2 or self.config.q2_joint_mode != 'joint':
            self.msg["move"].append({"q2": {"pos": self.control.pos_q2, "speed": self.control.speed_q2}})
            self.status.pos_q2 = self.control.pos_q2
        if self.control.speed_q3 or self.config.q3_joint_mode != 'joint':
            self.msg["move"].append({"q3": {"pos": self.control.pos_q3, "speed": self.control.speed_q3}})
            self.status.pos_q3 = self.control.pos_q3
        if self.control.speed_b or self.config.b_joint_mode != 'joint':
            self.msg["move"].append({"b": {"pos": self.control.pos_b, "speed": self.control.speed_b}})
            self.status.pos_b = self.control.pos_b

        if self.control.speed_g or self.config.g_joint_mode != 'joint':
            self.msg["move"].append({"g": {"pos": self.control.pos_g, "speed": self.control.speed_g}})
            self.status.pos_g = self.control.pos_g

        self.serialPort.write(
            json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
        print(json.dumps(self.msg, ensure_ascii=False).encode("utf8"))  # выводим в консоль данные о скоростях мотора
        self.msgPrev = self.msg
        return True

    def start(self):
        self.running = True

        with self.lockTX:
            self.treadTX.start()
        with self.lockRX:
            self.treadRX.start()
            # = threading.Thread(target=self.sender, daemon=True).start()
        # with self.lockTX:
        # = threading.Thread(target=self.receiver, daemon=True).start()

    def stop(self):
        with self.lock:
            self.running = False

    def sender(self):
        with self.lockTX:
            while self.running:
                print("tx")
                self.moving()

                # answers = self.serialPort.readlines()
                # # print(answers)
                # for answer in answers:
                #     if is_json(answer):
                #         self.answer = json.loads(answer)
                #         print(self.answer)
                #         self.status = ManipulatorStatus(
                #             pos_a=self.answer["status"]["positions"]["a"]["pos"],
                #             pos_q1=self.answer['status']['positions']['q1']['pos'],
                #             pos_q2=self.answer['status']['positions']['q2']['pos'],
                #             pos_q3=self.answer['status']['positions']['q3']['pos'],
                #             pos_b=self.answer['status']['positions']['b']['pos'],
                #             pos_g=self.answer['status']['positions']['g']['pos'],
                #             speed_a=self.answer["status"]["positions"]["a"]["speed"],
                #             speed_q1=self.answer['status']['positions']['q1']['speed'],
                #             speed_q2=self.answer['status']['positions']['q2']['speed'],
                #             speed_q3=self.answer['status']['positions']['q3']['speed'],
                #             speed_b=self.answer['status']['positions']['b']['speed'],
                #             speed_g=self.answer['status']['positions']['g']['speed']
                #         )
                # todo: сделать остановку по тайм-ауту
                #
                # controlX = 0  # failsafe: останавливаемся в случае обрыва связи
                # controlY = 0  # failsafe: останавливаемся в случае обрыва связи
                #
                time.sleep(1 / self.sendFreq)

    def receiver(self):
        with self.lockRX:
            while self.running:
                print('rx')
                print(self.answer)

                answer = self.serialPort.readline()

                if not answer:
                    continue
                if is_json(answer):
                    self.answer = json.loads(answer)
                    print(self.answer)
                    # self.status = ManipulatorStatus(
                    #     pos_a=self.answer["status"]["positions"]["a"]["pos"],
                    #     pos_q1=self.answer['status']['positions']['q1']['pos'],
                    #     pos_q2=self.answer['status']['positions']['q2']['pos'],
                    #     pos_q3=self.answer['status']['positions']['q3']['pos'],
                    #     pos_b=self.answer['status']['positions']['b']['pos'],
                    #     pos_g=self.answer['status']['positions']['g']['pos'],
                    #     speed_a=self.answer["status"]["positions"]["a"]["speed"],
                    #     speed_q1=self.answer['status']['positions']['q1']['speed'],
                    #     speed_q2=self.answer['status']['positions']['q2']['speed'],
                    #     speed_q3=self.answer['status']['positions']['q3']['speed'],
                    #     speed_b=self.answer['status']['positions']['b']['speed'],
                    #     speed_g=self.answer['status']['positions']['g']['speed']
                    # )
                    # todo: сделать остановку по тайм-ауту
                    #
                    # controlX = 0  # failsafe: останавливаемся в случае обрыва связи
                    # controlY = 0  # failsafe: останавливаемся в случае обрыва связи
                    #
                time.sleep(1 / (self.sendFreq * 100))

    def getAnswer(self):
        return self.answer
