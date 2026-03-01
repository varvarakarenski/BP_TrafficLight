// ~~~~~~Segment 1
#define RED1 #
#define YELLOW1 #
#define GREEN1 #
#define WHITE1A #
#define WHITE1B #
#define BUTTON1A #
#define BUTTON1B #


// ~~~~~~ Segment 2
#define RED2 #
#define YELLOW2 #
#define GREEN2 #
#define WHITE2 #
#define WHITE2A #
#define WHITE2B #
#define BUTTON2A #
#define BUTTON2B #


// ~~~~~~ Segment 3
#define RED3 #
#define YELLOW3 #
#define GREEN3 #
#define WHITE3 #
#define WHITE3A #
#define WHITE3B #
#define BUTTON3A #
#define BUTTON3B #


// ~~~~~~ Segment 4
#define RED4 #
#define YELLOW4 #
#define GREEN4 #
#define WHITE4 #
#define WHITE4A #
#define WHITE4B #
#define BUTTON4A #
#define BUTTON4B #

//********IMPORTANT !!!!!!! DEFINE ALL BOOLEAN VALUES (seen in code)!!!!!!!!!!!!!!! ******
//define all cars_piling_up booleans for each segment (1-4) *set to false by default?

bool crossTrafficIsStopped1_3 = (digitalRead(RED2) == HIGH && digitalRead(RED4) == HIGH); ///These booleans need to include CV data
bool noPedestrians1_3 = (digitalRead(WHITE1A) == LOW && digitalRead(WHITE1B) == LOW && digitalRead(WHITE3A) == LOW && digitalRead(WHITE3B) == LOW);
bool carsWaiting1_3 = (cars_piling_up1 == true || cars_piling_up3 == true);

bool crossTrafficIsStopped2_4 = (digitalRead(RED1) == HIGH && digitalRead(RED3) == HIGH); ///These booleans need to include CV data
bool noPedestrians2_4 = (digitalRead(WHITE2A) == LOW && digitalRead(WHITE2B) == LOW && digitalRead(WHITE4A) == LOW && digitalRead(WHITE4B) == LOW);
bool carsWaiting2_4 = (cars_piling_up2 == true || cars_piling_up4 == true);



void setup(){


}


// ~~~~~~ White Lights
void white1() {
    if (digitalRead(BUTTON1A) == HIGH && digitalRead(RED1) == HIGH && digitalRead(RED3) == HIGH) {
        ledArray[12] = 1;
        delay(15000);
        ledArray[12] = 0;
    }
}


void white2() {
    if (digitalRead(BUTTON2A) == HIGH && digitalRead(RED2) == HIGH && digitalRead(RED4) == HIGH) {
        ledArray[13] = 1;
        delay(15000);
        ledArray[13] = 0;
    }
}


void white3() {
    if (digitalRead(BUTTON3A) == HIGH && digitalRead(RED3) == HIGH && digitalRead(RED1) == HIGH) {
        ledArray[14] = 1;
        delay(15000);
        ledArray[14] = 0;
    }
}


void white4() {
    if (digitalRead(BUTTON4A) == HIGH && digitalRead(RED4) == HIGH && digitalRead(RED2) == HIGH) {
        ledArray[15] = 1;
        delay(15000);
        ledArray[15] = 0;
    }
}



// ~~~~~~ Green Lights
void green1_3() {
    if (carsWaiting1_3 == true && noPedestrians1_3 == true && crossTrafficIsStopped1_3 == true) {
        ledArray[0] = 0;
        ledArray[6] = 0;
        ledArray[2] = 1;
        ledArray[8] = 1;
    }
}

void green2_4() {
    if (carsWaiting2_4 == true && noPedestrians2_4 == true && crossTrafficIsStopped2_4 == true) {
        ledArray[3] = 0;
        ledArray[9] = 0;
        ledArray[5] = 1;
        ledArray[11] = 1;
    }
}

// ~~~~~~ Red/Yellow Lights
void red1_3() {
    if (digitalRead(GREEN1) == HIGH && digitalRead(GREEN3) == HIGH && cars_waiting2_4 == true) {
        digitalWrite(GREEN1, LOW);
        digitalWrite(GREEN3, LOW);
        digitalWrite(YELLOW1, HIGH);
        digitalWrite(YELLOW3, HIGH);
        delay(5000); // extended yellow light duration for safety
        digitalWrite(YELLOW1, LOW);
        digitalWrite(YELLOW3, LOW);
        digitalWrite(RED1, HIGH);
        digitalWrite(RED3, HIGH);
    }
}

void red2_4() {
    if (digitalRead(GREEN2) == HIGH && digitalRead(GREEN4) == HIGH && cars_waiting1_3 == true) {
        digitalWrite(GREEN2, LOW);
        digitalWrite(GREEN4, LOW);
        digitalWrite(YELLOW2, HIGH);
        digitalWrite(YELLOW4, HIGH);
        delay(5000); // extended yellow light duration for safety
        digitalWrite(YELLOW2, LOW);
        digitalWrite(YELLOW4, LOW);
        digitalWrite(RED2, HIGH);
        digitalWrite(RED4, HIGH);
    }
}
void loop() {
   
}
