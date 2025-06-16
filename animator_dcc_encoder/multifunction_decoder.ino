#include <NmraDcc.h>

// Define the Arduino input Pin number for the DCC Signal
#define DCC_PIN 2
#define DccAckPin 3 // Pin for DCC ACK

NmraDcc Dcc;
DCC_MSG Packet;

// Maximum number of engines to track
#define MAX_ENGINES 10

// Struct to store last known engine state
struct EngineState {
  uint16_t addr;        // Locomotive address
  uint8_t speed;        // Speed (0–127)
  DCC_DIRECTION dir;    // Forward or Reverse
  uint8_t speedSteps;   // 14, 28, or 128
  uint8_t funcState[5]; // Function states for FN_0_4, FN_5_8, FN_9_12, FN_13_20, FN_21_28
  bool active;          // True if this slot is used
  bool initialPrinted;  // True if initial state has been printed
};

EngineState engineStates[MAX_ENGINES];

struct CVPair {
  uint16_t CV;
  uint8_t Value;
};

CVPair FactoryDefaultCVs[] = {
  {CV_ACCESSORY_DECODER_ADDRESS_LSB, DEFAULT_ACCESSORY_DECODER_ADDRESS & 0xFF},
  {CV_ACCESSORY_DECODER_ADDRESS_MSB, DEFAULT_ACCESSORY_DECODER_ADDRESS >> 8},
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

// Uncomment to print all DCC Packets (for debugging)
//#define NOTIFY_DCC_MSG
#ifdef NOTIFY_DCC_MSG
void notifyDccMsg(DCC_MSG *Msg) {
  Serial.print("notifyDccMsg: ");
  for (uint8_t i = 0; i < Msg->Size; i++) {
    Serial.print(Msg->Data[i], HEX);
    Serial.print(' ');
  }
  Serial.println();
}
#endif

// Print the full state of an engine
void printEngineState(int slot, DCC_ADDR_TYPE AddrType) {
  Serial.print("Engine State: Addr=");
  Serial.print(engineStates[slot].addr, DEC);
  Serial.print(AddrType == DCC_ADDR_SHORT ? " (Short)" : " (Long)");
  Serial.print(", Speed=");
  Serial.print(engineStates[slot].speed, DEC);
  Serial.print(", Dir=");
  Serial.print(engineStates[slot].dir == DCC_DIR_FWD ? "Forward" : "Reverse");
  Serial.print(", Steps=");
  Serial.println(engineStates[slot].speedSteps, DEC);

  // Print function states for all groups
  for (int grpIdx = 0; grpIdx < 5; grpIdx++) {
    FN_GROUP FuncGrp = (grpIdx == 0) ? FN_0_4 :
                       (grpIdx == 1) ? FN_5_8 :
                       (grpIdx == 2) ? FN_9_12 :
                       (grpIdx == 3) ? FN_13_20 : FN_21_28;
    uint8_t FuncState = engineStates[slot].funcState[grpIdx];
    Serial.print("  FuncGrp=");
    Serial.print(FuncGrp, DEC);
    Serial.print(", FuncState=0x");
    Serial.print(FuncState, HEX);
    if (FuncGrp == FN_0_4) {
      Serial.print(" (F0=");
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
      Serial.print(" (F5=");
      Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
      Serial.print(", F6=");
      Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
      Serial.print(", F7=");
      Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
      Serial.print(", F8=");
      Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
    } else if (FuncGrp == FN_9_12) {
      Serial.print(" (F9=");
      Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
      Serial.print(", F10=");
      Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
      Serial.print(", F11=");
      Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
      Serial.print(", F12=");
      Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
    } else if (FuncGrp == FN_13_20) {
      Serial.print(" (F13=");
      Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
      Serial.print(", F14=");
      Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
      Serial.print(", F15=");
      Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
      Serial.print(", F16=");
      Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
      Serial.print(", F17=");
      Serial.print((FuncState & FN_BIT_05) ? "ON" : "OFF");
      Serial.print(", F18=");
      Serial.print((FuncState & FN_BIT_06) ? "ON" : "OFF");
      Serial.print(", F19=");
      Serial.print((FuncState & FN_BIT_07) ? "ON" : "OFF");
      Serial.print(", F20=");
      Serial.print((FuncState & FN_BIT_08) ? "ON" : "OFF");
    } else if (FuncGrp == FN_21_28) {
      Serial.print(" (F21=");
      Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
      Serial.print(", F22=");
      Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
      Serial.print(", F23=");
      Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
      Serial.print(", F24=");
      Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
      Serial.print(", F25=");
      Serial.print((FuncState & FN_BIT_05) ? "ON" : "OFF");
      Serial.print(", F26=");
      Serial.print((FuncState & FN_BIT_06) ? "ON" : "OFF");
      Serial.print(", F27=");
      Serial.print((FuncState & FN_BIT_07) ? "ON" : "OFF");
      Serial.print(", F28=");
      Serial.print((FuncState & FN_BIT_08) ? "ON" : "OFF");
    }
    Serial.println(")");
  }
}

// Locomotive speed and direction packet
void notifyDccSpeed(uint16_t Addr, DCC_ADDR_TYPE AddrType, uint8_t Speed, DCC_DIRECTION Dir, DCC_SPEED_STEPS SpeedSteps) {
  // Find or create state entry
  int slot = -1;
  for (int i = 0; i < MAX_ENGINES; i++) {
    if (engineStates[i].active && engineStates[i].addr == Addr) {
      slot = i;
      break;
    } else if (!engineStates[i].active && slot == -1) {
      slot = i;
    }
  }

  if (slot >= 0) {
    // Check for state change or first packet
    bool isNewEngine = !engineStates[slot].active;
    bool stateChanged = engineStates[slot].speed != Speed ||
                        engineStates[slot].dir != Dir ||
                        engineStates[slot].speedSteps != SpeedSteps;

    if (isNewEngine || (!engineStates[slot].initialPrinted && stateChanged)) {
      // Update state before printing to ensure consistency
      engineStates[slot].addr = Addr;
      engineStates[slot].speed = Speed;
      engineStates[slot].dir = Dir;
      engineStates[slot].speedSteps = SpeedSteps;
      engineStates[slot].active = true;
      // Print full state once
      printEngineState(slot, AddrType);
      engineStates[slot].initialPrinted = true;
    } else if (stateChanged) {
      // Print only speed change
      Serial.print("notifyDccSpeed: Addr=");
      Serial.print(Addr, DEC);
      Serial.print(AddrType == DCC_ADDR_SHORT ? " (Short)" : " (Long)");
      Serial.print(", Speed=");
      Serial.print(Speed, DEC);
      Serial.print(", Dir=");
      Serial.print(Dir == DCC_DIR_FWD ? "Forward" : "Reverse");
      Serial.print(", Steps=");
      Serial.println(SpeedSteps, DEC);

      // Update state
      engineStates[slot].speed = Speed;
      engineStates[slot].dir = Dir;
      engineStates[slot].speedSteps = SpeedSteps;
    }
  }
}

// Locomotive function packet (F0–F28)
void notifyDccFunc(uint16_t Addr, DCC_ADDR_TYPE AddrType, FN_GROUP FuncGrp, uint8_t FuncState) {
  // Find or create state entry
  int slot = -1;
  for (int i = 0; i < MAX_ENGINES; i++) {
    if (engineStates[i].active && engineStates[i].addr == Addr) {
      slot = i;
      break;
    } else if (!engineStates[i].active && slot == -1) {
      slot = i;
    }
  }

  if (slot >= 0) {
    // Determine function group index
    uint8_t grpIdx = (FuncGrp == FN_0_4) ? 0 :
                     (FuncGrp == FN_5_8) ? 1 :
                     (FuncGrp == FN_9_12) ? 2 :
                     (FuncGrp == FN_13_20) ? 3 :
                     (FuncGrp == FN_21_28) ? 4 : 255;
    if (grpIdx < 5) {
      // Check for state change or first packet
      bool isNewEngine = !engineStates[slot].active;
      bool stateChanged = engineStates[slot].funcState[grpIdx] != FuncState;

      if (isNewEngine || (!engineStates[slot].initialPrinted && stateChanged)) {
        // Update state before printing
        engineStates[slot].addr = Addr;
        engineStates[slot].funcState[grpIdx] = FuncState;
        engineStates[slot].active = true;
        // Print full state once
        printEngineState(slot, AddrType);
        engineStates[slot].initialPrinted = true;
      } else if (stateChanged) {
        // Print only function change
        Serial.print("notifyDccFunc: Addr=");
        Serial.print(Addr, DEC);
        Serial.print(AddrType == DCC_ADDR_SHORT ? " (Short)" : " (Long)");
        Serial.print(", FuncGrp=");
        Serial.print(FuncGrp, DEC);
        Serial.print(", FuncState=0x");
        Serial.print(FuncState, HEX);
        // Decode functions
        if (FuncGrp == FN_0_4) {
          Serial.print(" (F0=");
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
          Serial.print(" (F5=");
          Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
          Serial.print(", F6=");
          Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
          Serial.print(", F7=");
          Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
          Serial.print(", F8=");
          Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
        } else if (FuncGrp == FN_9_12) {
          Serial.print(" (F9=");
          Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
          Serial.print(", F10=");
          Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
          Serial.print(", F11=");
          Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
          Serial.print(", F12=");
          Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
        } else if (FuncGrp == FN_13_20) {
          Serial.print(" (F13=");
          Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
          Serial.print(", F14=");
          Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
          Serial.print(", F15=");
          Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
          Serial.print(", F16=");
          Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
          Serial.print(", F17=");
          Serial.print((FuncState & FN_BIT_05) ? "ON" : "OFF");
          Serial.print(", F18=");
          Serial.print((FuncState & FN_BIT_06) ? "ON" : "OFF");
          Serial.print(", F19=");
          Serial.print((FuncState & FN_BIT_07) ? "ON" : "OFF");
          Serial.print(", F20=");
          Serial.print((FuncState & FN_BIT_08) ? "ON" : "OFF");
        } else if (FuncGrp == FN_21_28) {
          Serial.print(" (F21=");
          Serial.print((FuncState & FN_BIT_01) ? "ON" : "OFF");
          Serial.print(", F22=");
          Serial.print((FuncState & FN_BIT_02) ? "ON" : "OFF");
          Serial.print(", F23=");
          Serial.print((FuncState & FN_BIT_03) ? "ON" : "OFF");
          Serial.print(", F24=");
          Serial.print((FuncState & FN_BIT_04) ? "ON" : "OFF");
          Serial.print(", F25=");
          Serial.print((FuncState & FN_BIT_05) ? "ON" : "OFF");
          Serial.print(", F26=");
          Serial.print((FuncState & FN_BIT_06) ? "ON" : "OFF");
          Serial.print(", F27=");
          Serial.print((FuncState & FN_BIT_07) ? "ON" : "OFF");
          Serial.print(", F28=");
          Serial.print((FuncState & FN_BIT_08) ? "ON" : "OFF");
        }
        Serial.println(")");

        // Update state
        engineStates[slot].funcState[grpIdx] = FuncState;
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  uint8_t maxWaitLoops = 255;
  while (!Serial && maxWaitLoops--)
    delay(20);
  
  pinMode(DccAckPin, OUTPUT);
  Serial.println("NMRA DCC Decoder for Engine State Changes (F0-F28)");
  
#ifdef digitalPinToInterrupt
  Dcc.pin(DCC_PIN, 0);
#else
  Dcc.pin(0, DCC_PIN, 1);
#endif
  
  // Initialize as a multifunction decoder
  Dcc.init(MAN_ID_DIY, 10, 0, 0);

  // Initialize engine state array
  for (int i = 0; i < MAX_ENGINES; i++) {
    engineStates[i].active = false;
    engineStates[i].initialPrinted = false;
    for (int j = 0; j < 5; j++) {
      engineStates[i].funcState[j] = 0;
    }
  }

  Serial.println("Init Done");
}

void loop() {
  Dcc.process();
  
  if (FactoryDefaultCVIndex && Dcc.isSetCVReady()) {
    FactoryDefaultCVIndex--;
    Dcc.setCV(FactoryDefaultCVs[FactoryDefaultCVIndex].CV, FactoryDefaultCVs[FactoryDefaultCVIndex].Value);
  }
}