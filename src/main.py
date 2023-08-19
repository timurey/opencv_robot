from flask import Flask, render_template, Response, request
import cv2
import threading
import time
import argparse
from modules.vision.recognize import get_hands
from modules.hal.platform import moving
from modules.osd.osd import OSDModule
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
camera = cv2.VideoCapture(1)  # веб камера

controlX, controlY = 0, 0  # глобальные переменные положения джойстика с web-страницы
hands = {}
data = {"state": "do nothing", "battery": 68, "name": "zrak 4wd"}

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    global hands
    global data
    while True:
        # time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv2.flip(frame, 1)
            frame, hands = get_hands(frame)
            # _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)  # бинаризуем изображение
            frame = osd.doOSD(frame)
            _, buffer = cv2.imencode('.jpg', frame)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """ Генерируем и отправляем изображения с камеры"""
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
    parser.add_argument('-s', '--serial', type=str, default='/dev/ttyUSB0', help="Serial port")
    args = parser.parse_args()


    def sender():
        """ функция цикличной отправки пакетов по uart """
        global controlX, controlY
        while True:
            moving(controlX, controlY)

            # todo: сделать остановку по тайм-ауту

            controlX = 0  # failsafe: останавливаемся в случае обрыва связи
            controlY = 0  # failsafe: останавливаемся в случае обрыва связи

            time.sleep(1 / sendFreq)


    threading.Thread(target=sender, daemon=True).start()  # запускаем тред отправки пакетов по uart с демоном

    app.run(debug=False, host=args.ip, port=args.port)  # запускаем flask приложение
