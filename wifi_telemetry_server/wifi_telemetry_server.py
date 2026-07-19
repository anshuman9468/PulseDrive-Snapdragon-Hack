import http.server
import socketserver
import json
import time
import datetime
import threading
import os
import serial
import socket
from zeroconf import ServiceInfo, Zeroconf

PORT = 8080
UDP_PORT = 5005
SERIAL_PORT = "COM9"
BAUD_RATE = 115200

# Global state for real-time sensor telemetry
latest_telemetry = {
  "_id": {
    "$oid": "6a5bf43dcf19c30f73ad978e"
  },
  "vehicleId": "CAR001",
  "timestamp": {
    "$date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
  },
  "temperature": 25.0,
  "voltage": 9.6,
  "gasSensor": {
    "value": 200,
    "unit": "ppm"
  },
  "gps": {
    "lat": 28.6139,
    "lng": 77.209
  },
  "mpu1": {
    "accX": 0,
    "accY": 0,
    "accZ": 0,
    "gyroX": 0,
    "gyroY": 0,
    "gyroZ": 0
  },
  "mpu2": {
    "accX": 0,
    "accY": 0,
    "accZ": 0,
    "gyroX": 0,
    "gyroY": 0,
    "gyroZ": 0
  }
}

ser_conn = None

def get_local_ips():
    ips = []
    try:
        hostname = socket.gethostname()
        for item in socket.gethostbyname_ex(hostname)[2]:
            if not item.startswith("127."):
                ips.append(item)
    except Exception:
        pass
    return ips

def udp_listener_thread():
    global latest_telemetry
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", UDP_PORT))
        print(f"UDP Telemetry Listener Active on 0.0.0.0:{UDP_PORT}")
        while True:
            data, addr = sock.recvfrom(2048)
            if data:
                try:
                    payload_str = data.decode('utf-8', errors='ignore').strip()
                    if payload_str.startswith("{") and payload_str.endswith("}"):
                        parsed = json.loads(payload_str)
                        
                        # Handle compact format: {"t":..., "m1":[gx,gy,gz], "m2":[ax,ay,az,gx,gy,gz], "temp":..., "smoke":...}
                        now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                        
                        m1_arr = parsed.get("m1", [0, 0, 0])
                        m2_arr = parsed.get("m2", [0, 0, 0, 0, 0, 0])

                        print(f"[UDP RECEIVE] m1_arr: {m1_arr} (len={len(m1_arr)}), m2_arr: {m2_arr}")

                        # Extract MPU1 array (handles 3-element gyro-only or 6-element full 6-DOF IMU)
                        if len(m1_arr) >= 6:
                            mpu1_dict = {
                                "accX": m1_arr[0], "accY": m1_arr[1], "accZ": m1_arr[2],
                                "gyroX": m1_arr[3], "gyroY": m1_arr[4], "gyroZ": m1_arr[5]
                            }
                        else:
                            mpu1_dict = {
                                "accX": 0, "accY": 0, "accZ": 0,
                                "gyroX": m1_arr[0] if len(m1_arr) > 0 else 0,
                                "gyroY": m1_arr[1] if len(m1_arr) > 1 else 0,
                                "gyroZ": m1_arr[2] if len(m1_arr) > 2 else 0
                            }

                        # Extract MPU2 array (6-element full 6-DOF IMU)
                        mpu2_dict = {
                            "accX": m2_arr[0] if len(m2_arr) > 0 else 0,
                            "accY": m2_arr[1] if len(m2_arr) > 1 else 0,
                            "accZ": m2_arr[2] if len(m2_arr) > 2 else 0,
                            "gyroX": m2_arr[3] if len(m2_arr) > 3 else 0,
                            "gyroY": m2_arr[4] if len(m2_arr) > 4 else 0,
                            "gyroZ": m2_arr[5] if len(m2_arr) > 5 else 0
                        }

                        latest_telemetry = {
                          "_id": { "$oid": "6a5bf43dcf19c30f73ad978e" },
                          "vehicleId": "CAR001",
                          "timestamp": { "$date": now_iso },
                          "temperature": float(parsed.get("temp", parsed.get("temperature", 25.0))),
                          "voltage": 9.6,
                          "gasSensor": {
                            "value": int(parsed.get("smoke", parsed.get("gasSensor", {}).get("value", 200))),
                            "unit": "ppm"
                          },
                          "gps": { "lat": 28.6139, "lng": 77.209 },
                          "mpu1": mpu1_dict,
                          "mpu2": mpu2_dict
                        }
                except Exception as e:
                    print("[UDP PARSE ERROR]", e)
    except Exception as e:
        print("[UDP BIND ERROR]", e)
        print("UDP Bind Error:", e)

def serial_reader_thread():
    global latest_telemetry, ser_conn
    while True:
        try:
            if ser_conn is None or not ser_conn.is_open:
                try:
                    ser_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                    print(f"Connected to Serial Port {SERIAL_PORT} for Realtime Telemetry Streaming!")
                except Exception as e:
                    time.sleep(1)
                    continue

            line = ser_conn.readline().decode('utf-8', errors='ignore').strip()
            if line:
                if line.startswith("{") and line.endswith("}"):
                    try:
                        parsed = json.loads(line)
                        now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                        
                        if "m1" in parsed or "m2" in parsed:
                            m1_arr = parsed.get("m1", [0, 0, 0])
                            m2_arr = parsed.get("m2", [0, 0, 0, 0, 0, 0])
                            
                            if len(m1_arr) >= 6:
                                mpu1_dict = {
                                    "accX": m1_arr[0], "accY": m1_arr[1], "accZ": m1_arr[2],
                                    "gyroX": m1_arr[3], "gyroY": m1_arr[4], "gyroZ": m1_arr[5]
                                }
                            else:
                                mpu1_dict = {
                                    "accX": 0, "accY": 0, "accZ": 0,
                                    "gyroX": m1_arr[0] if len(m1_arr) > 0 else 0,
                                    "gyroY": m1_arr[1] if len(m1_arr) > 1 else 0,
                                    "gyroZ": m1_arr[2] if len(m1_arr) > 2 else 0
                                }

                            mpu2_dict = {
                                "accX": m2_arr[0] if len(m2_arr) > 0 else 0,
                                "accY": m2_arr[1] if len(m2_arr) > 1 else 0,
                                "accZ": m2_arr[2] if len(m2_arr) > 2 else 0,
                                "gyroX": m2_arr[3] if len(m2_arr) > 3 else 0,
                                "gyroY": m2_arr[4] if len(m2_arr) > 4 else 0,
                                "gyroZ": m2_arr[5] if len(m2_arr) > 5 else 0
                            }

                            latest_telemetry = {
                              "_id": { "$oid": "6a5bf43dcf19c30f73ad978e" },
                              "vehicleId": "CAR001",
                              "timestamp": { "$date": now_iso },
                              "temperature": float(parsed.get("temp", 25.0)),
                              "voltage": 9.6,
                              "gasSensor": { "value": int(parsed.get("smoke", 200)), "unit": "ppm" },
                              "gps": { "lat": 28.6139, "lng": 77.209 },
                              "mpu1": mpu1_dict,
                              "mpu2": mpu2_dict
                            }
                        else:
                            parsed["timestamp"] = {"$date": now_iso}
                            latest_telemetry = parsed
                    except Exception as e:
                        pass
        except Exception as e:
            ser_conn = None
            time.sleep(1)

class TelemetryHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
        except Exception:
            pass

    def do_GET(self):
        global latest_telemetry
        try:
            if self.path in ['/json', '/api/telemetry', '/data']:
                now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                latest_telemetry["timestamp"]["$date"] = now_iso
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.end_headers()
                self.wfile.write(json.dumps(latest_telemetry, indent=2).encode('utf-8'))
            elif self.path in ['/', '/dashboard', '/dashboard.html']:
                self.path = '/dashboard.html'
                return super().do_GET()
            else:
                return super().do_GET()
        except Exception:
            pass

    def do_POST(self):
        global ser_conn
        try:
            if self.path.startswith('/api/control'):
                cmd = 's'
                if 'cmd=' in self.path:
                    cmd = self.path.split('cmd=')[1][0]
                
                if ser_conn and ser_conn.is_open:
                    ser_conn.write(cmd.encode('utf-8'))
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "command": cmd}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        except Exception:
            pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

def register_mdns():
    try:
        local_ips = get_local_ips()
        if not local_ips:
            return None, None
        
        ip_bytes = socket.inet_aton(local_ips[0])
        info = ServiceInfo(
            "_http._tcp.local.",
            "PulseDrive Telemetry Gateway._http._tcp.local.",
            addresses=[ip_bytes],
            port=PORT,
            properties={'path': '/dashboard.html'},
            server="pulsedrive.local.",
        )

        zeroconf = Zeroconf()
        zeroconf.register_service(info)
        print("mDNS Domain Broadcast Active: http://pulsedrive.local")
        return zeroconf, info
    except Exception as e:
        print("mDNS registration notice:", e)
        return None, None

def run_server():
    # Serial reader disabled to guarantee 100% Wi-Fi UDP data transmission
    # t_serial = threading.Thread(target=serial_reader_thread, daemon=True)
    # t_serial.start()

    t_udp = threading.Thread(target=udp_listener_thread, daemon=True)
    t_udp.start()

    zc, info = register_mdns()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    try:
        with ThreadedTCPServer(("0.0.0.0", PORT), TelemetryHTTPHandler) as httpd:
            print(f"WiFi Telemetry HTTP Server Active on Port {PORT}")
            print(f"UDP Telemetry Listener Active on Port {UDP_PORT}")
            httpd.serve_forever()
    finally:
        if zc and info:
            zc.unregister_service(info)
            zc.close()

if __name__ == "__main__":
    run_server()
