"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CloudSun,
  Cloud,
  CloudRain,
  CloudLightning,
  Snowflake,
  Sun,
  Wind,
  Eye,
  RefreshCw,
  TrendingUp,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface WeatherRecord {
  weather_main: string;
  traffic_volume: number;
}

interface WeatherResponse {
  status: string;
  data: WeatherRecord[];
}

const weatherIcon = (weather: string) => {
  const value = weather.toLowerCase();

  if (value === "clear") {
    return <Sun size={22} />;
  }

  if (value === "clouds") {
    return <Cloud size={22} />;
  }

  if (value === "rain" || value === "drizzle") {
    return <CloudRain size={22} />;
  }

  if (value === "thunderstorm") {
    return <CloudLightning size={22} />;
  }

  if (value === "snow") {
    return <Snowflake size={22} />;
  }

  if (value === "squall") {
    return <Wind size={22} />;
  }

  if (
    value === "mist" ||
    value === "fog" ||
    value === "haze" ||
    value === "smoke"
  ) {
    return <Eye size={22} />;
  }

  return <CloudSun size={22} />;
};

export default function WeatherPage() {
  const [data, setData] = useState<WeatherRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadWeather() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/traffic-by-weather`);

      if (!response.ok) {
        throw new Error("Failed to load weather data.");
      }

      const result: WeatherResponse = await response.json();

      setData(result.data);
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
    loadWeather();
  }, []);

  const formatNumber = (value: number) =>
    new Intl.NumberFormat("en-US").format(Math.round(value));

  const statistics = useMemo(() => {
    if (!data.length) {
      return {
        average: 0,
        highest: null as WeatherRecord | null,
        lowest: null as WeatherRecord | null,
      };
    }

    const average =
      data.reduce((sum, item) => sum + item.traffic_volume, 0) /
      data.length;

    const highest = data.reduce((max, item) =>
      item.traffic_volume > max.traffic_volume ? item : max
    );

    const lowest = data.reduce((min, item) =>
      item.traffic_volume < min.traffic_volume ? item : min
    );

    return {
      average,
      highest,
      lowest,
    };
  }, [data]);

  const maxTraffic = useMemo(() => {
    if (!data.length) return 1;

    return Math.max(...data.map((item) => item.traffic_volume));
  }, [data]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="flex items-center justify-between px-6 py-5">
          <div>
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-slate-900 p-3 text-white">
                <CloudSun size={21} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  WEATHER ANALYTICS
                </p>

                <h1 className="text-2xl font-bold tracking-tight">
                  Weather Impact
                </h1>
              </div>
            </div>

            <p className="mt-3 text-sm text-slate-500">
              Analyze how different weather conditions are associated with
              traffic volume.
            </p>
          </div>

          <button
            onClick={loadWeather}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={loading ? "animate-spin" : ""}
            />
            Refresh
          </button>
        </div>
      </header>

      <div className="px-6 py-8">
        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Hero */}
        <section className="mb-8 rounded-2xl bg-slate-900 p-7 text-white">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
            <div>
              <p className="mb-2 text-sm font-medium text-slate-400">
                WEATHER & TRAFFIC RELATIONSHIP
              </p>

              <h2 className="max-w-3xl text-3xl font-bold tracking-tight">
                Understanding traffic patterns across weather conditions.
              </h2>

              <p className="mt-3 max-w-2xl text-slate-400">
                Compare average traffic volume across recorded weather
                conditions and identify conditions associated with higher or
                lower traffic activity.
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-5 py-4">
              <CloudSun size={22} />

              <div>
                <p className="text-xs text-slate-400">
                  WEATHER CONDITIONS
                </p>

                <p className="font-semibold">
                  {loading ? "—" : `${data.length} Conditions`}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* KPI Cards */}
        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Conditions"
            value={loading ? "—" : formatNumber(data.length)}
            description="Recorded weather categories"
            icon={<CloudSun size={21} />}
          />

          <MetricCard
            title="Average Traffic"
            value={
              loading ? "—" : formatNumber(statistics.average)
            }
            description="Across weather conditions"
            icon={<TrendingUp size={21} />}
          />

          <MetricCard
            title="Highest Traffic"
            value={
              loading || !statistics.highest
                ? "—"
                : formatNumber(statistics.highest.traffic_volume)
            }
            description={
              statistics.highest
                ? statistics.highest.weather_main
                : "Weather condition"
            }
            icon={<TrendingUp size={21} />}
          />

          <MetricCard
            title="Lowest Traffic"
            value={
              loading || !statistics.lowest
                ? "—"
                : formatNumber(statistics.lowest.traffic_volume)
            }
            description={
              statistics.lowest
                ? statistics.lowest.weather_main
                : "Weather condition"
            }
            icon={<Eye size={21} />}
          />
        </section>

        {/* Main Chart */}
        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                WEATHER COMPARISON
              </p>

              <h3 className="mt-1 text-xl font-bold">
                Average Traffic by Weather
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Traffic volume associated with each weather category.
              </p>
            </div>

            <div className="rounded-lg bg-slate-100 p-2">
              <CloudSun size={20} />
            </div>
          </div>

          {loading ? (
            <div className="h-80 animate-pulse rounded-xl bg-slate-100" />
          ) : data.length === 0 ? (
            <div className="flex h-80 items-center justify-center text-sm text-slate-400">
              No weather data available.
            </div>
          ) : (
            <div className="space-y-5">
              {data.map((item) => {
                const width =
                  (item.traffic_volume / maxTraffic) * 100;

                return (
                  <div key={item.weather_main}>
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-slate-100 p-2">
                          {weatherIcon(item.weather_main)}
                        </div>

                        <span className="text-sm font-semibold">
                          {item.weather_main}
                        </span>
                      </div>

                      <span className="text-sm font-semibold text-slate-700">
                        {formatNumber(item.traffic_volume)}
                      </span>
                    </div>

                    <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-slate-800 transition-all duration-500"
                        style={{
                          width: `${width}%`,
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Weather Cards */}
        <section className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((item) => (
            <div
              key={item.weather_main}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <div className="rounded-xl bg-slate-100 p-3">
                  {weatherIcon(item.weather_main)}
                </div>

                <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-500">
                  Weather
                </span>
              </div>

              <h3 className="mt-5 text-lg font-bold">
                {item.weather_main}
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Associated traffic volume
              </p>

              <div className="mt-5 flex items-end justify-between">
                <div>
                  <p className="text-3xl font-bold tracking-tight">
                    {formatNumber(item.traffic_volume)}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    vehicles per hour
                  </p>
                </div>

                <div className="text-slate-400">
                  <ActivityIcon />
                </div>
              </div>
            </div>
          ))}
        </section>

        {/* Insight */}
        {!loading && statistics.highest && statistics.lowest && (
          <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="rounded-xl bg-slate-100 p-3">
                <TrendingUp size={21} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  DATA INSIGHT
                </p>

                <h3 className="mt-1 text-xl font-bold">
                  Weather-related traffic variation
                </h3>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                  Among the weather categories returned by the API,{" "}
                  <span className="font-semibold text-slate-800">
                    {statistics.highest.weather_main}
                  </span>{" "}
                  has the highest associated average traffic volume at{" "}
                  <span className="font-semibold text-slate-800">
                    {formatNumber(statistics.highest.traffic_volume)}
                  </span>{" "}
                  vehicles per hour, while{" "}
                  <span className="font-semibold text-slate-800">
                    {statistics.lowest.weather_main}
                  </span>{" "}
                  has the lowest at{" "}
                  <span className="font-semibold text-slate-800">
                    {formatNumber(statistics.lowest.traffic_volume)}
                  </span>
                  .
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Data Table */}
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6">
            <p className="text-sm font-medium text-slate-500">
              WEATHER DATA
            </p>

            <h3 className="mt-1 text-xl font-bold">
              Weather Conditions & Traffic
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-4 py-3 font-semibold">
                    Weather
                  </th>

                  <th className="px-4 py-3 font-semibold">
                    Condition
                  </th>

                  <th className="px-4 py-3 text-right font-semibold">
                    Traffic Volume
                  </th>
                </tr>
              </thead>

              <tbody>
                {data.map((item) => (
                  <tr
                    key={item.weather_main}
                    className="border-b border-slate-100 transition hover:bg-slate-50"
                  >
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-slate-100 p-2">
                          {weatherIcon(item.weather_main)}
                        </div>

                        <span className="font-semibold">
                          {item.weather_main}
                        </span>
                      </div>
                    </td>

                    <td className="px-4 py-4 text-slate-500">
                      Recorded weather category
                    </td>

                    <td className="px-4 py-4 text-right font-semibold">
                      {formatNumber(item.traffic_volume)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-10 border-t border-slate-200 py-6 text-center text-sm text-slate-400">
          Traffic Prediction & Congestion Analytics System
          <span className="mx-2">•</span>
          Weather Impact Analysis
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
          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p className="mt-2 text-3xl font-bold tracking-tight">
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

function ActivityIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12h4l3-8 4 16 3-8h4" />
    </svg>
  );
}
