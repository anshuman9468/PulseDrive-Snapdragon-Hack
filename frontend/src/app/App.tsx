import { useState, useEffect, useRef, useCallback } from "react";
import {
  LayoutDashboard, Activity, Stethoscope, Calendar, BarChart2, FileText,
  Settings, Search, Bell, AlertTriangle, CheckCircle2, Shield, Layers,
  Download, Plus, ArrowRight, Info, ChevronRight, Cpu, Gauge, Zap,
  XCircle, RefreshCcw, Network, Thermometer, Clock, Users, Server,
  TrendingUp, TrendingDown, Filter, Eye, MoreHorizontal, CheckCheck,
  Play, Pause, RotateCcw, Wrench, Package, ChevronDown, Radio,
} from "lucide-react";

// ══════════════════════════════════════════════════════════════════════════════
// WEBSOCKET TELEMETRY HOOK
// ══════════════════════════════════════════════════════════════════════════════

const WS_URL = "ws://localhost:8000/ws/live";

interface AgentResult {
  agent: string;
  prediction: string;
  confidence: number;
  severity: string;
  evidence: string[];
  runtime_used?: string;
  execution_time_ms?: number;
}

interface TelemetryState {
  connected: boolean;
  vehicleId: string;
  healthScore: number;
  status: string;
  riskScore: number;
  failureProbability: number;
  riskTrend: string;
  primaryFault: string;
  secondaryFaults: string[];
  recommendation: string;
  confidence: number;
  agentResults: AgentResult[];
  executionContext: Record<string, unknown>;
  timestamp: string;
  // raw sensor values from sensor_data events
  temperature: number;
  voltage: number;
  accX: number; accY: number; accZ: number;
  gyroX: number; gyroY: number; gyroZ: number;
  gasValue: number;
  execLog: { t: string; msg: string; ok: boolean | null }[];
  healthHistory: { time: string; score: number }[];
}

const DEFAULT_TELEMETRY: TelemetryState = {
  connected: false,
  vehicleId: "--",
  healthScore: 0,
  status: "loading",
  riskScore: 0,
  failureProbability: 0,
  riskTrend: "stable",
  primaryFault: "Awaiting data...",
  secondaryFaults: [],
  recommendation: "Connect ESP32 to begin monitoring",
  confidence: 0,
  agentResults: [],
  executionContext: {},
  timestamp: "",
  temperature: 0,
  voltage: 0,
  accX: 0, accY: 0, accZ: 0,
  gyroX: 0, gyroY: 0, gyroZ: 0,
  gasValue: 0,
  execLog: [],
  healthHistory: [],
};

function useLiveTelemetry() {
  const [tel, setTel] = useState<TelemetryState>(DEFAULT_TELEMETRY);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setTel((prev) => ({ ...prev, connected: true }));
      };

      ws.onmessage = (evt) => {
        if (!mountedRef.current) return;
        try {
          const msg = JSON.parse(evt.data as string);

          if (msg.type === "prediction_update") {
            const agents: AgentResult[] = (msg.agentResults ?? []) as AgentResult[];
            // Build execution log from agent results
            const ts = new Date(msg.timestamp ?? Date.now());
            const timeStr = ts.toLocaleTimeString("en-GB", { hour12: false });
            const logEntries = agents.map((a) => ({
              t: timeStr,
              msg: `${a.agent}: ${a.prediction} (${(a.confidence * 100).toFixed(1)}%)`,
              ok: a.severity === "LOW" || a.severity === "NONE" ? true : (a.severity === "CRITICAL" || a.severity === "HIGH" ? false : (true as boolean | null)),
            }));
            logEntries.push({
              t: timeStr,
              msg: `Decision: ${(msg.status ?? "unknown").toUpperCase()} · Health ${msg.healthScore ?? 0}%`,
              ok: (msg.status ?? "").toLowerCase() === "healthy" ? true : null,
            });

            setTel((prev) => {
              const lastHistory = prev.healthHistory[prev.healthHistory.length - 1];
              let newHistory = prev.healthHistory;
              if (!lastHistory || lastHistory.time !== timeStr) {
                newHistory = [...prev.healthHistory, { time: timeStr, score: msg.healthScore ?? prev.healthScore }];
                if (newHistory.length > 24) {
                  newHistory.shift();
                }
              }
              return {
                ...prev,
                vehicleId: msg.vehicleId ?? prev.vehicleId,
                healthScore: msg.healthScore ?? prev.healthScore,
                status: msg.status ?? prev.status,
                riskScore: msg.riskScore ?? prev.riskScore,
                failureProbability: msg.failureProbability ?? prev.failureProbability,
                riskTrend: msg.riskTrend ?? prev.riskTrend,
                primaryFault: msg.primaryFault || prev.primaryFault,
                secondaryFaults: msg.secondaryFaults ?? prev.secondaryFaults,
                recommendation: msg.recommendation ?? prev.recommendation,
                confidence: msg.confidence ?? prev.confidence,
                agentResults: agents,
                executionContext: (msg.executionContext ?? {}) as Record<string, unknown>,
                timestamp: msg.timestamp ?? prev.timestamp,
                execLog: [...logEntries, ...prev.execLog].slice(0, 20),
                healthHistory: newHistory,
              };
            });
          }

          if (msg.type === "sensor_update") {
            const d = msg.data ?? msg;
            const mpu = d.mpu1 ?? d.mpu6050 ?? {};
            setTel((prev) => ({
              ...prev,
              temperature: d.temperature ?? prev.temperature,
              voltage: d.voltage ?? prev.voltage,
              accX: mpu.accX ?? mpu.ax ?? prev.accX,
              accY: mpu.accY ?? mpu.ay ?? prev.accY,
              accZ: mpu.accZ ?? mpu.az ?? prev.accZ,
              gyroX: mpu.gyroX ?? mpu.gx ?? prev.gyroX,
              gyroY: mpu.gyroY ?? mpu.gy ?? prev.gyroY,
              gyroZ: mpu.gyroZ ?? mpu.gz ?? prev.gyroZ,
              gasValue: d.gasSensor?.value ?? d.gasSensor?.val ?? prev.gasValue ?? 0,
            }));
          }
        } catch { /* ignore parse errors */ }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setTel((prev) => ({ ...prev, connected: false }));
        retryRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => ws.close();
    } catch { /* WebSocket unavailable (SSR/test) */ }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      wsRef.current?.close();
      if (retryRef.current) clearTimeout(retryRef.current);
    };
  }, [connect]);

  return tel;
}

// ── Shared Data ───────────────────────────────────────────────────────────────

const HEALTH_DATA = [
  { time: "00:00", score: 94 }, { time: "02:00", score: 93 },
  { time: "04:00", score: 91 }, { time: "06:00", score: 89 },
  { time: "08:00", score: 87 }, { time: "10:00", score: 85 },
  { time: "12:00", score: 83 }, { time: "14:00", score: 80 },
  { time: "16:00", score: 77 }, { time: "18:00", score: 74 },
  { time: "20:00", score: 72 }, { time: "22:00", score: 71 },
];

const SENSORS = [
  { key: "temp",  label: "Temperature",    value: "68.4",  unit: "°C",  sensor: "LM35",        status: "warning", trend: "up",     delta: "+2.1°C"  },
  { key: "volt",  label: "Battery Voltage",value: "12.8",  unit: "V",   sensor: "ADC/Divider", status: "healthy", trend: "stable", delta: "0.0V"    },
  { key: "gas",   label: "Cabin Gas Level",value: "25.0",  unit: "ppm", sensor: "MQ2",         status: "healthy", trend: "stable", delta: "0.0ppm"  },
  { key: "accX",  label: "Acc X",          value: "+1.23", unit: "g",   sensor: "MPU6050",     status: "warning", trend: "up",     delta: "+0.82g"  },
  { key: "accY",  label: "Acc Y",          value: "−0.87", unit: "g",   sensor: "MPU6050",     status: "healthy", trend: "down",   delta: "−0.11g"  },
  { key: "accZ",  label: "Acc Z",          value: "9.74",  unit: "g",   sensor: "MPU6050",     status: "healthy", trend: "down",   delta: "−0.06g"  },
  { key: "gyroX", label: "Gyro X",         value: "12.4",  unit: "°/s", sensor: "MPU6050",     status: "warning", trend: "up",     delta: "+4.2°/s" },
  { key: "gyroY", label: "Gyro Y",         value: "−8.1",  unit: "°/s", sensor: "MPU6050",     status: "healthy", trend: "down",   delta: "−1.2°/s" },
  { key: "gyroZ", label: "Gyro Z",         value: "3.2",   unit: "°/s", sensor: "MPU6050",     status: "healthy", trend: "up",     delta: "+0.5°/s" },
];

const HISTORY = [
  { ts: "2026-07-01 22:45:12", health: 71, prediction: "Coolant Loop Degradation", risk: "High",   status: "Warning" },
  { ts: "2026-07-01 20:30:08", health: 74, prediction: "Wheel Vibration Anomaly",   risk: "Medium", status: "Warning" },
  { ts: "2026-07-01 18:15:44", health: 78, prediction: "Normal Operation",          risk: "Low",    status: "Healthy" },
  { ts: "2026-07-01 16:00:22", health: 82, prediction: "Normal Operation",          risk: "Low",    status: "Healthy" },
  { ts: "2026-07-01 14:30:55", health: 85, prediction: "Mild Thermal Stress",        risk: "Low",    status: "Healthy" },
  { ts: "2026-07-01 12:00:17", health: 88, prediction: "Normal Operation",          risk: "Low",    status: "Healthy" },
];

const ALERTS = [
  { time: "22:45", level: "critical", msg: "Health score dropped below 75% threshold — immediate vehicle inspection recommended", machine: "CNC-Mill-07" },
  { time: "21:30", level: "warning",  msg: "Wheel vibration amplitude exceeding baseline by 23% on X-axis", machine: "CNC-Mill-07" },
  { time: "20:15", level: "warning",  msg: "Engine coolant temp trending above nominal range (target: ≤60°C)", machine: "CNC-Mill-07" },
  { time: "18:00", level: "info",     msg: "Scheduled AI vehicle diagnostics cycle completed successfully", machine: "CNC-Mill-07" },
  { time: "15:45", level: "info",     msg: "MPU6050 sensor calibration check passed all 6 axes", machine: "CNC-Mill-07" },
];

const WORKFLOW = [
  { id: 1, label: "LM35 Sensor",       sub: "Temperature",         status: "done",    Icon: Thermometer },
  { id: 2, label: "MPU6050 Sensor",    sub: "Accel + Gyro · 6-axis",status: "done",   Icon: Radio },
  { id: 3, label: "Monitoring Agent",  sub: "Real-time ingestion", status: "done",    Icon: Activity },
  { id: 4, label: "Supervisor Agent",  sub: "Orchestration",       status: "done",    Icon: Layers },
  { id: 5, label: "Diagnostic Agent",  sub: "ML inference",        status: "done",    Icon: Stethoscope },
  { id: 6, label: "Maintenance Agent", sub: "Action planning",     status: "running", Icon: Shield },
  { id: 7, label: "Report Agent",      sub: "Output generation",   status: "pending", Icon: FileText },
];

const NAV = [
  { id: "dashboard",   label: "Dashboard",          Icon: LayoutDashboard, group: "Overview" },
  { id: "monitoring",  label: "Live Monitoring",     Icon: Activity,        group: "Overview" },
  { id: "diagnostics", label: "Diagnostics",         Icon: Stethoscope,     group: "Overview" },
  { id: "maintenance", label: "Maintenance Planner", Icon: Calendar,        group: "Operations" },
  { id: "analytics",   label: "Analytics",           Icon: BarChart2,       group: "Operations" },
  { id: "reports",     label: "Reports",             Icon: FileText,        group: "Operations" },
  { id: "workflow",    label: "AI Workflow",          Icon: Network,         group: "Intelligence" },
  { id: "settings",   label: "Settings",             Icon: Settings,        group: "System" },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function dotColor(s: string) {
  const k = s.toLowerCase();
  if (["healthy", "done", "low", "online", "active"].includes(k)) return "bg-emerald-400";
  if (["warning", "running", "medium"].includes(k))               return "bg-amber-400";
  if (["critical", "high", "offline"].includes(k))               return "bg-red-400";
  return "bg-slate-500";
}

function badgeCls(s: string) {
  const k = s.toLowerCase();
  if (["healthy", "done", "low", "online", "active"].includes(k))
    return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  if (k === "info")
    return "bg-blue-500/10 text-blue-400 border-blue-500/20";
  if (["warning", "running", "medium"].includes(k))
    return "bg-amber-500/10 text-amber-400 border-amber-500/20";
  if (["critical", "high", "offline"].includes(k))
    return "bg-red-500/10 text-red-400 border-red-500/20";
  return "bg-slate-700/40 text-slate-400 border-slate-600/30";
}

function Badge({ label, status }: { label: string; status: string }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border ${badgeCls(status)}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor(status)}`} />
      {label}
    </span>
  );
}

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-[#0d1629]/90 rounded-xl border border-blue-500/10 shadow-lg shadow-black/30 backdrop-blur-sm ${className}`}>
      {children}
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[10px] font-semibold text-blue-400/60 uppercase tracking-widest mb-1.5">
      {children}
    </p>
  );
}

function PageHeader({
  title, subtitle, children,
}: { title: string; subtitle: string; children?: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between flex-wrap gap-4">
      <div>
        <h1 className="text-[22px] font-bold tracking-tight" style={{ background: 'linear-gradient(135deg, #e2e8f8 0%, #93c5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{title}</h1>
        <p className="text-[13px] text-slate-500 mt-1">{subtitle}</p>
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  );
}

// ── SVG Health Sparkline (shared) ─────────────────────────────────────────────

function MiniSparkline({ data, color = "#2563EB" }: { data: number[]; color?: string }) {
  const W = 80, H = 28;
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => [
    (i / (data.length - 1)) * W,
    H - ((v - min) / range) * H,
  ] as [number, number]);
  const line = pts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const area = `${line}L${W},${H}L0,${H}Z`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-20 h-7">
      <path d={area} fill={color} fillOpacity={0.1} />
      <path d={line} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" />
    </svg>
  );
}

// ── Circular Gauge ────────────────────────────────────────────────────────────

function CircularGauge({ value, color }: { value: number; color: string }) {
  const cx = 60, cy = 60, r = 44, sw = 10;
  const rad = (d: number) => (d * Math.PI) / 180;
  const arc = (startDeg: number, endDeg: number) => {
    const x1 = cx + r * Math.cos(rad(startDeg));
    const y1 = cy + r * Math.sin(rad(startDeg));
    const x2 = cx + r * Math.cos(rad(endDeg));
    const y2 = cy + r * Math.sin(rad(endDeg));
    const large = endDeg - startDeg > 180 ? 1 : 0;
    return `M${x1.toFixed(2)},${y1.toFixed(2)} A${r},${r} 0 ${large} 1 ${x2.toFixed(2)},${y2.toFixed(2)}`;
  };
  const filled = 135 + 270 * (value / 100);
  return (
    <svg width="108" height="108" viewBox="0 0 120 120">
      <path d={arc(135, 405)} fill="none" stroke="#f1f5f9" strokeWidth={sw} strokeLinecap="round" />
      <path d={arc(135, filled)} fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" />
      <text x="60" y="56" textAnchor="middle" fontSize="21" fontWeight="700" fill={color}>{value}%</text>
      <text x="60" y="72" textAnchor="middle" fontSize="10" fill="#94a3b8">Health</text>
    </svg>
  );
}

// ── Health Chart (pure SVG) ───────────────────────────────────────────────────

function HealthChart({ history, vehicleId }: { history: { time: string; score: number }[]; vehicleId: string }) {
  const [hover, setHover] = useState<{ idx: number } | null>(null);

  const VW = 480, VH = 200;
  const PAD = { top: 12, right: 16, bottom: 28, left: 36 };
  const CW = VW - PAD.left - PAD.right;
  const CH = VH - PAD.top - PAD.bottom;
  const MIN_Y = 0, MAX_Y = 100;

  const data = history && history.length > 0 ? history : HEALTH_DATA;

  const xOf = (i: number) => data.length <= 1 ? 0 : (i / (data.length - 1)) * CW;
  const yOf = (v: number) => CH - ((v - MIN_Y) / (MAX_Y - MIN_Y)) * CH;

  const pts = data.map((d, i) => [xOf(i), yOf(d.score)] as [number, number]);
  const linePath = pts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
  const areaPath = pts.length > 0 ? `${linePath}L${xOf(data.length - 1).toFixed(2)},${CH}L0,${CH}Z` : "";
  const thY = yOf(75);
  const yTicks = [0, 25, 50, 75, 100];

  const onMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (data.length === 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const svgX = ((e.clientX - rect.left) / rect.width) * VW - PAD.left;
    const idx = Math.round((svgX / CW) * (data.length - 1));
    setHover({ idx: Math.max(0, Math.min(data.length - 1, idx)) });
  };

  const hd = hover !== null && hover.idx < data.length ? data[hover.idx] : null;
  const hx = hover !== null ? xOf(hover.idx) : 0;
  const hy = hover !== null && hd ? yOf(hd.score) : 0;
  const tipX = hover !== null ? (hx > CW / 2 ? hx - 88 : hx + 10) : 0;

  const displayVehicle = vehicleId && vehicleId !== "--" ? vehicleId : "CNC-Mill-07";
  const labelInterval = Math.max(1, Math.ceil(data.length / 6));

  return (
    <Card className="p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-[13px] font-semibold text-slate-200">Health Trend</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Live monitoring · {displayVehicle}</p>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-500">
          <div className="flex items-center gap-1.5">
            <span className="w-5 h-0.5 bg-blue-500 rounded-full inline-block" />
            Health Score
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 border-t border-dashed border-red-400 inline-block" />
            Threshold 75%
          </div>
        </div>
      </div>
      <div className="flex-1 min-h-[200px]">
        <svg viewBox={`0 0 ${VW} ${VH}`} className="w-full h-full" onMouseMove={onMouseMove} onMouseLeave={() => setHover(null)}>
          <g transform={`translate(${PAD.left},${PAD.top})`}>
            {yTicks.map((v) => (
              <line key={v} x1={0} y1={yOf(v)} x2={CW} y2={yOf(v)} stroke="#f1f5f9" strokeWidth={1} />
            ))}
            {areaPath && <path d={areaPath} fill="#2563EB" fillOpacity={0.08} />}
            <line x1={0} y1={thY} x2={CW} y2={thY} stroke="#f87171" strokeWidth={1.5} strokeDasharray="5 3" />
            {linePath && <path d={linePath} fill="none" stroke="#2563EB" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />}
            {yTicks.map((v) => (
              <text key={`y${v}`} x={-6} y={yOf(v) + 4} textAnchor="end" fontSize={10} fill="#94a3b8">{v}%</text>
            ))}
            {data.map((d, i) => {
              if (i % labelInterval === 0 || i === data.length - 1) {
                return (
                  <text key={`${d.time}-${i}`} x={xOf(i)} y={CH + 18} textAnchor="middle" fontSize={10} fill="#94a3b8">
                    {d.time}
                  </text>
                );
              }
              return null;
            })}
            {hover !== null && hd !== null && (
              <>
                <line x1={hx} y1={0} x2={hx} y2={CH} stroke="#e2e8f0" strokeWidth={1} />
                <circle cx={hx} cy={hy} r={4} fill="#2563EB" stroke="white" strokeWidth={2} />
                <g transform={`translate(${tipX},${Math.max(4, hy - 36)})`}>
                  <rect x={0} y={0} width={82} height={30} rx={5} fill="white" stroke="#e2e8f0" strokeWidth={1} />
                  <text x={8} y={12} fontSize={9} fill="#94a3b8">{hd.time}</text>
                  <text x={8} y={24} fontSize={11} fontWeight="600" fill="#0f172a">{hd.score.toFixed(1)}% health</text>
                </g>
              </>
            )}
          </g>
        </svg>
      </div>
    </Card>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: DASHBOARD
// ══════════════════════════════════════════════════════════════════════════════

function DashboardPage({ tel }: { tel: TelemetryState }) {
  const isLive = tel.connected;

  // Derive display values — fall back to last-known when disconnected
  const healthScore  = isLive ? tel.healthScore  : 0;
  const statusStr    = tel.status;
  const confidence   = Math.round((tel.confidence ?? 0) * 100);
  const primaryFault = tel.primaryFault  || "No active fault";
  const riskLabel    = tel.riskScore > 0.7 ? "High" : tel.riskScore > 0.4 ? "Medium" : "Low";
  const riskStatus   = tel.riskScore > 0.7 ? "critical" : tel.riskScore > 0.4 ? "warning" : "healthy";
  const gaugeColor   = healthScore >= 80 ? "#16a34a" : healthScore >= 60 ? "#d97706" : "#dc2626";

  const sensorChannels = [
    { key: "temp",  label: "Temperature", value: tel.temperature.toFixed(1), unit: "°C",  sensor: "LM35",    status: tel.temperature > 85 ? "critical" : tel.temperature > 72 ? "warning" : "healthy" as string, trend: "up" as string,   delta: `${tel.temperature.toFixed(1)}°C` },
    { key: "volt",  label: "Battery Voltage", value: tel.voltage.toFixed(2), unit: "V",   sensor: "ADC/Divider", status: tel.voltage < 11.0 ? "critical" : tel.voltage < 12.2 ? "warning" : "healthy" as string, trend: "down" as string, delta: `${tel.voltage.toFixed(2)}V` },
    { key: "gas",   label: "Cabin Gas Level", value: tel.gasValue.toFixed(1), unit: "ppm", sensor: "MQ2", status: tel.gasValue > 500 ? "critical" : tel.gasValue > 300 ? "warning" : "healthy" as string, trend: "up" as string, delta: `${tel.gasValue.toFixed(1)}ppm` },
    { key: "accX",  label: "Acc X",       value: tel.accX.toFixed(2),         unit: "g",   sensor: "MPU6050", status: Math.abs(tel.accX) > 1.2 ? "warning" : "healthy" as string, trend: "up" as string,   delta: `${tel.accX.toFixed(2)}g` },
    { key: "accY",  label: "Acc Y",       value: tel.accY.toFixed(2),         unit: "g",   sensor: "MPU6050", status: "healthy" as string, trend: "down" as string, delta: `${tel.accY.toFixed(2)}g` },
    { key: "accZ",  label: "Acc Z",       value: tel.accZ.toFixed(2),         unit: "g",   sensor: "MPU6050", status: "healthy" as string, trend: "down" as string, delta: `${tel.accZ.toFixed(2)}g` },
    { key: "gyroX", label: "Gyro X",      value: tel.gyroX.toFixed(1),        unit: "°/s", sensor: "MPU6050", status: Math.abs(tel.gyroX) > 12 ? "warning" : "healthy" as string, trend: "up" as string, delta: `${tel.gyroX.toFixed(1)}°/s` },
    { key: "gyroY", label: "Gyro Y",      value: tel.gyroY.toFixed(1),        unit: "°/s", sensor: "MPU6050", status: "healthy" as string, trend: "down" as string, delta: `${tel.gyroY.toFixed(1)}°/s` },
    { key: "gyroZ", label: "Gyro Z",      value: tel.gyroZ.toFixed(1),        unit: "°/s", sensor: "MPU6050", status: "healthy" as string, trend: "up" as string,   delta: `${tel.gyroZ.toFixed(1)}°/s` },
  ];

  // Use live sensor channels when connected, otherwise fall back to static SENSORS
  const activeSensors = isLive ? sensorChannels : SENSORS;

  return (
    <div className="space-y-5">
      {/* Hero */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge label={isLive ? `Live · ${tel.vehicleId}` : "Offline"} status={isLive ? (statusStr === "healthy" ? "healthy" : statusStr === "warning" ? "warning" : "critical") : "critical"} />
            <span className="text-[11px] text-slate-400">
              {tel.timestamp ? `Updated ${new Date(tel.timestamp).toLocaleTimeString()}` : "Awaiting data"}
            </span>
          </div>
          <h1 className="text-[22px] font-bold text-slate-100 tracking-tight">Pulse Drive</h1>
          <p className="text-[13px] text-slate-500 mt-1">AI-Powered Car Predictive Maintenance Platform</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 text-[13px] font-medium text-slate-400 border border-white/8 rounded-lg px-3.5 py-2 hover:bg-white/5 transition-colors">
            <Download className="w-3.5 h-3.5" /> Export
          </button>
          <button className="flex items-center gap-1.5 text-[13px] font-medium text-white bg-blue-600 rounded-lg px-3.5 py-2 hover:bg-blue-700 transition-colors shadow-sm shadow-blue-200">
            <Plus className="w-3.5 h-3.5" /> Create Work Order
          </button>
        </div>
      </div>

      {/* Vehicle Information */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-md bg-blue-500/10 flex items-center justify-center">
            <Cpu className="w-3.5 h-3.5 text-blue-600" />
          </div>
          <h3 className="text-[13px] font-semibold text-slate-200">Vehicle Information</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-3">
          {[
            { label: "Vehicle ID",   value: isLive ? tel.vehicleId : "CNC-Mill-07", mono: true  },
            { label: "Vehicle Model", value: isLive ? (tel.vehicleId === "CNC-Mill-07" ? "Tesla Model S CNC-07" : tel.vehicleId === "Lathe-03" ? "Tesla Model X L-03" : tel.vehicleId === "Robot-02" ? "Tesla Model 3 R-02" : tel.vehicleId === "Conv-09" ? "Tesla Roadster C-09" : "PulseDrive Car") : "Tesla Model S CNC-07", mono: false },
            { label: "Vehicle Sub-system", value: isLive ? (tel.vehicleId === "CNC-Mill-07" ? (tel.temperature > 80.0 ? "Engine Coolant & Thermal" : "Powertrain & ECU") : tel.vehicleId === "Lathe-03" ? "EV Battery Management" : tel.vehicleId === "Robot-02" ? "Exhaust & Cabin Gas" : tel.vehicleId === "Conv-09" ? "Chassis & Wheel Suspension" : "Electric Powertrain") : "Powertrain & ECU", mono: false },
            { label: "Last Updated", value: tel.timestamp ? new Date(tel.timestamp).toLocaleTimeString() : "22:45:12", mono: true  },
          ].map((f) => (
            <div key={f.label}>
              <SectionLabel>{f.label}</SectionLabel>
              <p
                className="text-[13px] font-semibold text-slate-200"
                style={f.mono ? { fontFamily: "monospace" } : undefined}
              >
                {f.value}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* KPI Row — Gauge + Prediction/Risk/Severity + Confidence + Alerts */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Health Score Gauge */}
        <Card className="p-5 flex flex-col items-center justify-center">
          <CircularGauge value={healthScore} color={gaugeColor} />
          <div className="text-center mt-2">
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${healthScore >= 80 ? "bg-emerald-500/10 text-green-600" : healthScore >= 60 ? "bg-amber-500/10 text-amber-600" : "bg-red-500/10 text-red-600"}`}>
              {statusStr.toUpperCase()}
            </span>
            <p className="text-[10px] text-slate-400 mt-1">Risk: {(tel.riskScore * 100).toFixed(0)}% · {riskLabel}</p>
          </div>
        </Card>

        {/* Prediction / Risk / Severity */}
        <Card className="p-5">
          <div className="flex items-start gap-2.5 mb-3">
            <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
              <Stethoscope className="w-3.5 h-3.5 text-blue-600" />
            </div>
            <div className="min-w-0">
              <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">AI Prediction</p>
              <p className="text-[13px] font-bold text-slate-100 leading-tight mt-0.5">{isLive ? primaryFault : "Bearing Degradation"}</p>
            </div>
          </div>
          <div className="space-y-2 pt-3 border-t border-slate-50">
            {[
              { label: "Risk Level",  el: <Badge label={isLive ? riskLabel : "High"}  status={isLive ? riskStatus : "critical"} /> },
              { label: "Failure Prob", el: <Badge label={isLive ? `${(tel.failureProbability*100).toFixed(0)}%` : "N/A"} status={tel.failureProbability > 0.6 ? "critical" : tel.failureProbability > 0.3 ? "warning" : "healthy"} /> },
              { label: "Confidence",  el: <span className="text-[12px] font-bold text-blue-600">{isLive ? `${confidence}%` : "--"}</span> },
            ].map((r) => (
              <div key={r.label} className="flex items-center justify-between">
                <span className="text-[11px] text-slate-500">{r.label}</span>
                {r.el}
              </div>
            ))}
          </div>
        </Card>

        {/* AI Confidence */}
        <Card className="p-5">
          <div className="flex items-start justify-between mb-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-blue-600" />
            </div>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-green-600">+2.1%</span>
          </div>
          <div className="text-[26px] font-bold tracking-tight leading-none text-blue-600">{isLive ? `${confidence}%` : "--"}</div>
          <div className="text-[12px] font-semibold text-slate-300 mt-1.5">AI Confidence</div>
          <div className="text-[11px] text-slate-400 mt-0.5">{isLive ? `${tel.agentResults.length} agents active` : "Awaiting connection"}</div>
        </Card>

        {/* Active Alerts */}
        <Card className="p-5">
          <div className="flex items-start justify-between mb-3">
            <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
              <Bell className="w-4 h-4 text-red-600" />
            </div>
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${tel.secondaryFaults.length > 0 ? "bg-red-500/10 text-red-600" : "bg-emerald-500/10 text-green-600"}`}>{isLive ? `${tel.secondaryFaults.length} secondary` : "--"}</span>
          </div>
          <div className={`text-[26px] font-bold tracking-tight leading-none ${tel.secondaryFaults.length > 0 ? "text-red-600" : "text-green-600"}`}>{isLive ? tel.secondaryFaults.length + 1 : "--"}</div>
          <div className="text-[12px] font-semibold text-slate-300 mt-1.5">Active Faults</div>
          <div className="text-[11px] text-slate-400 mt-0.5">{isLive ? `Trend: ${tel.riskTrend}` : "No data"}</div>
        </Card>
      </div>

      {/* Live Sensor Data — with trend indicators */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-[13px] font-semibold text-slate-200">Live Sensor Data</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Real-time telemetry · 100 ms · LM35 + MPU6050 · 7 channels</p>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
            Streaming
          </div>
        </div>
        <div className="grid grid-cols-4 sm:grid-cols-7 gap-2.5">
          {activeSensors.map((s) => (
            <div
              key={s.key}
              className={`rounded-lg p-3 border ${s.status === "warning" ? "border-amber-200 bg-amber-500/10/60" : "border-white/5 bg-white/5/60"}`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider leading-none">{s.label}</span>
                <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotColor(s.status)} animate-pulse`} />
              </div>
              <div className={`text-[17px] font-bold tracking-tight leading-none ${s.status === "warning" ? "text-amber-400" : "text-slate-200"}`}>
                {s.value}
              </div>
              <div className="text-[9px] text-slate-400 mt-0.5">{s.unit}</div>
              <div className="flex items-center gap-1 mt-2">
                {s.trend === "up"
                  ? <TrendingUp className={`w-3 h-3 flex-shrink-0 ${s.status === "warning" ? "text-amber-500" : "text-green-500"}`} />
                  : <TrendingDown className="w-3 h-3 flex-shrink-0 text-slate-400" />}
                <span className={`text-[9px] font-semibold truncate ${s.status === "warning" ? "text-amber-600" : "text-slate-500"}`}>
                  {s.delta}
                </span>
              </div>
              <div className="text-[8px] text-slate-400 mt-1 font-mono">{s.sensor}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* AI Insights */}
      <Card className="p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
            <Zap className="w-3.5 h-3.5 text-white" />
          </div>
          <div>
            <h3 className="text-[13px] font-semibold text-slate-200">AI Insights</h3>
            <p className="text-[11px] text-slate-400">
              Multi-Agent Orchestrator · {isLive ? `${tel.agentResults.length} agents` : "offline"} · {isLive ? `${((tel.executionContext as {executionTimeMs?: number}).executionTimeMs ?? 0).toFixed(0)} ms` : "--"}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white/5 rounded-lg p-4">
            <SectionLabel>Diagnostic Summary</SectionLabel>
            <p className="text-[12px] text-slate-300 leading-relaxed">
              {isLive
                ? `${primaryFault}. ${tel.secondaryFaults.length > 0 ? "Secondary: " + tel.secondaryFaults.join(", ") + "." : ""} AI confidence: ${confidence}%.`
                : "Elevated temperature warning in EV coolant loop. Engine temperature matches coolant degradation pattern. Potential radiator flow restriction detected (r²=0.91). Degradation rate estimated at ~3.2% per hour under current driving load."}
            </p>
          </div>
          <div className="bg-blue-500/10 border border-blue-100 rounded-lg p-4">
            <SectionLabel>Recommended Action</SectionLabel>
            <ul className="space-y-2 mt-1">
              {(isLive && tel.recommendation
                ? [tel.recommendation, ...tel.secondaryFaults.map((f) => `Monitor: ${f}`)]
                : [
                    "Schedule vehicle inspection within 24–48 hours",
                    "Inspect coolant reservoir level and sensor calibration",
                    "Check EV battery pack temperature sensors",
                    "Verify radiator fan activation duty cycle",
                  ]
              ).map((a, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="w-4 h-4 rounded-full bg-blue-600 text-white text-[9px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-[12px] text-blue-900 leading-snug">{a}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Card>

      {/* Chart row */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <div className="lg:col-span-3" style={{ minHeight: 280 }}><HealthChart history={tel.healthHistory} vehicleId={tel.vehicleId} /></div>
        <div className="lg:col-span-2">
          <Card className="p-5 flex flex-col h-full">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-[13px] font-semibold text-slate-200">AI Diagnosis</h3>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {isLive ? `Run · ${new Date(tel.timestamp || Date.now()).toLocaleTimeString()}` : "LangGraph · Awaiting data"}
                </p>
              </div>
              <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Stethoscope className="w-3.5 h-3.5 text-blue-600" />
              </div>
            </div>
            <div className="divide-y divide-slate-50 mb-4">
              {[
                { label: "Prediction", value: isLive ? primaryFault : "--", type: "text" },
                { label: "Risk Level", value: isLive ? riskLabel : "--", type: isLive ? (riskStatus === "critical" ? "badge-critical" : riskStatus === "warning" ? "badge-warning" : "badge-healthy") : "text" },
                { label: "Severity",   value: isLive ? (tel.riskScore > 0.7 ? "Major" : tel.riskScore > 0.4 ? "Moderate" : "Low") : "--", type: isLive ? (tel.riskScore > 0.7 ? "badge-warning" : "text") : "text" },
                { label: "Confidence", value: isLive ? `${confidence}%` : "--", type: "blue" },
              ].map((r) => (
                <div key={r.label} className="flex items-center justify-between py-2.5">
                  <span className="text-[12px] text-slate-500">{r.label}</span>
                  {r.type === "badge-critical" ? <Badge label={r.value} status="critical" />
                    : r.type === "badge-warning" ? <Badge label={r.value} status="warning" />
                    : r.type === "badge-healthy" ? <Badge label={r.value} status="healthy" />
                    : <span className={`text-[12px] font-semibold ${r.type === "blue" ? "text-blue-600" : "text-slate-200"}`}>{r.value}</span>}
                </div>
              ))}
            </div>
            <div className="bg-white/5 rounded-lg p-3 mb-3">
              <SectionLabel>Summary</SectionLabel>
              <p className="text-[12px] text-slate-300 leading-relaxed">
                {isLive ? primaryFault : "Connect ESP32 to begin AI diagnostics."}
              </p>
            </div>
            <div>
              <SectionLabel>Agent Evidence</SectionLabel>
              <ul className="space-y-1.5">
                {(isLive && tel.agentResults.length > 0
                  ? tel.agentResults.flatMap((a) => a.evidence ?? []).slice(0, 3)
                  : ["Awaiting telemetry data..."])
                  .map((c, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="w-1 h-1 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                    <span className="text-[12px] text-slate-400">{c}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        </div>
      </div>

      {/* Maintenance + Workflow */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card className="p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-[13px] font-semibold text-slate-200">Maintenance Plan</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Generated by Maintenance Agent</p>
            </div>
            <Badge label={isLive ? (riskStatus === "critical" ? "High Priority" : riskStatus === "warning" ? "Medium Priority" : "Low Priority") : "Pending"} status={isLive ? riskStatus : "info"} />
          </div>
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className={`border rounded-lg p-3 ${riskStatus === "critical" ? "bg-red-500/10 border-red-500/15" : riskStatus === "warning" ? "bg-amber-500/10 border-amber-500/15" : "bg-emerald-500/10 border-emerald-500/15"}`}>
              <SectionLabel>Priority</SectionLabel>
              <p className={`text-[13px] font-bold ${riskStatus === "critical" ? "text-red-400" : riskStatus === "warning" ? "text-amber-400" : "text-emerald-400"}`}>
                {isLive ? (riskStatus === "critical" ? "P1 — Critical" : riskStatus === "warning" ? "P2 — High" : "P3 — Normal") : "--"}
              </p>
            </div>
            <div className="bg-white/5 border border-white/5 rounded-lg p-3">
              <SectionLabel>Est. Repair Time</SectionLabel>
              <p className="text-[13px] font-bold text-slate-300">
                {isLive ? (riskStatus === "critical" ? "3 – 4 hours" : riskStatus === "warning" ? "1 – 2 hours" : "< 1 hour") : "--"}
              </p>
            </div>
          </div>
          <div className="mb-5">
            <SectionLabel>Recommended Actions</SectionLabel>
            <ul className="space-y-2.5">
              {(isLive && tel.recommendation
                ? [tel.recommendation, ...tel.secondaryFaults.map((f) => `Monitor: ${f}`)]
                : ["Awaiting AI agent analysis..."])
                .slice(0, 4).map((a, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-400 text-[9px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                  <span className="text-[12px] text-slate-300">{a}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="flex gap-2 pt-4 border-t border-white/5 mt-auto">
            <button className="flex-1 flex items-center justify-center gap-1.5 text-[13px] font-semibold text-white bg-blue-600 rounded-lg py-2.5 hover:bg-blue-700 transition-colors">
              <Plus className="w-4 h-4" /> Create Work Order
            </button>
            <button className="flex items-center gap-1.5 text-[13px] font-medium text-slate-400 border border-white/8 rounded-lg px-4 py-2.5 hover:bg-white/5 transition-colors">
              <Download className="w-4 h-4" /> Report
            </button>
          </div>
        </Card>

        <Card className="p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-[13px] font-semibold text-slate-200">AI Workflow Pipeline</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">LangGraph Multi-Agent</p>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-blue-400 font-medium bg-blue-500/10 border border-blue-500/20 rounded-full px-2.5 py-1">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" /> Running
            </div>
          </div>
          <div className="flex items-start overflow-x-auto pb-1 mb-4">
            {WORKFLOW.map((step, i) => (
              <div key={step.id} className="flex items-start flex-shrink-0">
                <div className={`w-[74px] rounded-xl p-2 border text-center relative ${step.status === "done" ? "bg-emerald-500/10 border-green-200" : step.status === "running" ? "bg-blue-500/10 border-blue-500/20" : "bg-white/5 border-white/8"}`}>
                  <div className="absolute -top-1 -right-1 z-10">
                    {step.status === "done" ? <CheckCircle2 className="w-3.5 h-3.5 text-green-500 fill-white" />
                      : step.status === "running" ? <span className="block w-3.5 h-3.5 bg-blue-500 rounded-full animate-pulse" />
                      : <span className="block w-3.5 h-3.5 bg-slate-200 rounded-full" />}
                  </div>
                  <div className={`w-6 h-6 rounded-md mx-auto mb-1 flex items-center justify-center ${step.status === "done" ? "bg-green-500" : step.status === "running" ? "bg-blue-500" : "bg-slate-300"}`}>
                    <step.Icon className="w-3 h-3 text-white" />
                  </div>
                  <p className={`text-[9px] font-semibold leading-tight ${step.status === "done" ? "text-green-800" : step.status === "running" ? "text-blue-800" : "text-slate-400"}`}>{step.label}</p>
                </div>
                {i < WORKFLOW.length - 1 && (
                  <div className="flex items-center justify-center w-4 flex-shrink-0 pt-4">
                    <ArrowRight className="w-3 h-3 text-slate-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="bg-slate-950 rounded-lg p-4 flex-1">
            <p className="text-[9px] font-semibold text-slate-500 uppercase tracking-widest mb-3">Execution Log</p>
            <div className="space-y-2" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
              {(isLive && tel.execLog.length > 0 ? tel.execLog : [
                { t: "--:--:--", msg: "Waiting for WebSocket connection...", ok: null },
              ]).slice(0, 8).map((log, i) => (
                <div key={i} className="flex items-start gap-3 text-[10px]">
                  <span className="text-slate-400 flex-shrink-0">{log.t}</span>
                  <span className={log.ok === true ? "text-slate-300" : log.ok === false ? "text-red-400" : "text-blue-400"}>
                    {log.msg}{log.ok === null && <span className="inline-block w-1 h-3 bg-blue-400 ml-0.5 animate-pulse align-middle" />}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* History Table */}
      <Card className="overflow-hidden">
        <div className="px-5 py-4 border-b border-white/5">
          <h3 className="text-[13px] font-semibold text-slate-200">Vehicle History</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Last 6 diagnostic cycles</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-50 bg-white/5/60">
                {["Timestamp", "Health Score", "Prediction", "Risk Level", "Status"].map((h) => (
                  <th key={h} className="text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-5 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {HISTORY.map((row, i) => (
                <tr key={i} className="border-b border-slate-50 hover:bg-white/5/40 transition-colors">
                  <td className="px-5 py-3.5 text-[11px] text-slate-500" style={{ fontFamily: "monospace" }}>{row.ts}</td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-16 h-1.5 bg-white/8 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${row.health >= 80 ? "bg-green-500" : row.health >= 70 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${row.health}%` }} />
                      </div>
                      <span className="text-[12px] font-semibold text-slate-300">{row.health}%</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-[12px] font-medium text-slate-300">{row.prediction}</td>
                  <td className="px-5 py-3.5"><Badge label={row.risk} status={row.risk === "High" ? "critical" : row.risk === "Medium" ? "warning" : "healthy"} /></td>
                  <td className="px-5 py-3.5"><Badge label={row.status} status={row.status.toLowerCase()} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Alerts */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-[13px] font-semibold text-slate-200">Recent Alerts</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Today · 5 events</p>
          </div>
        </div>
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-px bg-white/8" />
          <div className="space-y-4">
            {ALERTS.map((alert, i) => {
              const cfg = alert.level === "critical" ? { Icon: XCircle, bg: "bg-red-100", fg: "text-red-600" }
                : alert.level === "warning" ? { Icon: AlertTriangle, bg: "bg-amber-100", fg: "text-amber-600" }
                : { Icon: Info, bg: "bg-blue-100", fg: "text-blue-600" };
              return (
                <div key={i} className="flex gap-4">
                  <div className={`w-8 h-8 rounded-full ${cfg.bg} flex items-center justify-center flex-shrink-0 z-10 ring-2 ring-white`}>
                    <cfg.Icon className={`w-4 h-4 ${cfg.fg}`} />
                  </div>
                  <div className="flex-1 min-w-0 pt-0.5">
                    <div className="flex items-center flex-wrap gap-2 mb-0.5">
                      <span className="text-[12px] font-semibold text-slate-300">{alert.machine}</span>
                      <span className="text-[11px] text-slate-400" style={{ fontFamily: "monospace" }}>{alert.time}</span>
                      <Badge label={alert.level} status={alert.level} />
                    </div>
                    <p className="text-[12px] text-slate-400 leading-relaxed">{alert.msg}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: LIVE MONITORING
// ══════════════════════════════════════════════════════════════════════════════

const MACHINES = [
  { id: "Normal (Healthy State)",           type: "Tesla Model S CNC-07 · Powertrain & ECU",   health: 98, status: "healthy", temp: "38.5°C", uptime: "142h 15m", alerts: 0, vehicleId: "CNC-Mill-07" },
  { id: "High Temperature Warning",         type: "Tesla Model S CNC-07 · Cooling & Thermal", health: 68, status: "warning",  temp: "92.4°C", uptime: "18h 42m",  alerts: 1, vehicleId: "CNC-Mill-07" },
  { id: "Battery Voltage Degradation",      type: "Tesla Model X L-03 · Battery Management",   health: 54, status: "warning",  temp: "42.1°C", uptime: "22h 10m",  alerts: 1, vehicleId: "Lathe-03" },
  { id: "Smoke/Gas Leak Emergency",         type: "Tesla Model 3 R-02 · Exhaust & Cabin Gas",  health: 22, status: "critical", temp: "105.2°C", uptime: "6h 33m",   alerts: 3, vehicleId: "Robot-02" },
  { id: "Severe Vibration / Wheel Imbalance", type: "Tesla Roadster C-09 · Chassis & Suspension", health: 48, status: "critical", temp: "39.4°C", uptime: "20h 50m",  alerts: 2, vehicleId: "Conv-09" },
];

function LiveMonitoringPage({ tel }: { tel: TelemetryState }) {
  const isLive = tel.connected;
  const getActiveScenarioId = () => {
    if (!tel.connected) return "";
    const vId = tel.vehicleId;
    if (vId === "Lathe-03") return "Battery Voltage Degradation";
    if (vId === "Robot-02") return "Smoke/Gas Leak Emergency";
    if (vId === "Conv-09") return "Severe Vibration / Wheel Imbalance";
    if (vId === "CNC-Mill-07") {
      if (tel.temperature > 80.0) return "High Temperature Warning";
      return "Normal (Healthy State)";
    }
    return "Normal (Healthy State)";
  };

  const activeScenarioId = getActiveScenarioId();
  const [selected, setSelected] = useState("Normal (Healthy State)");

  useEffect(() => {
    if (tel.connected && activeScenarioId) {
      setSelected(activeScenarioId);
    }
  }, [tel.connected, activeScenarioId]);

  const machine = MACHINES.find((m) => m.id === selected) || MACHINES[0];
  const isSelectedActiveLive = tel.connected && selected === activeScenarioId;

  const getVal = (label: string, defaultVal: string) => {
    if (isSelectedActiveLive) {
      if (label === "Temperature") return tel.temperature.toFixed(1);
      if (label === "Voltage") return tel.voltage.toFixed(2);
      if (label === "Gas Level") return tel.gasValue.toFixed(1);
      if (label === "Acc X") return tel.accX.toFixed(2);
      if (label === "Acc Y") return tel.accY.toFixed(2);
      if (label === "Acc Z") return tel.accZ.toFixed(2);
      if (label === "Gyro X") return tel.gyroX.toFixed(1);
      if (label === "Gyro Y") return tel.gyroY.toFixed(1);
      if (label === "Gyro Z") return tel.gyroZ.toFixed(1);
    }
    return defaultVal;
  };

  const channelData = [
    { label: "Temperature", value: getVal("Temperature", "38.5"), unit: "°C", status: (isSelectedActiveLive ? tel.temperature > 65 : selected === "High Temperature Warning" || selected === "Smoke/Gas Leak Emergency") ? "warning" : "healthy", sparkData: [32, 35, 37, 36, 38, 38.5, 38.5, isSelectedActiveLive ? tel.temperature : 38.5] },
    { label: "Voltage", value: getVal("Voltage", selected === "Battery Voltage Degradation" ? "10.20" : "12.80"), unit: "V", status: (isSelectedActiveLive ? tel.voltage < 11.5 : selected === "Battery Voltage Degradation") ? "critical" : "healthy", sparkData: [12.8, 12.8, 12.7, 12.8, 12.8, isSelectedActiveLive ? tel.voltage : 12.8] },
    { label: "Gas Level", value: getVal("Gas Level", selected === "Smoke/Gas Leak Emergency" ? "650.0" : "25.0"), unit: "ppm", status: (isSelectedActiveLive ? tel.gasValue > 300 : selected === "Smoke/Gas Leak Emergency") ? "critical" : "healthy", sparkData: [25, 25, 24, 25, 25, isSelectedActiveLive ? tel.gasValue : 25] },
    { label: "Acc X",  value: getVal("Acc X", selected === "Severe Vibration / Wheel Imbalance" ? "+1.42" : "+0.02"), unit: "g",   status: (isSelectedActiveLive ? Math.abs(tel.accX) > 1.0 : selected === "Severe Vibration / Wheel Imbalance") ? "warning" : "healthy", sparkData: [0.01, 0.02, 0.01, 0.02, 0.02, isSelectedActiveLive ? tel.accX : 0.02] },
    { label: "Acc Y",  value: getVal("Acc Y", selected === "Severe Vibration / Wheel Imbalance" ? "−1.28" : "−0.01"), unit: "g",   status: (isSelectedActiveLive ? Math.abs(tel.accY) > 1.0 : selected === "Severe Vibration / Wheel Imbalance") ? "warning" : "healthy", sparkData: [-0.01, -0.02, -0.01, -0.01, -0.01, isSelectedActiveLive ? tel.accY : -0.01] },
    { label: "Acc Z",  value: getVal("Acc Z", selected === "Severe Vibration / Wheel Imbalance" ? "8.82" : "9.81"),  unit: "g",   status: (isSelectedActiveLive ? Math.abs(tel.accZ - 9.8) > 1.0 : selected === "Severe Vibration / Wheel Imbalance") ? "warning" : "healthy", sparkData: [9.8, 9.81, 9.81, 9.81, 9.81, isSelectedActiveLive ? tel.accZ : 9.81] },
    { label: "Gyro X", value: getVal("Gyro X", selected === "Severe Vibration / Wheel Imbalance" ? "14.2" : "0.2"), unit: "°/s", status: (isSelectedActiveLive ? Math.abs(tel.gyroX) > 10.0 : selected === "Severe Vibration / Wheel Imbalance") ? "warning" : "healthy", sparkData: [0.1, 0.2, 0.1, 0.2, 0.2, isSelectedActiveLive ? tel.gyroX : 0.2] },
    { label: "Gyro Y", value: getVal("Gyro Y", selected === "Severe Vibration / Wheel Imbalance" ? "−11.5" : "−0.1"), unit: "°/s", status: (isSelectedActiveLive ? Math.abs(tel.gyroY) > 10.0 : selected === "Severe Vibration / Wheel Imbalance") ? "warning" : "healthy", sparkData: [-0.1, -0.2, -0.1, -0.1, -0.1, isSelectedActiveLive ? tel.gyroY : -0.1] },
    { label: "Gyro Z", value: getVal("Gyro Z", selected === "Severe Vibration / Wheel Imbalance" ? "8.9" : "0.3"),  unit: "°/s", status: (isSelectedActiveLive ? Math.abs(tel.gyroZ) > 10.0 : selected === "Severe Vibration / Wheel Imbalance") ? "warning" : "healthy", sparkData: [0.2, 0.3, 0.2, 0.3, 0.3, isSelectedActiveLive ? tel.gyroZ : 0.3] },
  ];

  return (
    <div className="space-y-5">
      <PageHeader title="Live Monitoring" subtitle="Real-time sensor streams across all registered diagnostic scenarios">
        <div className="flex items-center gap-1.5 text-[12px] text-emerald-400 bg-emerald-500/10 border border-green-200 rounded-lg px-3 py-1.5 font-medium">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" /> 5 monitoring states active
        </div>
        <button className="flex items-center gap-1.5 text-[13px] text-slate-400 border border-white/8 rounded-lg px-3 py-1.5 hover:bg-white/5">
          <Filter className="w-3.5 h-3.5" /> Filter
        </button>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        <div className="space-y-2">
          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-1 mb-3">Diagnostic Scenarios</p>
          {MACHINES.map((m) => {
            const isActiveLive = tel.connected && m.id === activeScenarioId;
            const health = isActiveLive ? tel.healthScore : m.health;
            const status = isActiveLive ? tel.status : m.status;
            return (
              <button
                key={m.id}
                onClick={() => setSelected(m.id)}
                className={`w-full text-left rounded-xl border p-3.5 transition-all ${selected === m.id ? "border-blue-500/30 bg-blue-600/15 ring-1 ring-blue-500/20" : "border-white/5 bg-[#0d1629]/90 hover:border-white/10 hover:bg-[#121c33]/90"}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[12px] font-semibold text-slate-200">{m.id}</span>
                  <Badge label={isActiveLive ? "Live Streaming" : status} status={status} />
                </div>
                <p className="text-[11px] text-slate-500 mb-2">{m.type}</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1 bg-white/8 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${health >= 80 ? "bg-green-500" : health >= 60 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${health}%` }} />
                  </div>
                  <span className="text-[11px] font-semibold text-slate-400">{health}%</span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="lg:col-span-3 space-y-4">
          <Card className="p-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-[15px] font-bold text-slate-100">{machine.id}</h2>
                  <Badge label={isSelectedActiveLive ? "Active Live Stream" : machine.status} status={isSelectedActiveLive ? tel.status : machine.status} />
                </div>
                <p className="text-[12px] text-slate-500">{machine.type} · Uptime {machine.uptime} · {machine.temp}</p>
              </div>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-1.5 text-[12px] text-slate-400 border border-white/8 rounded-lg px-3.5 py-1.5 hover:bg-white/5">
                  <Pause className="w-3.5 h-3.5" /> Pause Stream
                </button>
                <button className="flex items-center gap-1.5 text-[12px] text-white bg-blue-600 rounded-lg px-3.5 py-1.5 hover:bg-blue-700">
                  <Eye className="w-3.5 h-3.5" /> Full View
                </button>
              </div>
            </div>
          </Card>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {channelData.map((ch) => (
              <Card key={ch.label} className={`p-3.5 border ${ch.status === "warning" || ch.status === "critical" ? "border-amber-200/20" : "border-white/5"}`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{ch.label}</span>
                  <span className={`w-1.5 h-1.5 rounded-full ${dotColor(ch.status)} animate-pulse`} />
                </div>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-[18px] font-bold text-slate-100">{ch.value}</span>
                  <span className="text-[10px] text-slate-500">{ch.unit}</span>
                </div>
                <MiniSparkline data={ch.sparkData} color={ch.status === "warning" ? "#d97706" : ch.status === "critical" ? "#dc2626" : "#2563EB"} />
              </Card>
            ))}
          </div>

          <Card className="p-5 overflow-hidden">
            <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-3">
              <div>
                <h3 className="text-[13px] font-bold text-slate-200">AI Predictive Decision</h3>
                <p className="text-[11px] text-slate-400 mt-0.5">Real-time Multi-Agent consensus & prediction telemetry</p>
              </div>
              <span className="text-[11px] text-green-600 font-semibold flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-green-500/20">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" /> {isLive ? "Active Live Stream" : "Baseline Diagnostics"}
              </span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Terminal Logs Panel */}
              <div className="lg:col-span-2 space-y-2">
                <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/60 rounded-t-lg border-t border-x border-white/5">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">Agent Reasoning Stream</span>
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500/30" />
                    <span className="w-2 h-2 rounded-full bg-yellow-500/30" />
                    <span className="w-2 h-2 rounded-full bg-green-500/30" />
                  </div>
                </div>
                <div className="bg-slate-950 p-4 rounded-b-lg border-b border-x border-white/5 h-[170px] overflow-y-auto space-y-2.5" style={{ fontFamily: "monospace", scrollbarWidth: 'thin' }}>
                  {isLive ? (
                    <>
                      <div className="text-[11px] text-blue-400/90 border-b border-slate-900 pb-1.5">
                        [{new Date(tel.timestamp || Date.now()).toLocaleTimeString("en-GB", { hour12: false })}] Telemetry packet: temp={tel.temperature.toFixed(1)}°C, volt={tel.voltage.toFixed(2)}V, gas={tel.gasValue.toFixed(1)}ppm
                      </div>
                      {tel.execLog.slice(0, 5).map((log, i) => (
                        <div key={i} className="flex gap-2.5 text-[11px] leading-relaxed">
                          <span className="text-slate-500 flex-shrink-0">{log.t}</span>
                          <span className={log.ok === true ? "text-emerald-400" : log.ok === false ? "text-red-400" : "text-slate-300"}>
                            {log.ok === true ? "✓" : log.ok === false ? "✗" : "ℹ"} {log.msg}
                          </span>
                        </div>
                      ))}
                    </>
                  ) : (
                    [
                      { t: "10:13:58.201", msg: "Telemetry Ingestion Agent: Received baseline package", ok: true },
                      { t: "10:13:58.344", msg: "Vibration Agent: Analyzing accelerometer FFT axes...", ok: true },
                      { t: "10:13:58.502", msg: "Thermal Agent: Analyzing cabin thermistor levels...", ok: true },
                      { t: "10:13:58.691", msg: "LangGraph Supervisor: Consensus reached. Vehicle health is at nominal 98%", ok: null },
                    ].map((log, i) => (
                      <div key={i} className="flex gap-2.5 text-[11px] leading-relaxed">
                        <span className="text-slate-500 flex-shrink-0">{log.t}</span>
                        <span className={log.ok === true ? "text-emerald-400" : log.ok === false ? "text-red-400" : "text-blue-400"}>
                          {log.ok === true ? "✓" : log.ok === false ? "✗" : "ℹ"} {log.msg}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Recommendation Panel */}
              <div className="bg-[#121e36]/40 rounded-lg p-4 border border-blue-500/10 flex flex-col justify-between">
                <div>
                  <span className="text-[9px] font-bold text-blue-400 uppercase tracking-widest block mb-1">AI Recommendation</span>
                  <h4 className="text-[13px] font-bold text-slate-100 mb-2 leading-snug">
                    {isLive ? (tel.recommendation || "System operating nominally. Continue normal operation.") : "Nominal State Identified"}
                  </h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                    {isLive 
                      ? "AI analyzed telemetry parameters and predicted failure mitigation steps automatically."
                      : "Continuous background model tracking active. No diagnostic alerts scheduled."
                    }
                  </p>
                </div>
                
                <div className="border-t border-white/5 pt-3 mt-auto">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[11px] text-slate-400">Model Confidence</span>
                    <span className="text-[11px] font-bold text-blue-400">{isLive ? `${(tel.confidence * 100).toFixed(0)}%` : "98%"}</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500" 
                      style={{ width: isLive ? `${tel.confidence * 100}%` : "98%" }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: DIAGNOSTICS
// ══════════════════════════════════════════════════════════════════════════════

function DiagnosticsPage({ tel }: { tel: TelemetryState }) {
  const [activeTab, setActiveTab] = useState<"results" | "model" | "history">("results");
  const isLive = tel.connected;
  const primaryFault = tel.primaryFault || "--";
  const confidence = Math.round((tel.confidence ?? 0) * 100);
  const riskLabel = tel.riskScore > 0.7 ? "High" : tel.riskScore > 0.4 ? "Medium" : "Low";
  const riskStatus = tel.riskScore > 0.7 ? "critical" : tel.riskScore > 0.4 ? "warning" : "healthy";
  const severity = tel.riskScore > 0.7 ? "Major" : tel.riskScore > 0.4 ? "Moderate" : "Low";
  const urgency = tel.riskScore > 0.7 ? "24 hours" : tel.riskScore > 0.4 ? "72 hours" : "Routine";

  return (
    <div className="space-y-5">
      <PageHeader title="Diagnostics" subtitle="AI-powered fault classification and health analysis">
        <button className="flex items-center gap-1.5 text-[13px] text-white bg-blue-600 rounded-lg px-3.5 py-2 hover:bg-blue-700">
          <Play className="w-3.5 h-3.5" /> Run Diagnostics
        </button>
      </PageHeader>

      {/* Tabs */}
      <div className="flex gap-1 bg-white/8 rounded-lg p-1 w-fit">
        {(["results", "model", "history"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`px-4 py-1.5 rounded-md text-[13px] font-medium transition-colors capitalize ${activeTab === t ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:text-slate-300"}`}
          >
            {t === "results" ? "Current Results" : t === "model" ? "Model Performance" : "History"}
          </button>
        ))}
      </div>

      {activeTab === "results" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Primary result */}
          <div className="lg:col-span-2 space-y-4">
            {/* Prediction hero */}
            <Card className="p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <Badge label={isLive ? "Live Analysis" : "No Data"} status={isLive ? "healthy" : "warning"} />
                  <h2 className="text-[20px] font-bold text-slate-100 mt-2 leading-tight">
                    {isLive ? primaryFault : "Awaiting telemetry..."}
                  </h2>
                  <p className="text-[13px] text-slate-500 mt-1">
                    {isLive ? `${tel.agentResults.length} agents · ${tel.timestamp ? new Date(tel.timestamp).toLocaleTimeString() : "--"}` : "Connect ESP32 to start analysis"}
                  </p>
                </div>
                <div className="text-right flex-shrink-0 ml-4">
                  <div className="text-[32px] font-bold text-blue-600 leading-none">{isLive ? `${confidence}%` : "--"}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">Confidence</div>
                </div>
              </div>
              {/* Key metrics row */}
              <div className="grid grid-cols-3 gap-3 mb-5 pb-5 border-b border-slate-50">
                <div className={`border rounded-lg p-3 text-center ${riskStatus === "critical" ? "bg-red-500/10 border-red-500/15" : riskStatus === "warning" ? "bg-amber-500/10 border-amber-500/15" : "bg-emerald-500/10 border-emerald-500/15"}`}>
                  <SectionLabel>Risk Level</SectionLabel>
                  <Badge label={isLive ? riskLabel : "--"} status={isLive ? riskStatus : "info"} />
                </div>
                <div className="bg-amber-500/10 border border-amber-500/15 rounded-lg p-3 text-center">
                  <SectionLabel>Severity</SectionLabel>
                  <Badge label={isLive ? severity : "--"} status={isLive ? (tel.riskScore > 0.7 ? "warning" : "healthy") : "info"} />
                </div>
                <div className="bg-blue-500/10 border border-blue-100 rounded-lg p-3 text-center">
                  <SectionLabel>Act Within</SectionLabel>
                  <p className="text-[13px] font-bold text-blue-400">{isLive ? urgency : "--"}</p>
                </div>
              </div>
              {/* Probability bars */}
              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-3">Agent Results</p>
              <div className="space-y-3">
                {isLive && tel.agentResults.length > 0 ? (
                  tel.agentResults.map((a) => (
                    <div key={a.agent}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[12px] font-semibold text-slate-100">{a.agent}: {a.prediction}</span>
                        <span className="text-[12px] font-bold text-blue-600">{(a.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-2 bg-white/8 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${a.confidence * 100}%` }} />
                      </div>
                    </div>
                  ))
                ) : (
                  [{ fault: "Awaiting agent results...", prob: 0, color: "bg-slate-200", primary: true }].map((item) => (
                    <div key={item.fault}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[12px] text-slate-400">{item.fault}</span>
                      </div>
                      <div className="h-2 bg-white/8 rounded-full" />
                    </div>
                  ))
                )}
              </div>
            </Card>

            {/* Feature Importance */}
            <Card className="p-5">
              <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Feature Importance</h3>
              <div className="space-y-2.5">
                {[
                  { feature: "Vibration RMS (Acc X)", importance: 92, role: "Primary indicator" },
                  { feature: "Temperature Delta",     importance: 78, role: "Secondary" },
                  { feature: "Gyro X Drift",          importance: 65, role: "Correlated" },
                  { feature: "Acc Z Deviation",       importance: 43, role: "Supporting" },
                  { feature: "Temperature Absolute",  importance: 31, role: "Supporting" },
                ].map((f) => (
                  <div key={f.feature} className="flex items-center gap-3">
                    <div className="w-36 text-[11px] text-slate-400 flex-shrink-0">{f.feature}</div>
                    <div className="flex-1 h-1.5 bg-white/8 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: `${f.importance}%` }} />
                    </div>
                    <div className="w-6 text-[11px] font-bold text-slate-300 text-right">{f.importance}</div>
                    <div className="text-[10px] text-slate-400 w-24 flex-shrink-0">{f.role}</div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Diagnostic Summary + Possible Causes */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Card className="p-5">
                <SectionLabel>Diagnostic Summary</SectionLabel>
                <p className="text-[12px] text-slate-300 leading-relaxed mt-1">
                  {isLive ? primaryFault : "Awaiting live telemetry from ESP32 device."}
                </p>
              </Card>
              <Card className="p-5">
                <SectionLabel>Possible Causes</SectionLabel>
                <ul className="space-y-2 mt-1">
                  {[
                    "Degraded engine coolant properties",
                    "Radiator flow restriction / partial blockage",
                    "Excessive payload / uphill towing stress",
                    "High ambient operating temperature (>42°C)",
                  ].map((c) => (
                    <li key={c} className="flex items-start gap-2">
                      <span className="w-1 h-1 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                      <span className="text-[12px] text-slate-400 leading-snug">{c}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </div>
          </div>

          {/* Side panel */}
          <div className="space-y-4">
            <Card className="p-5">
              <SectionLabel>Diagnostic Details</SectionLabel>
              <div className="space-y-2.5 mt-2">
                {[
                  { k: "Vehicle ID",     v: "CNC-Mill-07",          mono: false },
                  { k: "Run ID",         v: "#2847",                mono: true  },
                  { k: "Model",          v: "RandomForest v4.2.1",  mono: false },
                  { k: "Inference Time", v: "3.4 ms",               mono: false },
                  { k: "Data Window",    v: "30 sec · 300 pts",     mono: false },
                  { k: "Timestamp",      v: "2026-07-01 22:45:08",  mono: true  },
                ].map((r) => (
                  <div key={r.k} className="flex justify-between border-b border-slate-50 pb-2.5 last:border-0">
                    <span className="text-[12px] text-slate-500">{r.k}</span>
                    <span
                      className="text-[12px] font-medium text-slate-200"
                      style={r.mono ? { fontFamily: "monospace" } : undefined}
                    >
                      {r.v}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-5">
              <SectionLabel>Severity Assessment</SectionLabel>
              <div className="mt-3 space-y-2">
                {[
                  { label: "Risk Level", value: isLive ? riskLabel : "--",   status: isLive ? riskStatus : "info" },
                  { label: "Severity",   value: isLive ? severity : "--",    status: isLive ? (tel.riskScore > 0.7 ? "warning" : "healthy") : "info" },
                  { label: "Urgency",    value: isLive ? urgency : "--",     status: isLive ? (tel.riskScore > 0.7 ? "warning" : "healthy") : "info" },
                ].map((r) => (
                  <div key={r.label} className="flex items-center justify-between py-1.5">
                    <span className="text-[12px] text-slate-500">{r.label}</span>
                    <Badge label={r.value} status={r.status} />
                  </div>
                ))}
              </div>
              {isLive && tel.riskScore > 0.4 && (
                <div className="mt-4 bg-amber-500/10 border border-amber-200 rounded-lg p-3">
                  <p className="text-[11px] text-amber-400 font-medium">⚠ {tel.recommendation || "Schedule maintenance based on AI diagnosis."}</p>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {activeTab === "model" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {[
            { label: "Accuracy",  value: "94.7%", sub: "On validation set",   color: "text-green-600" },
            { label: "Precision", value: "91.2%", sub: "Fault classification", color: "text-blue-600" },
            { label: "Recall",    value: "96.8%", sub: "Fault detection rate", color: "text-blue-600" },
          ].map((m) => (
            <Card key={m.label} className="p-5">
              <div className={`text-[28px] font-bold ${m.color}`}>{m.value}</div>
              <div className="text-[13px] font-semibold text-slate-200 mt-1">{m.label}</div>
              <div className="text-[11px] text-slate-400">{m.sub}</div>
            </Card>
          ))}
          <div className="lg:col-span-3">
            <Card className="p-5">
              <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Model Information</h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { k: "Algorithm", v: "Random Forest Classifier" },
                  { k: "Features", v: "7 sensor channels" },
                  { k: "Training Size", v: "48,320 samples" },
                  { k: "Last Retrained", v: "2026-06-15" },
                  { k: "Classes", v: "4 fault categories" },
                  { k: "Cross-Val Score", v: "0.943 ± 0.012" },
                  { k: "Inference Engine", v: "scikit-learn 1.4" },
                  { k: "Deployed Version", v: "v4.2.1" },
                ].map((r) => (
                  <div key={r.k} className="bg-white/5 rounded-lg p-3">
                    <p className="text-[10px] text-slate-400 uppercase tracking-wide mb-1">{r.k}</p>
                    <p className="text-[13px] font-semibold text-slate-200">{r.v}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      )}

      {activeTab === "history" && (
        <Card className="overflow-hidden">
          <div className="px-5 py-4 border-b border-white/5">
            <h3 className="text-[13px] font-semibold text-slate-200">Diagnostic Run History</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">All runs · CNC-Mill-07</p>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-50 bg-white/5/60">
                {["Run ID", "Timestamp", "Prediction", "Confidence", "Risk", "Duration"].map((h) => (
                  <th key={h} className="text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-5 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { id: "#2847", ts: "22:45:08", pred: "Bearing Degradation", conf: "87.3%", risk: "High",   dur: "3.4ms" },
                { id: "#2846", ts: "20:30:04", pred: "Vibration Anomaly",   conf: "81.0%", risk: "Medium", dur: "3.1ms" },
                { id: "#2845", ts: "18:15:42", pred: "Normal Operation",    conf: "96.2%", risk: "Low",    dur: "2.9ms" },
                { id: "#2844", ts: "16:00:18", pred: "Normal Operation",    conf: "97.8%", risk: "Low",    dur: "2.8ms" },
                { id: "#2843", ts: "14:30:51", pred: "Thermal Stress",      conf: "74.1%", risk: "Low",    dur: "3.2ms" },
              ].map((r) => (
                <tr key={r.id} className="border-b border-slate-50 hover:bg-white/5/40">
                  <td className="px-5 py-3 text-[12px] font-mono text-blue-600">{r.id}</td>
                  <td className="px-5 py-3 text-[11px] text-slate-500 font-mono">{r.ts}</td>
                  <td className="px-5 py-3 text-[12px] font-medium text-slate-300">{r.pred}</td>
                  <td className="px-5 py-3 text-[12px] font-semibold text-slate-200">{r.conf}</td>
                  <td className="px-5 py-3"><Badge label={r.risk} status={r.risk === "High" ? "critical" : r.risk === "Medium" ? "warning" : "healthy"} /></td>
                  <td className="px-5 py-3 text-[11px] text-slate-400 font-mono">{r.dur}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: MAINTENANCE PLANNER
// ══════════════════════════════════════════════════════════════════════════════

function MaintenancePlannerPage({ tel }: { tel: TelemetryState }) {
  const isLive = tel.connected;
  const riskStatus = tel.riskScore > 0.7 ? "critical" : tel.riskScore > 0.4 ? "warning" : "healthy";
  const priority = isLive ? (riskStatus === "critical" ? "P1 — Critical" : riskStatus === "warning" ? "P2 — High" : "P3 — Normal") : "Pending";
  const repairTime = isLive ? (riskStatus === "critical" ? "3 – 4 hours" : riskStatus === "warning" ? "1 – 2 hours" : "< 1 hour") : "--";
  const vehicleLabel = isLive && tel.vehicleId !== "--" ? tel.vehicleId : "ESP32-DEV";
  const woTitle = isLive ? `${vehicleLabel} · ${tel.primaryFault || "Awaiting diagnosis"}` : "Awaiting AI diagnosis...";
  const maintenanceActions: string[] = isLive && tel.recommendation
    ? [tel.recommendation, ...tel.secondaryFaults.map((f: string) => `Monitor: ${f}`)]
    : ["Awaiting AI agent analysis..."];

  const tasks = [
    { id: "WO-AI",   machine: vehicleLabel,  task: isLive ? (tel.primaryFault || "Pending diagnosis") : "Pending", priority: riskStatus === "critical" ? "P1" : riskStatus === "warning" ? "P2" : "P3", due: new Date(Date.now() + 86400000).toISOString().split("T")[0], est: repairTime, status: isLive ? "pending" : "scheduled",  assignee: "AI Agent" },
    { id: "WO-1041", machine: "Tesla Model 3 R-02",    task: "Inspect cabin air quality and gas sensors",        priority: "P1", due: "2026-07-02", est: "2h", status: "in-progress", assignee: "Priya S." },
    { id: "WO-1040", machine: "Tesla Model S CNC-07", task: "Engine coolant flush & radiator inspection",         priority: "P2", due: "2026-07-03", est: "1h", status: "pending",    assignee: "Amit K." },
    { id: "WO-1039", machine: "Tesla Roadster C-09",     task: "Chassis wheel alignment and suspension check",               priority: "P3", due: "2026-07-05", est: "1h", status: "pending",    assignee: "Raj M." },
    { id: "WO-1038", machine: "Tesla Model S Press-12",    task: "Brake fluid flush and pad replacement",  priority: "P2", due: "2026-07-06", est: "2h", status: "scheduled",  assignee: "Priya S." },
    { id: "WO-1037", machine: "Tesla Model X L-03",    task: "Battery pack voltage load testing",       priority: "P3", due: "2026-07-10", est: "4h", status: "scheduled",  assignee: "Amit K." },
  ];

  return (
    <div className="space-y-5">
      <PageHeader title="Maintenance Planner" subtitle="Work orders, schedules, and parts inventory">
        <button className="flex items-center gap-1.5 text-[13px] text-white bg-blue-600 rounded-lg px-3.5 py-2 hover:bg-blue-700">
          <Plus className="w-3.5 h-3.5" /> New Work Order
        </button>
      </PageHeader>

      {/* Active Work Order Detail */}
      <Card className={`p-5 border-l-4 ${riskStatus === "critical" ? "border-l-red-500" : riskStatus === "warning" ? "border-l-amber-500" : "border-l-green-500"}`}>
        <div className="flex items-start justify-between flex-wrap gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-mono text-blue-600 font-semibold">WO-AI</span>
              <Badge label="Open" status="warning" />
              <Badge label={priority} status={riskStatus} />
            </div>
            <h3 className="text-[14px] font-bold text-slate-100">{woTitle}</h3>
            <p className="text-[12px] text-slate-500 mt-0.5">
              {isLive ? `Generated by Maintenance Agent · ${tel.agentResults.length} agent(s) active` : "Awaiting AI agent analysis"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 text-[12px] text-slate-400 border border-white/8 rounded-lg px-3 py-1.5 hover:bg-white/5">
              <Download className="w-3.5 h-3.5" /> Export
            </button>
            <button className="flex items-center gap-1.5 text-[12px] text-white bg-blue-600 rounded-lg px-3 py-1.5 hover:bg-blue-700">
              <CheckCheck className="w-3.5 h-3.5" /> Mark Complete
            </button>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-5">
          {[
            { label: "Priority",          value: priority,   cls: riskStatus === "critical" ? "text-red-400" : riskStatus === "warning" ? "text-amber-400" : "text-emerald-400", bg: riskStatus === "critical" ? "bg-red-500/10 border-red-500/15" : riskStatus === "warning" ? "bg-amber-500/10 border-amber-500/15" : "bg-emerald-500/10 border-emerald-500/15" },
            { label: "Est. Repair Time",  value: repairTime, cls: "text-slate-200", bg: "bg-white/5 border-white/5" },
            { label: "Work Order Status", value: isLive ? "Open" : "Pending",       cls: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/15" },
            { label: "Assigned To",       value: "AI Maintenance Agent",            cls: "text-slate-200", bg: "bg-white/5 border-white/5" },
            { label: "Vehicle",           value: vehicleLabel,                      cls: "text-slate-200", bg: "bg-white/5 border-white/5" },
            { label: "Confidence",        value: isLive ? `${Math.round((tel.confidence ?? 0) * 100)}%` : "--", cls: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/15" },
          ].map((f) => (
            <div key={f.label} className={`rounded-lg p-3 border ${f.bg}`}>
              <SectionLabel>{f.label}</SectionLabel>
              <p className={`text-[12px] font-bold ${f.cls}`}>{f.value}</p>
            </div>
          ))}
        </div>
        <div>
          <SectionLabel>Maintenance Actions</SectionLabel>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
            {maintenanceActions.slice(0, 4).map((action: string, i: number) => (
              <div key={i} className="flex items-start gap-2.5 bg-white/5 rounded-lg p-3">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-[9px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                <div className="min-w-0">
                  <p className="text-[12px] font-medium text-slate-200 leading-snug">{action}</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    {isLive ? `Source: ${tel.agentResults[0]?.agent ?? "AI Agent"}` : "Awaiting agent"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Open Orders", value: "6",   sub: "2 overdue",     Icon: Wrench,   color: "text-blue-600",  bg: "bg-blue-500/10"  },
          { label: "In Progress", value: "1",   sub: "1 technician",  Icon: Activity, color: "text-amber-600", bg: "bg-amber-500/10" },
          { label: "Due Today",   value: "2",   sub: "P1 priority",   Icon: Clock,    color: "text-red-600",   bg: "bg-red-500/10"   },
          { label: "Parts Ready", value: "4/6", sub: "2 on order",    Icon: Package,  color: "text-green-600", bg: "bg-emerald-500/10" },
        ].map((k) => (
          <Card key={k.label} className="p-4 flex items-center gap-4">
            <div className={`w-9 h-9 rounded-lg ${k.bg} flex items-center justify-center flex-shrink-0`}>
              <k.Icon className={`w-4 h-4 ${k.color}`} />
            </div>
            <div>
              <div className={`text-[22px] font-bold leading-none ${k.color}`}>{k.value}</div>
              <div className="text-[12px] font-medium text-slate-300 mt-0.5">{k.label}</div>
              <div className="text-[11px] text-slate-400">{k.sub}</div>
            </div>
          </Card>
        ))}
      </div>

      {/* Work orders table */}
      <Card className="overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
          <h3 className="text-[13px] font-semibold text-slate-200">Work Orders</h3>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 text-[12px] text-slate-400 border border-white/8 rounded-lg px-3 py-1.5 hover:bg-white/5">
              <Filter className="w-3.5 h-3.5" /> Filter
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-50 bg-white/5/60">
                {["Order ID", "Vehicle / Unit", "Task", "Priority", "Due Date", "Est. Time", "Assignee", "Status"].map((h) => (
                  <th key={h} className="text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id} className="border-b border-slate-50 hover:bg-white/5/40">
                  <td className="px-4 py-3 text-[12px] font-mono text-blue-600">{t.id}</td>
                  <td className="px-4 py-3 text-[12px] font-medium text-slate-300">{t.machine}</td>
                  <td className="px-4 py-3 text-[12px] text-slate-400 max-w-[200px]">{t.task}</td>
                  <td className="px-4 py-3">
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded ${t.priority === "P1" ? "bg-red-500/10 text-red-600" : t.priority === "P2" ? "bg-amber-500/10 text-amber-600" : "bg-white/5 text-slate-400"}`}>{t.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-[12px] text-slate-400 font-mono">{t.due}</td>
                  <td className="px-4 py-3 text-[12px] text-slate-500">{t.est}</td>
                  <td className="px-4 py-3 text-[12px] text-slate-300">{t.assignee}</td>
                  <td className="px-4 py-3">
                    <Badge label={t.status} status={t.status === "in-progress" ? "running" : t.status === "scheduled" ? "info" : "warning"} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: ANALYTICS
// ══════════════════════════════════════════════════════════════════════════════

function AnalyticsPage() {
  return (
    <div className="space-y-5">
      <PageHeader title="Analytics" subtitle="Fleet performance trends, uptime metrics, and cost analysis">
        <button className="flex items-center gap-1.5 text-[13px] text-slate-400 border border-white/8 rounded-lg px-3.5 py-2 hover:bg-white/5">
          <Download className="w-3.5 h-3.5" /> Export CSV
        </button>
      </PageHeader>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Fleet Availability", value: "91.4%", change: "+2.3%", up: true },
          { label: "MTBF",              value: "342h",   change: "+18h",  up: true },
          { label: "MTTR",              value: "3.8h",   change: "−0.4h", up: true },
          { label: "Maintenance Cost",  value: "₹48,200", change: "−12%", up: true },
        ].map((k) => (
          <Card key={k.label} className="p-5">
            <div className="flex items-center justify-between mb-3">
              <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${k.up ? "bg-emerald-500/10 text-green-600" : "bg-red-500/10 text-red-600"}`}>{k.change}</span>
              <TrendingUp className="w-4 h-4 text-green-500" />
            </div>
            <div className="text-[24px] font-bold text-slate-100">{k.value}</div>
            <div className="text-[12px] text-slate-500 mt-1">{k.label}</div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card className="p-5">
          <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Vehicle Health Comparison</h3>
          <div className="space-y-3">
            {MACHINES.map((m) => (
              <div key={m.id}>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[12px] font-medium text-slate-300">{m.id}</span>
                    <span className="text-[10px] text-slate-400">{m.type}</span>
                  </div>
                  <span className={`text-[12px] font-bold ${m.health >= 80 ? "text-green-600" : m.health >= 70 ? "text-amber-600" : "text-red-600"}`}>{m.health}%</span>
                </div>
                <div className="h-2 bg-white/8 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full transition-all ${m.health >= 80 ? "bg-green-500" : m.health >= 70 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${m.health}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5">
          <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Alert Distribution — Last 7 Days</h3>
          <div className="space-y-3">
            {[
              { type: "Critical Alerts", count: 4,  pct: 15, color: "bg-red-500" },
              { type: "Warning Alerts",  count: 14, pct: 52, color: "bg-amber-500" },
              { type: "Info Events",     count: 9,  pct: 33, color: "bg-blue-400" },
            ].map((a) => (
              <div key={a.type}>
                <div className="flex justify-between mb-1">
                  <span className="text-[12px] text-slate-300">{a.type}</span>
                  <span className="text-[12px] font-semibold text-slate-200">{a.count} ({a.pct}%)</span>
                </div>
                <div className="h-2 bg-white/8 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${a.color}`} style={{ width: `${a.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-white/5">
            <div className="grid grid-cols-3 gap-3 text-center">
              {[{ v: "27", l: "Total Events" }, { v: "2.1d", l: "Avg Resolution" }, { v: "96%", l: "SLA Met" }].map((s) => (
                <div key={s.l}>
                  <div className="text-[18px] font-bold text-slate-100">{s.v}</div>
                  <div className="text-[10px] text-slate-400">{s.l}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: REPORTS
// ══════════════════════════════════════════════════════════════════════════════

function ReportsPage() {
  const reports = [
    { id: "RPT-0094", title: "Weekly Vehicle Predictive Maintenance Report", type: "Maintenance Summary",    format: "PDF",  machine: "All Vehicles", generated: "2026-07-01 23:00:12", size: "2.4 MB", status: "ready",      generatedBy: "Report Agent", prediction: "Coolant Loop Degradation", confidence: "87.3%" },
    { id: "RPT-0093", title: "Tesla Model S CNC-07 Fault Analysis — Run #2847", type: "Fault Diagnosis",        format: "PDF",  machine: "Tesla Model S CNC-07",  generated: "2026-07-01 22:45:51", size: "1.1 MB", status: "ready",      generatedBy: "Report Agent", prediction: "Coolant Loop Degradation", confidence: "87.3%" },
    { id: "RPT-0092", title: "Tesla Model 3 R-02 Cabin Gas Alert Report",     type: "Cabin Analysis",         format: "PDF",  machine: "Tesla Model 3 R-02",     generated: "2026-06-30 18:30:04", size: "0.8 MB", status: "ready",      generatedBy: "Report Agent", prediction: "Cabin Gas Intrusion",   confidence: "79.1%" },
    { id: "RPT-0091", title: "Monthly Fleet Health Summary — June 2026", type: "Fleet Health",           format: "PDF",  machine: "All Vehicles", generated: "2026-06-30 00:02:44", size: "4.2 MB", status: "ready",      generatedBy: "Report Agent", prediction: "Multi-vehicle",       confidence: "—" },
    { id: "RPT-0090", title: "Maintenance Cost Analysis — Q2 2026",      type: "Cost Analysis",          format: "XLSX", machine: "All Vehicles", generated: "Generating…",          size: "—",      status: "generating", generatedBy: "Report Agent", prediction: "—",                   confidence: "—" },
    { id: "RPT-0089", title: "Sensor Calibration Log",                   type: "Calibration Log",        format: "CSV",  machine: "Tesla Model S CNC-07",  generated: "2026-06-25 09:15:33", size: "0.3 MB", status: "ready",      generatedBy: "Report Agent", prediction: "Normal Operation",    confidence: "96.2%" },
  ];

  return (
    <div className="space-y-5">
      <PageHeader title="Reports" subtitle="Auto-generated diagnostics and maintenance reports by Report Agent">
        <button className="flex items-center gap-1.5 text-[13px] text-white bg-blue-600 rounded-lg px-3.5 py-2 hover:bg-blue-700">
          <Plus className="w-3.5 h-3.5" /> Generate Report
        </button>
      </PageHeader>

      <Card className="overflow-hidden">
        <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
          <div>
            <h3 className="text-[13px] font-semibold text-slate-200">All Reports</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Generated by LangGraph Report Agent</p>
          </div>
          <button className="flex items-center gap-1.5 text-[12px] text-slate-400 border border-white/8 rounded-lg px-3 py-1.5 hover:bg-white/5">
            <Filter className="w-3.5 h-3.5" /> Filter
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-50 bg-white/5/60">
                {["Format", "Report", "Type", "Generated At", "Generated By", "Prediction", "Confidence", "Status", ""].map((h) => (
                  <th key={h} className="text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-4 py-3 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id} className="border-b border-slate-50 hover:bg-white/5/40 transition-colors">
                  <td className="px-4 py-3">
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-[10px] font-bold ${r.format === "PDF" ? "bg-red-500/10 text-red-600" : r.format === "XLSX" ? "bg-emerald-500/10 text-emerald-400" : "bg-blue-500/10 text-blue-600"}`}>
                      {r.format}
                    </div>
                  </td>
                  <td className="px-4 py-3 min-w-[220px]">
                    <p className="text-[12px] font-semibold text-slate-200 leading-snug">{r.title}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5 font-mono">{r.id} · {r.machine} · {r.size}</p>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="text-[11px] font-medium text-slate-400 bg-white/8 px-2 py-0.5 rounded">{r.type}</span>
                  </td>
                  <td className="px-4 py-3 text-[11px] text-slate-500 font-mono whitespace-nowrap">{r.generated}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <div className="w-5 h-5 rounded-md bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <Network className="w-3 h-3 text-blue-600" />
                      </div>
                      <span className="text-[11px] text-slate-400 whitespace-nowrap">{r.generatedBy}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-[12px] font-medium text-slate-300 whitespace-nowrap">{r.prediction}</td>
                  <td className="px-4 py-3 text-[12px] font-bold text-blue-600">{r.confidence}</td>
                  <td className="px-4 py-3">
                    <Badge label={r.status} status={r.status === "ready" ? "healthy" : "running"} />
                  </td>
                  <td className="px-4 py-3">
                    {r.status === "ready" && (
                      <button className="flex items-center gap-1 text-[12px] text-blue-600 font-medium hover:text-blue-400 whitespace-nowrap">
                        <Download className="w-3.5 h-3.5" /> Download
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: AI WORKFLOW
// ══════════════════════════════════════════════════════════════════════════════

function AIWorkflowPage({ tel }: { tel: TelemetryState }) {
  const isLive = tel.connected;
  const execMs = isLive ? `${((tel.executionContext as {executionTimeMs?: number}).executionTimeMs ?? 0).toFixed(0)} ms` : "3.4 ms";
  const diagConf = isLive ? `${Math.round((tel.confidence ?? 0) * 100)}%` : "87.3%";
  const nodes = [
    { id: 1, label: "LM35 Sensor",       sub: "Temperature",          status: "Completed", execTime: "—",       conf: "—",        Icon: Thermometer, role: "Hardware sensor · reads ambient + surface temperature at 10-bit resolution" },
    { id: 2, label: "MPU6050 Sensor",    sub: "Accel + Gyro · 6-axis",status: "Completed", execTime: "—",       conf: "—",        Icon: Radio,       role: "Hardware sensor · 3-axis accelerometer + 3-axis gyroscope via I²C" },
    { id: 3, label: "Monitoring Agent",  sub: "Anomaly detection",     status: "Completed", execTime: "1.2 ms",  conf: "—",        Icon: Activity,    role: "Z-score anomaly detection on 7 channels · raises flag when score > 0.65" },
    { id: 4, label: "Supervisor Agent",  sub: "Orchestration",         status: "Completed", execTime: "0.8 ms",  conf: "—",        Icon: Layers,      role: "LangGraph router · decides which downstream agent to invoke based on anomaly type" },
    { id: 5, label: "Diagnostic Agent",  sub: "ML classification",     status: isLive ? "Completed" : "Completed", execTime: execMs, conf: diagConf, Icon: Stethoscope, role: "Multi-agent ensemble · fault classification across gyro, battery, and thermal agents" },
    { id: 6, label: "Maintenance Agent", sub: "Action planning",       status: isLive ? (tel.riskScore > 0 ? "Running" : "Waiting") : "Running", execTime: "~8 ms", conf: "—", Icon: Shield, role: "LLM + rule engine · generates work order, priority, repair steps, parts list" },
    { id: 7, label: "Report Agent",      sub: "Output generation",     status: "Waiting",   execTime: "—",       conf: "—",        Icon: FileText,    role: "Template engine · produces PDF/XLSX reports and updates dashboard state" },
  ];

  const statusCfg = (s: string) =>
    s === "Completed" ? { badge: "healthy",  node: "bg-emerald-500/10 border-green-200", icon: "bg-green-500",  text: "text-green-800" }
    : s === "Running"  ? { badge: "running",  node: "bg-blue-500/10 border-blue-500/20",  icon: "bg-blue-500",   text: "text-blue-800"  }
    :                    { badge: "info",     node: "bg-white/5 border-white/8", icon: "bg-slate-300",  text: "text-slate-400" };

  return (
    <div className="space-y-5">
      <PageHeader title="AI Workflow" subtitle="LangGraph multi-agent pipeline — Run #2847">
        <button className="flex items-center gap-1.5 text-[13px] text-slate-400 border border-white/8 rounded-lg px-3.5 py-2 hover:bg-white/5">
          <RotateCcw className="w-3.5 h-3.5" /> Re-run Pipeline
        </button>
      </PageHeader>

      {/* Full pipeline flow */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-[13px] font-semibold text-slate-200">Pipeline · Run #2847</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">LM35 → MPU6050 → Monitoring → Supervisor → Diagnostic → Maintenance → Report</p>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-blue-400 font-medium bg-blue-500/10 border border-blue-500/20 rounded-full px-2.5 py-1">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" /> Running
          </div>
        </div>
        <div className="flex items-start overflow-x-auto pb-2 gap-0">
          {nodes.map((n, i) => {
            const cfg = statusCfg(n.status);
            return (
              <div key={n.id} className="flex items-start flex-shrink-0">
                <div className={`w-[88px] rounded-xl p-2.5 border text-center relative ${cfg.node}`}>
                  <div className="absolute -top-1.5 -right-1.5 z-10">
                    {n.status === "Completed" ? <CheckCircle2 className="w-4 h-4 text-green-500 fill-white" />
                      : n.status === "Running" ? <span className="block w-4 h-4 bg-blue-500 rounded-full animate-pulse border-2 border-white" />
                      : <span className="block w-4 h-4 bg-slate-200 rounded-full border-2 border-white" />}
                  </div>
                  <div className={`w-7 h-7 rounded-lg mx-auto mb-1.5 flex items-center justify-center ${cfg.icon}`}>
                    <n.Icon className="w-3.5 h-3.5 text-white" />
                  </div>
                  <p className={`text-[10px] font-bold leading-tight ${cfg.text}`}>{n.label}</p>
                  <p className="text-[8px] text-slate-400 mt-0.5 leading-tight">{n.sub}</p>
                  {n.execTime !== "—" && (
                    <p className="text-[8px] text-slate-400 mt-1 font-mono">{n.execTime}</p>
                  )}
                  {n.conf !== "—" && (
                    <p className="text-[9px] font-bold text-blue-600 mt-0.5">{n.conf}</p>
                  )}
                </div>
                {i < nodes.length - 1 && (
                  <div className="flex items-center justify-center w-5 flex-shrink-0 pt-6">
                    <ArrowRight className="w-3 h-3 text-slate-300" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Node / Agent detail cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {nodes.map((n) => {
          const cfg = statusCfg(n.status);
          return (
            <Card key={n.id} className="p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${n.status === "Completed" ? "bg-green-100" : n.status === "Running" ? "bg-blue-100" : "bg-white/8"}`}>
                    <n.Icon className={`w-4 h-4 ${n.status === "Completed" ? "text-green-600" : n.status === "Running" ? "text-blue-600" : "text-slate-400"}`} />
                  </div>
                  <div className="min-w-0">
                    <p className="text-[13px] font-semibold text-slate-200">{n.label}</p>
                    <p className="text-[11px] text-slate-400">{n.sub}</p>
                  </div>
                </div>
                <Badge label={n.status} status={cfg.badge} />
              </div>
              <p className="text-[11px] text-slate-500 leading-relaxed mb-4">{n.role}</p>
              <div className="grid grid-cols-3 gap-3 text-center border-t border-slate-50 pt-4">
                <div>
                  <p className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Status</p>
                  <p className={`text-[12px] font-bold ${n.status === "Completed" ? "text-green-600" : n.status === "Running" ? "text-blue-600" : "text-slate-400"}`}>{n.status}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Exec Time</p>
                  <p className="text-[12px] font-bold text-slate-200 font-mono">{n.execTime}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-400 mb-0.5 uppercase tracking-wide">Confidence</p>
                  <p className={`text-[12px] font-bold ${n.conf !== "—" ? "text-blue-600" : "text-slate-400"}`}>{n.conf}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE: SETTINGS
// ══════════════════════════════════════════════════════════════════════════════

function SettingsPage() {
  const [notifications, setNotifications] = useState(true);
  const [autoReport, setAutoReport] = useState(true);
  const [threshold, setThreshold] = useState("75");
  const [interval, setInterval] = useState("100");

  return (
    <div className="space-y-5 max-w-2xl">
      <PageHeader title="Settings" subtitle="System configuration and notification preferences" />

      {/* Platform */}
      <Card className="p-5">
        <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Platform Configuration</h3>
        <div className="space-y-4">
          {[
            { label: "Health Alert Threshold (%)", desc: "Alert when health score drops below this value", value: threshold, onChange: setThreshold },
            { label: "Sensor Poll Interval (ms)", desc: "How often to fetch sensor readings", value: interval, onChange: setInterval },
          ].map((f) => (
            <div key={f.label}>
              <label className="block text-[12px] font-medium text-slate-300 mb-1">{f.label}</label>
              <p className="text-[11px] text-slate-400 mb-2">{f.desc}</p>
              <input
                type="number"
                value={f.value}
                onChange={(e) => f.onChange(e.target.value)}
                className="w-full border border-white/8 rounded-lg px-3 py-2 text-[13px] text-slate-200 bg-[#080f22] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          ))}
        </div>
      </Card>

      {/* Notifications */}
      <Card className="p-5">
        <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Notifications</h3>
        <div className="space-y-4">
          {[
            { label: "Push Notifications", desc: "Receive alerts for critical vehicle events", value: notifications, onChange: setNotifications },
            { label: "Auto-Generate Reports", desc: "Automatically create reports after each diagnostic run", value: autoReport, onChange: setAutoReport },
          ].map((f) => (
            <div key={f.label} className="flex items-center justify-between">
              <div>
                <p className="text-[13px] font-medium text-slate-300">{f.label}</p>
                <p className="text-[11px] text-slate-400 mt-0.5">{f.desc}</p>
              </div>
              <button
                onClick={() => f.onChange(!f.value)}
                className={`w-11 h-6 rounded-full transition-colors flex-shrink-0 relative ${f.value ? "bg-blue-600" : "bg-slate-200"}`}
              >
                <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-all ${f.value ? "left-5.5" : "left-0.5"}`} style={{ left: f.value ? "22px" : "2px" }} />
              </button>
            </div>
          ))}
        </div>
      </Card>

      {/* Vehicle config */}
      <Card className="p-5">
        <h3 className="text-[13px] font-semibold text-slate-200 mb-4">Registered Vehicles</h3>
        <div className="space-y-2">
          {MACHINES.map((m) => (
            <div key={m.id} className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${dotColor(m.status)}`} />
                <div>
                  <p className="text-[13px] font-medium text-slate-200">{m.id}</p>
                  <p className="text-[11px] text-slate-400">{m.type}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge label={m.status} status={m.status} />
                <button className="text-[12px] text-blue-600 hover:text-blue-400 font-medium">Configure</button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="flex gap-2">
        <button className="flex items-center gap-1.5 text-[13px] font-semibold text-white bg-blue-600 rounded-lg px-4 py-2.5 hover:bg-blue-700 transition-colors">
          <CheckCheck className="w-4 h-4" /> Save Changes
        </button>
        <button className="text-[13px] text-slate-400 border border-white/8 rounded-lg px-4 py-2.5 hover:bg-white/5">Cancel</button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// SHELL: Sidebar + TopNav
// ══════════════════════════════════════════════════════════════════════════════

function Sidebar({ active, onSelect, tel }: { active: string; onSelect: (id: string) => void; tel: TelemetryState }) {
  const groups = [...new Set(NAV.map((n) => n.group))];
  const sidebarStatus = tel.connected
    ? (tel.status === "healthy" ? "healthy" : tel.status === "warning" ? "warning" : "critical")
    : "critical";
  const sidebarHealth = tel.connected ? tel.healthScore : 0;
  const sidebarAlerts = tel.connected ? (tel.secondaryFaults.length + (tel.status !== "healthy" ? 1 : 0)) : 0;
  const sidebarLabel = tel.connected ? (tel.status === "healthy" ? "Healthy" : tel.status === "warning" ? "Warning" : "Critical") : "Offline";
  const sidebarVehicle = tel.connected && tel.vehicleId !== "--" ? tel.vehicleId : "ESP32-DEV";

  return (
    <aside className="w-[230px] flex-shrink-0 flex flex-col h-full" style={{ background: 'linear-gradient(180deg, #080f22 0%, #060b18 100%)', borderRight: '1px solid rgba(59,130,246,0.08)' }}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-[60px] flex-shrink-0" style={{ borderBottom: '1px solid rgba(59,130,246,0.08)' }}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)', boxShadow: '0 0 14px rgba(37,99,235,0.5)' }}>
          <Activity className="w-4 h-4 text-white" strokeWidth={2.5} />
        </div>
        <div>
          <p className="text-[13px] font-bold tracking-tight leading-none" style={{ background: 'linear-gradient(90deg, #e2e8f8 0%, #93c5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>PulseDrive</p>
          <p className="text-[10px] text-blue-400/50 mt-0.5">AI Vehicle Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {groups.map((group) => (
          <div key={group}>
            <p className="text-[9px] font-semibold text-blue-400/40 uppercase tracking-[0.15em] px-2 mb-1.5">{group}</p>
            <div className="space-y-0.5">
              {NAV.filter((n) => n.group === group).map(({ id, label, Icon }) => (
                <button
                  key={id}
                  onClick={() => onSelect(id)}
                  className="w-full flex items-center gap-2.5 px-2.5 py-[7px] rounded-lg text-[13px] transition-all text-left"
                  style={active === id ? {
                    background: 'linear-gradient(90deg, rgba(59,130,246,0.18) 0%, rgba(59,130,246,0.05) 100%)',
                    borderLeft: '2px solid #3b82f6',
                    color: '#93c5fd',
                    fontWeight: 600,
                    boxShadow: 'inset 0 0 12px rgba(59,130,246,0.06)',
                  } : { color: '#64748b', borderLeft: '2px solid transparent' }}
                >
                  <Icon
                    className="w-4 h-4 flex-shrink-0"
                    strokeWidth={active === id ? 2.5 : 2}
                    style={{ color: active === id ? '#3b82f6' : '#475569' }}
                  />
                  {label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Vehicle status chip */}
      <div className="p-3 flex-shrink-0" style={{ borderTop: '1px solid rgba(59,130,246,0.08)' }}>
        <div className="rounded-lg p-3" style={{ background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.12)' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[12px] font-semibold text-slate-300">{sidebarVehicle}</span>
            <Badge label={sidebarLabel} status={sidebarStatus} />
          </div>
          <div className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${dotColor(sidebarStatus)} animate-pulse`} />
            <span className="text-[11px] text-slate-500">Health {sidebarHealth}% · {sidebarAlerts} alert{sidebarAlerts !== 1 ? "s" : ""}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}


function TopNav({ active, tel }: { active: string; tel: TelemetryState }) {
  const page = NAV.find((n) => n.id === active);
  void page;
  return (
    <header
      className="h-[60px] flex items-center gap-4 px-6 flex-shrink-0"
      style={{ background: 'rgba(8,15,34,0.95)', borderBottom: '1px solid rgba(59,130,246,0.08)', backdropFilter: 'blur(12px)' }}
    >
      <div className="flex-1 max-w-sm">
        <div className="flex items-center gap-2 rounded-lg px-3 py-2" style={{ background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.12)' }}>
          <Search className="w-3.5 h-3.5 text-blue-400/50 flex-shrink-0" />
          <span className="text-[13px] text-slate-400">Search vehicles, alerts...</span>
          <span className="ml-auto text-[10px] text-slate-400 px-1.5 py-0.5 rounded font-mono" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>⌘K</span>
        </div>
      </div>
      <div className="flex items-center gap-2 ml-auto">
        {/* Connection badge */}
        <div className={`flex items-center gap-1.5 text-[12px] font-medium rounded-lg px-3 py-1.5 ${
          tel.connected
            ? "text-emerald-400 border-emerald-500/20"
            : "text-red-400 border-red-500/20"
        }`} style={{ background: tel.connected ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)', border: `1px solid ${tel.connected ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
          <span className={`w-1.5 h-1.5 rounded-full ${tel.connected ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`} />
          {tel.connected ? "Live" : "Offline"}
        </div>
        {/* Bell */}
        <button className="relative w-8 h-8 flex items-center justify-center rounded-lg transition-colors" style={{ color: '#64748b' }}>
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" style={{ border: '1.5px solid #060b18' }} />
        </button>
        {/* User chip */}
        <button className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 transition-colors" style={{ border: '1px solid rgba(59,130,246,0.12)', background: 'rgba(59,130,246,0.06)' }}>
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #2563eb, #7c3aed)' }}>
            <span className="text-[9px] text-white font-bold">PD</span>
          </div>
          <span className="text-[13px] font-medium text-slate-400">PulseDrive</span>
          <ChevronDown className="w-3 h-3 text-slate-400" />
        </button>
      </div>
    </header>
  );
}


// ══════════════════════════════════════════════════════════════════════════════
// ROOT APP
// ══════════════════════════════════════════════════════════════════════════════

export default function App() {
  const [activeNav, setActiveNav] = useState("dashboard");

  const tel = useLiveTelemetry();

  const pages: Record<string, React.ReactNode> = {
    dashboard:   <DashboardPage tel={tel} />,
    monitoring:  <LiveMonitoringPage tel={tel} />,
    diagnostics: <DiagnosticsPage tel={tel} />,
    maintenance: <MaintenancePlannerPage tel={tel} />,
    analytics:   <AnalyticsPage />,
    reports:     <ReportsPage />,
    workflow:    <AIWorkflowPage tel={tel} />,
    settings:    <SettingsPage />,
  };

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        background: 'radial-gradient(ellipse 120% 80% at 10% 0%, #0a1628 0%, #060b18 55%, #040810 100%)',
      }}
    >
      <Sidebar active={activeNav} onSelect={setActiveNav} tel={tel} />
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <TopNav active={activeNav} tel={tel} />
        <main
          className="flex-1 overflow-y-auto p-6"
          style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(59,130,246,0.2) transparent' }}
        >
          {pages[activeNav]}
          <div className="h-6" />
        </main>
      </div>
    </div>
  );
}
