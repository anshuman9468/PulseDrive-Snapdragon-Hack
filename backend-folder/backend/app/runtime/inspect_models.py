import os
import pickle
import onnxruntime as ort
import numpy as np
from ai_edge_litert.interpreter import Interpreter

def inspect_onnx(model_path):
    print(f"=== Inspecting ONNX Model: {os.path.basename(model_path)} ===")
    session = ort.InferenceSession(model_path)
    
    # Inputs info
    inputs = session.get_inputs()
    for i, inp in enumerate(inputs):
        print(f"Input {i}: name='{inp.name}', shape={inp.shape}, type={inp.type}")
        
    # Outputs info
    outputs = session.get_outputs()
    for i, out in enumerate(outputs):
        print(f"Output {i}: name='{out.name}', shape={out.shape}, type={out.type}")
        
    # Metadata info
    meta = session.get_modelmeta()
    print("Metadata props:", meta.custom_metadata_map)
    print("Model version:", meta.version)
    print("Producer name:", meta.producer_name)
    
    # Determine quantization
    # Usually quantized models have uint8 or int8 inputs/outputs, or ConvInteger/QLinearConv nodes.
    # We can list node types to be sure.
    model = ort.InferenceSession(model_path)
    # Check if input type is float32 or int8/uint8
    inp_type = inputs[0].type
    is_quantized = "int" in inp_type or "uint" in inp_type
    print(f"Quantized (heuristics): {is_quantized}")
    print()

def inspect_tflite(model_path):
    print(f"=== Inspecting TFLite Model: {os.path.basename(model_path)} ===")
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    # Get input and output details
    input_details = interpreter.get_input_details()
    for i, inp in enumerate(input_details):
        print(f"Input {i}: name='{inp['name']}', shape={inp['shape']}, dtype={inp['dtype']}, quantization={inp['quantization']}")
        
    output_details = interpreter.get_output_details()
    for i, out in enumerate(output_details):
        print(f"Output {i}: name='{out['name']}', shape={out['shape']}, dtype={out['dtype']}, quantization={out['quantization']}")
        
    # Quantization check
    quant = any(inp['quantization'] != (0.0, 0) for inp in input_details)
    print(f"Quantized: {quant}")
    print()

def inspect_scaler(scaler_path):
    print(f"=== Inspecting Scaler: {os.path.basename(scaler_path)} ===")
    scaler = None
    try:
        import joblib
        scaler = joblib.load(scaler_path)
        print("Loaded successfully with joblib")
    except Exception as je:
        print(f"Joblib load failed: {je}")
        try:
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            print("Loaded successfully with pickle")
        except Exception as pe:
            print(f"Pickle load failed: {pe}")
            return
        
    print("Type of scaler:", type(scaler).__name__)
    
    # Check attributes of StandardScaler or MinMaxScaler
    attrs = dir(scaler)
    if 'feature_names_in_' in attrs:
        print("Feature Names In (ordering):", scaler.feature_names_in_.tolist())
    else:
        print("Feature Names In: Not directly found (possibly no feature names fit during training)")
        
    if 'mean_' in attrs:
        print("Mean:", scaler.mean_.tolist())
    if 'var_' in attrs:
        print("Variance:", scaler.var_.tolist())
    if 'scale_' in attrs:
        print("Scale (Standard Deviation or Range):", scaler.scale_.tolist())
    if 'min_' in attrs:
        print("Min / Offset:", scaler.min_.tolist())
        
    # Check inverse transform capability
    has_inv = hasattr(scaler, 'inverse_transform')
    print("Has inverse_transform:", has_inv)
    print()

if __name__ == "__main__":
    inspect_onnx("/home/anshumandutta/Downloads/PulseDrive Snapdragon Hack/smoke_detector_static.onnx")
    inspect_tflite("/home/anshumandutta/Downloads/vehicle_state_model.tflite")
    inspect_tflite("/home/anshumandutta/Downloads/wheel_imbalance_model.tflite")
    inspect_scaler("/home/anshumandutta/Downloads/PulseDrive Snapdragon Hack/vehicle_state_scaler.pkl")
    inspect_scaler("/home/anshumandutta/Downloads/PulseDrive Snapdragon Hack/wheel_imbalance_scaler.pkl")
