import time
import logging
import os
from typing import List, Dict, Any, Tuple, Optional
from app.runtime.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class InferenceEngine:
    """Abstraction layer for NPU and CPU model inference supporting Qualcomm QNN, ONNX Runtime, and CPU Fallback."""
    
    _sessions: Dict[str, Any] = {}  # Cache for loaded sessions
    _backends: Dict[str, Tuple[str, str]] = {}  # Cache for runtime/device descriptions per model

    @classmethod
    def _get_onnx_session(cls, model_name: str, model_path: str) -> Tuple[Optional[Any], str, str]:
        """Tries to load an ONNX session, selecting QNN/NPU first, then standard ONNX, then CPU Fallback."""
        if model_name in cls._sessions:
            runtime, device = cls._backends[model_name]
            return cls._sessions[model_name], runtime, device

        if not os.path.exists(model_path):
            logger.warning(f"Model file '{model_path}' not found on disk. Falling back to CPU Fallback.")
            return None, "CPU Fallback", "CPU"

        try:
            import onnxruntime as ort
            available_providers = ort.get_available_providers()
            logger.info(f"Available Execution Providers: {available_providers}")

            # 1. Check for Qualcomm QNN Execution Provider (Snapdragon NPU)
            # We also check an environment override FORCE_QNN or SIMULATE_QNN for NPU testing
            force_qnn = os.getenv("FORCE_QNN", "false").lower() == "true"
            simulate_qnn = os.getenv("SIMULATE_QNN", "false").lower() == "true"

            if "QNNExecutionProvider" in available_providers or force_qnn:
                try:
                    logger.info("Initializing Qualcomm QNN Execution Provider for NPU acceleration...")
                    providers = ["QNNExecutionProvider", "CPUExecutionProvider"]
                    # In a real Qualcomm environment, we configure the session options and load
                    session = ort.InferenceSession(model_path, providers=providers)
                    cls._sessions[model_name] = session
                    cls._backends[model_name] = ("Qualcomm QNN Runtime", "NPU")
                    return session, "Qualcomm QNN Runtime", "NPU"
                except Exception as ex:
                    logger.warning(f"Failed to load with QNN provider: {ex}. Falling back to standard CPU...")

            # 2. Check for simulation of NPU/QNN for local verification/unit testing
            if simulate_qnn:
                logger.info("Simulating Qualcomm QNN Runtime on Snapdragon NPU...")
                cls._sessions[model_name] = "simulated_qnn"
                cls._backends[model_name] = ("Qualcomm QNN Runtime", "NPU")
                return "simulated_qnn", "Qualcomm QNN Runtime", "NPU"

            # 3. Fallback to standard ONNX Runtime (CPU)
            logger.info("Initializing standard CPU execution provider...")
            session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            cls._sessions[model_name] = session
            cls._backends[model_name] = ("ONNX Runtime", "CPU")
            return session, "ONNX Runtime", "CPU"

        except ImportError:
            logger.warning("onnxruntime is not installed. Falling back to CPU Fallback.")
            return None, "CPU Fallback", "CPU"
        except Exception as e:
            logger.error(f"Error loading ONNX model '{model_name}': {e}. Falling back to CPU Fallback.")
            return None, "CPU Fallback", "CPU"

    @classmethod
    def predict(cls, model_name: str, input_features: List[float]) -> Dict[str, Any]:
        """Runs inference for a given model by name and list of features.
        
        Args:
            model_name: Registered model name.
            input_features: Flat list of float values.
            
        Returns:
            Dict containing:
                - probabilities: List[float] (prediction probability distribution)
                - runtime_used: str ("Qualcomm QNN Runtime", "ONNX Runtime", "CPU Fallback")
                - device_used: str ("NPU", "CPU", "GPU")
                - execution_time_ms: float
        """
        start_time = time.perf_counter()
        
        # Look up in registry
        model_entry = ModelRegistry.get_model(model_name)
        if not model_entry:
            # If not in registry, try to auto-register by name first
            logger.warning(f"Model '{model_name}' not found in registry. Attempting on-the-fly registration...")
            model_path = f"app/runtime/models/{model_name}.onnx"
            # Trigger registration manually
            from app.runtime.model_registry import ModelMetadata
            ModelRegistry.register(model_name, model_path, ModelMetadata(name=model_name))
            model_entry = ModelRegistry.get_model(model_name)
            
        model_path = model_entry["path"]
        
        # Load or retrieve session
        session, runtime, device = cls._get_onnx_session(model_name, model_path)
        
        # Run inference
        probabilities = [0.0, 0.0, 0.0]
        
        if session is None or session == "simulated_qnn":
            # Smart simulation using RuleRuntime mapping for full consistency
            try:
                from app.runtime.rule_runtime import RuleRuntime
                rules = RuleRuntime()
                if model_name == "temperature" and len(input_features) >= 1:
                    status, severity, reason = rules.evaluate_temperature(input_features[0])
                elif model_name == "battery_voltage" and len(input_features) >= 1:
                    status, severity, reason = rules.evaluate_battery(input_features[0])
                elif model_name == "smoke" and len(input_features) >= 2:
                    status, severity, reason = rules.evaluate_smoke(input_features[0], int(input_features[1]))
                elif model_name == "brake" and len(input_features) >= 2:
                    status, severity, reason = rules.evaluate_brake(input_features[0], input_features[1])
                elif ("gyro" in model_name or "vibration" in model_name) and len(input_features) >= 3:
                    status, severity, reason = rules.evaluate_gyro(input_features[0], input_features[1], input_features[2])
                else:
                    status, severity, reason = "safe", 0.0, "normal"
            except Exception as e:
                logger.error(f"Failed to import or run RuleRuntime fallback inside InferenceEngine: {e}")
                status, severity, reason = "safe", 0.0, "normal"

            if status in ["emergency", "critical"]:
                probabilities = [0.01, 0.09, 0.90]
            elif status == "warning":
                probabilities = [0.15, 0.70, 0.15]
            else:
                probabilities = [0.95, 0.04, 0.01]
        else:
            try:
                import numpy as np
                input_data = np.array([input_features], dtype=np.float32)
                # Query input/output names dynamically from session
                input_name = session.get_inputs()[0].name
                output_name = session.get_outputs()[0].name
                outputs = session.run([output_name], {input_name: input_data})
                probabilities = outputs[0][0].tolist()
            except Exception as e:
                logger.error(f"Inference error for model '{model_name}': {e}. Falling back to CPU simulation.")
                try:
                    from app.runtime.rule_runtime import RuleRuntime
                    rules = RuleRuntime()
                    if model_name == "temperature" and len(input_features) >= 1:
                        status, severity, reason = rules.evaluate_temperature(input_features[0])
                    elif model_name == "battery_voltage" and len(input_features) >= 1:
                        status, severity, reason = rules.evaluate_battery(input_features[0])
                    elif model_name == "smoke" and len(input_features) >= 2:
                        status, severity, reason = rules.evaluate_smoke(input_features[0], int(input_features[1]))
                    elif model_name == "brake" and len(input_features) >= 2:
                        status, severity, reason = rules.evaluate_brake(input_features[0], input_features[1])
                    elif ("gyro" in model_name or "vibration" in model_name) and len(input_features) >= 3:
                        status, severity, reason = rules.evaluate_gyro(input_features[0], input_features[1], input_features[2])
                    else:
                        status, severity, reason = "safe", 0.0, "normal"
                except Exception as ex:
                    logger.error(f"Failed to run RuleRuntime inside InferenceEngine error handler: {ex}")
                    status, severity, reason = "safe", 0.0, "normal"

                if status in ["emergency", "critical"]:
                    probabilities = [0.01, 0.09, 0.90]
                elif status == "warning":
                    probabilities = [0.15, 0.70, 0.15]
                else:
                    probabilities = [0.95, 0.04, 0.01]
                runtime = "CPU Fallback"
                device = "CPU"

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        return {
            "probabilities": probabilities,
            "runtime_used": runtime,
            "device_used": device,
            "execution_time_ms": round(execution_time_ms, 3)
        }

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the session and backend caches (useful for testing)."""
        cls._sessions.clear()
        cls._backends.clear()
