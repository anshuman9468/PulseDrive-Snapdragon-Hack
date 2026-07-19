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

<br>

> PulseDrive is an end-to-end AI-driven predictive maintenance platform that continuously monitors vehicle health using multiple IoT sensors, Edge AI, Agentic AI orchestration, and Qualcomm AI acceleration. Unlike traditional diagnostic systems that only detect faults **after** they occur, PulseDrive continuously analyzes real-time sensor telemetry to **predict failures before they happen**, estimate **Remaining Useful Life (RUL)**, generate **AI-powered recommendations**, and **automatically schedule maintenance** — all designed to run locally on Qualcomm Snapdragon AI hardware.

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

## 📑 Table of Contents

<table>
<tr valign="top">
<td width="33%">

**Foundation**
- [Overview](#overview)
- [Objectives](#objectives)
- [Problem Statement](#problem-statement)
- [Our Solution](#our-solution)
- [System Architecture](#system-architecture)
- [Hardware Implementation](#hardware-implementation)
- [Sensor Schema & Telemetry](#data-pipeline)

</td>
<td width="33%">

**Intelligence Layer**
- [Machine Learning Models](#ml-models)
- [Qualcomm Edge AI Pipeline](#edge-ai-pipeline)
- [Qualcomm GenIE](#genie)
- [INT8 Quantization](#quantization)
- [AI Assistant](#ai-assistant)
- [Agentic AI](#agentic-ai)
- [Edge AI Features](#edge-ai-advantages)

</td>
<td width="33%">

**Application Layer**
- [Software Architecture](#software-architecture)
- [Vehicle Health Dashboard](#dashboard)
- [Live Demo Scenarios](#demo-scenarios)
- [Android Application](#android-app)
- [Security & APIs](#security-apis)
- [Future Scope](#future-scope)
- [Why PulseDrive Stands Out](#stands-out)
- [Gallery & Demo Video](#gallery)
- [Team](#team)

</td>
</tr>
</table>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<a id="overview"></a>
## 🚘 Overview

Modern vehicles usually detect failures **after the problem has already occurred**.

> A component fails → the driver notices abnormal behavior → a repair is performed.

<div align="center">

| ❌ Reactive | ❌ Expensive | ❌ Time Consuming | ❌ Manual | ❌ Opaque |
|:---:|:---:|:---:|:---:|:---:|

</div>

**PulseDrive flips this model.** It continuously observes vehicle conditions, detects abnormal patterns, predicts possible failures before breakdown, explains *why* using AI, estimates how much life a component has left, and can autonomously schedule maintenance — powered end-to-end by:

- 📡 Multi-sensor IoT monitoring
- 🧠 Machine Learning fault detection
- ⏱️ Real-time WebSocket telemetry
- ⚡ Edge AI inference
- 🤖 Agentic AI orchestration
- 🚀 Qualcomm Snapdragon NPU acceleration + GenIE SDK
- ☁️ Cloud-connected web dashboard
- 📱 Android vehicle companion application

```mermaid
flowchart LR
    S["🔍 Sense"] --> A["🧠 Analyze"] --> P["📈 Predict"] --> X["💬 Explain"] --> V["🛡️ Prevent"]
    style S fill:#CE0E2D,color:#ffffff,stroke:#000000,stroke-width:2px
    style A fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style P fill:#CE0E2D,color:#ffffff,stroke:#000000,stroke-width:2px
    style X fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style V fill:#CE0E2D,color:#ffffff,stroke:#000000,stroke-width:2px
```

---

<a id="objectives"></a>
## 🎯 Objectives

<table>
<tr><td>

✅ Monitor live vehicle telemetry
✅ Predict failures before breakdown
✅ Estimate Remaining Useful Life (RUL)
✅ Detect hazardous conditions

</td><td>

✅ Explain AI decisions
✅ Automatically recommend maintenance
✅ Schedule service automatically
✅ Notify users in real time

</td><td>

✅ Run AI locally on Qualcomm Snapdragon
✅ Operate fully offline via Edge AI
✅ Deliver millisecond-latency updates

</td></tr>
</table>

---

<a id="problem-statement"></a>
## 🚧 Problem Statement

Vehicle failures usually occur without sufficient warning because existing monitoring systems rely on **reactive diagnostics**. Current systems generally:

- Detect faults only **after** damage occurs
- Require manual inspection
- Cannot explain *why* a failure occurred
- Cannot estimate Remaining Useful Life
- Cannot automatically schedule maintenance
- Cannot operate completely offline using edge AI

```mermaid
flowchart TD
    subgraph Reactive["❌ Traditional Reactive Maintenance"]
        direction TB
        R1["Vehicle Component Failure"] --> R2["Driver Notices Problem"]
        R2 --> R3["Manual Diagnosis"]
        R3 --> R4["Repair"]
    end

    subgraph Predictive["✅ PulseDrive Predictive Maintenance"]
        direction TB
        P1["Continuous Vehicle Monitoring"] --> P2["AI Pattern Recognition"]
        P2 --> P3["Early Fault Detection + RUL"] --> P4["Autonomous Maintenance"]
    end

    style Reactive fill:#FFFFFF,stroke:#000000,stroke-width:2px,color:#000000
    style Predictive fill:#CE0E2D,stroke:#000000,stroke-width:2px,color:#ffffff
    style R1 fill:#FFFFFF,color:#000000,stroke:#CE0E2D
    style R2 fill:#FFFFFF,color:#000000,stroke:#CE0E2D
    style R3 fill:#FFFFFF,color:#000000,stroke:#CE0E2D
    style R4 fill:#FFFFFF,color:#000000,stroke:#CE0E2D
    style P1 fill:#7A0000,color:#ffffff,stroke:#ffffff
    style P2 fill:#7A0000,color:#ffffff,stroke:#ffffff
    style P3 fill:#7A0000,color:#ffffff,stroke:#ffffff
    style P4 fill:#7A0000,color:#ffffff,stroke:#ffffff
```

**PulseDrive solves these challenges** by combining IoT sensors, predictive AI, edge inference, and autonomous maintenance orchestration into one intelligent platform.

---

<a id="our-solution"></a>
## 💡 Our Solution

PulseDrive creates a miniature intelligent vehicle ecosystem using an **RC vehicle platform** as a real-world automotive testing environment.

| Vehicle Condition | Sensor | AI Function |
|---|---|---|
| 🛞 Wheel imbalance | MPU6050 #1 | Vibration analysis |
| 🚗 Vehicle motion / stability | MPU6050 #2 | Differential vibration & alignment |
| 🌡️ Thermal stress | Temperature Sensor | Overheating detection |
| 🔥 Smoke / electrical fault | Gas Sensor | Smoke & fire hazard detection |
| 🔋 Battery health | Voltage Sensor | Power monitoring |
| 📍 Vehicle location | GPS Module | Tracking & fleet monitoring |

---

<a id="system-architecture"></a>
## 🏗️ System Architecture

<table>
<tr><td>

```
                Vehicle
          ┌──────────────────┐
          │ Temperature       │
          │ Voltage           │
          │ Gas Sensor        │
          │ MPU6050 #1        │
          │ MPU6050 #2        │
          │ GPS               │
          └────────┬──────────┘
                    │
                    ▼
             Arduino UNO Q
            (Built-in WiFi)
                    │
           Live WebSocket Stream
                    │
                    ▼
        FastAPI Backend Server
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
  MongoDB      AI Prediction   Broadcast
  Database        Engine       WebSocket
      │             │             │
      ▼             ▼             ▼
  Android       React Web      Qualcomm
Application     Dashboard      GenIE SDK
```

</td></tr>
</table>

```mermaid
flowchart TD
    A["📐 MPU6050 #1<br/>Wheel Vibration"] --> UNO
    B["📐 MPU6050 #2<br/>Vehicle Motion"] --> UNO
    C["🌡️ Temperature Sensor"] --> UNO
    D["🔥 Gas Sensor"] --> UNO
    E["🔋 Voltage Sensor"] --> UNO
    F["📍 GPS Module"] --> UNO

    UNO["🔌 Arduino UNO Q<br/>Built-in WiFi"]
    UNO -- Live WebSocket Stream --> API

    API["⚙️ FastAPI Backend"]
    API --> DB[("🗄️ MongoDB")]
    API --> AI["🧠 AI Prediction Engine"]
    API --> BC["📡 Broadcast WebSocket"]

    BC --> APP["📱 Android Application"]
    BC --> DASH["💻 React Dashboard"]
    AI --> QNN["🚀 Qualcomm GenIE SDK"]
    QNN --> NPU["⚡ Hexagon NPU"]

    style A fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style B fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style C fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style D fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style E fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style F fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style UNO fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style API fill:#000000,color:#fff,stroke:#CE0E2D,stroke-width:2px
    style DB fill:#FFFFFF,color:#000000,stroke:#000000,stroke-width:2px
    style AI fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style BC fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
    style DASH fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style APP fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style QNN fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
    style NPU fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
```

---

<a id="hardware-implementation"></a>
## 🚗 Hardware Implementation

Current prototype uses: **Arduino UNO Q**, Temperature Sensor, Smoke/Gas Sensor, MPU6050 #1, MPU6050 #2, GPS Module.

<details>
<summary><b>📟 Sensor-by-sensor purpose (click to expand)</b></summary>

<br>

**🌡️ Temperature Sensor** — Detects engine overheating, cooling failure, thermal anomalies.

**🔥 Gas / Smoke Sensor** — Detects smoke, gas leakage, fire hazard.

**📐 MPU6050 #1** — Mounted near one wheel. Used for suspension vibration, wheel imbalance, chassis movement.

**📐 MPU6050 #2** — Mounted on another wheel. Used for comparative vibration analysis, vehicle stability, wheel alignment detection.

> Using **two MPU sensors** enables *differential vibration analysis*, which significantly improves predictive accuracy compared to a single IMU.

**📍 GPS** — Provides vehicle location, route tracking, fleet monitoring.

</details>

| Component | Purpose |
|---|---|
| Arduino UNO Q | Edge processing, built-in WiFi, sensor acquisition |
| Temperature Sensor | Overheating / thermal anomaly detection |
| Gas / Smoke Sensor | Smoke, gas leak, fire hazard detection |
| MPU6050 #1 | Wheel vibration / suspension monitoring |
| MPU6050 #2 | Comparative vibration / stability & alignment |
| GPS Module | Location tracking & fleet monitoring |
| Voltage Sensor | Battery health monitoring |

---

<a id="data-pipeline"></a>
## 📡 Sensor Schema & Telemetry

PulseDrive follows an **edge-cloud hybrid architecture**, streaming a single structured JSON payload per cycle.

### 📊 Final Sensor Schema

```json
{
  "vehicleId": "CAR001",
  "temperature": 99.8,
  "voltage": 9.6,
  "gasSensor": {
    "value": 425
  },
  "gps": {
    "lat": 28.6139,
    "lng": 77.2090
  },
  "mpu1": {
    "accX": 4.8,
    "accY": 3.9,
    "accZ": 10.2,
    "gyroX": 2.7,
    "gyroY": 2.4,
    "gyroZ": 2.1
  },
  "mpu2": {
    "accX": 0.8,
    "accY": 1.2,
    "accZ": 9.7,
    "gyroX": 0.3,
    "gyroY": 0.5,
    "gyroZ": 0.2
  }
}
```

### 📶 Live Streaming — WebSockets, not Polling

```
Arduino UNO Q → WebSocket → FastAPI → Broadcast → Dashboard → Android
```

No refresh required — everything updates in **milliseconds**.

### 🔌 WebSocket Architecture

The Connection Manager separates clients into:

| Role | Clients |
|---|---|
| **Sender** | Arduino UNO Q |
| **Receiver** | Android · Dashboard · Future Admin Panel |

> Only receivers receive broadcasts. Hardware never receives its own packets. Heartbeat support is implemented.

---

<a id="dataset-collection"></a>
## 🧠 Dataset Collection

**Vehicle Health Dataset**

| Category | Features |
|---|---|
| Motion | Temperature, Acceleration X/Y/Z, Gyroscope X/Y/Z |
| Classes | Normal · High Vibration · High Temperature · Fault |
| Size | 4,000+ real sensor samples |

**Smoke Detection Dataset**

| Input Features | Output Classes |
|---|---|
| `Gas_Level_Analog` | `0` → Normal |
| `Digital_Pin_Value` | `1` → Smoke / Fault Condition |

---

<a id="ml-models"></a>
## 🧠 Machine Learning Models

### 🚗 Vehicle State Classification Model

```mermaid
flowchart LR
    IN["Accel X, Y, Z<br/>Gyro X, Y, Z"] --> FE["Feature Extraction"] --> CLS["AI Classification"] --> OUT["Vehicle State"]
    style IN fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style FE fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style CLS fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style OUT fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
```

| Output Classes | Accuracy |
|---|---|
| Stationary · Moving · Inclined · Declined | **~96%** |

### ⚙️ Wheel Imbalance Detection Model

| Output Classes | Accuracy |
|---|---|
| Balanced · Imbalance | **~95%** |

### 🌫️ Smoke Detection Edge AI Model

```mermaid
flowchart TD
    I["Input Layer<br/>2 Sensor Features"] --> D1["Dense · 16 Neurons + ReLU"]
    D1 --> D2["Dense · 8 Neurons + ReLU"]
    D2 --> O["Output · Softmax"]
    style I fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style D1 fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style D2 fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style O fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
```

---

<a id="edge-ai-pipeline"></a>
## 🚀 Qualcomm Edge AI Deployment Pipeline

```mermaid
flowchart TD
    TF["TensorFlow / Keras Model"] --> ONNX["ONNX Conversion"]
    ONNX --> HUB["Qualcomm AI Hub Upload"]
    HUB --> QNN["QNN Execution Provider"]
    QNN --> NPU["Hexagon NPU Acceleration"]
    NPU --> RT["Real-Time Vehicle Intelligence"]

    style TF fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style ONNX fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style HUB fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style QNN fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
    style NPU fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
    style RT fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
```

Random Forest / `TreeEnsembleClassifier` models were **CPU-only** on Qualcomm AI Hub, so PulseDrive moved to lightweight `Dense → MatMul → Activation → Softmax` neural networks — fully compatible with QNN + Hexagon NPU.

| Target Device | Backend | Verified Runtime |
|---|---|---|
| Snapdragon X Elite (X1E78100) | `QNNExecutionProvider` | Hexagon NPU |

### 📱 Mobile Deployment — Snapdragon 8 Elite Gen 5

The same optimized pipeline extends from laptop to smartphone — with the **OnePlus 15**, one of the first phones powered by the **Snapdragon 8 Elite Gen 5**, as the reference mobile target for on-device inference.

```mermaid
flowchart LR
    XE["💻 Snapdragon X Elite<br/>Laptop"] <---> M8["📱 OnePlus 15<br/>Snapdragon 8 Elite Gen 5"]
    style XE fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style M8 fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
```

---

<a id="genie"></a>
## 🔮 Qualcomm GenIE — Future AI Pipeline

The backend has been intentionally designed so **Qualcomm GenIE SDK** can be inserted without changing the overall architecture.

```mermaid
flowchart LR
    S["Sensor"] --> A["Arduino"] --> F["FastAPI"] --> G["GenIE SDK"] --> N["Qualcomm NPU"] --> P["Prediction"] --> B["Broadcast"]
    style S fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style A fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style F fill:#000000,color:#fff,stroke:#CE0E2D,stroke-width:2px
    style G fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style N fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
    style P fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style B fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
```

Final deployment executes the language model **locally** on Snapdragon hardware instead of cloud inference.

✅ Offline AI ✅ Low latency ✅ Privacy ✅ No internet dependency ✅ NPU acceleration

---

<a id="quantization"></a>
## 🔋 INT8 Quantization

```mermaid
flowchart LR
    FP["FP32 Model"] --> Q["INT8 Quantization"] --> RM["Reduced Precision"] --> SR["Snapdragon AI Runtime"]
    style FP fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style Q fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style RM fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
    style SR fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
```

| Parameter | Improvement |
|---|---|
| Model Size | Reduced |
| Memory Usage | Lower |
| Inference Speed | Faster |
| Power Consumption | Reduced |

---

<a id="ai-assistant"></a>
## 💬 AI Assistant

PulseDrive includes a **conversational AI assistant** — instead of generic responses, it grounds every answer in live context:

`Current telemetry` · `Health score` · `Temperature` · `Voltage` · `Gas level` · `MPU readings` · `Remaining Useful Life` · `Historical data`

**The assistant answers questions like:**

> *"Can I drive another 300 km?"*
> *"Why is my vehicle overheating?"*
> *"What happens if I ignore this warning?"*
> *"How urgent is this issue?"*

---

<a id="edge-ai-advantages"></a>
## 🧩 Edge AI Features

| Feature | Description |
|---|---|
| ⚡ **Offline Inference** | No internet dependency |
| 🚀 **Snapdragon NPU Acceleration** | Hexagon NPU-mapped execution |
| 💬 **Local AI Assistant** | Runs directly on-device via GenIE |
| 🩺 **Real-Time Diagnostics** | Millisecond-latency prediction |
| 🔒 **Privacy-First** | Vehicle data stays on-device |

---

<a id="software-architecture"></a>
## 🖥️ Software Architecture

### 🧩 Backend Stack

`FastAPI` · `Python` · `MongoDB` · `Pydantic` · `WebSockets` · `JWT Authentication` · `Groq AI` · *Future: Qualcomm GenIE Integration*

### 🗄️ Database

MongoDB stores: sensor history, vehicle telemetry, health scores, predictions, AI diagnosis, Remaining Useful Life, maintenance logs.

### 🔁 AI Processing Pipeline

```mermaid
flowchart TD
    IN["📥 Incoming Sensor Packet"] --> VAL["✅ Validation"]
    VAL --> DB[("🗄️ MongoDB")]
    VAL --> HC["📊 Health Calculation"]
    HC --> PR["📈 Prediction"]
    PR --> DIAG["🧠 AI Diagnosis"]
    DIAG --> RUL["⏳ Remaining Useful Life"]
    RUL --> BC["📡 Broadcast"]
    BC --> DASH["💻 Dashboard"]

    style IN fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style VAL fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
    style HC fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style PR fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style DIAG fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
    style RUL fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
    style BC fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
    style DASH fill:#FFFFFF,color:#000000,stroke:#CE0E2D,stroke-width:2px
```

---

<a id="dashboard"></a>
## 📊 Vehicle Health Dashboard

| Metric | Status |
|---|---|
| Vehicle Health | **98%** |
| Temperature | Normal |
| Vibration | Stable |
| Smoke | No Detection |

Also shown: Remaining Useful Life · GPS · MPU1 / MPU2 · AI Diagnosis · Recommendation · Connection Status

---

<a id="demo-scenarios"></a>
## 🎮 Live Demonstration Scenarios

<table>
<tr><th>#</th><th>Scenario</th><th>Key Readings</th><th>Status</th><th>Recommendation</th></tr>
<tr><td>1</td><td>🟢 Normal Vehicle</td><td>Temp 28–40°C · Voltage 12.4V · Smoke 0–20 ppm</td><td><b>Health 100%</b></td><td>—</td></tr>
<tr><td>2</td><td>🟡 Tyre Imbalance</td><td>MPU1 vibration ↑, MPU2 normal (one wheel loaded)</td><td><b>Warning</b></td><td>Wheel Alignment</td></tr>
<tr><td>3</td><td>🟠 Overheating</td><td>Temperature &gt; 90°C</td><td><b>Critical</b></td><td>Inspect Cooling System</td></tr>
<tr><td>4</td><td>🔴 Fire Hazard</td><td>Smoke 200–500 ppm · Temp 110°C</td><td><b>Emergency</b></td><td>Stop Vehicle Immediately</td></tr>
<tr><td>5</td><td>🟠 Motor Overloading</td><td>Voltage drop + high vibration</td><td><b>Warning</b></td><td>Reduce Load</td></tr>
</table>

---

<a id="agentic-ai"></a>
## 🤖 Agentic AI Maintenance Assistant

Multiple autonomous agents collaborate together:

```mermaid
flowchart TD
    D["🩺 Diagnostic Agent<br/>Predicts failures"] --> M["🛠️ Maintenance Agent<br/>Schedules service"]
    M --> N["🔔 Notification Agent<br/>Pushes alerts"]
    N --> C["📞 Communication Agent<br/>Contacts service centers"]
    C --> H["🕓 History Agent<br/>Analyzes past failures"]
    H --> E["💡 Explainability Agent<br/>Explains every prediction"]

    style D fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style M fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
    style N fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style C fill:#7A0000,color:#fff,stroke:#000000,stroke-width:2px
    style H fill:#CE0E2D,color:#fff,stroke:#000000,stroke-width:2px
    style E fill:#000000,color:#CE0E2D,stroke:#CE0E2D,stroke-width:2px
```

| Agent | Responsibility |
|---|---|
| Diagnostic Agent | Predicts failures |
| Maintenance Agent | Schedules maintenance automatically |
| Notification Agent | Pushes alerts |
| Communication Agent | Contacts service centers |
| History Agent | Analyzes historical failures |
| Explainability Agent | Explains every AI prediction |

---

<a id="android-app"></a>
## 📱 Android Application

Built using `Kotlin` · `Jetpack Compose` · `MVVM` · `Retrofit` · `Hilt`

<details>
<summary><b>📲 Full feature breakdown (click to expand)</b></summary>

<br>

**Core:** Login · Registration · Dashboard · Live Monitoring · AI Assistant · Maintenance · Maps · Notifications · Analytics

**Dashboard shows:** Vehicle Status · Health Score · Remaining Useful Life · Temperature · Voltage · Smoke · GPS · MPU1 · MPU2 · AI Diagnosis · Recommendation · Connection Status

**Live Monitoring (real-time):** Temperature · Voltage · Smoke · MPU1 · MPU2 · GPS · Charts · Logs · Alerts

**Maintenance Module** automatically generates: Service Recommendation · Priority · Estimated Time · Estimated Cost · Schedule

**Maps:** Google Maps integration — displays vehicle location and live GPS

</details>

---

<a id="security-apis"></a>
## 🔐 Security & APIs

**Security:** JWT Authentication for Login, Registration, and Protected APIs

| REST APIs | WebSocket APIs |
|---|---|
| Authentication | `ws://<IP>:8000/ws/live` |
| Dashboard | `GET /ws/status` |
| Live Telemetry | |
| Prediction | |
| Ask AI | |
| Users | |
| Health | |

---

<a id="future-scope"></a>
## 🔭 Future Scope

<table>
<tr><td>

- Fleet Management
- OBD-II Integration
- CAN Bus Support
- Predictive Battery Analytics

</td><td>

- Digital Twin
- Federated Learning
- Vehicle-to-Vehicle Health Sharing

</td><td>

- Qualcomm AI Hub Deployment
- Cloud + Edge Hybrid Intelligence
- Autonomous Maintenance Orchestration

</td></tr>
</table>

---

<a id="stands-out"></a>
## 🏆 Why PulseDrive Stands Out

PulseDrive is not just a vehicle monitoring application — it is a complete **intelligent predictive maintenance ecosystem**. By combining multi-sensor IoT telemetry, real-time WebSocket streaming, AI-powered diagnostics, Remaining Useful Life prediction, conversational AI, agentic maintenance orchestration, and Qualcomm GenIE edge inference, the platform demonstrates how modern vehicles can evolve from **reactive maintenance** to **proactive, autonomous, and explainable vehicle intelligence**.

For the Qualcomm Snapdragon Hackathon, the entire architecture is designed to showcase real-time Edge AI — where sensor data flows seamlessly from hardware to AI inference and back to the user with minimal latency, enabling safer, smarter, and more reliable mobility.

✅ Multi-sensor vehicle intelligence · ✅ Predictive maintenance · ✅ Real-time IoT telemetry · ✅ Edge AI inference · ✅ Qualcomm AI Hub + GenIE · ✅ QNN + Hexagon NPU · ✅ Laptop + Mobile Snapdragon deployment · ✅ Explainable, agentic AI

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:CE0E2D,100:7A0000&height=4&width=1200" width="100%"/>
</div>

<a id="gallery"></a>
## 📸 Vehicle Prototype Gallery

<table>
<tr>
<td align="center" width="25%">
<br><br>
🖼️<br><i>Front View</i><br>
<sub>Add photo here</sub>
<br><br>
</td>
<td align="center" width="25%">
<br><br>
🖼️<br><i>Side View</i><br>
<sub>Add photo here</sub>
<br><br>
</td>
<td align="center" width="25%">
<br><br>
🖼️<br><i>Electronics Setup</i><br>
<sub>Add photo here</sub>
<br><br>
</td>
<td align="center" width="25%">
<br><br>
🖼️<br><i>Sensor Mounting</i><br>
<sub>Add photo here</sub>
<br><br>
</td>
</tr>
</table>

```markdown
<!-- Drop images into assets/images/ and reference them like this: -->
![Front View](assets/images/car_front.jpg)
![Side View](assets/images/car_side.jpg)
![Electronics Setup](assets/images/electronics_setup.jpg)
![Sensor Mounting](assets/images/sensor_mounting.jpg)
```

### 🎥 Demo Video

<div align="center">

![Demo Video](https://img.shields.io/badge/DEMO%20VIDEO-ADD%20GOOGLE%20DRIVE%20LINK%20HERE-CE0E2D?style=for-the-badge&labelColor=000000&logo=googledrive&logoColor=CE0E2D)

**📌 [ Paste your Google Drive demo video link here ]**

</div>

---

<a id="team"></a>
## 👥 Team PulseDrive

| Member | Email | Role |
|---|---|---|
| Tanish Aggarwal | tanishaggarwal.in@gmail.com | IoT & Machine Learning |
| Ishaan Maheshwari | ishaan.m16082006@gmail.com | IoT |
| Anshuman Dutta | anshuman.123dutta@gmail.com | Agentic AI |
| Yash Goel | yashgoel15119@gmail.com | Development |

---

## 📌 Project Highlights

<table>
<tr><th>🔧 Hardware</th><th>🧠 AI</th><th>🚀 Qualcomm</th></tr>
<tr>
<td>

- Arduino UNO Q
- Multiple Vehicle Sensors
- RC Vehicle Platform

</td>
<td>

- Machine Learning
- Neural Networks
- Agentic AI (6 agents)
- Predictive Maintenance
- RUL Estimation

</td>
<td>

- Qualcomm AI Hub
- Qualcomm GenIE SDK
- QNN Runtime
- Hexagon NPU Acceleration
- Snapdragon X Elite + 8 Elite Gen 5

</td>
</tr>
</table>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7A0000,100:CE0E2D&height=200&section=footer&text=Predict.%20Prevent.%20Protect.&fontSize=32&fontColor=FFFFFF&animation=fadeIn&fontAlignY=75" width="100%"/>

**Intelligent Vehicle Health Monitoring with Snapdragon Edge AI**

</div>
