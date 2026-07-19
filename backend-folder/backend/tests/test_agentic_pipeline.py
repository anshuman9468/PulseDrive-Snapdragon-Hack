import asyncio
import unittest
import unittest.mock
from typing import Dict, Any

# Adjust paths to match package structure
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.temperature_agent import TemperatureAgent
from app.agents.battery_agent import BatteryAgent
from app.agents.smoke_agent import SmokeAgent
from app.agents.gyro_agent import GyroAgent
from app.agents.brake_agent import BrakeAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.vehicle_state_agent import VehicleStateAgent
from app.agents.wheel_imbalance_agent import WheelImbalanceAgent
from app.orchestrator.planner import Planner
from app.orchestrator.fusion_engine import FusionEngine
from app.orchestrator.decision_engine import DecisionEngine
from app.orchestrator.orchestrator import AgentOrchestrator


class TestAgenticPipeline(unittest.IsolatedAsyncioTestCase):

    async def test_temperature_agent(self):
        agent = TemperatureAgent()
        self.assertEqual(agent.name(), "TemperatureAgent")
        self.assertTrue(agent.can_handle({"temperature": 85.0}))
        self.assertFalse(agent.can_handle({"speed": 100}))

        # Safe case
        res_safe = await agent.predict({"temperature": 70.0})
        self.assertEqual(res_safe.status, "safe")
        self.assertEqual(res_safe.severity, 0.0)

        # Warning case
        res_warn = await agent.predict({"temperature": 82.0})
        self.assertEqual(res_warn.status, "warning")
        self.assertGreater(res_warn.severity, 0.0)

        # Critical case
        res_crit = await agent.predict({"temperature": 101.0})
        self.assertEqual(res_crit.status, "critical")
        self.assertGreater(res_crit.severity, 60.0)

    async def test_battery_agent(self):
        agent = BatteryAgent()
        self.assertEqual(agent.name(), "BatteryAgent")
        self.assertTrue(agent.can_handle({"battery_voltage": 12.0}))

        # Safe
        res_safe = await agent.predict({"battery_voltage": 13.8})
        self.assertEqual(res_safe.status, "safe")

        # Warning Low
        res_warn = await agent.predict({"battery_voltage": 12.0})
        self.assertEqual(res_warn.status, "warning")

    async def test_smoke_agent(self):
        agent = SmokeAgent()
        self.assertEqual(agent.name(), "SmokeAgent")
        self.assertTrue(agent.can_handle({"smoke": {"gas_level": 120, "digital": 0}}))

        # Critical digital trigger
        res_crit = await agent.predict({"smoke": {"gas_level": 120, "digital": 1}})
        self.assertEqual(res_crit.status, "emergency")
        self.assertEqual(res_crit.severity, 99.0)

        # Warning gas level
        res_warn = await agent.predict({"smoke": {"gas_level": 350, "digital": 0}})
        self.assertEqual(res_warn.status, "warning")

    async def test_gyro_agent(self):
        agent = GyroAgent()
        self.assertEqual(agent.name(), "GyroAgent")
        
        # Severe vibration (rule fallback path)
        res = await agent.predict({"gyro": {"ax": 1.0, "ay": 8.0, "az": 12.0}})
        self.assertEqual(res.status, "critical")
        self.assertEqual(res.metadata.get("execution_mode"), "rule_fallback")

    @unittest.mock.patch('app.runtime.inference_engine.InferenceEngine.predict')
    async def test_gyro_agent_onnx_mode(self, mock_predict):
        agent = GyroAgent()
        
        # Mock predictions for dual runtimes
        def side_effect(model_name, features):
            if model_name == "gyro_incline":
                return {
                    "probabilities": [0.9, 0.1, 0.0],
                    "runtime_used": "ONNX Runtime",
                    "device_used": "CPU",
                    "execution_time_ms": 1.5
                }
            elif model_name == "vibration":
                return {
                    "probabilities": [0.05, 0.15, 0.80],
                    "runtime_used": "ONNX Runtime",
                    "device_used": "CPU",
                    "execution_time_ms": 2.0
                }
            return {"probabilities": [0.95, 0.04, 0.01], "runtime_used": "CPU Fallback", "device_used": "CPU", "execution_time_ms": 0.0}
            
        mock_predict.side_effect = side_effect
        
        res = await agent.predict({"gyro": {"ax": 0.0, "ay": 0.0, "az": 9.81}})
        self.assertEqual(res.metadata.get("execution_mode"), "onnx")
        self.assertEqual(res.status, "critical") # Max index is 2 (critical), severity < 85.0
        self.assertIn("Critical mechanical vibration anomaly detected", res.reason)


    async def test_brake_agent(self):
        agent = BrakeAgent()
        self.assertEqual(agent.name(), "BrakeAgent")
        
        # High pad wear
        res = await agent.predict({"brake": {"pressure": 800.0, "pad_wear": 92.0}})
        self.assertEqual(res.status, "emergency")

    async def test_planner(self):
        planner = Planner()
        sensor_json = {
            "temperature": 90.0,
            "battery_voltage": 12.5,
            "smoke": {"gas_level": 100, "digital": 0}
        }
        applicable = planner.plan(sensor_json)
        names = [a.name() for a in applicable]
        
        self.assertIn("TemperatureAgent", names)
        self.assertIn("BatteryAgent", names)
        self.assertIn("SmokeAgent", names)
        # RecommendationAgent should handle if any metrics are present
        self.assertIn("RecommendationAgent", names)
        
        # GyroAgent & BrakeAgent should not be in there as their keys are missing
        self.assertNotIn("GyroAgent", names)
        self.assertNotIn("BrakeAgent", names)

    async def test_fusion_and_decision_engine(self):
        orchestrator = AgentOrchestrator()
        
        # Test emergency vehicle state
        sensor_json = {
            "temperature": 110.0, # critical/emergency
            "battery_voltage": 10.5, # critical
            "smoke": {"gas_level": 850, "digital": 1}, # emergency
            "gyro": {"ax": 0.0, "ay": 0.0, "az": 9.8},
            "brake": {"pressure": 800.0, "pad_wear": 10.0}
        }
        
        result = await orchestrator.execute(sensor_json)
        
        self.assertEqual(result.vehicle_status, "EMERGENCY")
        self.assertLess(result.health_score, 20.0)
        self.assertGreater(result.risk_score, 80.0)
        self.assertTrue(len(result.agent_results) > 0)
        self.assertTrue(len(result.recommendations) > 0)
        
        # Verify de-duplication of recommendations
        self.assertEqual(len(result.recommendations), len(set(result.recommendations)))

    async def test_empty_or_malformed_sensor_packet(self):
        orchestrator = AgentOrchestrator()
        result = await orchestrator.execute({})
        
        self.assertEqual(result.vehicle_status, "SAFE")
        self.assertEqual(result.health_score, 100.0)
        self.assertEqual(result.risk_score, 0.0)
        self.assertEqual(len(result.agent_results), 0)

    async def test_vehicle_state_agent(self):
        agent = VehicleStateAgent()
        self.assertEqual(agent.name(), "VehicleStateAgent")
        self.assertTrue(agent.can_handle({"gyro": {}}))
        self.assertTrue(agent.can_handle({"MPU2_Accel_X": 1000.0}))
        
        # Test real model execution (without mock) to verify it loads and runs
        res = await agent.predict({
            "MPU2_Accel_X": 4040.3,
            "MPU2_Accel_Y": 597.7,
            "MPU2_Accel_Z": 13862.4,
            "MPU2_Gyro_X": 28.7,
            "MPU2_Gyro_Y": -2.2,
            "MPU2_Gyro_Z": -151.2
        })
        self.assertIn(res.status, ["safe", "warning", "critical", "emergency"])
        self.assertEqual(res.runtime_used, "LiteRT Runtime")
        self.assertEqual(res.device_used, "CPU")

    @unittest.mock.patch('app.runtime.inference_engine.InferenceEngine.predict')
    async def test_vehicle_state_agent_classification(self, mock_predict):
        agent = VehicleStateAgent()
        
        # Class 0: Normal -> safe
        mock_predict.return_value = {
            "probabilities": [0.95, 0.02, 0.02, 0.01],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "safe")
        self.assertEqual(res.prediction, "normal")

        # Class 1: Friction Anomaly -> warning
        mock_predict.return_value = {
            "probabilities": [0.05, 0.85, 0.05, 0.05],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "warning")
        self.assertEqual(res.prediction, "friction anomaly")

        # Class 2: Gyro Anomaly -> critical
        mock_predict.return_value = {
            "probabilities": [0.05, 0.05, 0.85, 0.05],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "critical")
        self.assertEqual(res.prediction, "gyro anomaly")

        # Class 3: Critical State -> emergency
        mock_predict.return_value = {
            "probabilities": [0.01, 0.04, 0.05, 0.90],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "emergency")
        self.assertEqual(res.prediction, "critical state")

    async def test_wheel_imbalance_agent(self):
        agent = WheelImbalanceAgent()
        self.assertEqual(agent.name(), "WheelImbalanceAgent")
        self.assertTrue(agent.can_handle({"gyro": {}}))
        self.assertTrue(agent.can_handle({"MPU1_Gyro_X": 1000.0}))

        # Test real model execution
        res = await agent.predict({
            "MPU1_Gyro_X": 1693.9,
            "MPU1_Gyro_Y": 67.8,
            "MPU1_Gyro_Z": -207.7
        })
        self.assertIn(res.status, ["safe", "warning", "critical", "emergency"])
        self.assertEqual(res.runtime_used, "LiteRT Runtime")
        self.assertEqual(res.device_used, "CPU")

    @unittest.mock.patch('app.runtime.inference_engine.InferenceEngine.predict')
    async def test_wheel_imbalance_agent_classification(self, mock_predict):
        agent = WheelImbalanceAgent()

        # Class 0: Normal -> safe
        mock_predict.return_value = {
            "probabilities": [0.95, 0.05],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "safe")
        self.assertEqual(res.prediction, "normal")

        # Class 1: Imbalanced (high prob) -> critical
        mock_predict.return_value = {
            "probabilities": [0.15, 0.85],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "critical")
        self.assertEqual(res.prediction, "imbalanced")

        # Class 1: Imbalanced (medium prob) -> warning
        mock_predict.return_value = {
            "probabilities": [0.35, 0.65],
            "runtime_used": "LiteRT Runtime",
            "device_used": "CPU",
            "execution_time_ms": 1.0
        }
        res = await agent.predict({"gyro": {}})
        self.assertEqual(res.status, "warning")
        self.assertEqual(res.prediction, "imbalanced")

    async def test_risk_assessment_agent(self):
        from app.agents.risk_assessment_agent import RiskAssessmentAgent
        from app.models.prediction_models import AgentPredictionResult
        
        agent = RiskAssessmentAgent()
        self.assertEqual(agent.name(), "RiskAssessmentAgent")
        self.assertFalse(agent.can_handle({}))
        
        # Test default predict method
        pred_res = await agent.predict({})
        self.assertEqual(pred_res.status, "safe")
        
        # Test assess with no results
        assess_empty = agent.assess([])
        self.assertEqual(assess_empty["risk_score"], 0.0)
        self.assertEqual(assess_empty["failure_probability"], 0.0)
        
        # Test assess with normal safe results
        safe_result = AgentPredictionResult(
            agent="TempAgent", status="safe", confidence=1.0, severity=0.0,
            reason="Normal", prediction="normal", execution_time_ms=0.0,
            runtime_used="CPU", device_used="CPU"
        )
        assess_safe = agent.assess([safe_result], last_risk_score=10.0)
        self.assertEqual(assess_safe["risk_score"], 0.0)
        self.assertEqual(assess_safe["risk_trend"], "decreasing")
        
        # Test assess with anomaly
        anomaly_result = AgentPredictionResult(
            agent="TempAgent", status="critical", confidence=0.9, severity=75.0,
            reason="High Temperature", prediction="critical", execution_time_ms=0.0,
            runtime_used="CPU", device_used="CPU"
        )
        assess_anomaly = agent.assess([anomaly_result], last_risk_score=50.0)
        self.assertEqual(assess_anomaly["risk_score"], 75.0)
        self.assertEqual(assess_anomaly["risk_trend"], "increasing")
        self.assertGreater(assess_anomaly["failure_probability"], 0.5)

if __name__ == '__main__':
    unittest.main()

