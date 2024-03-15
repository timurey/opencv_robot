#include <Arduino.h>
#include <Wire.h>
#include "CG_RadSens.h"   //ClimateGuard Radsense https://github.com/climateguard/RadSens
#include "ArduinoJson.h"  //https://arduinojson.org/?utm_source=meta&utm_medium=library.properties

#define VERSION "0.1"

#define DEFAULT_TIMEOUT 300
#define DEFAULT_HOST_TRANSMIT_INTERVAL 1000


int hostTimeout = DEFAULT_TIMEOUT;
int hostTransmitInterval = DEFAULT_HOST_TRANSMIT_INTERVAL;


unsigned long timeNow;

unsigned long hostTimeRecivie = 0;
unsigned long hostTimeSend = 0;


//SDA pin4 on rp2040 zero
//SDl pin5 on rp2040 zero

CG_RadSens radSens(RS_DEFAULT_I2C_ADDRESS); /*Constructor of the class ClimateGuard_RadSens1v2,
                                                           sets the address parameter of I2C sensor.
                                                           Default address: 0x66.*/

int getHostTimeout(void) {
  return hostTimeout;
}

int setHostTimeout(int _timeout) {
  hostTimeout = _timeout;
  return hostTimeout;
}

int getHostReceive(void) {
  return hostTimeout;
}

int setHostTransmitInterval(int _interval) {
  hostTransmitInterval = _interval;
  return hostTransmitInterval;
}

int getHostTransmitInterval(void) {
  return hostTransmitInterval;
}

// json буфер для пакетов от orange pi
StaticJsonDocument<1024> jsondoc;
DynamicJsonDocument answer(1024);

void setup() {
  Serial.begin(115200);
  Wire.begin();  // This function initializes the Wire library
  delay(1000);
  while (!radSens.init()) /*Initializates function and sensor connection. Returns false if the sensor is not connected to the I2C bus.*/
  {
    Serial.println("Sensor wiring error!");
    delay(1000);
  }

  // Serial.println("HW generator example:\n");

  // Feedback->hvGeneratorState = radSens.getHVGeneratorState(); /*Returns state of high-voltage voltage Converter.
  //                                                          If return true -> on
  //                                                          If return false -> off or sensor isn't conneted*/

  // Serial.print("\n\t HV generator state: ");
  // Serial.println(Feedback->hvGeneratorState);
  // Serial.println("\t setHVGeneratorState(false)... ");

  // radSens.setHVGeneratorState(false); /*Set state of high-voltage voltage Converter.
  //                                       if setHVGeneratorState(true) -> turn on HV generator
  //                                       if setHVGeneratorState(false) -> turn off HV generator*/

  // Feedback->hvGeneratorState = radSens.getHVGeneratorState();
  // Serial.print("\t HV generator state: ");
  // Serial.println(Feedback->hvGeneratorState);
  // Serial.println("\t setHVGeneratorState(true)... ");

  // radSens.setHVGeneratorState(true);

  // Feedback->hvGeneratorState = radSens.getHVGeneratorState();
  // Serial.print("\t HV generator state: ");
  // Serial.println(Feedback->hvGeneratorState);
  // Serial.println("-------------------------------------");
  // Serial.println("LED indication control example:\n");

  // Feedback->ledState = radSens.getLedState(); /*Returns state of LED indicator.
  //                                                          If return true -> on
  //                                                          If return false -> off*/

  // Serial.print("\n\t LED indication state: ");
  // Serial.println(Feedback->ledState);
  // Serial.println("\t turn off LED indication... ");

  // radSens.setLedState(false); /*Set state of LED indicator.
  //                                       if setHVGeneratorState(true) -> turn on LED indicator
  //                                       if setHVGeneratorState(false) -> turn off LED indicator*/
  // Feedback->ledState = radSens.getLedState();
  // Serial.print("\t LED indication state: ");
  // Serial.println(Feedback->ledState);
  // Serial.println("\t turn on led indication... ");

  // radSens.setLedState(true);

  // Feedback->ledState = radSens.getLedState();
  // Serial.print("\t LED indication state: ");
  // Serial.print(Feedback->ledState);
  // Serial.println("\n-------------------------------------");
  // delay(5000);

  answer["name"] = "Rover radsense shield";
  // answer["control type"] = "steer";
  // answer["module type"] = "chassis";
  answer["version"] = VERSION;
  serializeJson(answer, Serial);
}

void sendStatus() {

  answer["status"]["radsens"]["intensyStatic"] = radSens.getRadIntensyStatic();
  answer["status"]["radsens"]["intensyDynamic"] = radSens.getRadIntensyDynamic();
  answer["status"]["radsens"]["sensorChipId"] = "0x"+String(radSens.getChipId(), HEX);
  answer["status"]["radsens"]["firwareVersion"] = radSens.getFirmwareVersion();
  answer["status"]["radsens"]["pulseCount"] = radSens.getNumberOfPulses();
  // answer["status"]["radsens"]["adressI2C"] = "0x"+String(radSens.getSensorAddress(), HEX);
  answer["status"]["radsens"]["HVGeneratorState"] = radSens.getHVGeneratorState();
  answer["status"]["radsens"]["sensivity"] = radSens.getSensitivity();
  answer["status"]["radsens"]["ledState"] = radSens.getLedState();
  answer["status"]["radsens"]["time"] = millis();
}

void recieveDataFromHost(void) {
  if (Serial.available()) {
    DeserializationError err = deserializeJson(jsondoc, Serial);  // получаем сообщение от orange pi через uart
    if (err == DeserializationError::Ok)                          // если cообщение принято
    {

      hostTimeRecivie = timeNow + getHostTimeout();
      // JsonObject root = jsondoc.to<JsonObject>();
      if (jsondoc["configure"]) {
#if (SERIAL_DEBUG == 1)
        Serial.println("Configure received!");
#endif
        String setLedState, setHVGeneratorState, setSensitivity;
        setLedState = jsondoc["configure"]["setLed"].as<String>();
        setHVGeneratorState = jsondoc["configure"]["setHVGeneratorState"].as<String>();
        setSensitivity = jsondoc["configure"]["setSensitivity"].as<String>();
        if (!setLedState.equalsIgnoreCase("null")) {
          if (setLedState.equalsIgnoreCase("true")) {
            radSens.setLedState(true);
            Serial.println("Led ON");
          } else if (setLedState.equalsIgnoreCase("false")) {
            radSens.setLedState(false);
            Serial.println("Led OFF");
          }
        }
        if (!setHVGeneratorState.equalsIgnoreCase("null")) {
          if (setHVGeneratorState.equalsIgnoreCase("true")) {
            radSens.setHVGeneratorState(true);
            Serial.println("HVGen ON");
          } else if (setHVGeneratorState.equalsIgnoreCase("false")) {
            radSens.setHVGeneratorState(false);
            Serial.println("HVGen OFF");
          }
        }

        if (!setSensitivity.equalsIgnoreCase("null")) {
          Serial.print("setSensitivity.length()");
          Serial.print(setSensitivity);
          Serial.println(setSensitivity.length());
          uint16_t sensitivity = jsondoc["configure"]["setSensitivity"].as<int>();
          radSens.setSensitivity(sensitivity);
          Serial.print("Set sensivity to ");
          Serial.println(sensitivity);
        }
      }
    } else {
      while (Serial.available() > 0)
        Serial.read();  // чистим буфер
    }
  }
}

void sendDataToHost(void) {
  if (hostTimeSend > timeNow)
    return;
  hostTimeSend = timeNow + getHostTransmitInterval();
  sendStatus();
  serializeJson(answer, Serial);
  Serial.println("");
}
void loop() {

  timeNow = millis();
  recieveDataFromHost();  // получаем данные от хоста
  sendDataToHost();       // отправляем данные хосту c интервалом hostTransmitInterval
  // showInfoOnDisplay();

  delay(2000);
}
