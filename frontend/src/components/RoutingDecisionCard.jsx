function RoutingDecisionCard({ data }) {
  return (
    <div className="bg-[#111827] border border-green-500 rounded-xl p-6">
      <h2>🚦 Routing Decision</h2>

      <h1 className="text-green-400 text-2xl">{data.decision}</h1>

      <p>
        Score Margin:
        {data.score_margin}
      </p>

      <ul>
        {data.reasons.map((r, i) => (
          <li key={i}>• {r}</li>
        ))}
      </ul>
    </div>
  );
}

export default RoutingDecisionCard;
