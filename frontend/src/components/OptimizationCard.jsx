function OptimizationCard({ data }) {
  const { badges, details, comparison, status } = data;

  const badgeList = [
    {
      key: "fast",
      label: "Fast",
      icon: "⚡",
      caption:
        details.response_time_s != null
          ? `${details.response_time_s}s (≤ ${details.fast_threshold_s}s threshold)`
          : "no timing data",
    },
    {
      key: "accurate",
      label: "Accurate",
      icon: "🎯",
      caption:
        details.score_margin != null
          ? `score margin ${details.score_margin >= 0 ? "+" : ""}${details.score_margin}`
          : "cloud - presumed capable",
    },
    {
      key: "energy_efficient",
      label: "Energy Efficient",
      icon: "🔋",
      caption: `${details.energy_wh} Wh vs ${details.alternative_energy_wh} Wh (${comparison.alternative_engine})`,
    },
    {
      key: "sustainable",
      label: "Sustainable",
      icon: "🌱",
      caption: `${details.carbon_g} g CO₂ vs ${details.alternative_carbon_g} g CO₂ (${comparison.alternative_engine})`,
    },
  ];

  return (
    <div className="bg-[#111827] border border-gray-800 border-l-4 border-l-emerald-500 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-8 h-8 rounded-full bg-emerald-500/15 flex items-center justify-center text-lg">
          {status === "Optimized" ? "✅" : "⚠️"}
        </span>
        <h2 className="text-lg font-bold">Final AI Response</h2>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {badgeList.map(({ key, label, icon, caption }) => (
          <div
            key={key}
            className={`rounded-lg px-3 py-2.5 border ${
              badges[key]
                ? "bg-emerald-900/30 border-emerald-500/50"
                : "bg-gray-800/40 border-gray-700"
            }`}
          >
            <div
              className={`text-sm font-semibold flex items-center gap-1.5 ${
                badges[key] ? "text-emerald-400" : "text-gray-500"
              }`}
            >
              <span>{icon}</span>
              <span>{label}</span>
            </div>
            <div className="text-xs text-gray-400 mt-1">{caption}</div>
          </div>
        ))}
      </div>

      <div className="bg-[#0b1220] rounded-lg p-4 space-y-2 text-sm">
        <p>
          <span className="text-gray-400">vs {comparison.alternative_engine}: </span>
          {comparison.energy}
        </p>

        <p>
          <span className="text-gray-400">Accuracy: </span>
          {comparison.accuracy}
        </p>
      </div>
    </div>
  );
}

export default OptimizationCard;
