# WebSocket Module - Quick Reference

## File Locations

| Component | File | Purpose |
|-----------|------|---------|
| Manager | `app/websocket/manager.py` | Connection management |
| API | `app/api/websocket.py` | WebSocket endpoints |
| Router | `app/main.py` | Router registration |

## Core Classes

### ConnectionManager

```python
from app.websocket.manager import ConnectionManager

manager = ConnectionManager()

# Connect a client
await manager.connect(websocket)

# Disconnect a client
manager.disconnect(websocket)

# Send to specific client
await manager.send_personal_message({"msg": "hello"}, websocket)

# Broadcast to all
await manager.broadcast({"data": sensor_data})

# Get active connections
count = manager.get_active_connections_count()
```

## WebSocket Endpoints

### Connect to Live Stream

```
WebSocket: ws://localhost:8000/ws/live
```

### Check Status

```
GET: http://localhost:8000/ws/status
```

Response:
```json
{
  "status": "healthy",
  "active_connections": 5,
  "timestamp": "2026-07-17T21:48:48Z",
  "message": "WebSocket server is running..."
}
```

## Message Types

### Sensor Update
```json
{
  "type": "sensor_update",
  "source": "VH001",
  "data": {
    "vehicleId": "VH001",
    "rpm": 3000,
    "temperature": 85.5
  },
  "received_at": "2026-07-17T21:48:48Z"
}
```

### Connection Established
```json
{
  "type": "connection_established",
  "message": "Connected to PulseDrive live sensor stream",
  "active_connections": 5
}
```

### Client Disconnected
```json
{
  "type": "client_disconnected",
  "message": "A client has disconnected from the stream",
  "active_connections": 4
}
```

## ESP32 Arduino Example

```cpp
void sendSensorData() {
  StaticJsonDocument<200> doc;
  doc["vehicleId"] = "VH001";
  doc["rpm"] = readRPM();
  doc["temperature"] = readTemp();
  doc["timestamp"] = getCurrentTime();
  
  String json;
  serializeJson(doc, json);
  webSocket.sendTXT(json);
}
```

## Angular TypeScript Example

```typescript
subscribe to stream() {
  this.wsService.connect();
  return this.wsService.getMessages().pipe(
    filter(msg => msg.type === 'sensor_update'),
    map(msg => msg.data)
  );
}
```

## React/React Native Example

```javascript
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/live');
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'sensor_update') {
      updateSensorData(message.data);
    }
  };
  
  return () => ws.close();
}, []);
```

## Python Client Example

```python
import asyncio
import json
import websockets

async def listen():
    async with websockets.connect('ws://localhost:8000/ws/live') as ws:
        async for message in ws:
            data = json.loads(message)
            print(f"Received: {data['type']}")

asyncio.run(listen())
```

## Testing Commands

### Connect with websocat
```bash
websocat ws://localhost:8000/ws/live
```

### Check Status
```bash
curl http://localhost:8000/ws/status
```

### Send Test Data
```bash
echo '{"vehicleId":"VH001","rpm":3000}' | websocat ws://localhost:8000/ws/live
```

## Features

| Feature | Status |
|---------|--------|
| Multiple concurrent clients | ✓ |
| Broadcast to all | ✓ |
| Personal messages | ✓ |
| Safe disconnection | ✓ |
| Error recovery | ✓ |
| Logging | ✓ |
| Status monitoring | ✓ |

## Common Use Cases

| Use Case | Implementation |
|----------|-----------------|
| ESP32 → Server | Send JSON to `/ws/live` |
| Server → Web | Receives broadcasts |
| Fleet monitoring | Subscribe to sensor_update |
| Real-time dashboard | Receive and display in Angular |
| Mobile app | Connect to `/ws/live` endpoint |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check server is running |
| No messages | Verify sender is connected |
| Slow performance | Check network latency |
| Disconnection errors | Automatic retry implemented |
| Memory growth | Monitor active connections |

## Performance Targets

- Latency: <10ms per broadcast
- Throughput: 1000+ msg/sec
- Concurrent connections: 1000+
- Memory per connection: ~50KB

## Security

### Enable WSS (Secure WebSocket)
```
wss://your-domain.com/ws/live
```

### Add Authentication
```python
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    if not verify_token(token):
        await websocket.close(code=1008)
```

## Deployment

### Docker Run
```bash
docker run -p 8000:8000 pulsedrive:latest
```

### Kubernetes Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: pulsedrive-ws
spec:
  selector:
    app: pulsedrive
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## Documentation Files

- `WEBSOCKET_MODULE.md` - Complete guide
- `WEBSOCKET_TESTING.md` - Testing procedures
- `WEBSOCKET_QUICK_REFERENCE.md` - This file

## Status

✅ Production-Ready
✅ Fully Tested
✅ Error-Safe
✅ Well-Documented

---

Last Updated: 2026-07-17
Version: 1.0.0
