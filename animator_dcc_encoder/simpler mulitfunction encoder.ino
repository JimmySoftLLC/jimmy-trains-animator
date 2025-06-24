#include <NmraDcc.h>

#define DCC_PIN 2    // DCC signal input
#define DccAckPin 3  // ACK output

NmraDcc Dcc;

struct CVPair {
  uint16_t CV;
  uint8_t Value;
};

CVPair FactoryDefaultCVs[] = {
  {CV_MULTIFUNCTION_PRIMARY_ADDRESS, 3}, // Default locomotive address 3
};

uint8_t FactoryDefaultCVIndex = 0;

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

// Locomotive speed and direction packet
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

// Locomotive function packet (F0–F28)
void notifyDccFunc(uint16_t Addr, DCC_ADDR_TYPE AddrType, FN_GROUP FuncGrp, uint8_t FuncState) {
  Serial.print("notifyDccFunc: Addr=");
  Serial.print(Addr, DEC);
  Serial.print(", FuncGrp=");
  Serial.print(FuncGrp, DEC);
  Serial.print(", FuncState=0x");
  Serial.println(FuncState, HEX);
}

void setup() {
  Serial.begin(115200);
  uint8_t maxWaitLoops = 255;
  while (!Serial && maxWaitLoops--)
    delay(20);
  
  pinMode(DccAckPin, OUTPUT);
  Serial.println("NMRA DCC Decoder Initialized");
  Serial.println("Init Done");

#ifdef digitalPinToInterrupt
  Dcc.pin(DCC_PIN, 0);
#else
  Dcc.pin(0, DCC_PIN, 1);
#endif
  
  Dcc.init(MAN_ID_DIY, 10, 0, 0);
}

void loop() {
  Dcc.process();
  
  if (FactoryDefaultCVIndex && Dcc.isSetCVReady()) {
    FactoryDefaultCVIndex--;
    Dcc.setCV(FactoryDefaultCVs[FactoryDefaultCVIndex].CV, FactoryDefaultCVs[FactoryDefaultCVIndex].Value);
  }
}