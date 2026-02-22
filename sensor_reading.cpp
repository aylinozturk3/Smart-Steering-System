#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const int PulseSensorPin = A0; // Heart rate sensor analog input
int threshold = 500; // Threshold for heart rate sensor

// TTP223 sensor pins
const int dokunma_sensor_pins[12] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}; 
#define ONE_WIRE_BUS 15 // Pin for DS18B20 data

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ates_sensors(&oneWire);

const float upper_feverThreshold = 37.5;
const float lower_feverThreshold = 35.5;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  ates_sensors.begin();

  pinMode(PulseSensorPin, INPUT);

  for (int i = 0; i < 12; i++) {
    pinMode(dokunma_sensor_pins[i], INPUT);
  }
}

void loop() {
  int PulseSensorValue = analogRead(PulseSensorPin);

  PulseRead_Write(PulseSensorValue);
  detectHandPositions();
  CheckTemperature();

  delay(1000); // 1s delay
}

void PulseRead_Write(int pulsevalue) {
  if (pulsevalue > threshold) {
    Serial.print("Kalp Nabiz Degeri: ");
    Serial.println(pulsevalue);
  } else {
    Serial.println("Dokunma algilanmadi");
  }
}

void detectHandPositions() {
  bool detected = false;
  Serial.print("Ellerin Konumu: ");

  bool rightHandPosition = false;
  bool leftHandPosition = false;

  for (int i = 0; i < 11; i++) {
    if (digitalRead(dokunma_sensor_pins[i]) == HIGH) {
      int angle = i * 30; // 30 degree resolution
      Serial.print(angle);
      Serial.print(" ");

      if (i >= 0 && i <= 4) {
        rightHandPosition = true;
      } else if (i >= 4 && i <= 8) {
        leftHandPosition = true;
      }
      detected = true;
    }
  }

  if (!detected) {
    Serial.println("- Eller algilanmadi - gorsel ve isitsel uyari gonder !");
  } else if (rightHandPosition && leftHandPosition) {
    Serial.println("- Dogru el tutusu!");
  } else {
    Serial.println("- Yanlis el tutusu - UYARI");
  }
}

void CheckTemperature() {
  ates_sensors.requestTemperatures();
  float temperature = ates_sensors.getTempCByIndex(0);

  if (temperature == DEVICE_DISCONNECTED_C) {
    Serial.println("HATA: SENSOR BAGLANTI KOPUK");
    return;
  }

  if (temperature > upper_feverThreshold || temperature < lower_feverThreshold) {
    Serial.print("UYARI VER: Ates ");
    Serial.println(temperature);
  } else {
    Serial.print("Ates Normal: ");
    Serial.println(temperature);
  }
}