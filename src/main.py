from flask import Flask, render_template, Response, request
import cv2
import serial
import threading
import time
import argparse
from modules.vision.recognize import get_hands
from modules.vision.cardBoard import doCardBoardImage
from modules.hal.platform import moving, lighting
from modules.osd.osd import OSDModule
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
cameraL = cv2.VideoCapture(1)  # веб камера
cameraR = cv2.VideoCapture(0)  # веб камера

controlX, controlY = 0, 0  # глобальные переменные положения джойстика с web-страницы
screenWidth, screenHeight = 896, 414  # размер экрана пользователя по умолчанию
hands = {}
data = {"state": "do nothing", "battery": 68, "name": "zrak 4wd"}

def list_ports():
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    while len(non_working_ports) < 6: # if there are more than 5 non working ports stop the testing.
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print("Port %s is not working." %dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1
    return available_ports,working_ports,non_working_ports

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    global hands
    global data
    while True:
        # time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frameLeft = cameraL.read()  # Получаем фрейм с камеры\
        success, frameRight= cameraR.read()  # Получаем фрейм с камеры

        if success:
            # frameLeft = cv2.flip(frameLeft, 1)
            # frameRight = cv2.flip(frameRight, 1)
            # frameRight = frameLeft
            frameLeft, hands = get_hands(frameLeft)
            # _, frameLeft = cv2.threshold(frameLeft, 127, 255, cv2.THRESH_BINARY)  # бинаризуем изображение

            # frame = doCardBoardImage(frameLeft, frameRight, screenWidth, screenHeight)
            frame = frameLeft

            frame = osd.doOSD(frame, stereo=False)
            _, buffer = cv2.imencode('.jpg', frame)

            yield (b'--frameLeft\r\n'
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
    global controlX, controlY
    controlX, controlY = float(request.args.get('x')) / 100.0, float(request.args.get('y')) / 100.0
    return '', 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':

    sendFreq = 10  # слать 10 пакетов в секунду
    osd = OSDModule("zrak")
    osd.setBatteryCharging(0, 38)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='127.0.0.1', help="Ip address")
    parser.add_argument('-s', '--serial', type=str, default='/dev/tty.usbmodem101', help="Serial port")
    args = parser.parse_args()

    list_ports()

    def sender():
        """ функция цикличной отправки пакетов по uart """
        global controlX, controlY
        while True:

            moving(controlX, controlY)
            lighting(controlX, controlY)

            # todo: сделать остановку по тайм-ауту

            controlX = 0  # failsafe: останавливаемся в случае обрыва связи
            controlY = 0  # failsafe: останавливаемся в случае обрыва связи

            time.sleep(1 / sendFreq)


    threading.Thread(target=sender, daemon=True).start()  # запускаем тред отправки пакетов по uart с демоном

    app.run(debug=False, host=args.ip, port=args.port)  # запускаем flask приложение
