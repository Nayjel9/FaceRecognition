const int relayPin = 2;  // Change this to the appropriate pin number

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'a') {
      digitalWrite(relayPin, HIGH);  // Turn on the relay
    } else if (command == 'b') {
      digitalWrite(relayPin, LOW);   // Turn off the relay
    }
  }
}
