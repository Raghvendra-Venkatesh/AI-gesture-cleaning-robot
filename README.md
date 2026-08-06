# AI Gesture-Controlled Cleaning Robot

An AI-powered cleaning robot that combines **Computer Vision**, **Artificial Intelligence**, and **Robotics** to provide an intuitive, touch-free cleaning experience. The robot is controlled using real-time hand gestures detected through a webcam and performs floor cleaning using a front-mounted mop attachment.

This project integrates **OpenCV**, **YOLOv11**, and gesture recognition with a four-wheel mobile robot, making it suitable as an AI & Robotics academic project.


## 🚀 Features

- ✋ Real-time hand gesture recognition
- 🤖 Gesture-based robot control
- 📷 Computer vision using OpenCV
- 🎯 YOLOv11-based object detection
- 🚧 Obstacle detection and avoidance
- 🧹 Front-mounted cleaning mechanism
- 🔄 Real-time movement control
- 🏠 Designed for indoor floor cleaning
- 📡 Wireless communication between PC and robot


## 🛠️ Tech Stack

### Software
- Python 3.x
- OpenCV
- YOLOv11
- Ultralytics
- NumPy
- PySerial

### Hardware
- 4-Wheel Robot Chassis
- ESP32 / Arduino (depending on implementation)
- Motor Driver (L298N / TB6612FNG)
- DC Gear Motors
- Webcam
- Battery Pack
- Mop Attachment
- Ultrasonic Sensor (optional)
- Bluetooth/Wi-Fi Module (if required)


## 📂 Project Structure

```
AI-Gesture-Cleaning-Robot/
│
├── dataset/
├── models/
├── src/
│   ├── gesture_detection.py
│   ├── object_detection.py
│   ├── robot_control.py
│   ├── navigation.py
│   └── main.py
│
├── docs/
├── images/
├── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ How It Works

1. The webcam captures the user's hand gestures.
2. OpenCV processes the video frames.
3. The gesture recognition module identifies the performed gesture.
4. The corresponding movement command is generated.
5. The command is transmitted wirelessly to the robot.
6. The robot performs the requested action while cleaning the floor.
7. YOLOv11 continuously detects nearby objects for safer navigation.


## ✋ Supported Gestures

| Gesture | Robot Action |
|----------|--------------|
| Open Palm | Stop |
| Thumb Up | Move Forward |
| Thumb Down | Move Backward |
| Swipe Left | Turn Left |
| Swipe Right | Turn Right |
| Fist | Start/Stop Cleaning |

*(Gestures can be customized.)*


## 🎯 Future Enhancements

- Autonomous cleaning mode
- SLAM-based mapping
- Voice control
- Mobile application
- Path planning
- Room mapping
- Battery monitoring
- Automatic charging dock
- AI-based dirt detection
- Multi-room navigation


## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/ai-gesture-cleaning-robot.git
```

Move into the project directory:

```bash
cd ai-gesture-cleaning-robot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python src/main.py
```


## 📸 Demo

Add images, videos, or GIFs here demonstrating:

- Gesture recognition
- Robot movement
- Cleaning operation
- Object detection


## 📈 Project Goals

- Integrate AI with Robotics
- Develop an intuitive gesture-based control system
- Implement real-time computer vision
- Improve indoor cleaning automation
- Demonstrate practical applications of AI in robotics


## 👨‍💻 Author

**Raghvendra Venkatesh**
**Sashwathi Sri**
**BS MONICA**


### ⭐ If you found this project useful, consider giving it a star!
