# PulseDrive — Model Documentation

## Overview

The PulseDrive model classifies vehicle health into three categories
based on real-time sensor readings.

---

## Classification Labels

| Index | Label    | Risk Level | Description                              |
|-------|----------|------------|------------------------------------------|
| 0     | NORMAL   | LOW        | All sensors within expected ranges       |
| 1     | WARNING  | MEDIUM     | Minor anomaly detected, monitor closely  |
| 2     | CRITICAL | HIGH       | Serious fault, immediate action required |

---

## Input Features

| Feature     | Unit      | Description                   | Expected Range  |
|-------------|-----------|-------------------------------|-----------------|
| temperature | °C        | Battery/engine temperature    | -40 → 150       |
| current     | Amperes   | Electrical current draw       | 0 → 100         |
| smoke       | Binary    | Smoke sensor reading          | 0 or 1          |
| vibration   | g-force   | Vibration magnitude           | 0 → 20          |
| speed       | km/h      | Vehicle speed                 | 0 → 300         |

---

## Architecture (To Be Finalized)

**Option A (Prototype):** XGBoost Classifier
- Input: 5 features (+ derived features)
- Output: 3-class probability vector
- Export: skl2onnx → .onnx
- Size: ~100KB

**Option B (Production):** MLP Neural Network
- Input: 5 features
- Hidden: 2 × Dense(64, ReLU)
- Output: Dense(3, Softmax)
- Export: PyTorch → ONNX
- Size: ~200KB

---

## ONNX Specification

| Property       | Value                   |
|----------------|-------------------------|
| Opset Version  | 17                      |
| Input Name     | float_input             |
| Input Shape    | (1, 5) float32          |
| Output Name    | output_probability      |
| Output Shape   | (1, 3) float32          |

---

## Qualcomm Optimization

After ONNX export, the model is compiled by Qualcomm AI Hub for
Snapdragon HTP with INT8 quantization.

**Expected improvements:**
- ~10× latency reduction
- ~4× model size reduction (INT8)
- ~5× power efficiency improvement

---

## TODO

- [ ] Finalize model architecture choice (XGBoost vs. MLP)
- [ ] Collect and label real vehicle sensor dataset
- [ ] Train and evaluate model
- [ ] Export to ONNX
- [ ] Submit to Qualcomm AI Hub
- [ ] Populate benchmark results in `qualcomm/benchmark.md`
