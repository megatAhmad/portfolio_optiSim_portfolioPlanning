export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
      <p className="text-gray-600">
        Monte Carlo simulation, sensitivity analysis, and risk metrics.
      </p>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <h3 className="text-lg font-semibold">Tornado Chart</h3>
          <p className="mt-2 text-sm text-gray-500">
            Sensitivity analysis will render here
          </p>
          <div className="mt-4 h-64 rounded bg-gray-100" />
        </div>
        <div className="rounded-lg border bg-white p-6">
          <h3 className="text-lg font-semibold">NPV Distribution</h3>
          <p className="mt-2 text-sm text-gray-500">
            Monte Carlo histogram will render here
          </p>
          <div className="mt-4 h-64 rounded bg-gray-100" />
        </div>
      </div>
    </div>
  );
}
