export default function ScenariosPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Scenarios</h1>
        <button className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          New Scenario
        </button>
      </div>

      <div className="rounded-lg border bg-white p-6">
        <p className="text-gray-500">
          No scenarios created yet. Create a new scenario to start optimizing
          your portfolio.
        </p>
      </div>
    </div>
  );
}
