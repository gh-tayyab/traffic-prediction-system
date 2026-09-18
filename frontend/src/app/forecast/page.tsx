"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  CalendarDays,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  BarChart3,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_URL = "http://127.0.0.1:8000";

interface ForecastData {
  date_time: string;
  actual: number;
}

interface ForecastResponse {
  status: string;
  records: number;
  data: ForecastData[];
}

export default function ForecastPage() {
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadForecast() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/forecast`);

      if (!response.ok) {
        throw new Error("Unable to load forecast data.");
      }

      const result: ForecastResponse = await response.json();

      setForecastData(result.data || []);
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
    loadForecast();
  }, []);

  const formatNumber = (value: number) =>
    new Intl.NumberFormat("en-US").format(Math.round(value));

  const averageTraffic = useMemo(() => {
    if (!forecastData.length) return 0;

    return (
      forecastData.reduce(
        (sum, item) => sum + item.actual,
        0
      ) / forecastData.length
    );
  }, [forecastData]);

  const maximumTraffic = useMemo(() => {
    if (!forecastData.length) return 0;

    return Math.max(
      ...forecastData.map((item) => item.actual)
    );
  }, [forecastData]);

  const minimumTraffic = useMemo(() => {
    if (!forecastData.length) return 0;

    return Math.min(
      ...forecastData.map((item) => item.actual)
    );
  }, [forecastData]);

  const peakRecord = useMemo(() => {
    if (!forecastData.length) return null;

    return forecastData.reduce((previous, current) =>
      current.actual > previous.actual
        ? current
        : previous
    );
  }, [forecastData]);

  const lowestRecord = useMemo(() => {
    if (!forecastData.length) return null;

    return forecastData.reduce((previous, current) =>
      current.actual < previous.actual
        ? current
        : previous
    );
  }, [forecastData]);

  const chartData = useMemo(() => {
    return forecastData.map((item) => {
      const date = new Date(
        item.date_time.replace(" ", "T")
      );

      return {
        date_time: item.date_time,
        label: `${date.getDate()}/${date.getMonth() + 1} ${date
          .getHours()
          .toString()
          .padStart(2, "0")}:00`,
        traffic: item.actual,
      };
    });
  }, [forecastData]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Activity size={23} />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Traffic Forecast
              </h1>

              <p className="text-sm text-slate-500">
                Historical traffic forecast timeline
              </p>
            </div>
          </div>

          <button
            onClick={loadForecast}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw
              size={16}
              className={loading ? "animate-spin" : ""}
            />
            Refresh
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Hero */}
        <section className="mb-8">
          <div className="rounded-2xl bg-slate-900 p-7 text-white shadow-sm">
            <p className="mb-2 text-sm font-medium text-slate-400">
              FORECAST ANALYSIS
            </p>

            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Analyze traffic across the forecast period.
            </h2>

            <p className="mt-3 max-w-2xl text-slate-400">
              Explore hourly traffic behavior across the
              seven-day forecast window and identify peak
              traffic periods.
            </p>
          </div>
        </section>

        {/* Summary Cards */}
        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <SummaryCard
            title="Forecast Records"
            value={
              loading
                ? "—"
                : formatNumber(forecastData.length)
            }
            description="Hourly observations"
            icon={<CalendarDays size={21} />}
          />

          <SummaryCard
            title="Average Traffic"
            value={
              loading
                ? "—"
                : formatNumber(averageTraffic)
            }
            description="Vehicles per hour"
            icon={<Activity size={21} />}
          />

          <SummaryCard
            title="Peak Traffic"
            value={
              loading
                ? "—"
                : formatNumber(maximumTraffic)
            }
            description="Highest recorded volume"
            icon={<TrendingUp size={21} />}
          />

          <SummaryCard
            title="Lowest Traffic"
            value={
              loading
                ? "—"
                : formatNumber(minimumTraffic)
            }
            description="Lowest recorded volume"
            icon={<TrendingDown size={21} />}
          />
        </section>

        {/* Main Forecast Chart */}
        <section className="mt-8">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-slate-100 p-2">
                  <BarChart3 size={20} />
                </div>

                <div>
                  <p className="text-sm font-medium text-slate-500">
                    HOURLY FORECAST
                  </p>

                  <h3 className="text-xl font-bold">
                    Traffic Volume Over Time
                  </h3>
                </div>
              </div>

              {forecastData.length > 0 && (
                <div className="hidden rounded-lg bg-slate-50 px-4 py-2 text-right sm:block">
                  <p className="text-xs text-slate-400">
                    Records
                  </p>

                  <p className="text-sm font-semibold">
                    {forecastData.length} hours
                  </p>
                </div>
              )}
            </div>

            {loading ? (
              <div className="h-96 animate-pulse rounded-xl bg-slate-100" />
            ) : forecastData.length === 0 ? (
              <EmptyState message="No forecast data available." />
            ) : (
              <div className="h-96 w-full">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <LineChart
                    data={chartData}
                    margin={{
                      top: 10,
                      right: 20,
                      left: 0,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="label"
                      tick={{
                        fontSize: 10,
                      }}
                      interval={11}
                    />

                    <YAxis
                      tick={{
                        fontSize: 11,
                      }}
                      tickFormatter={(value) =>
                        new Intl.NumberFormat("en-US", {
                          notation: "compact",
                        }).format(value)
                      }
                    />

                    <Tooltip
                      formatter={(value) => [
                        formatNumber(Number(value)),
                        "Traffic",
                      ]}
                      labelFormatter={(label) =>
                        `Time: ${label}`
                      }
                    />

                    <Line
                      type="monotone"
                      dataKey="traffic"
                      stroke="#1e293b"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </section>

        {/* Forecast Details */}
        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          {/* Peak Traffic */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <TrendingUp size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  PEAK PERIOD
                </p>

                <h3 className="text-xl font-bold">
                  Highest Traffic
                </h3>
              </div>
            </div>

            {loading || !peakRecord ? (
              <div className="h-32 animate-pulse rounded-xl bg-slate-100" />
            ) : (
              <div className="rounded-xl bg-slate-50 p-5">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Maximum traffic volume
                </p>

                <p className="mt-2 text-4xl font-bold">
                  {formatNumber(peakRecord.actual)}
                </p>

                <p className="mt-2 text-sm text-slate-500">
                  vehicles
                </p>

                <div className="mt-5 border-t border-slate-200 pt-4">
                  <p className="text-xs text-slate-400">
                    Recorded at
                  </p>

                  <p className="mt-1 text-sm font-semibold">
                    {peakRecord.date_time}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Lowest Traffic */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <TrendingDown size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  LOWEST PERIOD
                </p>

                <h3 className="text-xl font-bold">
                  Lowest Traffic
                </h3>
              </div>
            </div>

            {loading || !lowestRecord ? (
              <div className="h-32 animate-pulse rounded-xl bg-slate-100" />
            ) : (
              <div className="rounded-xl bg-slate-50 p-5">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Minimum traffic volume
                </p>

                <p className="mt-2 text-4xl font-bold">
                  {formatNumber(lowestRecord.actual)}
                </p>

                <p className="mt-2 text-sm text-slate-500">
                  vehicles
                </p>

                <div className="mt-5 border-t border-slate-200 pt-4">
                  <p className="text-xs text-slate-400">
                    Recorded at
                  </p>

                  <p className="mt-1 text-sm font-semibold">
                    {lowestRecord.date_time}
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Forecast Period */}
        <section className="mt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <CalendarDays size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  FORECAST PERIOD
                </p>

                <h3 className="text-xl font-bold">
                  Timeline Information
                </h3>
              </div>
            </div>

            {forecastData.length > 0 && (
              <div className="grid gap-4 md:grid-cols-3">
                <InfoBox
                  label="Start"
                  value={forecastData[0].date_time}
                />

                <InfoBox
                  label="End"
                  value={
                    forecastData[
                      forecastData.length - 1
                    ].date_time
                  }
                />

                <InfoBox
                  label="Total Hours"
                  value={String(forecastData.length)}
                />
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

function SummaryCard({
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
          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold tracking-tight">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {description}
          </p>
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

      <p className="mt-2 text-sm font-bold">
        {value}
      </p>
    </div>
  );
}

function EmptyState({
  message,
}: {
  message: string;
}) {
  return (
    <div className="flex h-72 items-center justify-center rounded-xl bg-slate-50 text-sm text-slate-400">
      {message}
    </div>
  );
}