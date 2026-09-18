"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  CalendarDays,
  Cloud,
  RefreshCw,
  TrendingUp,
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_URL = "http://127.0.0.1:8000";

interface HourData {
  hour: number;
  traffic_volume: number;
}

interface DayData {
  day_name: string;
  traffic_volume: number;
}

interface WeatherData {
  weather_main: string;
  traffic_volume: number;
}

export default function AnalyticsPage() {
  const [hourData, setHourData] = useState<HourData[]>([]);
  const [dayData, setDayData] = useState<DayData[]>([]);
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadAnalytics() {
    try {
      setLoading(true);
      setError("");

      const [
        hourResponse,
        dayResponse,
        weatherResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/traffic-by-hour`),
        fetch(`${API_URL}/traffic-by-day`),
        fetch(`${API_URL}/traffic-by-weather`),
      ]);

      if (
        !hourResponse.ok ||
        !dayResponse.ok ||
        !weatherResponse.ok
      ) {
        throw new Error("Unable to load analytics data.");
      }

      const hourResult = await hourResponse.json();
      const dayResult = await dayResponse.json();
      const weatherResult = await weatherResponse.json();

      setHourData(hourResult.data || []);
      setDayData(dayResult.data || []);
      setWeatherData(weatherResult.data || []);
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
    loadAnalytics();
  }, []);

  const formatNumber = (value: number) =>
    new Intl.NumberFormat("en-US").format(
      Math.round(value)
    );

  const average = (values: number[]) => {
    if (!values.length) return 0;

    return (
      values.reduce((sum, value) => sum + value, 0) /
      values.length
    );
  };

  const averageHourlyTraffic = average(
    hourData.map((item) => item.traffic_volume)
  );

  const averageDailyTraffic = average(
    dayData.map((item) => item.traffic_volume)
  );

  const averageWeatherTraffic = average(
    weatherData.map((item) => item.traffic_volume)
  );

  const busiestHour =
    hourData.length > 0
      ? hourData.reduce((previous, current) =>
          current.traffic_volume >
          previous.traffic_volume
            ? current
            : previous
        )
      : null;

  const busiestDay =
    dayData.length > 0
      ? dayData.reduce((previous, current) =>
          current.traffic_volume >
          previous.traffic_volume
            ? current
            : previous
        )
      : null;

  const busiestWeather =
    weatherData.length > 0
      ? weatherData.reduce((previous, current) =>
          current.traffic_volume >
          previous.traffic_volume
            ? current
            : previous
        )
      : null;

  const hourChartData = hourData.map((item) => ({
    hour: `${item.hour}:00`,
    traffic: Math.round(item.traffic_volume),
  }));

  const dayChartData = dayData.map((item) => ({
    day: item.day_name,
    traffic: Math.round(item.traffic_volume),
  }));

  const weatherChartData = weatherData.map((item) => ({
    weather: item.weather_main,
    traffic: Math.round(item.traffic_volume),
  }));

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
              <BarChart3 size={23} />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Traffic Analytics
              </h1>

              <p className="text-sm text-slate-500">
                Historical traffic patterns and insights
              </p>
            </div>
          </div>

          <button
            onClick={loadAnalytics}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw
              size={16}
              className={
                loading ? "animate-spin" : ""
              }
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
              TRAFFIC ANALYTICS
            </p>

            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Understand traffic patterns.
            </h2>

            <p className="mt-3 max-w-2xl text-slate-400">
              Explore how traffic changes throughout the day,
              across the week, and under different weather
              conditions.
            </p>
          </div>
        </section>

        {/* Summary Cards */}
        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <SummaryCard
            title="Average Hourly Traffic"
            value={
              loading
                ? "—"
                : formatNumber(averageHourlyTraffic)
            }
            description="Vehicles per hour"
            icon={<Activity size={21} />}
          />

          <SummaryCard
            title="Busiest Hour"
            value={
              loading || !busiestHour
                ? "—"
                : `${busiestHour.hour}:00`
            }
            description={
              busiestHour
                ? `${formatNumber(
                    busiestHour.traffic_volume
                  )} vehicles`
                : "Highest hourly traffic"
            }
            icon={<TrendingUp size={21} />}
          />

          <SummaryCard
            title="Busiest Day"
            value={
              loading || !busiestDay
                ? "—"
                : busiestDay.day_name
            }
            description={
              busiestDay
                ? `${formatNumber(
                    busiestDay.traffic_volume
                  )} vehicles`
                : "Highest daily traffic"
            }
            icon={<CalendarDays size={21} />}
          />

          <SummaryCard
            title="Weather Categories"
            value={
              loading
                ? "—"
                : String(weatherData.length)
            }
            description="Recorded conditions"
            icon={<Cloud size={21} />}
          />
        </section>

        {/* Hourly Traffic */}
        <section className="mt-8">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-slate-100 p-2">
                  <Activity size={20} />
                </div>

                <div>
                  <p className="text-sm font-medium text-slate-500">
                    HOURLY PATTERN
                  </p>

                  <h3 className="text-xl font-bold">
                    Average Traffic by Hour
                  </h3>
                </div>
              </div>

              {busiestHour && (
                <div className="hidden rounded-lg bg-slate-50 px-4 py-2 text-right sm:block">
                  <p className="text-xs text-slate-400">
                    Peak hour
                  </p>

                  <p className="text-sm font-semibold">
                    {busiestHour.hour}:00
                  </p>
                </div>
              )}
            </div>

            {loading ? (
              <div className="h-80 animate-pulse rounded-xl bg-slate-100" />
            ) : hourData.length === 0 ? (
              <EmptyState message="No hourly traffic data available." />
            ) : (
              <div className="h-80 w-full">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart
                    data={hourChartData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="hour"
                      tick={{
                        fontSize: 11,
                      }}
                      interval={1}
                    />

                    <YAxis
                      tick={{
                        fontSize: 11,
                      }}
                      tickFormatter={(value) =>
                        new Intl.NumberFormat(
                          "en-US",
                          {
                            notation: "compact",
                          }
                        ).format(value)
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

                    <Bar
                      dataKey="traffic"
                      fill="#1e293b"
                      radius={[
                        5,
                        5,
                        0,
                        0,
                      ]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </section>

        {/* Daily + Weather */}
        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          {/* Daily */}
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

            {loading ? (
              <div className="h-72 animate-pulse rounded-xl bg-slate-100" />
            ) : dayData.length === 0 ? (
              <EmptyState message="No daily traffic data available." />
            ) : (
              <div className="h-72">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart
                    data={dayChartData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="day"
                      tick={{
                        fontSize: 11,
                      }}
                    />

                    <YAxis
                      tick={{
                        fontSize: 11,
                      }}
                      tickFormatter={(value) =>
                        new Intl.NumberFormat(
                          "en-US",
                          {
                            notation: "compact",
                          }
                        ).format(value)
                      }
                    />

                    <Tooltip
                      formatter={(value) => [
                        formatNumber(Number(value)),
                        "Traffic",
                      ]}
                    />

                    <Bar
                      dataKey="traffic"
                      fill="#334155"
                      radius={[
                        5,
                        5,
                        0,
                        0,
                      ]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {busiestDay && (
              <div className="mt-5 rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Highest traffic day
                </p>

                <div className="mt-2 flex items-center justify-between">
                  <span className="font-semibold">
                    {busiestDay.day_name}
                  </span>

                  <span className="text-sm text-slate-500">
                    {formatNumber(
                      busiestDay.traffic_volume
                    )}{" "}
                    vehicles
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Weather */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <Cloud size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  WEATHER IMPACT
                </p>

                <h3 className="text-xl font-bold">
                  Traffic by Weather
                </h3>
              </div>
            </div>

            {loading ? (
              <div className="h-72 animate-pulse rounded-xl bg-slate-100" />
            ) : weatherData.length === 0 ? (
              <EmptyState message="No weather traffic data available." />
            ) : (
              <div className="h-72">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart
                    data={weatherChartData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="weather"
                      tick={{
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      tick={{
                        fontSize: 11,
                      }}
                      tickFormatter={(value) =>
                        new Intl.NumberFormat(
                          "en-US",
                          {
                            notation: "compact",
                          }
                        ).format(value)
                      }
                    />

                    <Tooltip
                      formatter={(value) => [
                        formatNumber(Number(value)),
                        "Traffic",
                      ]}
                    />

                    <Bar
                      dataKey="traffic"
                      fill="#475569"
                      radius={[
                        5,
                        5,
                        0,
                        0,
                      ]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {busiestWeather && (
              <div className="mt-5 rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Highest traffic condition
                </p>

                <div className="mt-2 flex items-center justify-between">
                  <span className="font-semibold">
                    {busiestWeather.weather_main}
                  </span>

                  <span className="text-sm text-slate-500">
                    {formatNumber(
                      busiestWeather.traffic_volume
                    )}{" "}
                    vehicles
                  </span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Analytics Summary */}
        <section className="mt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-medium text-slate-500">
                ANALYTICS SUMMARY
              </p>

              <h3 className="mt-1 text-xl font-bold">
                Traffic Pattern Overview
              </h3>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <InsightCard
                title="Hourly Average"
                value={formatNumber(
                  averageHourlyTraffic
                )}
                description="Average traffic volume across the 24-hour cycle."
              />

              <InsightCard
                title="Daily Average"
                value={formatNumber(
                  averageDailyTraffic
                )}
                description="Average traffic volume across recorded weekdays."
              />

              <InsightCard
                title="Weather Average"
                value={formatNumber(
                  averageWeatherTraffic
                )}
                description="Average traffic volume across weather categories."
              />
            </div>
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

function InsightCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-xl bg-slate-50 p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {title}
      </p>

      <p className="mt-2 text-2xl font-bold">
        {value}
      </p>

      <p className="mt-2 text-sm leading-5 text-slate-500">
        {description}
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