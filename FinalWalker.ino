int fallSensor = 3;         // the number of the input pin. Must be an interrupt pin, as a fall is a serious event that must take priority
// over everythin else
int fallState = LOW;            // the current reading from the input pin
int debounceState = LOW;    // the previous reading from the input pin

long time = 0;              // the last time the output pin was toggled
long debounce = 50;         // the debounce time, increase if the output flickers

//Enable pins for the tripwire setup
int tripWire1 = 2;
int tripWire2 = 4;

//LEDs to indicate if the user has gone to far
int goodLED = 8;
int badLED = 9;

// Thresholds for IR TripWire
int threshold1 = 750;
int threshold2 = 700;

int sensor1 = A0;
int sensor2 = A1;

int tripWireFlag = 0;
long tripWireCounter = 0;

void setup()
{
  Serial.begin(9600);
  pinMode(fallSensor, INPUT);

  pinMode(tripWire1, OUTPUT);
  pinMode(tripWire2, OUTPUT);
  pinMode(goodLED,   OUTPUT);
  pinMode(badLED,    OUTPUT);

  digitalWrite(tripWire1, HIGH);         //supply 5 volts to photodiode to enable the tripwire
  digitalWrite(tripWire2, HIGH);

  digitalWrite(goodLED, LOW);
  digitalWrite(badLED, HIGH);            //By default, start off in an incorrect state, the user moves into a correct state
}
boolean fall = 0;
boolean pic = 0;
boolean warn = 0;
boolean sent = 0;
void loop()
{
  int switchstate;

  int amplitude1 = analogRead(sensor1);       //variable to store values from the photodiode/resistor network
  int amplitude2 = analogRead(sensor2);

  fallState = digitalRead(fallSensor);

  // If the switch changed, due to bounce or pressing...
  if (fallState != debounceState) {
    // reset the debouncing timer
    time = millis();
  }

  if ((millis() - time) > debounce) {
    debounceState = fallState;
    if (debounceState == HIGH) {
      tripWireFlag = 0;
      tripWireCounter = 0;
      if (!fall) {
        Serial.print("F");
        fall = true;
      }
    }
    else {
      fall = false;
    }
  }
  if (amplitude2 < threshold2) {
    digitalWrite(badLED,  HIGH);
    digitalWrite(goodLED, LOW);
    if (!tripWireFlag) {
      tripWireCounter = millis();
      tripWireFlag = 1;
    }
  }
  else {
    digitalWrite(goodLED, HIGH);
    digitalWrite(badLED,  LOW);
    tripWireFlag = 0;
    tripWireCounter = 0;
    pic = false;
    warn = false;
  }
  if (tripWireFlag) {
    if (((millis() - tripWireCounter) > 1000) && ((millis() - tripWireCounter) < 10000)) {
      if (!pic) {
        Serial.print("P");
        pic = true;
      }
    }
    else if ((millis() - tripWireCounter) >= 10000) {
      if (!warn) {
        Serial.print("W");
        warn = true;
      }
    }
  }

  // Save the last reading so we keep a running tally
  debounceState = fallState;
}

