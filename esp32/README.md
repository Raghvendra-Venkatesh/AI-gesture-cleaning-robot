# ESP32 Firmware

This firmware starts stopped, exposes a small HTTP server, validates commands, and stops the motors if commands stop arriving. It matches one dual-channel L298N, with the two left motors paired on one channel and the two right motors paired on the other.

## Commands

- `GET /command?cmd=FORWARD`
- `GET /command?cmd=BACKWARD`
- `GET /command?cmd=LEFT`
- `GET /command?cmd=RIGHT`
- `GET /command?cmd=STOP`
- `GET /status`
- `GET /speed?value=120`

The status JSON includes the current command, speed, milliseconds since the last accepted command, and requested PWM duty for each input pair. These PWM values confirm firmware output intent; they do not measure motor voltage, current, or rotation.

## Wiring

Connect the ESP32 and L298N control inputs as follows:

| L298N input | ESP32 pin |
|---|---|
| IN1 (your IN0) | D26 / GPIO26 |
| IN2 (your IN1) | D27 / GPIO27 |
| IN3 (your IN2) | D32 / GPIO32 |
| IN4 (your IN3) | D33 / GPIO33 |

Wire the left-side motors in parallel to OUT1/OUT2 and the right-side motors in parallel to OUT3/OUT4. Keep both ENA/ENB jumpers installed. The firmware varies speed by PWM on the IN pins, so separate ESP32 enable-pin wires are not required.

Before pairing two motors on one channel, check that their combined stall current is within the L298N channel and board limits. Keep motor power separate from ESP32 logic power, share ground, and never power motors from the ESP32. Use a motor-supply disconnect and test with the wheels raised.

## Safe Test Order

1. Upload firmware with motor power disconnected.
2. Open Serial Monitor at 115200 baud. In AP mode, it prints the ESP32 IP (normally `192.168.4.1`).
3. Before uploading, replace `change-this-password` in the firmware with a private password of at least 8 characters. Join the `GestureRobot` Wi-Fi network using that password.
4. Browse to `http://192.168.4.1/status` and confirm the JSON response. In STOP, all four input PWM values should be zero. During a FORWARD test, each side should show one input at the configured speed and the other at zero.
5. With the robot securely raised, test `http://192.168.4.1/command?cmd=STOP`.
6. The firmware starts at speed 150/255, which was verified to spin the wheels in the raised-wheel test. Keep the wheels raised for the first powered test.
7. Test each direction briefly. Flip the `reversed` setting for a side if it spins opposite to the expected direction.
