#define GLED_1 2
#define GLED_2 5
#define GLED_3 8
#define GLED_4 11

#define YLED_1 3
#define YLED_2 6
#define YLED_3 9
#define YLED_4 12

#define RLED_1 4
#define RLED_2 7
#define RLED_3 10
#define RLED_4 13

#define PED_1 53
#define PED_2 51
#define PED_3 49
#define PED_4 47

bool pinValues[16] = {
  true, false, true, false,
  false, false, false, true,
  true, true, true, false,
  true, false, true, false
};
byte pinNumbers[16] = {GLED_1, GLED_2, GLED_3, GLED_4, YLED_1, YLED_2, YLED_3, YLED_4, RLED_1, RLED_2, RLED_3, RLED_4, PED_1, PED_2, PED_3, PED_4};

String incoming = "";

void setup() {
  Serial.begin(921600);
  for (int i = 0; i < 16; i++) {
    pinMode(pinNumbers[i], OUTPUT);
  }
  for (int i = 0; i < 16; i++) {
    digitalWrite(pinNumbers[i], pinValues[i]);
  }
}

void loop() {
  if (Serial.available()) {
    incoming = Serial.readStringUntil('\n');
    incoming.trim();
    if (incoming.length() == 16) {
      for (int i = 0; i < 16; i++) {
        // FIX: update pinValues so the state is remembered
        pinValues[i] = (incoming[i] == '1');
        digitalWrite(pinNumbers[i], pinValues[i] ? HIGH : LOW);
      }
    }
  }
}