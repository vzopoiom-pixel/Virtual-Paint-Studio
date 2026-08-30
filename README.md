# 🎨 AirPaint Pro — AI-Powered Touchless Virtual Canvas

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange.svg)](https://mediapipe.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AirPaint Pro** is a real-time computer vision application that turns your webcam into a touchless, interactive digital canvas. Draw, erase, switch colors, and adjust brush sizes mid-air using natural hand gestures.

---

## ✨ Features

- ☝️ **Gesture-Based Drawing:** Draw seamlessly with your index finger.
- ✌️ **Smart Eraser:** Raise two fingers (Index + Middle) to erase mistakes without losing momentum.
- 👌 **Quick-Switch Palette:** Pinch thumb and index finger (the "OK" gesture) to cycle through a rich color palette instantly.
- 🎛️ **Interactive Touch UI:**
  - **Brush Sizes:** Tap virtual buttons on the screen (`S`, `M`, `L`) to change brush thickness.
  - **Hold-to-Clear Protection:** Hold the `CLEAR` button for 0.8 seconds to wipe the canvas safely without accidental deletion.
- 🌊 **Jitter-Free Smooth Lines:** Integrated Exponential Moving Average (EMA) and deadzone filters ensure buttery-smooth strokes even with noisy camera feeds.
- 🎯 **Visual Cyber Hitboxes:** Real-time visual feedback on every fingertip showing active modes, brushes, and touch targets.
- 📱 **Mobile Camera Support:** Plug-and-play compatibility with webcams and streaming apps like **DroidCam** and **Iriun**.

---

## 🎮 Gesture Controls

| Gesture | Action | Preview |
| :--- | :--- | :--- |
| **Index Finger Up ☝️** | **Draw** using the currently selected color & size | Single fingertip tracer |
| **Index + Middle Up ✌️** | **Eraser** mode | Red circular eraser hitbox |
| **Pinch / "OK" Gesture 👌** | **Cycle to Next Color** | Green pop-up confirmation |
| **Touch `S / M / L` Buttons** | **Change Brush Size** (Small / Medium / Large) | Yellow active outline |
| **Hold `CLEAR` Button** | **Reset & Clean Canvas** (Hold for 0.8s) | Progress loading bar |
| **Press 'q' Key** | **Exit** application | Close window |

---

## 🎨 Color Palette

The app includes 9 vibrant BGR colors:
- 🟢 **Green**
- 🩵 **Cyan**
- 🔵 **Blue**
- 🟣 **Purple**
- 🔴 **Red**
- 🟠 **Orange**
- 🟡 **Yellow**
- ⚪ **White**
- ⚫ **Black**

---

## 🚀 Installation & Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/vzopoiom-pixel/Virtual-Paint-Studio.git
