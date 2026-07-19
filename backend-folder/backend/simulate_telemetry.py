import asyncio
import json
import random
import sys
import argparse
from datetime import datetime
import websockets

# WebSocket server address
WS_URL = "ws://localhost:8000/ws/live"

# Setup different scenarios
SCENARIOS = {
    "1": {
        "name": "Normal (Healthy State)",
        "temperature": lambda: random.uniform(65.0, 72.0),
        "voltage": lambda: random.uniform(12.8, 13.8),
        "gas_value": lambda: random.uniform(10.0, 45.0),
        "ax": lambda: random.uniform(-0.1, 0.1),
        "ay": lambda: random.uniform(-0.1, 0.1),
        "az": lambda: random.uniform(9.7, 9.9),
        "gx": lambda: random.uniform(-1.0, 1.0),
        "gy": lambda: random.uniform(-1.0, 1.0),
        "gz": lambda: random.uniform(-1.0, 1.0),
    },
    "2": {
        "name": "High Temperature Warning",
        "temperature": lambda: random.uniform(85.0, 95.0),
        "voltage": lambda: random.uniform(12.5, 13.2),
        "gas_value": lambda: random.uniform(15.0, 50.0),
        "ax": lambda: random.uniform(-0.1, 0.1),
        "ay": lambda: random.uniform(-0.1, 0.1),
        "az": lambda: random.uniform(9.7, 9.9),
        "gx": lambda: random.uniform(-1.0, 1.0),
        "gy": lambda: random.uniform(-1.0, 1.0),
        "gz": lambda: random.uniform(-1.0, 1.0),
    },
    "3": {
        "name": "Battery Voltage Degradation",
        "temperature": lambda: random.uniform(70.0, 75.0),
        "voltage": lambda: random.uniform(9.5, 10.8),
        "gas_value": lambda: random.uniform(10.0, 40.0),
        "ax": lambda: random.uniform(-0.1, 0.1),
        "ay": lambda: random.uniform(-0.1, 0.1),
        "az": lambda: random.uniform(9.7, 9.9),
        "gx": lambda: random.uniform(-1.0, 1.0),
        "gy": lambda: random.uniform(-1.0, 1.0),
        "gz": lambda: random.uniform(-1.0, 1.0),
    },
    "4": {
        "name": "Smoke/Gas Leak Emergency",
        "temperature": lambda: random.uniform(95.0, 115.0),
        "voltage": lambda: random.uniform(12.0, 13.0),
        "gas_value": lambda: random.uniform(400.0, 850.0),
        "ax": lambda: random.uniform(-0.1, 0.1),
        "ay": lambda: random.uniform(-0.1, 0.1),
        "az": lambda: random.uniform(9.7, 9.9),
        "gx": lambda: random.uniform(-1.0, 1.0),
        "gy": lambda: random.uniform(-1.0, 1.0),
        "gz": lambda: random.uniform(-1.0, 1.0),
    },
    "5": {
        "name": "Severe Vibration / Wheel Imbalance",
        "temperature": lambda: random.uniform(68.0, 74.0),
        "voltage": lambda: random.uniform(12.8, 13.5),
        "gas_value": lambda: random.uniform(10.0, 35.0),
        "ax": lambda: random.uniform(-1.5, 1.5),
        "ay": lambda: random.uniform(-1.5, 1.5),
        "az": lambda: random.uniform(7.5, 11.5),
        "gx": lambda: random.uniform(-15.0, 15.0),
        "gy": lambda: random.uniform(-15.0, 15.0),
        "gz": lambda: random.uniform(-15.0, 15.0),
    }
}

async def listen_to_server(ws):
    """Listens for and displays real-time server messages (diagnostics, traces, etc.)."""
    try:
        async for message in ws:
            try:
                data = json.loads(message)
                msg_type = data.get("type", "unknown")
                if msg_type == "prediction_update":
                    print(f"\n[AI Prediction Update]")
                    print(f"  Vehicle Status    : {data.get('status', 'N/A').upper()}")
                    print(f"  Health Score      : {data.get('healthScore', 'N/A')}%")
                    print(f"  Risk Score / Prob : {data.get('riskScore', 0)}% / {data.get('failureProbability', 0)}")
                    print(f"  Primary Fault     : {data.get('primaryFault', 'None')}")
                    print(f"  Recommendation    : {data.get('recommendation', 'None')}")
                    print(f"====================================================\n")
                elif msg_type == "execution_trace":
                    node_id = data.get("node_id", "")
                    status = data.get("status", "")
                    print(f"  -> Pipeline Step: {node_id} ({status})")
                elif msg_type == "connection_established":
                    print(f"Server Connection Info: {data.get('message')} (Active: {data.get('active_connections')})")
            except Exception as parse_err:
                print(f"Raw Server Message: {message[:120]}")
    except websockets.exceptions.ConnectionClosed:
        print("\nWebSocket server closed the connection.")
    except Exception as e:
        print(f"Error in server listener: {e}")

async def run_simulator():
    parser = argparse.ArgumentParser(description="PulseDrive Telemetry Simulator")
    parser.add_argument("--scenario", type=str, default=None, choices=["1", "2", "3", "4", "5"], help="Scenario to run")
    parser.add_argument("--vehicle", type=str, default="CNC-Mill-07", help="Vehicle/Machine ID")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between packets in seconds")
    args, unknown = parser.parse_known_args()

    print("====================================================")
    print("       PulseDrive Telemetry Simulator & Agent Tester")
    print("====================================================")
    
    choice = args.scenario
    if choice is None:
        if sys.stdin.isatty():
            print("Available Scenarios:")
            for key, val in SCENARIOS.items():
                print(f"  [{key}] - {val['name']}")
            try:
                choice = input("\nSelect Scenario to start [1-5] (default is 1): ").strip()
            except KeyboardInterrupt:
                return
        if not choice or choice not in SCENARIOS:
            choice = "1"
    
    scenario = SCENARIOS[choice]
    vehicle_id = args.vehicle
    interval = args.interval
    
    print(f"\nStarting simulation with scenario: {scenario['name']}")
    print(f"Target Vehicle ID: {vehicle_id}")
    print(f"Connecting to WebSocket: {WS_URL}...")
    
    try:
        async with websockets.connect(WS_URL) as ws:
            print("Connected! Streaming live sensor packets to the dashboard...\nPress Ctrl+C to stop.")
            
            # Start background listener task to print predictions
            listener_task = asyncio.create_task(listen_to_server(ws))
            
            step = 0
            try:
                while True:
                    step += 1
                    
                    # Build mock sensor data that satisfies the SensorData schema
                    payload = {
                        "vehicleId": vehicle_id,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "temperature": scenario["temperature"](),
                        "voltage": scenario["voltage"](),
                        "gasSensor": {
                            "value": scenario["gas_value"](),
                            "unit": "ppm"
                        },
                        "gps": {
                            "lat": 28.6273 + random.uniform(-0.001, 0.001),
                            "lng": 77.3725 + random.uniform(-0.001, 0.001)
                        },
                        "mpu1": {
                            "accX": scenario["ax"](),
                            "accY": scenario["ay"](),
                            "accZ": scenario["az"](),
                            "gyroX": scenario["gx"](),
                            "gyroY": scenario["gy"](),
                            "gyroZ": scenario["gz"]()
                        },
                        "mpu2": {
                            "accX": scenario["ax"](),
                            "accY": scenario["ay"](),
                            "accZ": scenario["az"](),
                            "gyroX": scenario["gx"](),
                            "gyroY": scenario["gy"](),
                            "gyroZ": scenario["gz"]()
                        }
                    }
                    
                    # Send telemetry data payload
                    await ws.send(json.dumps(payload))
                    print(f"[{step}] Sent: Temp={payload['temperature']:.1f}°C, Volt={payload['voltage']:.2f}V, Gas={payload['gasSensor']['value']:.1f}ppm")
                    
                    # Wait specified interval before sending next reading
                    await asyncio.sleep(interval)
            finally:
                # Cancel the listener when the main loop exits
                listener_task.cancel()
                try:
                    await listener_task
                except asyncio.CancelledError:
                    pass
                
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    except Exception as e:
        print(f"\nConnection / execution error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_simulator())
    except KeyboardInterrupt:
        print("\nExiting.")
