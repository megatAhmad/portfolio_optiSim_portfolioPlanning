export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Executive Dashboard
      </h1>
      <p className="text-gray-600">
        Portfolio overview with key metrics, CAPEX/production/emissions charts,
        and composition views.
      </p>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Portfolio NPV" value="$0" unit="MM" />
        <MetricCard label="Total CAPEX" value="$0" unit="MM" />
        <MetricCard label="Peak Production" value="0" unit="boe/d" />
        <MetricCard label="Total Emissions" value="0" unit="MtCO2e" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <h3 className="text-lg font-semibold">CAPEX Profile</h3>
          <p className="mt-2 text-sm text-gray-500">
            Annual capital expenditure chart will render here (Recharts)
          </p>
          <div className="mt-4 h-64 rounded bg-gray-100" />
        </div>
        <div className="rounded-lg border bg-white p-6">
          <h3 className="text-lg font-semibold">Production Forecast</h3>
          <p className="mt-2 text-sm text-gray-500">
            Production profile by commodity will render here (Recharts)
          </p>
          <div className="mt-4 h-64 rounded bg-gray-100" />
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  unit,
}: {
  label: string;
  value: string;
  unit: string;
}) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900">
        {value} <span className="text-sm font-normal text-gray-500">{unit}</span>
      </p>
    </div>
  );
}
