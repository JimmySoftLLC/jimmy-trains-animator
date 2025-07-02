#include <NmraDcc.h>

#define DCC_PIN 2    // DCC signal input
#define DccAckPin 3  // ACK output

NmraDcc Dcc;

struct CVPair {
  uint16_t CV;
  uint8_t Value;
};

CVPair FactoryDefaultCVs[] = {
  {CV_MULTIFUNCTION_PRIMARY_ADDRESS, DEFAULT_MULTIFUNCTION_DECODER_ADDRESS},
  {CV_MULTIFUNCTION_EXTENDED_ADDRESS_MSB, CALC_MULTIFUNCTION_EXTENDED_ADDRESS_MSB(DEFAULT_MULTIFUNCTION_DECODER_ADDRESS)},
  {CV_MULTIFUNCTION_EXTENDED_ADDRESS_LSB, CALC_MULTIFUNCTION_EXTENDED_ADDRESS_LSB(DEFAULT_MULTIFUNCTION_DECODER_ADDRESS)},
  {CV_29_CONFIG, CV29_F0_LOCATION}, // Short Address, 28/128 Speed Steps
};

uint8_t FactoryDefaultCVIndex = 0;

// Define bit masks for F13–F28, matching the NmraDcc example
#define FN_BIT_13 0x01
#define FN_BIT_14 0x02
#define FN_BIT_15 0x04
#define FN_BIT_16 0x08
#define FN_BIT_17 0x10
#define FN_BIT_18 0x20
#define FN_BIT_19 0x40
#define FN_BIT_20 0x80
#define FN_BIT_21 0x01
#define FN_BIT_22 0x02
#define FN_BIT_23 0x04
#define FN_BIT_24 0x08
#define FN_BIT_25 0x10
#define FN_BIT_26 0x20
#define FN_BIT_27 0x40
#define FN_BIT_28 0x80

void notifyCVResetFactoryDefault() {
  FactoryDefaultCVIndex = sizeof(FactoryDefaultCVs)/sizeof(CVPair);
  Serial.println("notifyCVResetFactoryDefault: Settings CVs to Factory Defaults");
}

void notifyCVAck(void) {
  Serial.println("notifyCVAck");
  digitalWrite(DccAckPin, HIGH);
  delay(6);
  digitalWrite(DccAckPin, LOW);
}

void notifyDccSpeed(uint16_t Addr, DCC_ADDR_TYPE AddrType, uint8_t Speed, DCC_DIRECTION Dir, DCC_SPEED_STEPS SpeedSteps) {
  Serial.print("notifyDccSpeed: Addr=");
  Serial.print(Addr, DEC);
  Serial.print(", Speed=");
  Serial.print(Speed, DEC);
  Serial.print(", Dir=");
  Serial.print(Dir == DCC_DIR_FWD ? "Forward" : "Reverse");
  Serial.print(", Steps=");
  Serial.println(SpeedSteps, DEC);
}

void notifyDccFunc(uint16_t Addr, DCC_ADDR_TYPE AddrType, FN_GROUP FuncGrp, uint8_t FuncState) {
  Serial.print("notifyDccFunc: Addr=");
  Serial.print(Addr, DEC);
  Serial.print(" (");
  
  if (FuncGrp == FN_0_4) {
    Serial.print("F0=");
    Serial.print((FuncState & FN_BIT_00) ? "ON" : "OFF");
    Serial.print(", F1=");
    Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
    Serial.print(", F2=");
    Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
    Serial.print(", F3=");
    Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
    Serial.print(", F4=");
    Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
  } else if (FuncGrp == FN_5_8) {
    Serial.print("F5=");
    Serial.print((FuncState & FN_BIT_05) ? "ON" : "OFF");
    Serial.print(", F6=");
    Serial.print((FuncState & FN_BIT_06) ? "ON" : "OFF");
    Serial.print(", F7=");
    Serial.print((FuncState & FN_BIT_07) ? "ON" : "OFF");
    Serial.print(", F8=");
    Serial.print((FuncState & FN_BIT_08) ? "ON" : "OFF");
  } else if (FuncGrp == FN_9_12) {
    Serial.print("F9=");
    Serial.print((FuncState & FN_BIT_09) ? "ON" : "OFF");
    Serial.print(", F10=");
    Serial.print((FuncState & FN_BIT_10) ? "ON" : "OFF");
    Serial.print(", F11=");
    Serial.print((FuncState & FN_BIT_11) ? "ON" : "OFF");
    Serial.print(", F12=");
    Serial.print((FuncState & FN_BIT_12) ? "ON" : "OFF");
  } else if (FuncGrp == FN_13_20) {
    Serial.print("FN_13_20, Raw FuncState=0x");
    Serial.print(FuncState, HEX);
    Serial.print(" (F13=");
    Serial.print((FuncState & FN_BIT_13) ? "ON" : "OFF");
    Serial.print(", F14=");
    Serial.print((FuncState & FN_BIT_14) ? "ON" : "OFF");
    Serial.print(", F15=");
    Serial.print((FuncState & FN_BIT_15) ? "ON" : "OFF");
    Serial.print(", F16=");
    Serial.print((FuncState & FN_BIT_16) ? "ON" : "OFF");
    Serial.print(", F17=");
    Serial.print((FuncState & FN_BIT_17) ? "ON" : "OFF");
    Serial.print(", F18=");
    Serial.print((FuncState & FN_BIT_18) ? "ON" : "OFF");
    Serial.print(", F19=");
    Serial.print((FuncState & FN_BIT_19) ? "ON" : "OFF");
    Serial.print(", F20=");
    Serial.print((FuncState & FN_BIT_20) ? "ON" : "OFF");
    Serial.print(")");
  } else if (FuncGrp == FN_21_28) {
    Serial.print("FN_21_28, Raw FuncState=0x");
    Serial.print(FuncState, HEX);
    Serial.print(" (F21=");
    Serial.print((FuncState & FN_BIT_21) ? "ON" : "OFF");
    Serial.print(", F22=");
    Serial.print((FuncState & FN_BIT_22) ? "ON" : "OFF");
    Serial.print(", F23=");
    Serial.print((FuncState & FN_BIT_23) ? "ON" : "OFF");
    Serial.print(", F24=");
    Serial.print((FuncState & FN_BIT_24) ? "ON" : "OFF");
    Serial.print(", F25=");
    Serial.print((FuncState & FN_BIT_25) ? "ON" : "OFF");
    Serial.print(", F26=");
    Serial.print((FuncState & FN_BIT_26) ? "ON" : "OFF");
    Serial.print(", F27=");
    Serial.print((FuncState & FN_BIT_27) ? "ON" : "OFF");
    Serial.print(", F28=");
    Serial.print((FuncState & FN_BIT_28) ? "ON" : "OFF");
    Serial.print(")");
  }
  Serial.println(")");
}

void setup() {
  Serial.begin(115200);
  uint8_t maxWaitLoops = 255;
  while (!Serial && maxWaitLoops--)
    delay(20);
  
  pinMode(DccAckPin, OUTPUT);
  Serial.println("NMRA DCC Decoder Initialized");

#ifdef digitalPinToInterrupt
  Dcc.pin(DCC_PIN, 0);
#else
  Dcc.pin(0, DCC_PIN, 1);
#endif
  
  Dcc.init(MAN_ID_DIY, 10, 0, 0);
  Serial.println("Init Done");
}

void loop() {
  Dcc.process();
  
  if (FactoryDefaultCVIndex && Dcc.isSetCVReady()) {
    FactoryDefaultCVIndex--;
    Dcc.setCV(FactoryDefaultCVs[FactoryDefaultCVIndex].CV, FactoryDefaultCVs[FactoryDefaultCVIndex].Value);
  }
}