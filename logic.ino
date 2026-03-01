// ~~~~~~Segment 1
#define BUTTON1A #
#define BUTTON1B #


// ~~~~~~ Segment 2
#define BUTTON2A #
#define BUTTON2B #


// ~~~~~~ Segment 3
#define BUTTON3A #
#define BUTTON3B #


// ~~~~~~ Segment 4
#define BUTTON4A #
#define BUTTON4B #

//********IMPORTANT !!!!!!! DEFINE ALL BOOLEAN VALUES (seen in code)!!!!!!!!!!!!!!! ******
//define all cars_piling_up booleans for each segment (1-4) *set to false by default?

bool crossTrafficIsStopped1_3 = (ledArray[3] == 1 && ledArray[9] == 1); ///These booleans need to include CV data
bool noPedestrians1_3 = (ledArray[12] == 0 && ledArray[14] == 0);
bool carsWaiting1_3 = (cars_piling_up1 == true || cars_piling_up3 == true);

bool crossTrafficIsStopped2_4 = (ledArray[0] == 1 && ledArray[6] == 1); ///These booleans need to include CV data
bool noPedestrians2_4 = (ledArray[13] == 0 && ledArray[15] == 0);
bool carsWaiting2_4 = (cars_piling_up2 == true || cars_piling_up4 == true);



void setup(){


}



// ~~~~~~ White Lights
void white1() {
    if (digitalRead(BUTTON1A) == HIGH || digitalRead(BUTTON1B) && crossTrafficIsStopped2_4 == true) {
        ledArray[12] = 1;
        delay(15000);
        ledArray[12] = 0;
    }
}


void white2() {
    if (digitalRead(BUTTON2A) == HIGH || digitalRead(BUTTON2B) == HIGH && crossTrafficIsStopped1_3 == true) {
        ledArray[13] = 1;
        delay(15000);
        ledArray[13] = 0;
    }
}


void white3() {
    if (digitalRead(BUTTON3A) == HIGH || digitalRead(BUTTON3B) == HIGH && crossTrafficIsStopped2_4 == true) {
        ledArray[14] = 1;
        delay(15000);
        ledArray[14] = 0;
    }
}


void white4() {
    if (digitalRead(BUTTON4A) == HIGH || digitalRead(BUTTON4B) == HIGH && crossTrafficIsStopped1_3 == true) {
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
    if (ledArray[2] == 1 && ledArray[8] == 1 && carsWaiting2_4 == true) {
        ledArray[2] = 0;
        ledArray[8] = 0;
        ledArray[1] = 1;
        ledArray[7] = 1;
        delay(5000); // extended yellow light duration for safety
        ledArray[1] = 0;
        ledArray[7] = 0;
        ledArray[0] = 1;
        ledArray[6] = 1;
    }
}

void red2_4() {
    if (ledArray[5] == 1 && ledArray[11] == 1 && carsWaiting1_3 == true) {
        ledArray[5] = 0;
        ledArray[11] = 0;
        ledArray[4] = 1;
        ledArray[10] = 1;
        delay(5000); // extended yellow light duration for safety
        ledArray[4] = 0;
        ledArray[10] = 0;
        ledArray[3] = 1;
        ledArray[9] = 1;
    }
}

void loop() {
   
}
