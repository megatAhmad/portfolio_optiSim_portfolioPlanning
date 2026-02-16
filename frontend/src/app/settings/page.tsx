export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      <div className="rounded-lg border bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold">Solver Configuration</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Default Solver
            </label>
            <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
              <option value="highs">HiGHS (Open Source - Recommended)</option>
              <option value="or-tools">Google OR-Tools (Open Source)</option>
              <option value="glpk">GLPK (Open Source)</option>
              <option value="cbc">CBC/CLP (COIN-OR, Open Source)</option>
              <option value="gurobi">Gurobi (Commercial)</option>
              <option value="cplex">CPLEX (Commercial)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Default MIP Gap
            </label>
            <input
              type="number"
              defaultValue="0.001"
              step="0.001"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
