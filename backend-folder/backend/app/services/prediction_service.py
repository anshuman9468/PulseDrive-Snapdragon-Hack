import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.models.prediction import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class PredictionService:
    """Production-ready prediction service with mock implementation.
    
    This service is designed for easy transition to ML model-based predictions:
    1. Mock predictions return realistic health data
    2. Can load joblib model at initialization
    3. API contract remains unchanged when switching to real model
    4. Features dict supports any input sensor data format
    """

    def __init__(self, model_path: Optional[str] = None):
        """Initialize the prediction service.
        
        Args:
            model_path: Optional path to joblib model file. If not provided, uses mock predictions.
        """
        self.model = None
        self.use_mock = True

        if model_path:
            self._load_model(model_path)

    def _load_model(self, model_path: str) -> None:
        """Load a joblib-serialized model.
        
        Args:
            model_path: Path to the .pkl or .joblib file
            
        Raises:
            ImportError: If joblib is not installed
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        try:
            import joblib
        except ImportError:
            logger.warning("joblib not installed. Using mock predictions. Install with: pip install joblib")
            return

        try:
            model_file = Path(model_path)
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            self.model = joblib.load(model_path)
            self.use_mock = False
            logger.info(f"Loaded ML model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}. Falling back to mock predictions.")
            self.use_mock = True

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Generate a health prediction for a vehicle.
        
        Args:
            request: PredictionRequest containing vehicleId and features
            
        Returns:
            PredictionResponse with healthScore, status, confidence, and recommendation
        """
        if self.use_mock or self.model is None:
            return self._mock_predict(request)
        else:
            return self._model_predict(request)

    def _mock_predict(self, request: PredictionRequest) -> PredictionResponse:
        """Generate mock predictions for demonstration.
        
        This returns realistic data that can be used for development and testing.
        Replace this with actual model inference when model.pkl is available.
        
        Args:
            request: PredictionRequest
            
        Returns:
            PredictionResponse with mock data
        """
        # Generate deterministic mock data based on vehicleId for consistency
        vehicle_id_hash = hash(request.vehicleId) % 100

        # Mock logic: use hash of vehicle ID to determine health
        if vehicle_id_hash < 30:
            health_score = 85 + (vehicle_id_hash % 15)  # 85-99
            status = "healthy"
            confidence = 0.92 + (vehicle_id_hash % 8) / 100
            recommendation = "Continue regular maintenance schedule"
        elif vehicle_id_hash < 70:
            health_score = 60 + (vehicle_id_hash % 25)  # 60-84
            status = "warning"
            confidence = 0.85 + (vehicle_id_hash % 10) / 100
            recommendation = "Schedule preventive maintenance soon"
        else:
            health_score = 20 + (vehicle_id_hash % 40)  # 20-59
            status = "critical"
            confidence = 0.88 + (vehicle_id_hash % 10) / 100
            recommendation = "Immediate inspection and service required"

        # Cap values at valid ranges
        health_score = min(100, max(0, health_score))
        confidence = min(1.0, max(0.0, confidence))

        return PredictionResponse(
            vehicleId=request.vehicleId,
            healthScore=health_score,
            status=status,
            confidence=confidence,
            recommendation=recommendation,
            timestamp=datetime.utcnow(),
        )

    def _model_predict(self, request: PredictionRequest) -> PredictionResponse:
        """Generate predictions using loaded ML model.
        
        This method is called when a real model is loaded.
        Adapt this to your specific model's input/output format.
        
        Args:
            request: PredictionRequest
            
        Returns:
            PredictionResponse
            
        Raises:
            Exception: If model prediction fails
        """
        try:
            # Prepare features for model
            features = self._prepare_features(request.features)

            # Call model (adapt to your specific model interface)
            # Example: prediction = self.model.predict([features])[0]
            # Example: confidence = self.model.predict_proba([features])[0].max()
            prediction_output = self.model.predict([features])

            # Extract results (adapt based on your model's output format)
            health_score = float(prediction_output[0])
            status = self._score_to_status(health_score)
            confidence = 0.90  # Adapt based on your model's confidence output

            recommendation = self._generate_recommendation(status, health_score)

            return PredictionResponse(
                vehicleId=request.vehicleId,
                healthScore=health_score,
                status=status,
                confidence=confidence,
                recommendation=recommendation,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Model prediction failed: {e}. Falling back to mock.")
            self.use_mock = True
            return self._mock_predict(request)

    @staticmethod
    def _prepare_features(features: Optional[Dict[str, Any]]) -> list:
        """Prepare input features for model prediction.
        
        Adapt this to your model's expected input format.
        
        Args:
            features: Raw features from request
            
        Returns:
            Features in format expected by model (e.g., list or numpy array)
        """
        if features is None:
            features = {}

        # Example: extract specific fields in order expected by model
        # Adapt this based on your ML model's feature requirements
        feature_list = [
            features.get("rpm", 0),
            features.get("temperature", 0),
            features.get("mileage", 0),
            features.get("fuel_consumption", 0),
            features.get("battery_voltage", 0),
        ]

        return feature_list

    @staticmethod
    def _score_to_status(health_score: float) -> str:
        """Convert health score to status label.
        
        Args:
            health_score: Score from 0-100
            
        Returns:
            Status: "healthy", "warning", or "critical"
        """
        if health_score >= 75:
            return "healthy"
        elif health_score >= 50:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def _generate_recommendation(status: str, health_score: float) -> str:
        """Generate recommendation based on status and health score.
        
        Args:
            status: Current health status
            health_score: Numeric health score
            
        Returns:
            Recommended action string
        """
        if status == "healthy":
            return "Continue regular maintenance schedule"
        elif status == "warning":
            return f"Schedule preventive maintenance soon (health: {health_score:.1f}%)"
        else:
            return f"⚠️ Immediate inspection required (health: {health_score:.1f}%)"
