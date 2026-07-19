<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:CE0E2D,100:7A0000&height=230&section=header&text=PulseDrive&fontSize=62&fontColor=FFFFFF&animation=fadeIn&fontAlignY=32&desc=AI-Powered%20Predictive%20Vehicle%20Health%20Monitoring&descAlignY=52&descSize=17" width="100%"/>

<img src="https://commons.wikimedia.org/wiki/Special:FilePath/Snapdragon_Logo.svg" width="230"/>

### Built for the Qualcomm Snapdragon Hackathon 2026

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=21&duration=3000&pause=900&color=CE0E2D&center=true&vCenter=true&width=760&lines=Predict.+Prevent.+Protect.;From+Reactive+Repairs+to+Predictive+Intelligence;Agentic+AI+%2B+Qualcomm+GenIE+%2B+Hexagon+NPU;Sense+%E2%86%92+Analyze+%E2%86%92+Predict+%E2%86%92+Prevent" alt="Typing SVG" />

<br>

![Status](https://img.shields.io/badge/STATUS-ACTIVE%20DEVELOPMENT-CE0E2D?style=for-the-badge&labelColor=000000)
![Platform](https://img.shields.io/badge/PLATFORM-SNAPDRAGON%20X%20ELITE-CE0E2D?style=for-the-badge&labelColor=000000)
![Mobile](https://img.shields.io/badge/MOBILE-SNAPDRAGON%208%20ELITE%20GEN%205-CE0E2D?style=for-the-badge&labelColor=000000)

![AI](https://img.shields.io/badge/AI-QUALCOMM%20GENIE%20SDK-FFFFFF?style=for-the-badge&labelColor=CE0E2D)
![Runtime](https://img.shields.io/badge/RUNTIME-QNN%20%2B%20HEXAGON%20NPU-FFFFFF?style=for-the-badge&labelColor=CE0E2D)
![Agentic](https://img.shields.io/badge/AGENTIC%20AI-6%20AUTONOMOUS%20AGENTS-FFFFFF?style=for-the-badge&labelColor=CE0E2D)

<br>

![Python](https://img.shields.io/badge/Python-000000?style=flat-square&logo=python&logoColor=CE0E2D)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=flat-square&logo=fastapi&logoColor=CE0E2D)
![MongoDB](https://img.shields.io/badge/MongoDB-000000?style=flat-square&logo=mongodb&logoColor=CE0E2D)
![WebSocket](https://img.shields.io/badge/WebSockets-000000?style=flat-square&logo=socketdotio&logoColor=CE0E2D)
![React](https://img.shields.io/badge/React-000000?style=flat-square&logo=react&logoColor=CE0E2D)
![TypeScript](https://img.shields.io/badge/TypeScript-000000?style=flat-square&logo=typescript&logoColor=CE0E2D)
![Kotlin](https://img.shields.io/badge/Kotlin-000000?style=flat-square&logo=kotlin&logoColor=CE0E2D)
![Android](https://img.shields.io/badge/Android-000000?style=flat-square&logo=android&logoColor=CE0E2D)
![Arduino](https://img.shields.io/badge/Arduino-000000?style=flat-square&logo=arduino&logoColor=CE0E2D)
![JWT](https://img.shields.io/badge/JWT%20Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=CE0E2D)

</div>
<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Demo%20Video&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>

[![Watch the demo](https://img.shields.io/badge/▶%20WATCH%20DEMO-CE0E2D?style=for-the-badge&labelColor=000000)](https://drive.google.com/file/d/1ZgpC-3mUBnqxjNxovwh-o_ULIpidJMEM/view?usp=sharing)

</div>
<br>

> PulseDrive is an end-to-end AI-driven predictive maintenance platform that continuously monitors vehicle health using multiple IoT sensors, Edge AI, Agentic AI orchestration, and Qualcomm AI acceleration. Unlike traditional diagnostic systems that only detect faults **after** they occur, PulseDrive continuously analyzes real-time sensor telemetry to **predict failures before they happen**, estimate **Remaining Useful Life (RUL)**, generate **AI-powered recommendations**, and **automatically schedule maintenance** — all designed to run locally on Qualcomm Snapdragon AI hardware.

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=System%20Architecture&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

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

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Why%20AI%20on%20the%20Edge%20%2B%20Snapdragon%20X%20Elite&fontSize=26&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

| | Cloud-only | PulseDrive (Edge) |
|---|:---:|:---:|
| Latency | High | ⚡ Milliseconds |
| Works offline | ❌ | ✅ |
| Battery cost | Network-heavy | 🔋 NPU-efficient |
| Scales across vehicles | Backend bottleneck | Backend just stores + summarizes |

We evaluated Qualcomm's **Track 1 (LiteRT-LM / Gemma)** vs **Track 2 (LiteRT / TFLite / classical ML)** and chose **Track 2** — our problem is classification on IMU data, not a language task, so an LLM adds cost without adding accuracy. Snapdragon X Elite's dedicated **NPU** is what makes running two always-on models on a phone battery-realistic, and the same NPU access on a **Copilot+ PC** let us validate models locally during development — GenIE integration stays open as a future upgrade, not a requirement.

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Team&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

<div align="center">

**Team Name: PulseDrive**

| 👤 Member | ✉️ Email | 🛠️ Role |
|:---:|:---:|:---:|
| Tanish Aggarwal | tanishaggarwal.in@gmail.com | IoT & Machine Learning |
| Ishaan Maheshwari | ishaan.m16082006@gmail.com | IoT |
| Anshuman Dutta | anshuman.123dutta@gmail.com | Agentic AI |
| Yash Goel | yashgoel15119@gmail.com | Development |

</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Setup%20Instructions&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

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

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Hardware%20Setup&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

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

<img width="1200" height="1600" alt="image" src="https://github.com/user-attachments/assets/a3c37231-ebb4-4ab9-ab14-b641811c15ab" />


<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Backend%20%26%20Frontend%20Stack&fontSize=30&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

**Backend:** `FastAPI` · `WebSockets` · `MongoDB` · `Pydantic` · `Groq` (diagnosis text) · `JWT`
Flow: packet arrives → validated → health score/status/RUL/diagnosis computed → stored in MongoDB → broadcast to all receivers (never back to sender).

**Frontend:** `React` · `TypeScript` · `Vite` · `Tailwind` · `Chart.js` — every UI element (gauges, GPS, diagnosis, charts, alerts) is driven live from the socket, nothing hardcoded.

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=AI%20Models&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

| | Vehicle State Model | Wheel Imbalance Model |
|---|---|---|
| **File** | `vehicle_state_model_int8.tflite` | `wheel_imbalance_model_int8.tflite` |
| **Input** | `[1,6]` — Accel X,Y,Z · Gyro X,Y,Z | `[1,3]` — Gyro X,Y,Z |
| **Output** | Stationary / Moving / Inclined / Declined | Balanced / Imbalance |

Both run on-device via LiteRT. Test-rig confidence: ~0.996 for both — strong, but worth re-validating on real driving data.

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Vehicle%20Scenarios&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

| Status | Trigger | Theme |
|---|---|:---:|
| 🟢 Healthy | Normal temp/voltage/smoke, stable MPU | Green pulse |
| 🟡 Warning | Tyre imbalance (MPU1 ≠ MPU2 vibration) | Yellow glow |
| 🟠 Critical | Overheating (90–120°C) or motor overload | Orange pulse |
| 🔴 Emergency | Smoke 200–500ppm + high temp | Flashing red |

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rounded&color=0:CE0E2D,100:7A0000&height=90&section=header&text=Run%20Instructions&fontSize=34&fontColor=FFFFFF&fontAlignY=60&width=1200" width="100%"/>
</div>

```mermaid
flowchart LR
    A[1️⃣ Flash Arduino] --> B[2️⃣ Connect WiFi] --> C[3️⃣ Start Backend] --> D[4️⃣ Start Frontend/App] --> E[5️⃣ Open Dashboard] --> F[6️⃣ Drive / Move Rig] --> G[7️⃣ 🎉 Live Predictions]

    style G fill:#22c55e,color:#fff
```

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:CE0E2D,100:7A0000&height=120&section=footer&width=1200" width="100%"/>
</div>
