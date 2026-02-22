##Smart Steering System (SSS)
A real-time health and safety monitoring system integrated into a vehicle's steering wheel. This project tracks the driver's heart rate, body temperature, and hand positioning and provides a visual dashboard for safety alerts.

## Key Features
Hand Position Tracking: Uses 12 capacitive touch sensors (TTP223) to detect if the driver is holding the wheel correctly (10-and-2 position).

Health Monitoring: Monitors heart rate (Pulse Sensor) and body temperature (DS18B20) in real-time.

Safety Alerts:

Safe Driving: Green status when grip and vitals are normal.

Grip Warning: Yellow status if the driver removes one or both hands.

Fever/Vital Warning: Red status if high body temperature or abnormal pulse is detected.

Live Dashboard: A Python-based GUI displaying real-time data and historical graphs.

