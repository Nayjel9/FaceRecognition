int sirenPin = 9; // Replace with the actual pin number where your siren is connected

void setup() {
  pinMode(sirenPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'ON') {
      digitalWrite(sirenPin, HIGH); // Turn siren on
    } else if (command == 'OFF') {
      digitalWrite(sirenPin, LOW); // Turn siren off
    }
  }
}