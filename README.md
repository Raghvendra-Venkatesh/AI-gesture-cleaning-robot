# AI Hand Gesture Cleaning Robot

This project controls a four-wheel robot from laptop hand gestures. The laptop runs OpenCV and the provided YOLO gesture model, then sends movement commands to an ESP32 over Wi-Fi. The ESP32 controls one dual-channel L298N, with the two left motors paired on one channel and the two right motors on the other.

## Dataset And Gesture Model

The supplied dataset is a YOLO detection dataset with `train`, `valid`, and `test` image/label splits. Its seven gesture classes are `Down`, `Left`, `Right`, `Stop`, `Thumbs Down`, `Thumbs up`, and `Up`, defined in `dataset/data.yaml`. The included `models/yolo_gesture_best.pt` is used by the webcam app.

The gesture mapping in `config/gesture_mapping.json` maps `Up` and `Thumbs up` to forward, `Down` and `Thumbs Down` to backward, `Left` and `Right` to turns, and `Stop` to stop. Any unrecognized or unmapped gesture defaults to STOP.

Optionally retrain the YOLO model from the provided dataset:

```powershell
python -m training.train_yolo --data dataset/data.yaml --epochs 40
python -m training.evaluate_yolo --model models/yolo_gesture_best.pt --data dataset/data.yaml --split test
```

The test split is for evaluation, not training.

## Project Layout

```text
config/       Runtime settings, gesture mapping, Wi-Fi example config
dataset/      Dataset notes
training/     Dataset inspection, training, evaluation scripts
models/       Trained model output location
src/          OpenCV runtime app and robot command modules
esp32/        Arduino ESP32 firmware
tests/        Hardware-free automated tests
reports/      Generated dataset and model reports
```

## Setup

Python 3.11 or 3.12 is recommended for broad ML/camera package compatibility.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `py -3.11` is unavailable, install Python 3.11 or 3.12 first, then rerun the commands above.

## Inspect The Dataset

```powershell
python -m training.inspect_yolo_dataset --dataset dataset --output reports/yolo_dataset_summary.json
```

## Gesture To Movement

Default gestures: `Up` or `Thumbs up` = forward, `Down` or `Thumbs Down` = backward, `Left` = turn left, `Right` = turn right, and `Stop` = stop. Edit `config/gesture_mapping.json` to change this. Unknown gestures resolve to STOP.

## Run The Robot

The app is configured to contact the ESP32 by default. To try the camera without moving the robot, set `dry_run` to `true` in `config/settings.json`.

```powershell
python -m src.main
```

With `dry_run` enabled, the app opens the webcam, displays predicted gestures and commands, and does not contact the ESP32.

## Run With ESP32

1. Wire one L298N as documented in [esp32/README.md](./esp32/README.md): D26/D27 control the left motor pair, and D32/D33 control the right motor pair. Keep ENA/ENB jumpers installed.
2. Check that the paired motors' combined stall current is within the L298N rating. Keep the wheels raised and motor power disconnected while flashing.
3. In Arduino IDE, install ESP32 board support, select your actual ESP32 board and COM port, and upload `esp32/esp32_robot_controller.ino`. Before uploading, replace `change-this-password` in the firmware with a private password of at least 8 characters. The access point is named `GestureRobot`.
4. Open Serial Monitor at 115200 baud, connect your laptop to the `GestureRobot` network (it may show "No internet"), and verify `http://192.168.4.1/status` returns JSON.
5. Test `http://192.168.4.1/command?cmd=STOP` with the wheels raised.
6. With wheels raised and motor power connected, run:

```powershell
python -m src.main
```

The program sends a STOP command when it starts and fails with a clear message if it cannot reach the ESP32. The camera window shows the raw detected gesture separately from the stable gesture used for control; the command changes only after four consecutive matching detections. Show a mapped gesture to move; show `Stop`, remove your hand, or press `Q`/`ESC` to stop. The firmware starts at speed 150/255 and its watchdog stops the motors if no command arrives for 2 seconds. ESP32 `/status` reports requested PWM duty and command age for diagnostics; these are not motor voltage/current measurements.

## Safe Hardware Test Order

1. Flash ESP32 and test `/status` with motor power disconnected.
2. Test `/command?cmd=STOP`.
3. Connect motor power with the robot lifted securely.
4. Start the app and test each direction briefly; adjust the side `reversed` setting in firmware if necessary.
5. Test STOP gesture, hand disappearance, app exit, Wi-Fi loss, and ESP32 watchdog stop.

## Safety Notes

- The ESP32 boots with motors stopped.
- Invalid commands stop the motors.
- The ESP32 watchdog stops motion if commands stop arriving.
- The Python app stops on low confidence, missing hand, camera failure, and exit.
- The default speed is 150/255; keep the robot raised for first powered tests.
- Use a physical disconnect switch for motor power.
- Do not power motors from the ESP32.
- Share ground between ESP32 logic and motor driver power.

## Dataset Attribution

The hand-gesture dataset is from [Roboflow Universe](https://universe.roboflow.com/yolo-zxvpk/hand-gesture-r7qgb/dataset/6) and is identified as CC BY 4.0 in the dataset metadata. The repository includes the exported dataset and its attribution files; review the license terms before redistributing dataset content.

## Authors

- Raghvendra Venkatesh
- Sashwathi Sri
- BS MONICA
