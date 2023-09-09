int relayPin = 9; // Replace with the appropriate pin number

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW); // Initial state: Relay is off
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      digitalWrite(relayPin, LOW); // Turn on the relay
      Serial.println("Relay is OFF");
    } else if (command == '0') {
      digitalWrite(relayPin, HIGH); // Turn off the relay
      Serial.println("Relay is ON");
    }
  }
}
