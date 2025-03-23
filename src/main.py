from flask import Flask, render_template, Response, request
from modules.vision.camera import Camera
from modules.vision.cardBoard import doCardBoardImage
from modules.chassis.chassis import Chassis
from modules.radsens.radsens import Radsens
from modules.manipulator.manipulator import Manipulator
from modules.manipulator.manipulator import ManipulatorConfig

import logging
import cv2
from utils.config_reader import read_config

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

controlX, controlY = 0, 0  # глобальные переменные положения джойстика с web-страницы
screenWidth, screenHeight = 896, 414  # размер экрана пользователя по умолчанию


def shut_down(really):
    if really != "true":
        return
    print("shutting down")
    command = "/usr/bin/sudo /sbin/shutdown -h now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)


def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    global hands
    while True:
        # time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame_left = cameras.ReadLeftCamera()  # Получаем фрейм с камеры
        success, frame_right = cameras.ReadRightCamera()  # Получаем фрейм с камеры

        if success:
            # frame = doCardBoardImage(frame_left, frame_right, screenWidth, screenHeight)
            _, buffer = cv2.imencode('.jpg', frame_left)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """ Генерируем и отправляем изображения с камеры"""
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/screensize')
def getScreenSize():
    global screenWidth, screenHeight
    screenWidth, screenHeight = request.args.get('w'), request.args.get('h')
    return '', 200, {'Content-Type': 'text/plain'}


@app.route('/')
def index():
    """ Крутим html страницу """
    return render_template('index.html')


@app.route('/control')
def control():
    """ Пришел запрос на управления роботом """
    # global controlX, controlY
    chassis.setControl(float(request.args.get('x')) / 100.0, float(request.args.get('y')) / 100.0)

    try:
        l_ = float(request.args.get('l')) / 100.0
        t_ = float(request.args.get('t')) / 100.0
        z_ = float(request.args.get('z')) / 100.0
        c_ = float(request.args.get('c')) / 100.0
        r_ = float(request.args.get('r')) / 100.0
        manipulator.setControl(l_, t_, z_, c_, r_)
    except:
        print(request)

    return '', 200, {'Content-Type': 'text/plain'}


@app.route('/data')
def data():
    pos = {"l": 0, "z": 0, "t": 0, "status": manipulator.answer["status"]}
    """ Пришел запрос на данные с робота """
    # _data = ma.answer

    _data = pos
    return _data, 200, {'Content-Type': 'application/json'}


@app.route('/device')
def device():
    """ Пришел запрос на выключение малинки """
    shut_down(request.args.get('poweroff'))
    return '', 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    # osd = OSDModule("zrak")
    # osd.setBatteryCharging(0, 38)
    # list_ports()
    cameras = Camera(
        read_config('camera', 'stereo'),
        read_config('camera', 'left_camera'),
        read_config('camera', 'right_camera'),
        read_config('camera', 'camera'),
        read_config('camera', 'left_flip'),
        read_config('camera', 'right_flip'),
        read_config('camera', 'flip')
    )
    manipulator_config = ManipulatorConfig(
        serial_port=read_config('manipulator', 'serial'),
        baudrate=115200,

        a_joint_name=read_config('manipulator', 'a_joint_name'),
        a_joint_id=read_config('manipulator', 'a_joint_id', 'int'),
        a_joint_mode=read_config('manipulator', 'a_joint_mode'),
        a_joint_ratio=read_config('manipulator', 'a_joint_ratio', 'float'),
        # a_limit_min=read_config('manipulator', 'a_limit_min', 'int'),
        # a_limit_max=read_config('manipulator', 'a_limit_max', 'int'),
        a_dynamixel_id=read_config('manipulator', 'a_dynamixel_id', 'int'),
        a_dynamixel_torque_limit=read_config('manipulator', 'a_dynamixel_torque_limit', 'int'),
        a_dynamixel_reverse=read_config('manipulator', 'a_dynamixel_reverse'),
        a_moving_speed=read_config('manipulator', 'a_moving_speed', 'int'),

        q1_joint_name=read_config('manipulator', 'q1_joint_name'),
        q1_joint_id=read_config('manipulator', 'q1_joint_id', 'int'),
        q1_joint_mode=read_config('manipulator', 'q1_joint_mode'),
        q1_joint_length=read_config('manipulator', 'q1_joint_length', 'int'),
        q1_limit_min=read_config('manipulator', 'q1_limit_min', 'int'),
        q1_limit_max=read_config('manipulator', 'q1_limit_max', 'int'),
        q1_moving_speed=read_config('manipulator', 'q1_moving_speed', 'int'),

        q1_1_dynamixel_id=read_config('manipulator', 'q1_1_dynamixel_id', 'int'),
        q1_1_dynamixel_min=read_config('manipulator', 'q1_1_dynamixel_min', 'int'),
        # q1_1_dynamixel_max=read_config('manipulator', 'q1_1_dynamixel_max'),
        q1_1_dynamixel_torque_limit=read_config('manipulator', 'q1_1_dynamixel_torque_limit', 'int'),
        q1_1_dynamixel_reverse=read_config('manipulator', 'q1_1_dynamixel_reverse'),
        q1_2_dynamixel_id=read_config('manipulator', 'q1_2_dynamixel_id', 'int'),
        q1_2_dynamixel_min=read_config('manipulator', 'q1_2_dynamixel_min', 'int'),
        # q1_2_dynamixel_max=read_config('manipulator', 'q1_2_dynamixel_max'),
        q1_2_dynamixel_torque_limit=read_config('manipulator', 'q1_2_dynamixel_torque_limit', 'int'),
        q1_2_dynamixel_reverse=read_config('manipulator', 'q1_2_dynamixel_reverse'),

        q2_joint_name=read_config('manipulator', 'q2_joint_name'),
        q2_joint_id=read_config('manipulator', 'q2_joint_id', 'int'),
        q2_joint_mode=read_config('manipulator', 'q2_joint_mode'),
        q2_joint_length=read_config('manipulator', 'q2_joint_length', 'int'),
        q2_limit_min=read_config('manipulator', 'q2_limit_min', 'int'),
        q2_limit_max=read_config('manipulator', 'q2_limit_max', 'int'),

        q2_1_dynamixel_id=read_config('manipulator', 'q2_1_dynamixel_id'),
        q2_1_dynamixel_min=read_config('manipulator', 'q2_1_dynamixel_min', 'int'),
        q2_moving_speed=read_config('manipulator', 'q2_moving_speed', 'int'),
        # q2_dynamixel_max=read_config('manipulator', 'q2_dynamixel_max'),
        q2_1_dynamixel_torque_limit=read_config('manipulator', 'q2_1_dynamixel_torque_limit', 'int'),
        q2_1_dynamixel_reverse=read_config('manipulator', 'q2_1_dynamixel_reverse'),
        q2_2_dynamixel_id=read_config('manipulator', 'q2_2_dynamixel_id', 'int'),
        # q2_2_dynamixel_min=read_config('manipulator', 'q2_2_dynamixel_min'),
        # q2_2_moving_speed=read_config('manipulator', 'q2_2_moving_speed', 'int'),
        # q2_dynamixel_max=read_config('manipulator', 'q2_dynamixel_max'),
        q2_2_dynamixel_torque_limit=read_config('manipulator', 'q2_2_dynamixel_torque_limit', 'int'),
        q2_2_dynamixel_reverse=read_config('manipulator', 'q2_2_dynamixel_reverse'),
        q2_2_slave=read_config('manipulator', 'q2_2_slave'),
        q2_2_ratio=read_config('manipulator', 'q2_2_ratio'),

        q3_joint_name=read_config('manipulator', 'q3_joint_name'),
        q3_joint_id=read_config('manipulator', 'q3_joint_id'),
        q3_joint_mode=read_config('manipulator', 'q3_joint_mode'),
        q3_joint_length=read_config('manipulator', 'q3_joint_length', 'int'),
        q3_limit_min=read_config('manipulator', 'q3_limit_min', 'int'),
        q3_limit_max=read_config('manipulator', 'q3_limit_max', 'int'),
        q3_dynamixel_id=read_config('manipulator', 'q3_dynamixel_id', 'int'),
        q3_dynamixel_min=read_config('manipulator', 'q3_dynamixel_min', 'int'),
        q3_moving_speed=read_config('manipulator', 'q3_moving_speed', 'int'),
        # q3_dynamixel_max=read_config('manipulator', 'q3_dynamixel_max'),
        q3_dynamixel_torque_limit=read_config('manipulator', 'q3_dynamixel_torque_limit', 'int'),
        q3_dynamixel_reverse=read_config('manipulator', 'q3_dynamixel_reverse'),

        b_joint_name=read_config('manipulator', 'b_joint_name'),
        b_joint_id=read_config('manipulator', 'b_joint_id', 'int'),
        b_joint_mode=read_config('manipulator', 'b_joint_mode'),
        b_joint_ratio=read_config('manipulator', 'b_joint_ratio', 'float'),
        b_limit_min=read_config('manipulator', 'b_limit_min', 'int'),
        b_limit_max=read_config('manipulator', 'b_limit_max', 'int'),
        b_moving_speed=read_config('manipulator', 'b_moving_speed', 'int'),

        b_dynamixel_id=read_config('manipulator', 'b_dynamixel_id', 'int'),
        b_dynamixel_torque_limit=read_config('manipulator', 'b_dynamixel_torque_limit', 'int'),
        b_dynamixel_reverse=read_config('manipulator', 'b_dynamixel_reverse'),

        g_joint_name=read_config('manipulator', 'g_joint_name'),
        g_joint_id=read_config('manipulator', 'g_joint_id', 'int'),
        g_joint_mode=read_config('manipulator', 'g_joint_mode'),
        g_joint_length=read_config('manipulator', 'g_joint_length', 'int'),
        g_limit_min=read_config('manipulator', 'g_limit_min', 'int'),
        g_limit_max=read_config('manipulator', 'g_limit_max', 'int'),
        g_moving_speed=read_config('manipulator', 'g_moving_speed', 'int'),

        g_dynamixel_id=read_config('manipulator', 'g_dynamixel_id', 'int'),
        g_dynamixel_min=read_config('manipulator', 'g_dynamixel_min', 'int'),
        # g_dynamixel_max=read_config('manipulator', 'g_dynamixel_max'),
        g_dynamixel_torque_limit=read_config('manipulator', 'g_dynamixel_torque_limit', 'int'),
        g_dynamixel_reverse=read_config('manipulator', 'g_dynamixel_reverse')
    )
    chassis = Chassis(read_config('chassis', 'serial'), 115200, read_config('chassis', 'type'))

    chassis.setMaxAbsSpeed(read_config('chassis', 'maxAbsSpeed'))
    chassis.start()

    manipulator = Manipulator(manipulator_config)
    manipulator.start()

    # radsens = Radsens(read_config('radsens', 'serial'), 115200)
    # radsens.start()
    # radsens.hvGeneratorStart()
    print(
        'Running webserver on http://{0}:{1}'.format(read_config('webserver', 'ip'), read_config('webserver', 'port')))

    # запускаем flask приложение
    app.run(debug=False, host=read_config('webserver', 'ip'), port=read_config('webserver', 'port'))
