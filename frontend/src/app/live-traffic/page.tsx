"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Clock3,
  Gauge,
  MapPin,
  Radio,
  RefreshCw,
  Wifi,
} from "lucide-react";
import dynamic from "next/dynamic";

const TrafficMap = dynamic(() => import("../../components/TrafficMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center bg-slate-100">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />

        <p className="mt-3 text-sm text-slate-500">Loading traffic map...</p>
      </div>
    </div>
  ),
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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

export default function LiveTrafficPage() {
  const [liveTraffic, setLiveTraffic] = useState<LiveTraffic | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [selectedJamId, setSelectedJamId] = useState<number | null>(null);

  const [severityFilter, setSeverityFilter] = useState<
    "All" | "Light" | "Moderate" | "Heavy" | "Severe"
  >("All");
  async function loadLiveTraffic() {
    try {
      setRefreshing(true);
      setError("");

      const response = await fetch(`${API_URL}/live-traffic`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Unable to load live traffic.");
      }

      const data: LiveTraffic = await response.json();

      setLiveTraffic(data);
    } catch (err) {
      console.error("Live traffic error:", err);
      setError("Live traffic data is currently unavailable.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadLiveTraffic();

    const interval = setInterval(() => {
      loadLiveTraffic();
    }, 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const getSeverity = (level: number) => {
    if (level >= 4) {
      return {
        label: "Severe",
        className: "border-red-200 bg-red-50 text-red-700",
      };
    }

    if (level === 3) {
      return {
        label: "Heavy",
        className: "border-orange-200 bg-orange-50 text-orange-700",
      };
    }

    if (level === 2) {
      return {
        label: "Moderate",
        className: "border-yellow-200 bg-yellow-50 text-yellow-700",
      };
    }

    return {
      label: "Light",
      className: "border-emerald-200 bg-emerald-50 text-emerald-700",
    };
  };

  const formatJamLength = (meters: number) => {
    if (meters >= 1000) {
      return `${(meters / 1000).toFixed(1)} km`;
    }

    return `${Math.round(meters)} m`;
  };

  const formatAge = (seconds: number | null) => {
    if (seconds === null) {
      return "Unknown";
    }

    if (seconds < 60) {
      return `${Math.round(seconds)} sec ago`;
    }

    return `${Math.round(seconds / 60)} min ago`;
  };
  const filteredJams =
    liveTraffic?.jams.filter((jam) => {
      if (severityFilter === "All") {
        return true;
      }

      return getSeverity(jam.level).label === severityFilter;
    }) ?? [];
  const selectedJam =
    liveTraffic?.jams.find((jam) => jam.id === selectedJamId) ?? null;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Header */}
        <section className="mb-8">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <p className="text-sm font-medium text-slate-500">
                  REAL-TIME MONITORING
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

              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
                Karachi Live Traffic
              </h1>

              <p className="mt-2 max-w-2xl text-slate-500">
                Monitor current traffic congestion, road speeds, and active
                traffic jams across Karachi.
              </p>
            </div>

            <button
              onClick={loadLiveTraffic}
              disabled={refreshing}
              className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
            >
              <RefreshCw
                size={17}
                className={refreshing ? "animate-spin" : ""}
              />
              Refresh Traffic
            </button>
          </div>
        </section>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading ? (
          <div className="grid gap-5 md:grid-cols-3">
            <div className="h-32 animate-pulse rounded-2xl bg-white" />
            <div className="h-32 animate-pulse rounded-2xl bg-white" />
            <div className="h-32 animate-pulse rounded-2xl bg-white" />
          </div>
        ) : liveTraffic ? (
          <>
            {/* Summary */}
            <section className="grid gap-5 md:grid-cols-3">
              <SummaryCard
                title="Active Jams"
                value={String(liveTraffic.jam_count)}
                description="Currently reported"
                icon={<AlertTriangle size={21} />}
              />

              <SummaryCard
                title="Highest Level"
                value={`Level ${liveTraffic.max_jam_level}`}
                description={liveTraffic.congestion_status}
                icon={<Gauge size={21} />}
              />

              <SummaryCard
                title="Data Source"
                value="Waze"
                description={`Updated ${formatAge(
                  liveTraffic.cache_age_seconds,
                )}`}
                icon={<Radio size={21} />}
              />
            </section>

            {/* Connection status */}
            <section className="mt-6">
              <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-center">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-emerald-50 p-3 text-emerald-600">
                    <Wifi size={20} />
                  </div>

                  <div>
                    <p className="font-semibold">Waze Traffic Feed</p>

                    <p className="text-sm text-slate-500">
                      {liveTraffic.stale
                        ? "Cached data is older than the refresh window."
                        : "Live traffic feed is up to date."}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Clock3 size={16} />

                  {formatAge(liveTraffic.cache_age_seconds)}
                </div>
              </div>
            </section>

            {/* Traffic Map Placeholder */}
            <section className="mt-6">
              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-200 p-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-slate-100 p-3">
                      <MapPin size={21} />
                    </div>

                    <div>
                      <p className="text-sm font-medium text-slate-500">
                        TRAFFIC MAP
                      </p>

                      <h2 className="mt-1 text-xl font-bold">
                        Karachi Traffic Map
                      </h2>
                    </div>
                  </div>
                </div>

                <div className="h-[500px] w-full">
                  <TrafficMap
                    jams={filteredJams}
                    selectedJamId={selectedJamId}
                    onSelectJam={(jam) => {
                      setSelectedJamId(jam.id);
                    }}
                  />
                </div>
                <div className="flex flex-wrap items-center gap-5 border-t border-slate-100 px-6 py-4 text-xs text-slate-500">
                  <span className="font-semibold text-slate-600">
                    Traffic Level
                  </span>

                  <span className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full bg-emerald-500" />
                    Light
                  </span>

                  <span className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full bg-yellow-500" />
                    Moderate
                  </span>

                  <span className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full bg-orange-500" />
                    Heavy
                  </span>

                  <span className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full bg-red-500" />
                    Severe
                  </span>
                </div>
              </div>
            </section>

            {selectedJam && (
              <section className="mt-6">
                <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                  <div className="border-b border-slate-200 p-6">
                    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                      <div>
                        <p className="text-sm font-medium text-slate-500">
                          SELECTED ROAD
                        </p>

                        <h2 className="mt-1 text-xl font-bold">
                          {selectedJam.street || "Unnamed Road"}
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                          {selectedJam.city || "Karachi"}
                          {selectedJam.end_node
                            ? ` • ${selectedJam.end_node}`
                            : ""}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() => setSelectedJamId(null)}
                        className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
                      >
                        Clear Selection
                      </button>
                    </div>
                  </div>

                  <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-4">
                    <DetailBox
                      label="Current Speed"
                      value={`${selectedJam.speed_kmh.toFixed(1)} km/h`}
                    />

                    <DetailBox
                      label="Jam Length"
                      value={formatJamLength(selectedJam.length_meters)}
                    />

                    <DetailBox
                      label="Traffic Level"
                      value={`Level ${selectedJam.level}`}
                    />

                    <DetailBox
                      label="Severity"
                      value={getSeverity(selectedJam.level).label}
                    />
                  </div>

                  <div className="border-t border-slate-100 px-6 py-4 text-xs text-slate-400">
                    Coordinates: {selectedJam.latitude.toFixed(5)},{" "}
                    {selectedJam.longitude.toFixed(5)}
                  </div>
                </div>
              </section>
            )}

            {/* Active Jams */}
            <section className="mt-6">
              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-200 p-6">
                  <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-500">
                        CURRENT ROAD CONDITIONS
                      </p>

                      <h2 className="mt-1 text-xl font-bold">
                        Active Traffic Jams
                      </h2>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      {(
                        ["All", "Light", "Moderate", "Heavy", "Severe"] as const
                      ).map((filter) => (
                        <button
                          key={filter}
                          onClick={() => {
                            setSeverityFilter(filter);

                            if (
                              selectedJam &&
                              filter !== "All" &&
                              getSeverity(selectedJam.level).label !== filter
                            ) {
                              setSelectedJamId(null);
                            }
                          }}
                          className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                            severityFilter === filter
                              ? "border-slate-900 bg-slate-900 text-white"
                              : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                          }`}
                        >
                          {filter}
                        </button>
                      ))}

                      <span className="ml-1 rounded-full bg-slate-100 px-3 py-1.5 text-sm font-semibold text-slate-600">
                        {filteredJams.length}{" "}
                        {filteredJams.length === 1 ? "road" : "roads"}
                      </span>
                    </div>
                  </div>
                </div>

                {filteredJams.length === 0 ? (
                  <div className="p-8 text-center">
                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
                      <Activity size={25} />
                    </div>

                    <h3 className="mt-4 text-lg font-semibold">
                      {severityFilter === "All"
                        ? "No Active Jams"
                        : `No ${severityFilter} Traffic`}
                    </h3>

                    <p className="mt-2 text-sm text-slate-500">
                      {severityFilter === "All"
                        ? "Waze is currently reporting no active traffic jams in the monitored Karachi area."
                        : `There are currently no ${severityFilter.toLowerCase()} traffic jams in the monitored Karachi area.`}
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {filteredJams.map((jam) => {
                      const severity = getSeverity(jam.level);

                      return (
                        <button
                          key={jam.id}
                          type="button"
                          onClick={() => setSelectedJamId(jam.id)}
                          className={`block w-full p-6 text-left transition ${
                            selectedJamId === jam.id
                              ? "bg-slate-50 ring-2 ring-inset ring-slate-900/10"
                              : "hover:bg-slate-50"
                          }`}
                        >
                          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                            <div className="flex items-start gap-4">
                              <div className="mt-0.5 rounded-xl bg-slate-100 p-3 text-slate-600">
                                <MapPin size={20} />
                              </div>

                              <div>
                                <div className="flex items-center gap-2">
                                  <h3 className="font-semibold">
                                    {jam.street || "Unnamed Road"}
                                  </h3>

                                  {selectedJamId === jam.id && (
                                    <span className="rounded-full bg-slate-900 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
                                      Selected
                                    </span>
                                  )}
                                </div>

                                <p className="mt-1 text-sm text-slate-500">
                                  {jam.city || "Karachi"}

                                  {jam.end_node ? ` • ${jam.end_node}` : ""}
                                </p>

                                <p className="mt-2 text-xs text-slate-400">
                                  Coordinates: {jam.latitude.toFixed(5)},{" "}
                                  {jam.longitude.toFixed(5)}
                                </p>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-5 sm:grid-cols-4">
                              <div>
                                <p className="text-xs uppercase tracking-wide text-slate-400">
                                  Speed
                                </p>

                                <p className="mt-1 font-bold">
                                  {jam.speed_kmh.toFixed(1)} km/h
                                </p>
                              </div>

                              <div>
                                <p className="text-xs uppercase tracking-wide text-slate-400">
                                  Jam Length
                                </p>

                                <p className="mt-1 font-bold">
                                  {formatJamLength(jam.length_meters)}
                                </p>
                              </div>

                              <div>
                                <p className="text-xs uppercase tracking-wide text-slate-400">
                                  Level
                                </p>

                                <p className="mt-1 font-bold">{jam.level}</p>
                              </div>

                              <div>
                                <p className="text-xs uppercase tracking-wide text-slate-400">
                                  Severity
                                </p>

                                <span
                                  className={`mt-1 inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${severity.className}`}
                                >
                                  {severity.label}
                                </span>
                              </div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </section>
          </>
        ) : null}

        {/* Footer note */}
        <div className="mt-6 flex items-center gap-2 text-xs text-slate-400">
          <Clock3 size={14} />

          <span>
            Traffic data is provided through the WazeAPI feed and may be subject
            to source availability and refresh intervals.
          </span>
        </div>
      </div>
    </main>
  );
}

function DetailBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-xl font-bold">{value}</p>
    </div>
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
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>

          <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>

          <p className="mt-2 text-sm text-slate-400">{description}</p>
        </div>

        <div className="rounded-xl bg-slate-100 p-3">{icon}</div>
      </div>
    </div>
  );
}
