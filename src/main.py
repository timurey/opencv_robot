from flask import Flask, render_template, Response, request
from modules.vision.camera import Camera
from modules.vision.cardBoard import doCardBoardImage
from modules.chassis.chassis import Chassis

import logging
import cv2
from utils.config_reader import read_config

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

controlX, controlY = 0, 0  # глобальные переменные положения джойстика с web-страницы
screenWidth, screenHeight = 896, 414  # размер экрана пользователя по умолчанию



def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    global hands
    while True:
        # time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame_left = cameras.ReadLeftCamera()  # Получаем фрейм с камеры
        success, frame_right = cameras.ReadRightCamera()  # Получаем фрейм с камеры

        if success:

            frame = doCardBoardImage(frame_left, frame_right, screenWidth, screenHeight)
            _, buffer = cv2.imencode('.jpg', frame)

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
    # controlX, controlY = float(request.args.get('x')) / 100.0, float(request.args.get('y')) / 100.0
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

    chassis = Chassis(read_config('chassis', 'serial'), 115200, read_config('chassis', 'type'))
    chassis.setMaxAbsSpeed(read_config('chassis', 'maxAbsSpeed'))
    chassis.start()

    print('Running webserver on http://{0}:{1}'.format(read_config('webserver', 'ip'), read_config('webserver', 'port')))

    # запускаем flask приложение
    app.run(debug=False, host=read_config('webserver', 'ip'), port=read_config('webserver', 'port'))
