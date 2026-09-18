"use client";

import { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  Brain,
  RefreshCw,
  Target,
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
  Legend,
} from "recharts";

const API_URL = "http://127.0.0.1:8000";

interface ModelData {
  Model: string;
  MAE: number;
  RMSE: number;
  R2: number;
  MAPE: number;
}

export default function ModelPerformancePage() {
  const [models, setModels] = useState<ModelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadPerformance() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/model-performance`);

      if (!response.ok) {
        throw new Error("Unable to load model performance.");
      }

      const result = await response.json();

      setModels(result.models || []);
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
    loadPerformance();
  }, []);

  const formatNumber = (value: number, decimals = 0) =>
    new Intl.NumberFormat("en-US", {
      maximumFractionDigits: decimals,
      minimumFractionDigits: decimals,
    }).format(value);

  const bestR2Model = useMemo(() => {
    if (!models.length) return null;

    return models.reduce((previous, current) =>
      current.R2 > previous.R2 ? current : previous
    );
  }, [models]);

  const lowestMAEModel = useMemo(() => {
    if (!models.length) return null;

    return models.reduce((previous, current) =>
      current.MAE < previous.MAE ? current : previous
    );
  }, [models]);

  const lowestRMSEModel = useMemo(() => {
    if (!models.length) return null;

    return models.reduce((previous, current) =>
      current.RMSE < previous.RMSE ? current : previous
    );
  }, [models]);

  const modelChartData = models.map((model) => ({
    model: model.Model,
    MAE: Math.round(model.MAE),
    RMSE: Math.round(model.RMSE),
  }));

  const r2ChartData = models.map((model) => ({
    model: model.Model,
    R2: Number((model.R2 * 100).toFixed(2)),
  }));

  const mapeChartData = models.map((model) => ({
    model: model.Model,
    MAPE: Number(model.MAPE.toFixed(2)),
  }));

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Brain size={23} />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Model Performance
              </h1>

              <p className="text-sm text-slate-500">
                Compare machine learning models and evaluation metrics
              </p>
            </div>
          </div>

          <button
            onClick={loadPerformance}
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
              MACHINE LEARNING EVALUATION
            </p>

            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Compare model performance.
            </h2>

            <p className="mt-3 max-w-2xl text-slate-400">
              Evaluate traffic prediction models using error metrics,
              goodness-of-fit, and percentage-based accuracy measures.
            </p>
          </div>
        </section>

        {/* Summary Cards */}
        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <SummaryCard
            title="Models Evaluated"
            value={loading ? "—" : String(models.length)}
            description="Prediction models"
            icon={<Brain size={21} />}
          />

          <SummaryCard
            title="Best R²"
            value={
              loading || !bestR2Model
                ? "—"
                : `${formatNumber(bestR2Model.R2 * 100, 2)}%`
            }
            description={
              bestR2Model
                ? bestR2Model.Model
                : "Highest explained variance"
            }
            icon={<Target size={21} />}
          />

          <SummaryCard
            title="Lowest MAE"
            value={
              loading || !lowestMAEModel
                ? "—"
                : formatNumber(lowestMAEModel.MAE, 1)
            }
            description={
              lowestMAEModel
                ? lowestMAEModel.Model
                : "Lowest mean absolute error"
            }
            icon={<TrendingUp size={21} />}
          />

          <SummaryCard
            title="Lowest RMSE"
            value={
              loading || !lowestRMSEModel
                ? "—"
                : formatNumber(lowestRMSEModel.RMSE, 1)
            }
            description={
              lowestRMSEModel
                ? lowestRMSEModel.Model
                : "Lowest root mean square error"
            }
            icon={<BarChart3 size={21} />}
          />
        </section>

        {/* Error Metrics */}
        <section className="mt-8">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <p className="text-sm font-medium text-slate-500">
                ERROR METRICS
              </p>

              <h3 className="mt-1 text-xl font-bold">
                MAE vs RMSE
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Lower values indicate smaller prediction errors.
              </p>
            </div>

            {loading ? (
              <div className="h-80 animate-pulse rounded-xl bg-slate-100" />
            ) : models.length === 0 ? (
              <EmptyState message="No model performance data available." />
            ) : (
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={modelChartData}
                    margin={{
                      top: 10,
                      right: 20,
                      left: 0,
                      bottom: 20,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="model"
                      tick={{
                        fontSize: 11,
                      }}
                    />

                    <YAxis
                      tick={{
                        fontSize: 11,
                      }}
                    />

                    <Tooltip
                      formatter={(value, name) => [
                        formatNumber(Number(value), 1),
                        name,
                      ]}
                    />

                    <Legend />

                    <Bar
                      dataKey="MAE"
                      fill="#1e293b"
                      radius={[5, 5, 0, 0]}
                    />

                    <Bar
                      dataKey="RMSE"
                      fill="#64748b"
                      radius={[5, 5, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </section>

        {/* R2 + MAPE */}
        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          {/* R2 */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <p className="text-sm font-medium text-slate-500">
                GOODNESS OF FIT
              </p>

              <h3 className="mt-1 text-xl font-bold">
                R² Comparison
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Higher values indicate stronger explanatory performance.
              </p>
            </div>

            {loading ? (
              <div className="h-72 animate-pulse rounded-xl bg-slate-100" />
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={r2ChartData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 20,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="model"
                      tick={{
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      domain={[0, 100]}
                      tick={{
                        fontSize: 11,
                      }}
                      tickFormatter={(value) => `${value}%`}
                    />

                    <Tooltip
                      formatter={(value) => [
                        `${formatNumber(Number(value), 2)}%`,
                        "R²",
                      ]}
                    />

                    <Bar
                      dataKey="R2"
                      fill="#334155"
                      radius={[5, 5, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* MAPE */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <p className="text-sm font-medium text-slate-500">
                PERCENTAGE ERROR
              </p>

              <h3 className="mt-1 text-xl font-bold">
                MAPE Comparison
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Lower percentage error indicates more accurate predictions.
              </p>
            </div>

            {loading ? (
              <div className="h-72 animate-pulse rounded-xl bg-slate-100" />
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={mapeChartData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 20,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="model"
                      tick={{
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      tick={{
                        fontSize: 11,
                      }}
                      tickFormatter={(value) => `${value}%`}
                    />

                    <Tooltip
                      formatter={(value) => [
                        `${formatNumber(Number(value), 2)}%`,
                        "MAPE",
                      ]}
                    />

                    <Bar
                      dataKey="MAPE"
                      fill="#475569"
                      radius={[5, 5, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </section>

        {/* Detailed Table */}
        <section className="mt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <p className="text-sm font-medium text-slate-500">
                DETAILED EVALUATION
              </p>

              <h3 className="mt-1 text-xl font-bold">
                Model Metrics
              </h3>
            </div>

            {loading ? (
              <div className="h-64 animate-pulse rounded-xl bg-slate-100" />
            ) : models.length === 0 ? (
              <EmptyState message="No model metrics available." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[700px] text-left">
                  <thead>
                    <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
                      <th className="px-4 py-4 font-medium">
                        Model
                      </th>

                      <th className="px-4 py-4 font-medium">
                        MAE
                      </th>

                      <th className="px-4 py-4 font-medium">
                        RMSE
                      </th>

                      <th className="px-4 py-4 font-medium">
                        R²
                      </th>

                      <th className="px-4 py-4 font-medium">
                        MAPE
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {models.map((model) => (
                      <tr
                        key={model.Model}
                        className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                      >
                        <td className="px-4 py-4">
                          <span className="font-semibold">
                            {model.Model}
                          </span>
                        </td>

                        <td className="px-4 py-4 text-sm text-slate-600">
                          {formatNumber(model.MAE, 2)}
                        </td>

                        <td className="px-4 py-4 text-sm text-slate-600">
                          {formatNumber(model.RMSE, 2)}
                        </td>

                        <td className="px-4 py-4">
                          <span className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium">
                            {formatNumber(model.R2 * 100, 2)}%
                          </span>
                        </td>

                        <td className="px-4 py-4 text-sm text-slate-600">
                          {formatNumber(model.MAPE, 2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        {/* Metric Explanation */}
        <section className="mt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-medium text-slate-500">
                METRIC GUIDE
              </p>

              <h3 className="mt-1 text-xl font-bold">
                Understanding the metrics
              </h3>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <MetricCard
                title="MAE"
                description="Mean Absolute Error. Measures the average absolute difference between predicted and actual traffic volume."
              />

              <MetricCard
                title="RMSE"
                description="Root Mean Square Error. Penalizes larger prediction errors more strongly than MAE."
              />

              <MetricCard
                title="R²"
                description="Coefficient of determination. Indicates how much variation in traffic volume is explained by the model."
              />

              <MetricCard
                title="MAPE"
                description="Mean Absolute Percentage Error. Expresses prediction error as a percentage of actual traffic."
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

function MetricCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl bg-slate-50 p-5">
      <p className="text-sm font-bold text-slate-900">
        {title}
      </p>

      <p className="mt-2 text-sm leading-6 text-slate-500">
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