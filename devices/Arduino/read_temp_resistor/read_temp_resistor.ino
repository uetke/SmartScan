/*
  Reads an analog input pin and temperature of a DHT 11 sensor.

 */

// These constants won't change.  They're used to give names
// to the pins used:
const int analogInPin = A0;  // Analog input pin to read the output of OpAmp
int sensorValue = 0;        // value read 

// Libraries for the DHT sensor
#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11   // DHT 11 
DHT dht(DHTPIN, DHTTYPE);

// String to request a measurement from Python
String readString;

void setup() {
  Serial.begin(9600); 
  dht.begin();
}

void loop() {
  while(!Serial.available()) {}
  // serial read section
  while (Serial.available())
  {
    if (Serial.available() >0)
    {
      char c = Serial.read();  //gets one byte from serial buffer
      readString += c; //makes the string readString
    }
  }

  if (readString == "0"){
    readString = "";
    // prints the humidity to the Serial Port
    float h = dht.readHumidity();
    Serial.print(h);
    Serial.print("\n");
  }
  else if (readString =="1"){
    readString = "";
    // prints the temperature to the Serial Port
    float t = dht.readTemperature();
    Serial.print(t);
    Serial.print("\n");
  }
  else if (readString =="2"){
    readString = "";
    // prints the analog value to the Serial Port
    int v = analogRead(analogInPin);
    Serial.print(v);
    Serial.print("\n");
  }
  else{
    readString = "";
  }
}
