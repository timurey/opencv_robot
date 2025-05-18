#define SERIAL_BUFFER_SIZE 2048
#include <DynamixelSDK.h> //install OpenCM9.04 1.5.1 board support first

#include "ArduinoJson.h"
#include <string.h>
#include <stdio.h>

// Control table address (ax12)
#define ADDR_12X_TORQUE_ENABLE 24  // Control table address is different in Dynamixel model
#define ADDR_12X_LED_ENABLE 25     //
#define ADDR_12X_GOAL_POSITION 30
#define ADDR_12X_MOVING_SPEED 32
#define ADDR_12X_TORQUE_LIMIT 34
#define ADDR_12X_PRESENT_POSITION 36
#define ADDR_12X_PRESENT_SPEED 38
#define ADDR_12X_PRESENT_LOAD 40
#define ADDR_12X_MOVING 46

#define ADDR_12X_CW_ANGLE_LIMIT 6
#define ADDR_12X_CCW_ANGLE_LIMIT 8
#define ADDR_12X_MAX_TORQUE 14
#define ADDR_12X_STATUS_RETURN_LEVEL 16
#define COMMON_WRONG_JOINT -4001
#define COMMON_WRONG_JOINT_TYPE -4002

// Protocol version
#define PROTOCOL_VERSION 1.0  // See which protocol version is used in the Dynamixel

// Default setting
#define BAUDRATE 1000000
#define DEVICENAME "1"  // Check which port is being used on your controller \
                        // ex) Windows: "COM1"   Linux: "/dev/ttyUSB0"

#define TORQUE_ENABLE 1                 // Value for enabling the torque
#define TORQUE_DISABLE 0                // Value for disabling the torque
#define DXL_MINIMUM_POSITION_VALUE 100  // Dynamixel will rotate between this value
#define DXL_MAXIMUM_POSITION_VALUE 900  // and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
#define DXL_MOVING_STATUS_THRESHOLD 20  // Dynamixel moving status threshold

#define ESC_ASCII_VALUE 0x1b

#define DYNAMIXEL_MAX_ID 10
#define JOINT_COUNT 6

#define GPP (300.0 / 1024.0)
#define PPG (1024.0 / 300.0)

uint8_t id[DYNAMIXEL_MAX_ID];  // = { 1, 2, 3, 4, 5, 6, 7 };
uint8_t status[DYNAMIXEL_MAX_ID];

int16_t current_position[DYNAMIXEL_MAX_ID];
int16_t target_position[DYNAMIXEL_MAX_ID];
int dx_joint_mode[DYNAMIXEL_MAX_ID];  // = { 0, 1, 1, 1, 1, 0, 1 };  //0 - wheel, 1 - joint

int16_t cw_angle_limit[DYNAMIXEL_MAX_ID];   // =         { 0,    223, 264, 58,   313, 0,   314 };
int16_t ccw_angle_limit[DYNAMIXEL_MAX_ID];  // =         { 1023, 449, 487, 350,  313, 0,   817 };
int16_t moving_speed[DYNAMIXEL_MAX_ID];     // =         { 10,   100, 100, 100,  100, 50,  50 };
int16_t torque_limit[DYNAMIXEL_MAX_ID];     // =         { 512,  512, 512, 900,  512, 512, 512 };
bool reverse[DYNAMIXEL_MAX_ID];
bool slave[DYNAMIXEL_MAX_ID];
float dx_ratio[DYNAMIXEL_MAX_ID];

bool joint_mode_is_joint[JOINT_COUNT];  // = { 0, 1, 1, 1, 0, 1 };  //0 - wheel mode, 1 - joint mode
uint joint_dx_id[JOINT_COUNT][2];       // = { { 1 }, { 2, 3 }, { 4 }, { 5 }, { 6 }, { 7 } };
int joint_dx_reverse[JOINT_COUNT][2];   // = { { 0 }, { 1, 0 }, { 0 }, { 1 }, { 0 }, { 0 } };
int joint_limits[JOINT_COUNT][2];       //[0,90]
float joint_ratio[JOINT_COUNT];

char jointName[JOINT_COUNT][3];
bool jointsIsConfigured = false;

JsonDocument jsonIn;
JsonDocument answer;

#define DEFAULT_TIMEOUT 300
#define DEFAULT_HOST_TRANSMIT_INTERVAL 500


int hostTimeout = DEFAULT_TIMEOUT;
int hostTransmitInterval = DEFAULT_HOST_TRANSMIT_INTERVAL;

unsigned long timeNow, hostTimeRecivie = 0, hostTimeSend = 0;



dynamixel::PortHandler *portHandler;

// Initialize PacketHandler instance
// Set the protocol version
// Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
dynamixel::PacketHandler *packetHandler;



int16_t getPresentPositionDX(uint8_t id) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  uint16_t dxl_present_position = 0;
  // Serial.printf("ID[\%03d] setting moving_speed to %d... ", id, moving_speed);

  dxl_comm_result = packetHandler->read2ByteTxRx(portHandler, id, ADDR_12X_PRESENT_POSITION, (uint16_t *)&dxl_present_position, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    // Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    // Serial.printf("error: %d\n", dxl_error);

  } else {
    // Serial.printf("success\n");
  }
  return dxl_present_position;
}
int16_t getPresentSpeedDX(uint8_t id) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  uint16_t dxl_present_speed = 0;
  // Serial.printf("ID[\%03d] setting moving_speed to %d... ", id, moving_speed);

  dxl_comm_result = packetHandler->read2ByteTxRx(portHandler, id, ADDR_12X_PRESENT_SPEED, (uint16_t *)&dxl_present_speed, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    // Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    // Serial.printf("error: %d\n", dxl_error);

  } else {
    // Serial.printf("success\n");
  }
  if (dxl_present_speed >= 1024) { dxl_present_speed -= 1024; }
  return dxl_present_speed;
}
int16_t getPresentLoadDX(uint8_t id) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  uint16_t dxl_present_load = 0;
  // Serial.printf("ID[\%03d] setting moving_speed to %d... ", id, moving_speed);

  dxl_comm_result = packetHandler->read2ByteTxRx(portHandler, id, ADDR_12X_PRESENT_LOAD, (uint16_t *)&dxl_present_load, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);

  } else {
  }
  if (dxl_present_load >= 1024) { dxl_present_load -= 1024; }

  return dxl_present_load;
}

bool getIsMovingDX(uint8_t id) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  uint8_t dxl_moving = 0;

  dxl_comm_result = packetHandler->read1ByteTxRx(portHandler, id, ADDR_12X_MOVING, (uint8_t *)&dxl_moving, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);

  } else {
  }
  Serial.printf("ID[\%03d] getting moving state %d... \n", id, dxl_moving);
  return (dxl_moving > 0);
}

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


int setLedDX(int id, uint8_t led) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting led to %d... ", id, led);
  dxl_comm_result = packetHandler->write2ByteTxRx(portHandler, id, ADDR_12X_LED_ENABLE, led, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
}

int set_status_return_level(int id, uint8_t level) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting status_return_level to %d... ", id, level);
  dxl_comm_result = packetHandler->write1ByteTxRx(portHandler, id, ADDR_12X_STATUS_RETURN_LEVEL, level, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
}

int set_cw_angle_limit(int id, uint16_t set_cw_angle_limit) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting set_cw_angle_limit to %d... ", id, set_cw_angle_limit);
  dxl_comm_result = packetHandler->write2ByteTxRx(portHandler, id, ADDR_12X_CW_ANGLE_LIMIT, set_cw_angle_limit, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
}


int set_ccw_angle_limit(int id, uint16_t set_ccw_angle_limit) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting set_ccw_angle_limit to %d... ", id, set_ccw_angle_limit);
  dxl_comm_result = packetHandler->write2ByteTxRx(portHandler, id, ADDR_12X_CCW_ANGLE_LIMIT, set_ccw_angle_limit, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
}

int set_moving_speed(int id, uint16_t _moving_speed) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting moving_speed to %d... ", id, _moving_speed);
  dxl_comm_result = packetHandler->write2ByteTxRx(portHandler, id, ADDR_12X_MOVING_SPEED, _moving_speed, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
  moving_speed[id] = _moving_speed;
}

int set_torque_limit(int id, uint16_t torque_limit) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting torque_limit to %d... ", id, torque_limit);
  dxl_comm_result = packetHandler->write2ByteTxRx(portHandler, id, ADDR_12X_TORQUE_LIMIT, torque_limit, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
}

int set_goal_position(int id, uint16_t goal_position) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  Serial.printf("ID[\%03d] setting goal_position to %d... ", id, goal_position);
  dxl_comm_result = packetHandler->write2ByteTxRx(portHandler, id, ADDR_12X_GOAL_POSITION, goal_position, &dxl_error);

  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("result: %d\n", dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("error: %d\n", dxl_error);

  } else {
    Serial.printf("success\n");
  }
  target_position[id] = goal_position;
}

int set_goal_position_with_speed(int id, uint16_t goal_position, uint16_t moving_speed) {
  set_moving_speed(id, moving_speed);
  set_goal_position(id, goal_position);
}

int get_joint_position(int jointIndex) {

  int minJointLimit = joint_limits[jointIndex][0];
  int maxJointLimit = joint_limits[jointIndex][1];

  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];


  bool isReversed1 = reverse[dxID1];
  bool isReversed2 = reverse[dxID2];


  uint16_t cwDxLimit1 = cw_angle_limit[dxID1];
  uint16_t cwDxLimit2 = cw_angle_limit[dxID2];


  uint16_t ccwDxLimit1 = ccw_angle_limit[dxID1];
  uint16_t ccwDxLimit2 = ccw_angle_limit[dxID2];


  int deg, deg_, deg1, deg2;

  if (dxID1 > 0) {
    deg1 = getPresentPositionDX(dxID1) * GPP;
    // Serial.printf("Pos[\%03d] in degrees: %hu\n", dxID1, deg1);

    if (!isReversed1) {
      //normal
      deg = deg1 + minJointLimit - cwDxLimit1;
      // Serial.print("deg(1) in degrees:");
      // Serial.println(deg);
    } else {
      //reversed
      deg = ccwDxLimit1 - deg1 - minJointLimit;
      // Serial.printf("deg(1)(R) in degrees: %d\n", deg);
    }
  }
  if (slave[dxID2]) {
    return (deg);
  }
  if (dxID2 > 0) {
    deg2 = getPresentPositionDX(dxID2) * GPP;
    // Serial.printf("Pos[\%03d] in degrees: %hu\n", dxID2, deg2);

    if (!isReversed2) {
      //normal
      deg_ = deg2 + minJointLimit - cwDxLimit2;
      // Serial.printf("deg(2) in degrees: %d\n", deg_);
    } else {
      //reversed
      deg_ = ccwDxLimit2 - deg2 - minJointLimit;
      // Serial.printf("deg(2)(R) in degrees: %d\n", deg_);
    }
    // Serial.println(((deg + deg_) / 2));
    return ((deg + deg_) / 2);

  } else {
    // Serial.println(deg);
    return (deg);
  }
}

int getJointIndexByName(char *name) {
  int index = 0;
  for (index = 0; index < JOINT_COUNT; index++) {
    if (strcmp(name, jointName[index]) == 0) {
      return index;
    }
  }
  return -1;
}

int get_joint_speed(int jointIndex) {

  int minJointLimit = joint_limits[jointIndex][0];
  int maxJointLimit = joint_limits[jointIndex][1];

  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];


  bool isReversed1 = reverse[dxID1];
  bool isReversed2 = reverse[dxID2];


  uint16_t cwDxLimit1 = cw_angle_limit[dxID1];
  uint16_t cwDxLimit2 = cw_angle_limit[dxID2];


  uint16_t ccwDxLimit1 = ccw_angle_limit[dxID1];
  uint16_t ccwDxLimit2 = ccw_angle_limit[dxID2];


  int deg, deg_, speed1, speed2;

  if (dxID1 > 0) {
    speed1 = getPresentSpeedDX(dxID1) * joint_ratio[jointIndex];
  }
  if (dxID2 > 0) {
    speed2 = getPresentSpeedDX(dxID2) * joint_ratio[jointIndex];

    return ((speed1 + speed2) / 2);

  } else {
    // Serial.println(deg);
    return (speed1);
  }
}

int get_joint_load(int jointIndex) {

  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];
  int load1, load2;

  if (dxID1 > 0) {
    load1 = getPresentLoadDX(dxID1);
  }
  if (dxID2 > 0) {
    load2 = getPresentLoadDX(dxID2);
    return (((load1 + load2) / 2) * 100 / 1023);
  } else {
    return ((load1 * 100) / 1023);
  }
}

uint16_t DxToDeg(uint16_t value) {
  Serial.print(value);
  Serial.print(" tug is ");
  Serial.print((uint16_t)(value * GPP));
  Serial.println(" deg");
  return (uint16_t)(value * GPP);
}

uint16_t DegToDx(uint16_t degrees) {
  return (uint16_t)(degrees * PPG);
}
int tugrikToDeg(int jointIndex, uint16_t tugrik) {
  int minJointLimit = joint_limits[jointIndex][0];
  int maxJointLimit = joint_limits[jointIndex][1];

  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];

  bool isReversed1 = reverse[dxID1];
  bool isReversed2 = reverse[dxID2];

  uint16_t cwDxLimit1 = cw_angle_limit[dxID1];
  uint16_t cwDxLimit2 = cw_angle_limit[dxID2];

  uint16_t ccwDxLimit1 = ccw_angle_limit[dxID1];
  uint16_t ccwDxLimit2 = ccw_angle_limit[dxID2];

  uint16_t angle = 0;

  Serial.printf("jointIndex: %d, minJointLimit: %d, maxJointLimit: %d, dxID1: %d, dxID2: %d, cwDxLimit1: %d, cwDxLimit2: %d, cwwDxLimit1: %d, cwwDxLimit2: %d, reverse: %s \n", jointIndex, minJointLimit, maxJointLimit, dxID1, dxID2, cwDxLimit1, cwDxLimit2, ccwDxLimit1, ccwDxLimit2, isReversed1 ? "true" : "false");
  if (isReversed1 != true) {
    Serial.println("Calculate for normal");
    angle = minJointLimit + DxToDeg(tugrik - cwDxLimit1);
  } else {
    Serial.println("Calculate for Reverse");

    angle = minJointLimit + DxToDeg(ccwDxLimit1 - tugrik);
  }
  return (angle);
}

int degToTugrik(int jointIndex, int degree) {
  uint16_t tugrik1, tugrik2;
  int minJointLimit = joint_limits[jointIndex][0];
  int maxJointLimit = joint_limits[jointIndex][1];

  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];

  bool isReversed1 = reverse[dxID1];
  bool isReversed2 = reverse[dxID2];

  uint16_t cwDxLimit1 = cw_angle_limit[dxID1];
  uint16_t cwDxLimit2 = cw_angle_limit[dxID2];

  uint16_t ccwDxLimit1 = ccw_angle_limit[dxID1];
  uint16_t ccwDxLimit2 = ccw_angle_limit[dxID2];

  Serial.printf("jointIndex: %d, minJointLimit: %d, maxJointLimit: %d, dxID1: %d, dxID2: %d, cwDxLimit1: %d, cwDxLimit2: %d, cwwDxLimit1: %d, cwwDxLimit2: %d, reverse: %s \n", jointIndex, minJointLimit, maxJointLimit, dxID1, dxID2, cwDxLimit1, cwDxLimit2, ccwDxLimit1, ccwDxLimit2, isReversed1 ? "true" : "false");
  if (dxID1 > 0) {

    if (isReversed1 != true) {
      Serial.println("Calculate for normal");
      tugrik1 = cwDxLimit1 + DegToDx(degree);
    } else {
      Serial.println("Calculate for Reverse");
      tugrik1 = cwDxLimit1 + DegToDx(maxJointLimit - minJointLimit - degree);
    }
  }

  if (dxID2 > 0) {
    if (isReversed2 != true) {
      Serial.println("Calculate for normal");
      tugrik2 = cwDxLimit2 + DegToDx(degree);
    } else {
      Serial.println("Calculate for Reverse");
      tugrik2 = cwDxLimit2 + DegToDx(maxJointLimit - minJointLimit - degree);
    }
  }
  Serial.printf("tugrik1 %d, tugrik2: %d\n", tugrik1, tugrik2);

  return (tugrik1);
}

void moveJoint(uint jointIndex, int deg) {
  Serial.print("Moving joint ");
  Serial.print(jointIndex);
  Serial.print(" to: ");
  Serial.println(deg);
  uint16_t tugrik1, tugrik2;
  int minJointLimit = joint_limits[jointIndex][0];
  int maxJointLimit = joint_limits[jointIndex][1];
  Serial.print("minJointLimit: ");
  Serial.print(minJointLimit);
  Serial.print(" maxJointLimit: ");
  Serial.println(maxJointLimit);
  if (deg < minJointLimit) {
    Serial.print("New pos: ");
    deg = minJointLimit;
    Serial.println(deg);
  }
  if (deg > maxJointLimit) {
    Serial.print("New pos: ");
    deg = maxJointLimit;
    Serial.println(deg);
  }
  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];
  Serial.print("dxID1: ");
  Serial.print(dxID1);
  Serial.print(" dxID2: ");
  Serial.println(dxID2);

  bool isReversed1 = reverse[dxID1];
  bool isReversed2 = reverse[dxID2];
  Serial.print("isReversed1: ");
  Serial.print(isReversed1);
  Serial.print(" isReversed2: ");
  Serial.println(isReversed2);

  uint16_t cwDxLimit1 = cw_angle_limit[dxID1];
  uint16_t cwDxLimit2 = cw_angle_limit[dxID2];
  Serial.print("cwDxLimit1: ");
  Serial.print(cwDxLimit1);
  Serial.print(" cwDxLimit2: ");
  Serial.println(cwDxLimit2);

  uint16_t ccwDxLimit1 = ccw_angle_limit[dxID1];
  uint16_t ccwDxLimit2 = ccw_angle_limit[dxID2];
  Serial.print("ccwDxLimit1: ");
  Serial.print(ccwDxLimit1);
  Serial.print(" ccwDxLimit2: ");
  Serial.println(ccwDxLimit2);

  int deg1, deg2;
  // Serial.printf("jointIndex: %d, minJointLimit: %d, maxJointLimit: %d, dxID1: %d, dxID2: %d, cwDxLimit1: %d, cwDxLimit2: %d, cwwDxLimit1: %d, cwwDxLimit2: %d, reverse: %s \n", jointIndex, minJointLimit, maxJointLimit, dxID1, dxID2, cwDxLimit1, cwDxLimit2, ccwDxLimit1, ccwDxLimit2, isReversed1 ? "true" : "false");
  // Serial.printf("Go to %d\n", deg);
  if (dxID1 > 0) {
    if (!isReversed1) {
      //normal
      deg1 = deg - minJointLimit + cwDxLimit1;
      Serial.printf("Pos1 in degrees: %d\n", deg1);
    } else {
      //reversed
      deg1 = ccwDxLimit1 - (deg - minJointLimit);
      Serial.printf("(R)Pos1 in degrees: %d\n", deg1);
    }
    set_goal_position(dxID1, DegToDx(deg1));
  }
  if (!slave[dxID2]) {
    if (dxID2 > 0) {
      if (!isReversed2) {
        //normal
        deg2 = deg - minJointLimit + cwDxLimit2;
        Serial.printf("Pos2 in degrees: %d\n", deg2);
      } else {
        //reversed
        deg2 = ccwDxLimit2 - (deg - minJointLimit);
        Serial.printf("(R)Pos2 in degrees: %d\n", deg2);
      }
      // Serial.println("\n");
      set_goal_position(dxID2, DegToDx(deg2));
    }
  } else {
  }
}
void moveJointWithSpeed(uint jointIndex, int deg, uint16_t speed) {
  Serial.print("Moving joint ");
  Serial.print(jointIndex);
  Serial.print(" to: ");
  Serial.println(deg);
  uint16_t tugrik1, tugrik2;
  int minJointLimit = joint_limits[jointIndex][0];
  int maxJointLimit = joint_limits[jointIndex][1];
  Serial.print("minJointLimit: ");
  Serial.print(minJointLimit);
  Serial.print(" maxJointLimit: ");
  Serial.println(maxJointLimit);

  uint dxID1 = joint_dx_id[jointIndex][0];
  uint dxID2 = joint_dx_id[jointIndex][1];
  Serial.print("dxID1: ");
  Serial.print(dxID1);
  Serial.print(" dxID2: ");
  Serial.println(dxID2);

  bool isReversed1 = reverse[dxID1];
  bool isReversed2 = reverse[dxID2];
  Serial.print("isReversed1: ");
  Serial.print(isReversed1);
  Serial.print(" isReversed2: ");
  Serial.println(isReversed2);

  uint16_t cwDxLimit1 = cw_angle_limit[dxID1];
  uint16_t cwDxLimit2 = cw_angle_limit[dxID2];
  Serial.print("cwDxLimit1: ");
  Serial.print(cwDxLimit1);
  Serial.print(" cwDxLimit2: ");
  Serial.println(cwDxLimit2);

  uint16_t ccwDxLimit1 = ccw_angle_limit[dxID1];
  uint16_t ccwDxLimit2 = ccw_angle_limit[dxID2];
  Serial.print("ccwDxLimit1: ");
  Serial.print(ccwDxLimit1);
  Serial.print(" ccwDxLimit2: ");
  Serial.println(ccwDxLimit2);

  current_position[dxID1] = (uint16_t)((float)getPresentPositionDX(dxID1) * GPP);

  int deg1, deg2;
  // Serial.printf("jointIndex: %d, minJointLimit: %d, maxJointLimit: %d, dxID1: %d, dxID2: %d, cwDxLimit1: %d, cwDxLimit2: %d, cwwDxLimit1: %d, cwwDxLimit2: %d, reverse: %s \n", jointIndex, minJointLimit, maxJointLimit, dxID1, dxID2, cwDxLimit1, cwDxLimit2, ccwDxLimit1, ccwDxLimit2, isReversed1 ? "true" : "false");
  // Serial.printf("Go to %d\n", deg);
  if (dxID1 > 0) {
    if (!isReversed1) {
      //normal
      deg1 = deg - minJointLimit + cwDxLimit1;
      Serial.printf("Pos1 in degrees: %d\n", deg1);
    } else {
      //reversed
      deg1 = ccwDxLimit1 - (deg - minJointLimit);
      Serial.printf("(R)Pos1 in degrees: %d\n", deg1);
    }
    if (joint_mode_is_joint[jointIndex]){
    set_goal_position_with_speed(dxID1, DegToDx(deg1), speed);
    }
    else{
        set_moving_speed(dxID1, speed);
    }
  }
  if (!slave[dxID2]) {
    if (dxID2 > 0) {
      if (!isReversed2) {
        //normal
        deg2 = deg - minJointLimit + cwDxLimit2;
        Serial.printf("Pos2 in degrees: %d\n", deg2);
      } else {
        //reversed
        deg2 = ccwDxLimit2 - (deg - minJointLimit);
        Serial.printf("(R)Pos2 in degrees: %d\n", deg2);
      }

      // Serial.println("\n");
      set_goal_position_with_speed(dxID2, DegToDx(deg2), speed);
    }
  }

  else {  //if secondary dx is slave, turn it on with needed speed
    uint16_t slave_speed = (uint16_t)((float)speed / dx_ratio[dxID2]);
    Serial.print("dx1 c_p: ");
    Serial.print(current_position[dxID1]);
    Serial.print("\tdeg1: ");
    Serial.print(deg1);
    Serial.print("\treverse 2: ");
    Serial.print(reverse[dxID2]);
    if (current_position[dxID1] < deg1) {  //master is rotating CCW and slave is reversed, so rotate CW
      Serial.print("\tturn CW with speed: ");
      if (reverse[dxID2]) {
        slave_speed |= 0x400;
      }
      Serial.print(slave_speed);

    } else {
      Serial.print("\tturn CCW with speed: ");
      if (!reverse[dxID2]) {
        slave_speed |= 0x400;
      }
      Serial.println(slave_speed);
    }
    set_moving_speed(dxID2, slave_speed);
  }
}
void reset(){
  HAL_NVIC_SystemReset();
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  while (!Serial)
    ;
  Serial.println("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n");
  Serial.println("Start..");

  // Initialize PortHandler instance
  // Set the port path
  // Get methods and members of PortHandlerLinux or PortHandlerWindows
  portHandler = dynamixel::PortHandler::getPortHandler(DEVICENAME);

  // Initialize PacketHandler instance
  // Set the protocol version
  // Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
  packetHandler = dynamixel::PacketHandler::getPacketHandler(PROTOCOL_VERSION);


  int index = 0;
  int dxl_comm_result = COMM_TX_FAIL;                                                     // Communication result
  int dxl_goal_position[2] = { DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE };  // Goal position

  uint8_t dxl_error = 0;             // Dynamixel error
  int16_t dxl_present_position = 0;  // Present position
  uint16_t dxl_model_number;         // Dynamixel model number

  // Open port
  if (portHandler->openPort()) {
    Serial.print("Succeeded to open the port!\n");
  } else {
    Serial.print("Failed to open the port!\n");
    Serial.print("Press any key to terminate...\n");
    return;
  }

  // Set port baudrate
  if (portHandler->setBaudRate(BAUDRATE)) {
    Serial.print("Succeeded to change the baudrate!\n");
  } else {
    Serial.print("Failed to change the baudrate!\n");
    Serial.print("Press any key to terminate...\n");
    return;
  }

  Serial.println("Find Dynamixels:");

  // find all dynamnxiles
  for (index = 0; index < DYNAMIXEL_MAX_ID; index++) {
    dxl_model_number = 0;
    dxl_comm_result = packetHandler->ping(portHandler, index, &dxl_model_number, &dxl_error);

    if (dxl_comm_result != COMM_SUCCESS) {
      packetHandler->getTxRxResult(dxl_comm_result);
    } else if (dxl_error != 0) {
      packetHandler->getRxPacketError(dxl_error);
    } else {
      status[index] = 1;
      Serial.printf("[ID:%03d] Finded. Dynamixel model number : %d\n", index, dxl_model_number);
    }
  }
  Serial.println("{\"status\": \"Waiting for configuration\"}");
}

void disableDX() {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
  // Disable Dynamixel Torque
  for (int index = 1; index < DYNAMIXEL_MAX_ID; index++) {
    // if (!status[index] == 1) { continue; }

    // Disable Dynamixel Torque
    dxl_comm_result = packetHandler->write1ByteTxRx(portHandler, index, ADDR_12X_TORQUE_ENABLE, TORQUE_DISABLE, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
      packetHandler->getTxRxResult(dxl_comm_result);
      Serial.printf("[\%03d] Result: \%d\n", index, dxl_comm_result);

    } else if (dxl_error != 0) {
      packetHandler->getRxPacketError(dxl_error);
      Serial.printf("[\%03d] Error: \%d\n", index, dxl_error);

    } else {
      Serial.print("Dynamixel has been successfully disconnected \n");
    }
  }
  // Close port
  portHandler->closePort();
}

void torqueEnableDX(int id) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
                                       // Disable Dynamixel Torque
  // Disable Dynamixel Torque
  dxl_comm_result = packetHandler->write1ByteTxRx(portHandler, id, ADDR_12X_TORQUE_ENABLE, TORQUE_ENABLE, &dxl_error);
  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("[\%03d] Result: \%d\n", index, dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("[\%03d] Error: \%d\n", index, dxl_error);

  } else {
    
  }
}
void torqueDisableDX(int id) {
  int dxl_comm_result = COMM_TX_FAIL;  // Communication result
  uint8_t dxl_error = 0;               // Dynamixel error
                                       // Disable Dynamixel Torque
  // Disable Dynamixel Torque
  dxl_comm_result = packetHandler->write1ByteTxRx(portHandler, id, ADDR_12X_TORQUE_ENABLE, TORQUE_DISABLE, &dxl_error);
  if (dxl_comm_result != COMM_SUCCESS) {
    packetHandler->getTxRxResult(dxl_comm_result);
    Serial.printf("[\%03d] Result: \%d\n", index, dxl_comm_result);

  } else if (dxl_error != 0) {
    packetHandler->getRxPacketError(dxl_error);
    Serial.printf("[\%03d] Error: \%d\n", index, dxl_error);

  } else {
    
  }
}

void doDemo() {


  moveJointWithSpeed(1, 50, 300);
  delay(4000);
  moveJointWithSpeed(1, 0, 150);
  delay(4000);
  disableDX();
}

void recieveDataFromHost(void) {
  uint dx_count = 0;
  if (Serial.available()) {
    JsonDocument jsonIn;

    // Serial.println("recivied");
    Serial.setTimeout(1000);
    DeserializationError err = deserializeJson(jsonIn, Serial);  // получаем сообщение от orange pi через uart
    if (err == DeserializationError::Ok)                         // если cообщение принято
    {
      // Serial.println("is Json");
      // serializeJson(jsonIn, Serial);
      hostTimeRecivie = timeNow + getHostTimeout();
      if (jsonIn["reset"]){
        Serial.println("{\"status\": \"resetting\"");
        disableDX();
        reset();
      }
      else if (jsonIn["configure"]) {

        Serial.println("\nConfiguring Dynamixels:");
        JsonArray configutation_joints = jsonIn["configure"]["joint"];

        for (int j = 0; j < configutation_joints.size(); j++) {
          JsonObject configutation_joint = configutation_joints[j];
          //id
          const int id = configutation_joint["id"];
          //Name
          strcpy(jointName[id], configutation_joint["name"]);
          //joint_mode
          const char *mode = configutation_joint["mode"];  //"joint" || "wheel"
          joint_mode_is_joint[id] = (strcmp(mode, "joint") == 0) ? true : false;
          //ratio
          joint_ratio[id] = 1.0;
          if (configutation_joint["ratio"]) {
            joint_ratio[id] = configutation_joint["ratio"].as<float>();
          }
          Serial.print("Ratio: ");
          Serial.printf("%.6f\n", joint_ratio[id]);
          JsonArray joint_limits_array = configutation_joint["limits"];

          joint_limits[id][0] = joint_limits_array[0];
          joint_limits[id][1] = joint_limits_array[1];
          Serial.printf("Configuring [%d] joint with name: %s, mode: [%s], limits: [%d, %d]. ratio: %f\n", id, jointName[id], mode, joint_limits[id][0], joint_limits[id][1], joint_ratio[id]);
          Serial.println("Dynamixels: ");
          JsonArray dynamixels_array = configutation_joint["dynamixels"];
          for (int dx = 0; dx < dynamixels_array.size(); dx++) {
            JsonObject dx_configuration = dynamixels_array[dx];

            //get id
            joint_dx_id[id][dx] = dx_configuration["id"];
            uint dx_index = joint_dx_id[id][dx];
            setLedDX(dx_index, true);
            //get reverse
            reverse[dx_index] = dx_configuration["reverse"].as<bool>() | false;
            //get slave mode
            slave[dx_index] = dx_configuration["slave"].as<bool>() | false;
            if (slave[dx_index]) {
              dx_ratio[dx_index] = dx_configuration["ratio"].as<float>();
            }

            set_status_return_level(joint_dx_id[id][dx], 2);

            //get limits
            if (joint_mode_is_joint[id] != true | slave[dx_index] == true) {
              cw_angle_limit[dx_index] = 0;
              ccw_angle_limit[dx_index] = 0;
            } else {
              if (!reverse[dx_index]) {
                cw_angle_limit[dx_index] = dx_configuration["cw_angle_limit"];
                ccw_angle_limit[dx_index] = cw_angle_limit[dx_index] + joint_limits[id][1] - joint_limits[id][0];
              } else {
                ccw_angle_limit[dx_index] = dx_configuration["cw_angle_limit"];
                cw_angle_limit[dx_index] = ccw_angle_limit[dx_index] - joint_limits[id][1] + joint_limits[id][0];
              }
            }

            //configure min/max position here:
            set_cw_angle_limit(joint_dx_id[id][dx], DegToDx(cw_angle_limit[dx_index]));
            delay(8);
            set_ccw_angle_limit(joint_dx_id[id][dx], DegToDx(ccw_angle_limit[dx_index]));
            delay(8);

            //configure moving_speed
            if (joint_mode_is_joint[id] && !slave[dx_index]) {
              moving_speed[dx_index] = configutation_joint["moving_speed"];

            } else {
              moving_speed[dx_index] = 0;
            }
            //configure moving speed here:
            set_moving_speed(joint_dx_id[id][dx], moving_speed[dx_index]);
            delay(8);

            //get torque_limit
            torque_limit[dx_index] = dx_configuration["torque_limit"];
            //todo: configure torque_limit speed here:
            set_torque_limit(joint_dx_id[id][dx], torque_limit[dx_index]);


            // if (dx_configuration["reverse"]) {
            //   reverse[dx_index] = dx_configuration["reverse"].as<bool>();
            // }
            Serial.print("Reverse: ");
            Serial.println(reverse[dx_index]);

            Serial.printf("ID:[%03d], CW_ANGLE_LIMIT:%d, CCW_ANGLE_LIMIT:%d , moving_speed: %d, torque_limit: %d, reverse: %d", dx_index, cw_angle_limit[dx_index], ccw_angle_limit[dx_index], moving_speed[dx_index], torque_limit[dx_index], reverse[dx_index]);
            dx_count++;
            Serial.println("\n");
            setLedDX(dx_index, false);
          }
        }
        Serial.printf("total: %u dynamixels\n", dx_count);
        Serial.printf("{\"status\":{\"configured_joints\": \"%u\"}}\n", configutation_joints.size());
      } else if (jsonIn["move"]) {
        //ожидаем следующий формат: {"move": [{"a":{"id":1, "pos": 45, "speed": 100}, {"q1":{"id": 2, "pos": 60, "speed": 100}}]}
        JsonArray movings = jsonIn["move"];

        for (int move = 0; move < movings.size(); move++) {
          JsonObject moveJoint = movings[move];
          for (JsonPair kv : moveJoint) {
            char *jointName = (char *)kv.key().c_str();
            int jointIndex = getJointIndexByName(jointName);
            int deg;
            int speed;
            if (jointIndex >= 0 && jointIndex < JOINT_COUNT) {
              deg = moveJoint[jointName]["pos"];
              speed = moveJoint[jointName]["speed"];
              if (!joint_mode_is_joint[jointIndex]) {
                if (speed<0) {
                  speed = abs(speed) | 0x400;
                }
              }
              Serial.printf("Moving joint %s with id: %d to pos: %d with speed: %d\n", jointName, jointIndex, deg, (uint16_t)speed);
              moveJointWithSpeed(jointIndex, deg, speed);
              delay(20);
            }
          }
        }
      } else if (jsonIn["do_demo"]) {
        doDemo();
      } else if (jsonIn["end_configure"]) {
        //todo: добавить возврат текущего положения манипуляторп
        jointsIsConfigured = true;
        addCurrentPositionsToAnswer();
      } else {
        while (Serial.available() > 0)
          Serial.read();  // чистим буфер
      }
    } else {
      Serial.println("Not a Json");
    }
  }
}

void sendStatus() {
  // answer["status"]["radsens"]["intensyStatic"] = radSens.getRadIntensyStatic();
  // answer["status"]["radsens"]["intensyDynamic"] = radSens.getRadIntensyDynamic();
  // answer["status"]["radsens"]["sensorChipId"] = "0x" + String(radSens.getChipId(), HEX);
  // answer["status"]["radsens"]["firwareVersion"] = radSens.getFirmwareVersion();
  // answer["status"]["radsens"]["pulseCount"] = radSens.getNumberOfPulses();
  // // answer["status"]["radsens"]["adressI2C"] = "0x"+String(radSens.getSensorAddress(), HEX);
  // answer["status"]["radsens"]["HVGeneratorState"] = radSens.getHVGeneratorState();
  // answer["status"]["radsens"]["sensivity"] = radSens.getSensitivity();
  // answer["status"]["radsens"]["ledState"] = radSens.getLedState();
  answer["status"]["radsens"]["time"] = millis();
}

void contolSlaveDXes() {
  uint8_t jointIndex = 0;
  for (jointIndex = 0; jointIndex < JOINT_COUNT; jointIndex++) {
    uint dxID1 = joint_dx_id[jointIndex][0];
    uint dxID2 = joint_dx_id[jointIndex][1];

    if (slave[dxID2] && target_position[dxID1] > 0) {
      // stop moving
      if (!getIsMovingDX(dxID1)) {
        if (moving_speed[dxID2] | 0x400) {  //curr speed is CW
          set_moving_speed(dxID2, 0x400);
          target_position[dxID1] = 0;
          torqueDisableDX(dxID1);
          torqueEnableDX(dxID1);

        } else {  //curr speed is CCW
          set_moving_speed(dxID2, 0x00);
          target_position[dxID1] = 0;
          torqueDisableDX(dxID1);
          torqueEnableDX(dxID1);
        }
      }
    }
  }
}
void checkHostTimeout(void)  // если не получали данные от хоста в течение таймаута, то останавливаемся
{
  if (hostTimeRecivie < timeNow) {
    // speed_r = 0;
    // speed_l = 0;

    digitalWrite(LED_BUILTIN, LOW);
  } else {
    digitalWrite(LED_BUILTIN, (timeNow % 2000) < 1000);
  }
}

void merge(JsonVariant dst, JsonVariantConst src) {
  if (src.is<JsonObjectConst>()) {
    for (JsonPairConst kvp : src.as<JsonObjectConst>()) {
      if (dst[kvp.key()])
        merge(dst[kvp.key()], kvp.value());
      else
        dst[kvp.key()] = kvp.value();
    }
  } else {
    dst.set(src);
  }
}

void addCurrentPositionsToAnswer(void) {
  if (!jointsIsConfigured) {
    answer["status"]["configured"] = jointsIsConfigured;
    return;
  }
  char position[1024];
  char *p = position;
  JsonDocument positions;
  p += sprintf(p, "{\"status\":{\"positions\":{");
  for (int jointIndex = 0; jointIndex < JOINT_COUNT; jointIndex++) {
    if (joint_dx_id[jointIndex][0] > 0) {
      const char *name = &jointName[jointIndex][0];
      p += sprintf(p, "\"%s\":{\"id\":%d, \"pos\":%d, \"speed\":%d, \"load\": %d},", name, jointIndex, get_joint_position(jointIndex), get_joint_speed(jointIndex), get_joint_load(jointIndex));
    }
  }
  p--;
  p += sprintf(p, "}}}\0");
  deserializeJson(positions, &position[0]);
  // answer["status"].remove("not_configured");
  answer["status"]["configured"] = jointsIsConfigured;
  answer["status"].remove("positions");
  merge(answer, positions);
}

void sendDataToHost(void) {
  if (hostTimeSend > timeNow)
    return;
  hostTimeSend = timeNow + getHostTransmitInterval();
  // sendStatus();
  addCurrentPositionsToAnswer();
  serializeJson(answer, Serial);
  Serial.println("");
}

void loop() {
  timeNow = millis();
  recieveDataFromHost();
  checkHostTimeout();
  sendDataToHost();
  contolSlaveDXes();
}
