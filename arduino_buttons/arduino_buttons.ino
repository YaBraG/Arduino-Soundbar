/*
  arduino_buttons.ino
  Simple Arduino sketch:
  - Uses internal pull-ups on digital pins 2,3,4,5 (buttons to GND).
  - On press, sends "BTN1", "BTN2", etc. over Serial.

  Match the number of buttons you configure in the PC app.
*/

const int buttonPins[] = {2, 3, 4, 5};  // Change / extend as needed
const int numButtons  = sizeof(buttonPins) / sizeof(buttonPins[0]);

int lastState[numButtons];

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);        // Button between pin and GND
    lastState[i] = digitalRead(buttonPins[i]);   // Store initial state
  }
}

void loop() {
  for (int i = 0; i < numButtons; i++) {
    int currentState = digitalRead(buttonPins[i]);

    // Detect HIGH -> LOW transition (button press with pull-up)
    if (lastState[i] == HIGH && currentState == LOW) {
      delay(20);  // Debounce delay
      currentState = digitalRead(buttonPins[i]);
      if (currentState == LOW) {
        // Send message like "BTN1"
        Serial.print("BTN");
        Serial.println(i + 1);

        // Wait until button is released so we only trigger once per press
        while (digitalRead(buttonPins[i]) == LOW) {
          delay(5);
        }
      }
    }

    lastState[i] = currentState;
  }
}
