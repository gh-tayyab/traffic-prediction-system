"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Car,
  Gauge,
  Brain,
  Cloud,
  CalendarDays,
  ArrowUpRight,
  RefreshCw,
  MapPin,
  Clock3,
  Radio,
  AlertTriangle,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface Statistics {
  total_records: number;
  average_traffic: number;
  median_traffic: number;
  minimum_traffic: number;
  maximum_traffic: number;
  standard_deviation: number;
  data_start: string;
  data_end: string;
}

interface Prediction {
  predicted_traffic: number;
  predicted_traffic_rounded: number;
  congestion_level: string;
  prediction_time: string;
  model: string;
  model_r2: number;
  model_mae: number;
}

interface HourData {
  hour: number;
  traffic_volume: number;
}

interface DayData {
  day_name: string;
  traffic_volume: number;
}

interface LiveJam {
  id: number;
  street: string;
  city: string;
  level: number;
  length_meters: number;
  speed_kmh: number;
  latitude: number;
  longitude: number;
  end_node: string | null;
  update_millis: number;
}

interface LiveTraffic {
  source: string;
  city: string;
  live: boolean;
  jam_count: number;
  max_jam_level: number;
  congestion_status: string;
  jams: LiveJam[];
  cached: boolean;
  stale: boolean;
  cache_age_seconds: number | null;
  cache_ttl_seconds: number;
}

interface SystemStatus {
  overall_status: "healthy" | "degraded";
  api: {
    status: string;
  };
  model: {
    status: string;
  };
  historical_data: {
    status: string;
    rows: number;
  };
  waze: {
    status: string;
  };
  live_traffic: {
    status: string;
    jam_count: number;
    congestion_status: string;
    cache_status: string;
    cache_age_seconds: number | null;
    cache_ttl_seconds: number;
  };
}

export default function Home() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [hourData, setHourData] = useState<HourData[]>([]);
  const [dayData, setDayData] = useState<DayData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [liveTraffic, setLiveTraffic] = useState<LiveTraffic | null>(null);
  const [liveLoading, setLiveLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [systemLoading, setSystemLoading] = useState(true);

  async function loadLiveTraffic() {
    try {
      setLiveLoading(true);

      const response = await fetch(`${API_URL}/live-traffic`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Unable to load live traffic.");
      }

      const data: LiveTraffic = await response.json();

      setLiveTraffic(data);

      // Refresh system status after live traffic cache is updated.
      await loadSystemStatus();
    } catch (err) {
      console.error("Live traffic error:", err);
    } finally {
      setLiveLoading(false);
    }
  }
  function getNextHourPredictionTime() {
    const now = new Date();

    now.setMinutes(0, 0, 0);
    now.setHours(now.getHours() + 1);

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hour = String(now.getHours()).padStart(2, "0");

    return `${year}-${month}-${day} ${hour}:00:00`;
  }
  async function loadSystemStatus() {
    try {
      setSystemLoading(true);

      const response = await fetch(`${API_URL}/system-status`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Unable to load system status.");
      }

      const data: SystemStatus = await response.json();

      setSystemStatus(data);
    } catch (err) {
      console.error("System status error:", err);

      setSystemStatus(null);
    } finally {
      setSystemLoading(false);
    }
  }
  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [
        statisticsResponse,
        predictionResponse,
        hourResponse,
        dayResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/statistics`),
        fetch(`${API_URL}/predict`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prediction_time: getNextHourPredictionTime(),
          }),
        }),
        fetch(`${API_URL}/traffic-by-hour`),
        fetch(`${API_URL}/traffic-by-day`),
      ]);

      if (
        !statisticsResponse.ok ||
        !predictionResponse.ok ||
        !hourResponse.ok ||
        !dayResponse.ok
      ) {
        throw new Error("Unable to load dashboard data.");
      }

      const statisticsData = await statisticsResponse.json();
      const predictionData = await predictionResponse.json();
      const hourDataResponse = await hourResponse.json();
      const dayDataResponse = await dayResponse.json();

      setStatistics(statisticsData);
      setPrediction(predictionData);
      setHourData(hourDataResponse.data);
      setDayData(dayDataResponse.data);
    } catch (err) {
      console.error(err);
      setError(
        "Could not connect to the Traffic Prediction API. Make sure FastAPI is running on port 8000.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
    loadLiveTraffic();

    const liveInterval = setInterval(() => {
      loadLiveTraffic();
    }, 60 * 1000);

    return () => clearInterval(liveInterval);
  }, []);

  const formatNumber = (value: number) =>
    new Intl.NumberFormat("en-US").format(Math.round(value));

  const congestionClass = (level?: string) => {
    switch (level) {
      case "Low":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "Medium":
        return "bg-yellow-50 text-yellow-700 border-yellow-200";
      case "High":
        return "bg-orange-50 text-orange-700 border-orange-200";
      case "Severe":
        return "bg-red-50 text-red-700 border-red-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const maxHourlyTraffic =
    hourData.length > 0
      ? Math.max(...hourData.map((item) => item.traffic_volume))
      : 1;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Activity size={23} />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Traffic Analytics
              </h1>

              <p className="text-sm text-slate-500">
                Prediction & Congestion Intelligence
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden items-center gap-2 text-sm text-slate-500 sm:flex">
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  systemStatus?.api.status === "online"
                    ? "bg-emerald-500"
                    : "bg-red-500"
                }`}
              />

              {systemStatus?.api.status === "online"
                ? "API Online"
                : "API Offline"}
            </div>

            <button
              onClick={loadDashboard}
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium transition hover:bg-slate-50"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Hero */}
        <section className="mb-8">
          <div className="rounded-2xl bg-slate-900 p-7 text-white shadow-sm">
            <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
              <div>
                <p className="mb-2 text-sm font-medium text-slate-400">
                  MACHINE LEARNING TRAFFIC SYSTEM
                </p>

                <h2 className="max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
                  Intelligent traffic prediction and congestion analytics.
                </h2>

                <p className="mt-3 max-w-2xl text-slate-400">
                  Analyze historical traffic patterns and predict the next hour
                  using a trained Random Forest forecasting model.
                </p>
              </div>

              <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-5 py-4">
                <Brain size={22} />

                <div>
                  <p className="text-xs text-slate-400">ACTIVE MODEL</p>
                  <p className="font-semibold">Random Forest</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* KPI Cards */}
        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Records"
            value={
              loading || !statistics
                ? "—"
                : formatNumber(statistics.total_records)
            }
            description="Historical observations"
            icon={<Car size={21} />}
          />

          <MetricCard
            title="Average Traffic"
            value={
              loading || !statistics
                ? "—"
                : formatNumber(statistics.average_traffic)
            }
            description="Vehicles per hour"
            icon={<Activity size={21} />}
          />

          <MetricCard
            title="Next Hour"
            value={
              loading || !prediction
                ? "—"
                : formatNumber(prediction.predicted_traffic_rounded)
            }
            description="Predicted vehicles"
            icon={<ArrowUpRight size={21} />}
          />

          <MetricCard
            title="Model R²"
            value={
              loading || !prediction
                ? "—"
                : `${(prediction.model_r2 * 100).toFixed(2)}%`
            }
            description="Forecasting performance"
            icon={<Gauge size={21} />}
          />
        </section>

        {/* Main Analytics */}
        <section className="mt-8 grid gap-6 lg:grid-cols-3">
          {/* Prediction */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-1">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  NEXT-HOUR FORECAST
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  ML forecast for the next hour based on historical traffic
                  patterns.
                </p>
                <h3 className="mt-1 text-xl font-bold">Traffic Prediction</h3>
              </div>

              <div className="rounded-lg bg-slate-100 p-2">
                <Gauge size={20} />
              </div>
            </div>

            {loading || !prediction ? (
              <div className="h-36 animate-pulse rounded-xl bg-slate-100" />
            ) : (
              <>
                <div className="text-5xl font-bold tracking-tight">
                  {formatNumber(prediction.predicted_traffic_rounded)}
                </div>

                <p className="mt-2 text-sm text-slate-500">
                  predicted vehicles
                </p>

                <div
                  className={`mt-6 inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${congestionClass(
                    prediction.congestion_level,
                  )}`}
                >
                  {prediction.congestion_level} Congestion
                </div>

                <div className="mt-6 space-y-3 border-t border-slate-100 pt-5 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Prediction time</span>
                    <span className="font-medium">
                      {prediction.prediction_time}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-500">Model</span>
                    <span className="font-medium">{prediction.model}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-500">MAE</span>
                    <span className="font-medium">{prediction.model_mae}</span>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Hourly Chart */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  HOURLY PATTERN
                </p>

                <h3 className="mt-1 text-xl font-bold">
                  Average Traffic by Hour
                </h3>
              </div>

              <div className="rounded-lg bg-slate-100 p-2">
                <Activity size={20} />
              </div>
            </div>

            <div className="flex h-64 items-end gap-1.5 sm:gap-2">
              {hourData.map((item) => {
                const height = Math.max(
                  (item.traffic_volume / maxHourlyTraffic) * 100,
                  4,
                );

                return (
                  <div
                    key={item.hour}
                    className="group flex h-full flex-1 flex-col justify-end"
                  >
                    <div className="relative flex flex-1 items-end">
                      <div
                        className="w-full rounded-t-md bg-slate-800 transition-all group-hover:bg-slate-600"
                        style={{ height: `${height}%` }}
                        title={`${item.hour}:00 — ${formatNumber(
                          item.traffic_volume,
                        )} vehicles`}
                      />
                    </div>

                    <span className="mt-2 text-center text-[10px] text-slate-400">
                      {item.hour}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Day Analytics */}
        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <CalendarDays size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  WEEKLY PATTERN
                </p>

                <h3 className="text-xl font-bold">Traffic by Day</h3>
              </div>
            </div>

            <div className="space-y-4">
              {dayData.map((item) => {
                const maxDay =
                  dayData.length > 0
                    ? Math.max(...dayData.map((day) => day.traffic_volume))
                    : 1;

                const width = (item.traffic_volume / maxDay) * 100;

                return (
                  <div key={item.day_name}>
                    <div className="mb-1.5 flex justify-between text-sm">
                      <span className="font-medium">{item.day_name}</span>

                      <span className="text-slate-500">
                        {formatNumber(item.traffic_volume)}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-slate-800"
                        style={{ width: `${width}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Dataset information */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <Cloud size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">DATASET</p>

                <h3 className="text-xl font-bold">Dataset Overview</h3>
              </div>
            </div>

            {statistics && (
              <div className="grid grid-cols-2 gap-4">
                <InfoBox
                  label="Median Traffic"
                  value={formatNumber(statistics.median_traffic)}
                />

                <InfoBox
                  label="Maximum Traffic"
                  value={formatNumber(statistics.maximum_traffic)}
                />

                <InfoBox
                  label="Minimum Traffic"
                  value={formatNumber(statistics.minimum_traffic)}
                />

                <InfoBox
                  label="Std. Deviation"
                  value={formatNumber(statistics.standard_deviation)}
                />

                <div className="col-span-2 rounded-xl bg-slate-50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Data Period
                  </p>

                  <p className="mt-2 text-sm font-semibold">
                    {statistics.data_start}
                  </p>

                  <p className="text-sm text-slate-500">to</p>

                  <p className="text-sm font-semibold">{statistics.data_end}</p>
                </div>
              </div>
            )}
          </div>
        </section>
        {/* System Status */}
        <section className="mb-8">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-slate-500">
                    SYSTEM MONITORING
                  </p>

                  {systemStatus && (
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        systemStatus.overall_status === "healthy"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-yellow-50 text-yellow-700"
                      }`}
                    >
                      {systemStatus.overall_status === "healthy"
                        ? "HEALTHY"
                        : "DEGRADED"}
                    </span>
                  )}
                </div>

                <h3 className="mt-1 text-xl font-bold">System Status</h3>
              </div>

              <button
                onClick={loadSystemStatus}
                disabled={systemLoading}
                className="flex items-center gap-2 self-start rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:opacity-50 sm:self-auto"
              >
                <RefreshCw
                  size={15}
                  className={systemLoading ? "animate-spin" : ""}
                />
                Refresh Status
              </button>
            </div>

            {systemLoading && !systemStatus ? (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                {Array.from({ length: 5 }).map((_, index) => (
                  <div
                    key={index}
                    className="h-24 animate-pulse rounded-xl bg-slate-100"
                  />
                ))}
              </div>
            ) : systemStatus ? (
              <>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                  <StatusItem label="API" status={systemStatus.api.status} />

                  <StatusItem
                    label="ML Model"
                    status={systemStatus.model.status}
                  />

                  <StatusItem
                    label="Historical Data"
                    status={systemStatus.historical_data.status}
                    detail={`${formatNumber(systemStatus.historical_data.rows)} rows`}
                  />

                  <StatusItem
                    label="WazeAPI"
                    status={systemStatus.waze.status}
                  />

                  <StatusItem
                    label="Live Traffic"
                    status={systemStatus.live_traffic.status}
                    detail={`${systemStatus.live_traffic.jam_count} active jams`}
                  />
                </div>

                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Live Status
                    </p>

                    <p className="mt-2 font-semibold">
                      {systemStatus.live_traffic.congestion_status}
                    </p>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Cache
                    </p>

                    <p className="mt-2 font-semibold capitalize">
                      {systemStatus.live_traffic.cache_status}
                    </p>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Cache Age
                    </p>

                    <p className="mt-2 font-semibold">
                      {systemStatus.live_traffic.cache_age_seconds === null
                        ? "Not loaded"
                        : `${Math.round(
                            systemStatus.live_traffic.cache_age_seconds,
                          )} sec ago`}
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                System status is currently unavailable.
              </div>
            )}
          </div>
        </section>
        {/* Live Traffic */}
        <section className="mb-8">
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 p-6">
              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-red-50 p-3 text-red-600">
                    <Radio size={21} />
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-slate-500">
                        REAL-TIME TRAFFIC
                      </p>

                      {liveTraffic && (
                        <span
                          className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
                            liveTraffic.stale
                              ? "bg-yellow-50 text-yellow-700"
                              : "bg-emerald-50 text-emerald-700"
                          }`}
                        >
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${
                              liveTraffic.stale
                                ? "bg-yellow-500"
                                : "animate-pulse bg-emerald-500"
                            }`}
                          />

                          {liveTraffic.stale ? "STALE" : "LIVE"}
                        </span>
                      )}
                    </div>

                    <h3 className="mt-1 text-xl font-bold">
                      Karachi Live Traffic
                    </h3>
                  </div>
                </div>

                {liveTraffic && (
                  <div
                    className={`rounded-full border px-4 py-2 text-sm font-semibold ${
                      liveTraffic.max_jam_level >= 4
                        ? "border-red-200 bg-red-50 text-red-700"
                        : liveTraffic.max_jam_level === 3
                          ? "border-orange-200 bg-orange-50 text-orange-700"
                          : liveTraffic.max_jam_level === 2
                            ? "border-yellow-200 bg-yellow-50 text-yellow-700"
                            : "border-emerald-200 bg-emerald-50 text-emerald-700"
                    }`}
                  >
                    {liveTraffic.congestion_status}
                  </div>
                )}
              </div>
            </div>

            {liveLoading ? (
              <div className="grid gap-4 p-6 sm:grid-cols-3">
                <div className="h-24 animate-pulse rounded-xl bg-slate-100" />
                <div className="h-24 animate-pulse rounded-xl bg-slate-100" />
                <div className="h-24 animate-pulse rounded-xl bg-slate-100" />
              </div>
            ) : liveTraffic ? (
              <>
                {/* Live Summary */}
                <div className="grid gap-4 border-b border-slate-100 p-6 sm:grid-cols-3">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <div className="flex items-center gap-2 text-slate-500">
                      <AlertTriangle size={17} />
                      <span className="text-xs font-medium uppercase tracking-wide">
                        Active Jams
                      </span>
                    </div>

                    <p className="mt-2 text-2xl font-bold">
                      {liveTraffic.jam_count}
                    </p>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <div className="flex items-center gap-2 text-slate-500">
                      <Gauge size={17} />
                      <span className="text-xs font-medium uppercase tracking-wide">
                        Highest Level
                      </span>
                    </div>

                    <p className="mt-2 text-2xl font-bold">
                      Level {liveTraffic.max_jam_level}
                    </p>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <div className="flex items-center gap-2 text-slate-500">
                      <Clock3 size={17} />
                      <span className="text-xs font-medium uppercase tracking-wide">
                        Data Source
                      </span>
                    </div>

                    <p className="mt-2 text-2xl font-bold">Waze</p>
                  </div>
                </div>

                {/* Road List */}
                <div className="p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-500">
                        CURRENT ROAD CONDITIONS
                      </p>

                      <h4 className="mt-1 text-lg font-bold">
                        Active Traffic Jams
                      </h4>
                    </div>

                    <button
                      onClick={loadLiveTraffic}
                      disabled={liveLoading}
                      className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:opacity-50"
                    >
                      <RefreshCw
                        size={15}
                        className={liveLoading ? "animate-spin" : ""}
                      />
                      Refresh
                    </button>
                  </div>

                  <div className="space-y-3">
                    {liveTraffic.jams.map((jam) => {
                      const levelClass =
                        jam.level >= 4
                          ? "border-red-200 bg-red-50 text-red-700"
                          : jam.level === 3
                            ? "border-orange-200 bg-orange-50 text-orange-700"
                            : jam.level === 2
                              ? "border-yellow-200 bg-yellow-50 text-yellow-700"
                              : "border-emerald-200 bg-emerald-50 text-emerald-700";

                      const levelText =
                        jam.level >= 4
                          ? "Severe"
                          : jam.level === 3
                            ? "Heavy"
                            : jam.level === 2
                              ? "Moderate"
                              : "Light";

                      return (
                        <div
                          key={jam.id}
                          className="flex flex-col gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4 md:flex-row md:items-center md:justify-between"
                        >
                          <div className="flex items-start gap-3">
                            <div className="mt-0.5 rounded-lg bg-white p-2 text-slate-500">
                              <MapPin size={18} />
                            </div>

                            <div>
                              <p className="font-semibold">
                                {jam.street || "Unnamed Road"}
                              </p>

                              <p className="mt-1 text-sm text-slate-500">
                                {jam.city || "Karachi"}
                                {jam.end_node ? ` • ${jam.end_node}` : ""}
                              </p>
                            </div>
                          </div>

                          <div className="flex flex-wrap items-center gap-3">
                            <div className="text-right">
                              <p className="text-xs text-slate-400">
                                CURRENT SPEED
                              </p>

                              <p className="font-bold">
                                {jam.speed_kmh.toFixed(1)} km/h
                              </p>
                            </div>

                            <div className="text-right">
                              <p className="text-xs text-slate-400">
                                JAM LENGTH
                              </p>

                              <p className="font-bold">
                                {jam.length_meters >= 1000
                                  ? `${(jam.length_meters / 1000).toFixed(1)} km`
                                  : `${Math.round(jam.length_meters)} m`}
                              </p>
                            </div>

                            <span
                              className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${levelClass}`}
                            >
                              {levelText}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </>
            ) : (
              <div className="p-6">
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
                  Live traffic data is currently unavailable.
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-10 border-t border-slate-200 py-6 text-center text-sm text-slate-400">
          Traffic Prediction & Congestion Analytics System
          <span className="mx-2">•</span>
          Machine Learning powered
        </footer>
      </div>
    </main>
  );
}

function MetricCard({
  title,
  value,
  description,
  icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
          <p className="mt-1 text-xs text-slate-400">{description}</p>
        </div>

        <div className="rounded-xl bg-slate-100 p-3">{icon}</div>
      </div>
    </div>
  );
}

function InfoBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-xl font-bold">{value}</p>
    </div>
  );
}

function StatusItem({
  label,
  status,
  detail,
}: {
  label: string;
  status: string;
  detail?: string;
}) {
  const isHealthy = ["online", "ready", "configured", "live"].includes(
    status.toLowerCase(),
  );

  const isWarning = ["stale", "expired", "degraded"].includes(
    status.toLowerCase(),
  );

  const dotClass = isHealthy
    ? "bg-emerald-500"
    : isWarning
      ? "bg-yellow-500"
      : "bg-red-500";

  const textClass = isHealthy
    ? "text-emerald-700"
    : isWarning
      ? "text-yellow-700"
      : "text-red-700";

  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
          {label}
        </p>

        <span className={`h-2.5 w-2.5 rounded-full ${dotClass}`} />
      </div>

      <p className={`mt-2 font-semibold capitalize ${textClass}`}>
        {status.replace("_", " ")}
      </p>

      {detail && <p className="mt-1 text-xs text-slate-400">{detail}</p>}
    </div>
  );
}
