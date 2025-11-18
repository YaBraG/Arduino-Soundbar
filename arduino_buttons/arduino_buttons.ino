// Press a button -> send a text code over Serial like "BTN1"

const int buttonPins[] = {2, 3, 4, 5};  // Digital pins used for buttons
const int numButtons  = sizeof(buttonPins) / sizeof(buttonPins[0]);

// This array stores the last known state of each button
int lastState[numButtons];

void setup() {
  // Initialize serial communication with the PC
  Serial.begin(9600);

  // Configure each button pin with internal pull-up
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);   // Button between pin and GND
    lastState[i] = digitalRead(buttonPins[i]); // Store initial state
  }
}

void loop() {
  // Check each button
  for (int i = 0; i < numButtons; i++) {
    int currentState = digitalRead(buttonPins[i]);

    // We detect a press on a HIGH->LOW transition (because of INPUT_PULLUP)
    if (lastState[i] == HIGH && currentState == LOW) {
      // Small debounce delay to avoid multiple triggers
      delay(20);
      // Read again after debounce
      currentState = digitalRead(buttonPins[i]);
      if (currentState == LOW) {
        // Button i was pressed, send a code over Serial
        Serial.print("BTN");
        Serial.println(i + 1); // BTN1, BTN2, ...

        // Optional: wait until button is released so it only triggers once
        while (digitalRead(buttonPins[i]) == LOW) {
          delay(5);
        }
      }
    }

    // Update last state for next loop
    lastState[i] = currentState;
  }
}