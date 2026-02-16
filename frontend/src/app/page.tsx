export default function HomePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Portfolio OptiSim
        </h1>
      </div>

      <p className="text-lg text-gray-600">
        Enterprise portfolio optimization platform for energy and
        capital-intensive industries.
      </p>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <DashboardCard
          title="Projects"
          description="Manage investment opportunities"
          href="/projects"
          metric="0"
          metricLabel="Total Projects"
        />
        <DashboardCard
          title="Scenarios"
          description="Configure and run optimizations"
          href="/scenarios"
          metric="0"
          metricLabel="Active Scenarios"
        />
        <DashboardCard
          title="Optimization"
          description="Portfolio selection and timing"
          href="/optimization"
          metric="-"
          metricLabel="Latest NPV"
        />
        <DashboardCard
          title="Analytics"
          description="Risk analysis and sensitivity"
          href="/analytics"
          metric="-"
          metricLabel="Monte Carlo Runs"
        />
      </div>
    </div>
  );
}

function DashboardCard({
  title,
  description,
  href,
  metric,
  metricLabel,
}: {
  title: string;
  description: string;
  href: string;
  metric: string;
  metricLabel: string;
}) {
  return (
    <a
      href={href}
      className="block rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
    >
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
      <div className="mt-4">
        <span className="text-2xl font-bold text-primary-600">{metric}</span>
        <span className="ml-2 text-sm text-gray-500">{metricLabel}</span>
      </div>
    </a>
  );
}
