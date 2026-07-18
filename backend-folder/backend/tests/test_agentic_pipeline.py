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
        
        self.assertEqual(result.vehicle_status, "Emergency")
        self.assertLess(result.health_score, 20.0)
        self.assertGreater(result.risk_score, 80.0)
        self.assertTrue(len(result.agent_results) > 0)
        self.assertTrue(len(result.recommendations) > 0)
        
        # Verify de-duplication of recommendations
        self.assertEqual(len(result.recommendations), len(set(result.recommendations)))

    async def test_empty_or_malformed_sensor_packet(self):
        orchestrator = AgentOrchestrator()
        result = await orchestrator.execute({})
        
        self.assertEqual(result.vehicle_status, "Safe")
        self.assertEqual(result.health_score, 100.0)
        self.assertEqual(result.risk_score, 0.0)
        self.assertEqual(len(result.agent_results), 0)

if __name__ == '__main__':
    unittest.main()
