// Define the pin connected to the relay
const int relayPin = 9; // Change this to the actual pin you are using

void setup() {
  // Initialize the relay pin as an output
  pinMode(relayPin, OUTPUT);
  // Start serial communication at 9600 baud
  Serial.begin(9600);
}

void loop() {
  // Check if there is data available to read from the serial port
  if (Serial.available() > 0) {
    // Read the incoming byte
    char incomingByte = Serial.read();
    
    // Check if the incoming byte is '1' (ASCII value)
    if (incomingByte == '1') {
      // Turn on the relay
      digitalWrite(relayPin, HIGH);
      Serial.println("Relay is ON");
    } 
    // Check if the incoming byte is '0' (ASCII value)
    else if (incomingByte == '0') {
      // Turn off the relay
      digitalWrite(relayPin, LOW);
      Serial.println("Relay is OFF");
    }
  }
}
