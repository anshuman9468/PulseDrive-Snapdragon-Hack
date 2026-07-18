#!/usr/bin/env python3
"""
Example usage of the Prediction module.

This script demonstrates how to:
1. Use the PredictionService directly
2. Generate mock predictions
3. Load and use a real model
4. Test the API endpoints
"""

import json
from datetime import datetime
from app.models.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService


def example_1_mock_predictions():
    """Example 1: Generate mock predictions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Mock Predictions")
    print("=" * 60)

    # Initialize service with mock predictions
    service = PredictionService()
    print(f"Service Status: Model Loaded = {service.model is not None}, Using Mock = {service.use_mock}")

    # Generate predictions for multiple vehicles
    vehicles = ["VH001", "VH002", "VH003", "VH999"]

    for vehicle_id in vehicles:
        request = PredictionRequest(
            vehicleId=vehicle_id,
            features={
                "rpm": 3000,
                "temperature": 85,
                "mileage": 45000,
                "fuel_consumption": 8.5,
                "battery_voltage": 13.5,
            },
        )

        response = service.predict(request)

        print(f"\nVehicle: {response.vehicleId}")
        print(f"  Health Score: {response.healthScore:.1f}")
        print(f"  Status: {response.status}")
        print(f"  Confidence: {response.confidence:.2%}")
        print(f"  Recommendation: {response.recommendation}")


def example_2_load_model():
    """Example 2: Load a real model (if available)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Loading Real Model")
    print("=" * 60)

    # Try to load a model from file
    model_path = "app/models/vehicle_health_model.pkl"
    print(f"Attempting to load model from: {model_path}")

    service = PredictionService(model_path=model_path)
    print(f"Service Status: Model Loaded = {service.model is not None}, Using Mock = {service.use_mock}")

    if not service.use_mock and service.model is not None:
        print("Model loaded successfully!")
        print("  Future predictions will use the real model.")
    else:
        print("Model not available, using mock predictions.")
        print("  To use a real model, place 'vehicle_health_model.pkl' in 'app/models/'")


def example_3_custom_features():
    """Example 3: Generate predictions with custom features."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Features")
    print("=" * 60)

    service = PredictionService()

    # Different feature scenarios
    scenarios = [
        {
            "name": "High RPM, High Temperature",
            "features": {
                "rpm": 5500,
                "temperature": 95,
                "mileage": 120000,
                "fuel_consumption": 12.0,
                "battery_voltage": 12.5,
            },
        },
        {
            "name": "Normal Operation",
            "features": {
                "rpm": 2000,
                "temperature": 80,
                "mileage": 30000,
                "fuel_consumption": 7.5,
                "battery_voltage": 13.8,
            },
        },
        {
            "name": "Minimal Data",
            "features": None,  # Empty features
        },
    ]

    for scenario in scenarios:
        request = PredictionRequest(
            vehicleId="VH_SCENARIO",
            features=scenario["features"],
        )

        response = service.predict(request)

        print(f"\n{scenario['name']}")
        print(f"  Health Score: {response.healthScore:.1f}")
        print(f"  Status: {response.status}")
        print(f"  Recommendation: {response.recommendation}")


def example_4_batch_prediction():
    """Example 4: Batch predictions for fleet."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Fleet Batch Predictions")
    print("=" * 60)

    service = PredictionService()

    # Simulate fleet data
    fleet = {
        f"TRUCK_{i:04d}": {
            "rpm": 2000 + (i % 3) * 500,
            "temperature": 80 + (i % 5) * 2,
            "mileage": 10000 * i,
            "fuel_consumption": 7.0 + (i % 3),
            "battery_voltage": 13.2 + (i % 3) * 0.3,
        }
        for i in range(1, 6)
    }

    print(f"\nProcessing {len(fleet)} vehicles:")

    # Generate predictions
    predictions = []
    for vehicle_id, features in fleet.items():
        request = PredictionRequest(vehicleId=vehicle_id, features=features)
        response = service.predict(request)
        predictions.append(response)

    # Summary statistics
    scores = [p.healthScore for p in predictions]
    statuses = [p.status for p in predictions]

    print(f"\nFleet Summary:")
    print(f"  Total Vehicles: {len(predictions)}")
    print(f"  Average Health Score: {sum(scores) / len(scores):.1f}")
    print(f"  Min Score: {min(scores):.1f}, Max Score: {max(scores):.1f}")
    print(f"\nStatus Breakdown:")
    print(f"  Healthy: {statuses.count('healthy')}")
    print(f"  Warning: {statuses.count('warning')}")
    print(f"  Critical: {statuses.count('critical')}")

    # Critical vehicles needing attention
    critical_vehicles = [p for p in predictions if p.status == "critical"]
    if critical_vehicles:
        print(f"\nVehicles Requiring Attention:")
        for pred in critical_vehicles:
            print(f"  - {pred.vehicleId}: {pred.recommendation}")


def example_5_response_serialization():
    """Example 5: Serialize/deserialize responses."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Response Serialization")
    print("=" * 60)

    service = PredictionService()

    request = PredictionRequest(
        vehicleId="VH_JSON_TEST",
        features={"rpm": 3000, "temperature": 85},
    )

    response = service.predict(request)

    # Serialize to JSON
    response_json = response.model_dump_json(indent=2)
    print("\nSerialized Response (JSON):")
    print(response_json)

    # Parse back
    parsed = PredictionResponse.model_validate_json(response_json)
    print(f"\nDeserialized Vehicle ID: {parsed.vehicleId}")
    print(f"Deserialized Health Score: {parsed.healthScore}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("PREDICTION MODULE - USAGE EXAMPLES")
    print("=" * 60)

    try:
        example_1_mock_predictions()
        example_2_load_model()
        example_3_custom_features()
        example_4_batch_prediction()
        example_5_response_serialization()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nError during examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
