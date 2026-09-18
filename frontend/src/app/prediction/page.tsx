"use client";

import { FormEvent, useState } from "react";
import {
  Activity,
  Brain,
  CalendarClock,
  Gauge,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface Prediction {
  status: string;
  prediction_time: string;
  predicted_traffic: number;
  predicted_traffic_rounded: number;
  congestion_level: string;
  model: string;
  model_r2: number;
  model_mae: number;
  model_rmse?: number;
  model_mape?: number;
}

export default function PredictionPage() {
  const [predictionTime, setPredictionTime] = useState(
    "2018-09-30T23:00"
  );

  const [prediction, setPrediction] =
    useState<Prediction | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handlePredict(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");
      setPrediction(null);

      const formattedTime =
        predictionTime.replace("T", " ") + ":00";

      const response = await fetch(
        `${API_URL}/predict`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prediction_time: formattedTime,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail?.[0]?.msg ||
            data?.detail ||
            "Prediction failed."
        );
      }

      setPrediction(data);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to generate prediction. Make sure the FastAPI server is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  const formatNumber = (value: number) =>
    new Intl.NumberFormat("en-US").format(
      Math.round(value)
    );

  const congestionClass = (level?: string) => {
    switch (level) {
      case "Low":
        return "border-emerald-200 bg-emerald-50 text-emerald-700";

      case "Medium":
        return "border-yellow-200 bg-yellow-50 text-yellow-700";

      case "High":
        return "border-orange-200 bg-orange-50 text-orange-700";

      case "Severe":
        return "border-red-200 bg-red-50 text-red-700";

      default:
        return "border-slate-200 bg-slate-50 text-slate-700";
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Brain size={23} />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Traffic Prediction
              </h1>

              <p className="text-sm text-slate-500">
                Generate next-hour traffic predictions
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Intro */}
        <section className="mb-8">
          <div className="rounded-2xl bg-slate-900 p-7 text-white shadow-sm">
            <p className="mb-2 text-sm font-medium text-slate-400">
              MACHINE LEARNING FORECASTING
            </p>

            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Predict future traffic volume.
            </h2>

            <p className="mt-3 max-w-2xl text-slate-400">
              Select a prediction time and let the trained
              Random Forest model estimate the expected traffic
              volume and congestion level.
            </p>
          </div>
        </section>

        {/* Prediction Form */}
        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-1">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <CalendarClock size={20} />
              </div>

              <div>
                <p className="text-sm font-medium text-slate-500">
                  PREDICTION INPUT
                </p>

                <h3 className="text-xl font-bold">
                  Select Time
                </h3>
              </div>
            </div>

            <form onSubmit={handlePredict}>
              <label
                htmlFor="prediction-time"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Prediction date & time
              </label>

              <input
                id="prediction-time"
                type="datetime-local"
                value={predictionTime}
                onChange={(event) =>
                  setPredictionTime(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
              />

              <button
                type="submit"
                disabled={loading}
                className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Activity
                      size={17}
                      className="animate-pulse"
                    />
                    Generating...
                  </>
                ) : (
                  <>
                    <TrendingUp size={17} />
                    Predict Traffic
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 rounded-xl bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Active Model
              </p>

              <div className="mt-2 flex items-center gap-2">
                <Brain size={17} />

                <span className="text-sm font-semibold">
                  Random Forest
                </span>
              </div>
            </div>
          </div>

          {/* Result */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
            {!prediction && !loading && (
              <div className="flex min-h-[360px] flex-col items-center justify-center text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
                  <Target size={30} />
                </div>

                <h3 className="mt-5 text-xl font-bold">
                  No prediction generated
                </h3>

                <p className="mt-2 max-w-md text-sm text-slate-500">
                  Select a date and time from the panel and
                  click Predict Traffic to generate a result.
                </p>
              </div>
            )}

            {loading && (
              <div className="space-y-5">
                <div className="h-6 w-40 animate-pulse rounded bg-slate-100" />

                <div className="h-32 animate-pulse rounded-2xl bg-slate-100" />

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="h-24 animate-pulse rounded-xl bg-slate-100" />
                  <div className="h-24 animate-pulse rounded-xl bg-slate-100" />
                </div>
              </div>
            )}

            {error && !loading && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-700">
                <div className="flex items-center gap-3">
                  <AlertTriangle size={20} />

                  <div>
                    <p className="font-semibold">
                      Prediction Error
                    </p>

                    <p className="mt-1 text-sm">
                      {error}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {prediction && !loading && (
              <>
                <div className="mb-6 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500">
                      PREDICTION RESULT
                    </p>

                    <h3 className="mt-1 text-xl font-bold">
                      Traffic Forecast
                    </h3>
                  </div>

                  <div
                    className={`rounded-full border px-4 py-2 text-sm font-semibold ${congestionClass(
                      prediction.congestion_level
                    )}`}
                  >
                    {prediction.congestion_level} Congestion
                  </div>
                </div>

                {/* Main Prediction */}
                <div className="rounded-2xl bg-slate-900 p-7 text-white">
                  <p className="text-sm text-slate-400">
                    Predicted traffic
                  </p>

                  <div className="mt-2 flex items-end gap-3">
                    <span className="text-6xl font-bold tracking-tight">
                      {formatNumber(
                        prediction.predicted_traffic_rounded
                      )}
                    </span>

                    <span className="mb-2 text-sm text-slate-400">
                      vehicles
                    </span>
                  </div>

                  <div className="mt-5 flex items-center gap-2 text-sm text-slate-400">
                    <CalendarClock size={16} />

                    {prediction.prediction_time}
                  </div>
                </div>

                {/* Metrics */}
                <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <Metric
                    label="Model R²"
                    value={`${(
                      prediction.model_r2 * 100
                    ).toFixed(2)}%`}
                  />

                  <Metric
                    label="MAE"
                    value={prediction.model_mae.toFixed(2)}
                  />

                  <Metric
                    label="RMSE"
                    value={
                      prediction.model_rmse !== undefined
                        ? prediction.model_rmse.toFixed(2)
                        : "—"
                    }
                  />

                  <Metric
                    label="MAPE"
                    value={
                      prediction.model_mape !== undefined
                        ? `${prediction.model_mape.toFixed(2)}%`
                        : "—"
                    }
                  />
                </div>

                {/* Model */}
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Forecasting Model
                    </p>

                    <div className="mt-2 flex items-center gap-2">
                      <Brain size={18} />

                      <span className="font-semibold">
                        {prediction.model}
                      </span>
                    </div>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Prediction Status
                    </p>

                    <div className="mt-2 flex items-center gap-2">
                      <CheckCircle2
                        size={18}
                        className="text-emerald-600"
                      />

                      <span className="font-semibold text-emerald-700">
                        Successful
                      </span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </section>

        {/* Explanation */}
        <section className="mt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="rounded-xl bg-slate-100 p-3">
                <Gauge size={21} />
              </div>

              <div>
                <h3 className="font-bold">
                  How the prediction works
                </h3>

                <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-500">
                  The forecasting model uses historical traffic
                  patterns, time-based features, lagged traffic
                  values, rolling statistics, weather information,
                  and other engineered features to estimate the
                  traffic volume for the selected prediction time.
                </p>
              </div>
            </div>
          </div>
        </section>

        <footer className="mt-10 border-t border-slate-200 py-6 text-center text-sm text-slate-400">
          Traffic Prediction & Congestion Analytics System
          <span className="mx-2">•</span>
          Machine Learning powered
        </footer>
      </div>
    </main>
  );
}

function Metric({
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

      <p className="mt-2 text-xl font-bold">
        {value}
      </p>
    </div>
  );
}
