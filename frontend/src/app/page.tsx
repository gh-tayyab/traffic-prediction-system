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
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

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

export default function Home() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [hourData, setHourData] = useState<HourData[]>([]);
  const [dayData, setDayData] = useState<DayData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
            prediction_time: "2018-09-30 23:00:00",
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
        "Could not connect to the Traffic Prediction API. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
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
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
              API Online
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
                  Analyze historical traffic patterns and predict the next
                  hour using a trained Random Forest forecasting model.
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

                <h3 className="mt-1 text-xl font-bold">
                  Traffic Prediction
                </h3>
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
                    prediction.congestion_level
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
                    <span className="font-medium">
                      {prediction.model_mae}
                    </span>
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
                const height =
                  Math.max(
                    (item.traffic_volume / maxHourlyTraffic) * 100,
                    4
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
                          item.traffic_volume
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

                <h3 className="text-xl font-bold">
                  Traffic by Day
                </h3>
              </div>
            </div>

            <div className="space-y-4">
              {dayData.map((item) => {
                const maxDay =
                  dayData.length > 0
                    ? Math.max(
                        ...dayData.map((day) => day.traffic_volume)
                      )
                    : 1;

                const width =
                  (item.traffic_volume / maxDay) * 100;

                return (
                  <div key={item.day_name}>
                    <div className="mb-1.5 flex justify-between text-sm">
                      <span className="font-medium">
                        {item.day_name}
                      </span>

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
                <p className="text-sm font-medium text-slate-500">
                  DATASET
                </p>

                <h3 className="text-xl font-bold">
                  Dataset Overview
                </h3>
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

                  <p className="text-sm text-slate-500">
                    to
                  </p>

                  <p className="text-sm font-semibold">
                    {statistics.data_end}
                  </p>
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

        <div className="rounded-xl bg-slate-100 p-3">
          {icon}
        </div>
      </div>
    </div>
  );
}

function InfoBox({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-xl font-bold">{value}</p>
    </div>
  );
}