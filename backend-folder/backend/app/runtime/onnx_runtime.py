import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class ONNXRuntime:
    """Wrapper for ONNX Runtime inference on CPU/GPU."""

    def __init__(self, model_path: Optional[str] = None):
        self.session = None
        self.input_name = None
        self.output_name = None
        self.model_path = model_path
        
        if model_path:
            self._load_model(model_path)

    def _load_model(self, model_path: str) -> None:
        """Dynamically import and initialize the ONNX Runtime session."""
        if not os.path.exists(model_path):
            logger.warning(f"ONNX model file not found at: {model_path}. Running in simulation mode.")
            return

        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(model_path)
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            logger.info(f"Loaded ONNX model successfully from {model_path}")
        except ImportError:
            logger.warning("onnxruntime is not installed. Running in simulation mode. Install with: pip install onnxruntime")
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")

    def run(self, input_features: List[float]) -> List[float]:
        """Run model prediction. Fallbacks to simulation if no model is loaded.
        
        Args:
            input_features: List of numerical features.
            
        Returns:
            List of predicted output logits or probabilities.
        """
        if self.session is None:
            # Simulation Mode: Predict status based on average of feature values
            avg_value = sum(input_features) / max(1, len(input_features))
            # Return mock probabilities for [Safe, Warning, Critical/Emergency]
            if avg_value > 80:
                return [0.05, 0.15, 0.80]
            elif avg_value > 50:
                return [0.15, 0.65, 0.20]
            else:
                return [0.85, 0.10, 0.05]

        try:
            import numpy as np
            input_data = np.array([input_features], dtype=np.float32)
            outputs = self.session.run([self.output_name], {self.input_name: input_data})
            return outputs[0][0].tolist()
        except Exception as e:
            logger.error(f"ONNX Runtime inference failed: {e}. Falling back to simulation.")
            return [0.33, 0.33, 0.34]
