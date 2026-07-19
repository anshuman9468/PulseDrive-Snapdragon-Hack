<div align="center">

# 🚗⚡ PulseDrive
### AI-Powered Predictive Vehicle Health Monitoring
**Qualcomm Snapdragon Hackathon**

![Status](https://img.shields.io/badge/status-active%20development-brightgreen)
![Platform](https://img.shields.io/badge/platform-Snapdragon%20X%20Elite-blueviolet)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20TypeScript-61DAFB)
![Android](https://img.shields.io/badge/android-Kotlin%20%2B%20Jetpack%20Compose-3ddc84)
![AI](https://img.shields.io/badge/on--device%20AI-LiteRT-orange)

</div>

---

## 🎥 Demo Video

<div align="center">

### ▶️ [**Watch the full working demo here**](PASTE_YOUR_VIDEO_LINK_HERE)

[![Watch the demo](https://img.shields.io/badge/▶-Watch%20Demo%20Video-red?style=for-the-badge)](PASTE_YOUR_VIDEO_LINK_HERE)

*(Replace the link above with your YouTube / Drive / hackathon submission video)*

</div>

---

## 🩺 What is PulseDrive?

Most vehicles only tell you something's wrong **after** it's already wrong. PulseDrive changes that — a sensor rig (2× MPU6050, temperature, gas, voltage, GPS) streams live telemetry to a backend that computes a health score and generates a real diagnosis, while two ML models run directly on the phone via **LiteRT** for instant, offline-capable predictions.

| 🚩 Problem | ✅ PulseDrive |
|---|---|
| Failures visible only after they happen | Continuous inference on live sensor data |
| Dashboards show numbers, not meaning | Health score + AI-generated diagnosis |
| Cloud AI adds latency a car can't afford | Motion & wheel-balance predicted on-device |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    S1[🎛️ MPU6050 ×2] --> ARD
    S2[🌡️ Temp Sensor] --> ARD
    S3[💨 Gas Sensor] --> ARD
    S4[📍 GPS] --> ARD
    S5[🔋 Voltage Sensor] --> ARD

    ARD[Arduino Uno R4 WiFi] -- WebSocket --> API[FastAPI Backend]

    API --> DB[(MongoDB<br/>Every packet stored)]
    API --> HC[Health Score +<br/>Status + RUL + AI Diagnosis]
    HC --> BC{Broadcast}

    BC --> WEB[💻 React Dashboard]
    BC --> AND[📱 Android App]

    AND --> LR[🧠 LiteRT<br/>on-device inference]
    LR --> AND

    style ARD fill:#1e293b,color:#fff
    style API fill:#009688,color:#fff
    style DB fill:#4f8a3d,color:#fff
    style LR fill:#f97316,color:#fff
    style WEB fill:#61dafb,color:#000
    style AND fill:#3ddc84,color:#000
```

**Key rule:** sensors never talk to the database directly, and the phone never waits on the backend to know if a wheel is imbalanced — that decision happens locally, instantly, on-device.

---

## 🧠 Why AI on the Edge + Snapdragon X Elite

| | Cloud-only | PulseDrive (Edge) |
|---|:---:|:---:|
| Latency | High | ⚡ Milliseconds |
| Works offline | ❌ | ✅ |
| Battery cost | Network-heavy | 🔋 NPU-efficient |
| Scales across vehicles | Backend bottleneck | Backend just stores + summarizes |

We evaluated Qualcomm's **Track 1 (LiteRT-LM / Gemma)** vs **Track 2 (LiteRT / TFLite / classical ML)** and chose **Track 2** — our problem is classification on IMU data, not a language task, so an LLM adds cost without adding accuracy. Snapdragon X Elite's dedicated **NPU** is what makes running two always-on models on a phone battery-realistic, and the same NPU access on a **Copilot+ PC** let us validate models locally during development — GenIE integration stays open as a future upgrade, not a requirement.

---

## 👥 Team
 
<div align="center">
**Team Name: PulseDrive**
 
| 👤 Member | ✉️ Email | 🛠️ Role |
|:---:|:---:|:---:|
| Tanish Aggarwal | tanishaggarwal.in@gmail.com | IoT & Machine Learning |
| Ishaan Maheshwari | ishaan.m16082006@gmail.com | IoT |
| Anshuman Dutta | anshuman.123dutta@gmail.com | Agentic AI |
| Yash Goel | yashgoel15119@gmail.com | Development |
 
</div>


---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/anshuman9468/PulseDrive-Snapdragon-Hack.git
cd PulseDrive-Snapdragon-Hack
```

### 🔧 Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 💻 Frontend
```bash
cd frontend
npm install
npm run dev
```

### 📱 Android App (Kotlin + Jetpack Compose)

1. **Open the project** — launch Android Studio (Hedgehog or newer) → `Open` → select the `android/` folder from the repo.
2. **Let Gradle sync** — Android Studio auto-downloads dependencies on first open. Key ones already declared in `app/build.gradle.kts`:
   ```kotlin
   implementation("com.hivemq:hivemq-mqtt-client:1.3.3") // or OkHttp WebSocket, depending on active build
   implementation("org.tensorflow:tensorflow-lite:2.14.0")
   implementation("org.tensorflow:tensorflow-lite-support:0.4.4")
   ```
3. **Add the LiteRT models** — copy both files into `app/src/main/assets/`:
   - `vehicle_state_model_int8.tflite`
   - `wheel_imbalance_model_int8.tflite`
4. **Point the app at your backend** — open `NetworkConfig.kt` and set:
   ```kotlin
   const val SERVER_IP = "192.168.X.X"   // your laptop's local IP, NOT localhost
   const val WS_PORT = 8000
   ```
5. **Check permissions** in `AndroidManifest.xml` — `INTERNET` and `ACCESS_FINE_LOCATION` (for GPS display) should already be declared; grant location permission on first launch when prompted.
6. **Run it:**
   - Plug in a phone via USB with **Developer Options → USB Debugging** enabled, select it as the run target, and hit ▶️ Run in Android Studio, **or**
   - Use an emulator with Google Play Services (needed for location/maps features).
7. **Build a release APK** (for sharing/demo without a cable):
   ```bash
   ./gradlew assembleDebug
   ```
   The APK lands in `app/build/outputs/apk/debug/app-debug.apk` — install it directly on any Android device with `adb install app-debug.apk`.

> 💡 Same network gotcha applies here as the frontend: your phone and your backend machine must be on the **same Wi-Fi/hotspot**, and the backend's IP (not `localhost`) must be used in step 4.

---

## 🔩 Hardware Setup

| Component | Purpose |
|---|---|
| 🎛️ Arduino Uno R4 WiFi *(or UNO Q)* | Main controller |
| 📈 2× MPU6050 | Accel + gyro — front & rear axle |
| 🌡️ HS3003 | Temperature / humidity |
| 💨 MQ Gas Sensor | Smoke / gas ppm |
| 📍 GPS Module | Location telemetry |
| 🔌 BTS7960 | Motor driver |
| 🔋 Voltage Sensor | Battery health (via divider) |

**Why two IMUs?** A healthy vehicle gives similar vibration signatures front and rear. An imbalanced wheel shows up as a *difference* between the two — one IMU alone can't catch that.

<img width="491" height="537" alt="image" src="https://github.com/user-attachments/assets/c6213546-8e1e-4dc9-9999-38ce313a93d4" />


---

## 🖥️ Backend & Frontend Stack

**Backend:** `FastAPI` · `WebSockets` · `MongoDB` · `Pydantic` · `Groq` (diagnosis text) · `JWT`
Flow: packet arrives → validated → health score/status/RUL/diagnosis computed → stored in MongoDB → broadcast to all receivers (never back to sender).

**Frontend:** `React` · `TypeScript` · `Vite` · `Tailwind` · `Chart.js` — every UI element (gauges, GPS, diagnosis, charts, alerts) is driven live from the socket, nothing hardcoded.

---

## 🤖 AI Models

| | Vehicle State Model | Wheel Imbalance Model |
|---|---|---|
| **File** | `vehicle_state_model_int8.tflite` | `wheel_imbalance_model_int8.tflite` |
| **Input** | `[1,6]` — Accel X,Y,Z · Gyro X,Y,Z | `[1,3]` — Gyro X,Y,Z |
| **Output** | Stationary / Moving / Inclined / Declined | Balanced / Imbalance |

Both run on-device via LiteRT. Test-rig confidence: ~0.996 for both — strong, but worth re-validating on real driving data.

---

## 🚦 Vehicle Scenarios

| Status | Trigger | Theme |
|---|---|:---:|
| 🟢 Healthy | Normal temp/voltage/smoke, stable MPU | Green pulse |
| 🟡 Warning | Tyre imbalance (MPU1 ≠ MPU2 vibration) | Yellow glow |
| 🟠 Critical | Overheating (90–120°C) or motor overload | Orange pulse |
| 🔴 Emergency | Smoke 200–500ppm + high temp | Flashing red |

---

## ▶️ Run Instructions

```mermaid
flowchart LR
    A[1️⃣ Flash Arduino] --> B[2️⃣ Connect WiFi] --> C[3️⃣ Start Backend] --> D[4️⃣ Start Frontend/App] --> E[5️⃣ Open Dashboard] --> F[6️⃣ Drive / Move Rig] --> G[7️⃣ 🎉 Live Predictions]

    style G fill:#22c55e,color:#fff
```

