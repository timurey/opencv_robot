#ifndef RoverFoc_h
#define RoverFoc_h

#include <Arduino.h>

typedef struct
{
  uint16_t start;
  int16_t steer;
  int16_t speed;
  uint16_t checksum;
} SerialCommand;

typedef struct
{
  uint16_t start;
  int16_t cmd1;
  int16_t cmd2;
  int16_t speedR_meas;
  int16_t speedL_meas;
  int16_t batVoltage;
  int16_t boardTemp;
  uint16_t cmdLed;
  uint16_t checksum;
} SerialFeedback;

// ########################## DEFINES ##########################
#define HOVER_SERIAL_BAUD 115200 // [-] Baud rate for HoverSerial (used to communicate with the hoverboard)
#define START_FRAME 0xABCD       // [-] Start frme definition for reliable serial communication
#define ROVER_TIME_SEND 100      // [ms] Sending time interval

class RoverHoc
{
public:
  RoverHoc(Uart *serial);
  void Send(int16_t uSteer, int16_t uSpeed);
  void begin();
  SerialFeedback *Receive(void);

private:
  SerialCommand Command;
  Uart *RoverHocSerial;

  uint8_t idx = 0;        // Index for new data pointer
  uint16_t bufStartFrame; // Buffer Start Frame
  byte *p;                // Pointer declaration for the new received data
  byte incomingByte;
  byte incomingBytePrev;

  SerialFeedback Feedback;
  SerialFeedback NewFeedback;
};

#endif