import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModelMetadata:
    """Metadata representing an ONNX/NPU model deployment."""
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        input_tensor: str = "input",
        output_tensor: str = "output",
        input_shape: str = "[-1, 3]",
        classes: str = "Safe, Warning, Critical",
        execution_backend: str = "ONNX Runtime",
        quantization: str = "FP32",
        target_device: str = "CPU"
    ):
        self.name = name
        self.version = version
        self.input_tensor = input_tensor
        self.output_tensor = output_tensor
        self.input_shape = input_shape
        self.classes = classes
        self.execution_backend = execution_backend
        self.quantization = quantization
        self.target_device = target_device

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "input_tensor": self.input_tensor,
            "output_tensor": self.output_tensor,
            "input_shape": self.input_shape,
            "classes": self.classes,
            "execution_backend": self.execution_backend,
            "quantization": self.quantization,
            "target_device": self.target_device
        }

class ModelRegistry:
    """Central registry tracking all active ONNX and Snapdragon NPU models."""
    _models: Dict[str, Dict[str, Any]] = {}
    _models_dir = "app/runtime/models"

    @classmethod
    def register(cls, name: str, model_path: str, metadata: ModelMetadata) -> None:
        """Register a model path and its metadata."""
        cls._models[name] = {
            "path": model_path,
            "metadata": metadata
        }
        logger.info(f"Successfully registered model '{name}' at '{model_path}' [Target: {metadata.target_device}].")

    @classmethod
    def get_model(cls, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve model metadata by model name."""
        return cls._models.get(name)

    @classmethod
    def list_models(cls) -> Dict[str, Dict[str, Any]]:
        """List all registered models."""
        return cls._models

    @classmethod
    def auto_register_models(cls) -> None:
        """Scan models directory and auto-register ONNX files with optional JSON metadata."""
        # Ensure directory exists relative to current working directory
        if not os.path.exists(cls._models_dir):
            os.makedirs(cls._models_dir, exist_ok=True)
            
        for file in os.listdir(cls._models_dir):
            if file.endswith(".onnx"):
                model_name = os.path.splitext(file)[0]
                model_path = os.path.join(cls._models_dir, file)
                json_path = os.path.join(cls._models_dir, f"{model_name}.json")
                
                metadata = None
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r") as f:
                            data = json.load(f)
                            metadata = ModelMetadata(
                                name=data.get("name", model_name),
                                version=data.get("version", "1.0.0"),
                                input_tensor=data.get("input_tensor", "input"),
                                output_tensor=data.get("output_tensor", "output"),
                                input_shape=data.get("input_shape", "[-1, 3]"),
                                classes=data.get("classes", "Safe, Warning, Critical"),
                                execution_backend=data.get("execution_backend", "ONNX Runtime"),
                                quantization=data.get("quantization", "FP32"),
                                target_device=data.get("target_device", "CPU")
                            )
                    except Exception as e:
                        logger.error(f"Failed to read model metadata JSON for '{model_name}': {e}")
                
                if metadata is None:
                    # Provide smart default metadata depending on the model name
                    if "gyro" in model_name:
                        metadata = ModelMetadata(
                            name=model_name,
                            version="1.0.0",
                            input_shape="[-1, 3]",
                            classes="Safe, Warning, Critical",
                            target_device="CPU"
                        )
                    elif "vibration" in model_name:
                        metadata = ModelMetadata(
                            name=model_name,
                            version="1.0.0",
                            input_shape="[-1, 3]",
                            classes="Safe, Warning, Critical",
                            target_device="CPU"
                        )
                    else:
                        metadata = ModelMetadata(name=model_name)
                
                cls.register(model_name, model_path, metadata)

# Run auto-registration on startup
ModelRegistry.auto_register_models()
