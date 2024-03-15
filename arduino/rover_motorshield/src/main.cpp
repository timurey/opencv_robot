// #include <Arduino.h>
#include "ArduinoJson.h"
#include "RoverFocSerial.h"
#include <Wire.h>

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "iot_iconset_16x16.h"

#define VERSION "0.2"

// Serial1 TX	6 pin
// Serial1 RX	7 pin

// Serial2 TX	4 pin
// Serial2 RX	5 pin

// Serial3 TX	10 pin
// Serial3 RX	9 pin

// I2C SDA 8 pin (gpio2)
// I2C SCL 9 pin (gpio3)

#define SERIAL_DEBUG 1

#define DEFAULT_TIMEOUT 300
#define DEFAULT_HOST_TRANSMIT_INTERVAL 1000

SerialFeedback *feedback0;
#define _4WD

#ifdef _4WD
#include "Serial3.h"
SerialFeedback *feedback1;
#endif

#define SCREEN_WIDTH 128    // OLED display width, in pixels
#define SCREEN_HEIGHT 32    // OLED display height, in pixels
#define OLED_RESET -1       // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
unsigned long displayUpdateInterval = 5000;
unsigned long displayUpdatedAt = 0;

int hostTimeout = DEFAULT_TIMEOUT;
int hostTransmitInterval = DEFAULT_HOST_TRANSMIT_INTERVAL;

// json буфер для пакетов от orange pi
StaticJsonDocument<1024> jsondoc;
DynamicJsonDocument answer(1024);

int16_t steer = 0;
int16_t speed = 0;

int16_t speed_l = 0;
int16_t speed_r = 0;

unsigned long timeNow;
unsigned long roverTimeSend = 0;

unsigned long hostTimeRecivie = 0;
unsigned long hostTimeSend = 0;

int roverMaxSpeed = 1000;
int roverMaxSteer = 1000;

RoverHoc *RoverHoc1 = new RoverHoc(&Serial1);
#ifdef _4WD
RoverHoc *RoverHoc2 = new RoverHoc(&Serial3);
#endif

int batteryInfo[2] = {24560, 42960};

int getRoverMaxSpeed(void)
{
  return roverMaxSpeed;
}

int setRoverMaxSpeed(int _roverMaxSpeed)
{
  roverMaxSpeed = _roverMaxSpeed;
#if (SERIAL_DEBUG == 1)
  Serial.print("Set max speed: ");
  Serial.println(roverMaxSpeed);
#endif
  return roverMaxSpeed;
}

int getRoverMaxSteer(void)
{
  return roverMaxSpeed;
}

int setRoverMaxSteer(int _roverMaxSteer)
{
  roverMaxSteer = _roverMaxSteer;
#if (SERIAL_DEBUG == 1)
  Serial.print("Set max steer: ");
  Serial.println(roverMaxSteer);
#endif
  return roverMaxSteer;
}

int getHostTimeout(void)
{
  return hostTimeout;
}

int setHostTimeout(int _timeout)
{
  hostTimeout = _timeout;
  return hostTimeout;
}

int getHostReceive(void)
{
  return hostTimeout;
}

int setHostTransmitInterval(int _interval)
{
  hostTransmitInterval = _interval;
  return hostTransmitInterval;
}

int getHostTransmitInterval(void)
{
  return hostTransmitInterval;
}

void setup()
{
  setHostTimeout(DEFAULT_TIMEOUT);
  setHostTransmitInterval(DEFAULT_HOST_TRANSMIT_INTERVAL);
  setRoverMaxSpeed(1000);
  setRoverMaxSteer(1000);

  Serial.begin(115200);
  delay(500);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS))
  {
    Serial.println("SSD1306 allocation failed");
    for (;;)
      ; // Don't proceed, loop forever
  }

  display.clearDisplay();

  answer["name"] = "Rover motorshield";
  answer["control type"] = "steer";
  answer["module type"] = "chassis";
  answer["version"] = VERSION;
  serializeJson(answer, Serial);

  RoverHoc1->begin();
#ifdef _4WD
  RoverHoc2->begin();
#endif
  pinMode(LED_BUILTIN, OUTPUT);
}

void sendStatus(SerialFeedback *Feedback, const char *boardName)
{
  if (!Feedback) // если данных нет, то выходим
    return;
  answer["status"][boardName]["cmd1"] = Feedback->cmd1;
  answer["status"][boardName]["cmd1"] = Feedback->cmd2;
  answer["status"][boardName]["speedR_meas"] = Feedback->speedR_meas;
  answer["status"][boardName]["speedR_meas"] = Feedback->speedL_meas;
  answer["status"][boardName]["batVoltage"] = Feedback->batVoltage;
  answer["status"][boardName]["boardTemp"] = Feedback->boardTemp;
  answer["status"][boardName]["cmdLed"] = Feedback->cmdLed;
  answer["status"][boardName]["time"] = millis();
}

void setBatteryStatus(SerialFeedback *Feedback, int index)
{
  if (!Feedback) // если данных нет, то выходим
    return;
#ifdef _4WD
  if (index > 1 || index < 0)
  {
    return;
  }
#else
  if (index > 0 || index < 0)
  {
    return;
  }
#endif
  batteryInfo[index] = Feedback->batVoltage * 10;
}
void recieveDataFromRover(void)
{
  feedback0 = RoverHoc1->Receive();
  sendStatus(feedback0, "rear");
  setBatteryStatus(feedback0, 0);
#ifdef _4WD
  feedback1 = RoverHoc2->Receive();
  sendStatus(feedback1, "front");
  setBatteryStatus(feedback1, 1);
#endif
}

void sendDataToRover(void)
{
  if (roverTimeSend > timeNow) // отправляем не чаще 100 ms по умолчанию
    return;
  roverTimeSend = timeNow + ROVER_TIME_SEND;

  RoverHoc1->Send(steer, speed);
#ifdef _4WD
  RoverHoc2->Send(steer, speed);
#endif
#if (SERIAL_DEBUG == 1)
  Serial.print("Send data. Steer: ");
  Serial.print(steer);
  Serial.print(" Speed: ");
  Serial.print(speed);
  Serial.print(" Timestamp: ");
  Serial.println(timeNow);
#endif
}

void recieveDataFromHost(void)
{
  if (Serial.available())
  {
    DeserializationError err = deserializeJson(jsondoc, Serial); // получаем сообщение от orange pi через uart
    if (err == DeserializationError::Ok)                         // если cообщение принято
    {
      // steer = constrain(jsondoc["steer"].as<int>(), getRoverMaxSteer() * -1, getRoverMaxSteer());
      // speed = constrain(jsondoc["speed"].as<int>(), getRoverMaxSpeed() * -1, getRoverMaxSpeed());
      speed_l = constrain(jsondoc["speed_l"].as<int>(), getRoverMaxSteer() * -1, getRoverMaxSteer());
      speed_r = constrain(jsondoc["speed_r"].as<int>(), getRoverMaxSpeed() * -1, getRoverMaxSpeed());
      steer = (speed_l - speed_r) / 2;
      speed = speed_l - steer;

      hostTimeRecivie = timeNow + getHostTimeout();
      // JsonObject root = jsondoc.to<JsonObject>();
      if (jsondoc["configure"])
      {
#if (SERIAL_DEBUG == 1)
        Serial.println("Configure received!");
#endif
        setRoverMaxSpeed(jsondoc["configure"]["maxSpeed"].as<int>());
        setRoverMaxSteer(jsondoc["configure"]["maxSteer"].as<int>());
      }
    }
    else
    {
      while (Serial.available() > 0)
        Serial.read(); // чистим буфер
    }
  }
}
void checkHostTimeout(void) // если не получали данные от хоста в течение таймаута, то останавливаемся
{
  if (hostTimeRecivie < timeNow)
  {
    steer = 0;
    speed = 0;
#if (SERIAL_DEBUG == 1)
    // Serial.println("Host data receive timeout! Stopping rover!");
#endif
    digitalWrite(LED_BUILTIN, LOW);
  }
  else
  {
    digitalWrite(LED_BUILTIN, (timeNow % 2000) < 1000);
  }
}

int calculateBatteryLevel(int voltage, int cellCount)
{
  if (voltage >= cellCount * 4200 )
    return 100;
  if (voltage >= cellCount * 4100)
    return 90;
  if (voltage >= cellCount * 4000)
    return 80;
  if (voltage >= cellCount * 3900)
    return 60;
  if (voltage >= cellCount * 3800)
    return 40;
  if (voltage >= cellCount * 3700)
    return 20;
  if (voltage >= cellCount * 3600)
    return 0;
  return 0;
}

const unsigned char *getBatteryIcon(int percent)
{
  if (percent >= 75)
    return &bat3_icon16x16[0];
  if (percent >= 50)
    return &bat2_icon16x16[0];
  if (percent >= 25)
    return &bat1_icon16x16[0];
  else
    return &bat3_icon16x16[0];
}

void showInfoOnDisplay(void)
{
  display.clearDisplay();
  display.setCursor(0, 4);
  display.setTextColor(1);
  display.setTextSize(1);
  display.print("Front");
  display.drawBitmap(33, 0, getBatteryIcon(calculateBatteryLevel(batteryInfo[0], 10)), 16, 16, 1);
  display.setCursor(50, 4);
  display.printf("%d%% %dmV",calculateBatteryLevel(batteryInfo[0], 10), batteryInfo[0]);
#ifdef _4WD
  display.setCursor(0, 20);
  display.setTextColor(1);
  display.setTextSize(1);
  display.print("Rear");
  display.drawBitmap(33, 16, getBatteryIcon(calculateBatteryLevel(batteryInfo[1], 10)), 16, 16, 1);
  display.setCursor(50, 20);
  display.printf("%d%% %dmV",calculateBatteryLevel(batteryInfo[1], 10), batteryInfo[1]);
#endif
  display.display();
}

void sendDataToHost(void)
{
  if (hostTimeSend > timeNow)
    return;
  hostTimeSend = timeNow + getHostTransmitInterval();
  serializeJson(answer, Serial);
  Serial.println("");
}
void loop()
{
  timeNow = millis();
  recieveDataFromHost();  // получаем данные от хоста
  checkHostTimeout();     // Проверяем, что последние данные получены не позднее таймаута hostTimeout.
  sendDataToHost();       // отправляем данные хосту c интервалом hostTransmitInterval
  recieveDataFromRover(); // Принимаем данные от ровера
  sendDataToRover();      // Отправляем данные роверу
  showInfoOnDisplay();
}
