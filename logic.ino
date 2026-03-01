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

//********IMPORTANT !!!!!!! DEFINE cars_piling_up!!!!!!!!!!!!!!! ******


void setup(){


}


// ~~~~~~ White Lights
void white1() {
    if (digitalRead(BUTTON1A) == HIGH && digitalRead(RED1) == HIGH && digitalRead(RED3) == HIGH) {
        digitalWrite(WHITE1A, HIGH);
        digitalWrite(WHITE1B, HIGH);
        delay(15000);
        digitalWrite(WHITE1B, LOW);
        digitalWrite(WHITE1A, LOW);
    }
}


void white2() {
    if (digitalRead(BUTTON2A) == HIGH && digitalRead(RED2) == HIGH && digitalRead(RED4) == HIGH) {
        digitalWrite(WHITE2A, HIGH);
        digitalWrite(WHITE2B, HIGH);
        delay(15000);
        digitalWrite(WHITE2B, LOW);
        digitalWrite(WHITE2A, LOW);
    }
}


void white3() {
    if (digitalRead(BUTTON3A) == HIGH && digitalRead(RED3) == HIGH && digitalRead(RED1) == HIGH) {
        digitalWrite(WHITE3A, HIGH);
        digitalWrite(WHITE3B, HIGH);
        delay(15000);
        digitalWrite(WHITE3B, LOW);
        digitalWrite(WHITE3A, LOW);
    }
}


void white4() {
    if (digitalRead(BUTTON4A) == HIGH && digitalRead(RED4) == HIGH && digitalRead(RED2) == HIGH) {
        digitalWrite(WHITE4A, HIGH);
        digitalWrite(WHITE4B, HIGH);
        delay(15000);
        digitalWrite(WHITE4B, LOW);
        digitalWrite(WHITE4A, LOW);
    }
}



// ~~~~~~ Green Lights
void green1_3() {
    // Check for safety confirmation
    bool crossTrafficIsStopped1_3 = (digitalRead(RED2) == HIGH && digitalRead(RED4) == HIGH); ///These booleans need to include CV data
    bool noPedestrians1_3 = (digitalRead(WHITE1A) == LOW && digitalRead(WHITE1B) == LOW && digitalRead(WHITE3A) == LOW && digitalRead(WHITE3B) == LOW);
    bool carsWaiting1_3 = (cars_piling_up1 == true || cars_piling_up3 == true);

    if (carsWaiting1_3 == true && noPedestrians1_3 == true && crossTrafficIsStopped1_3 == true) {
        digitalWrite(RED1, LOW);
        digitalWrite(RED3, LOW);
        digitalWrite(GREEN1, HIGH);
        digitalWrite(GREEN3, HIGH);
    }
}
void loop() {
   
}
