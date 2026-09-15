function ExecutionCard({ data }) {
  const isLocal = data.engine_used === "local";
  const engineLabel = isLocal ? "⚡ Local (Ollama)" : "☁️ Cloud (Gemini)";

  return (
    <div
      className={`bg-[#111827] border rounded-xl p-6 border-l-4 ${
        data.success ? "border-gray-800 border-l-amber-500" : "border-red-900 border-l-red-500"
      }`}
    >
      <div className="flex items-center gap-2 mb-4">
        <span className="w-8 h-8 rounded-full bg-amber-500/15 flex items-center justify-center text-lg">
          🤖
        </span>
        <h2 className="text-lg font-bold">Execution Result</h2>
      </div>

      <div className="flex justify-between text-sm py-1.5 border-b border-gray-800/60">
        <span className="text-gray-400">Engine</span>
        <span className="font-semibold text-white">{engineLabel}</span>
      </div>

      {data.success ? (
        <>
          <div className="flex justify-between text-sm py-1.5 border-b border-gray-800/60">
            <span className="text-gray-400">Model</span>
            <span className="font-semibold text-white">{data.model_used}</span>
          </div>

          <div className="bg-[#0b1220] rounded-lg p-4 my-3 whitespace-pre-wrap leading-relaxed text-sm">
            {data.response_text}
          </div>

          <div className="flex justify-between text-sm py-1.5 border-b border-gray-800/60">
            <span className="text-gray-400">Tokens</span>
            <span className="font-semibold text-white">
              {data.prompt_tokens} in / {data.completion_tokens} out
              {isLocal ? "" : ` (${data.total_tokens} total)`}
            </span>
          </div>

          <div className="flex justify-between text-sm py-1.5">
            <span className="text-gray-400">Time</span>
            <span className="font-semibold text-white">
              {isLocal ? data.total_duration_s : data.latency_s}s
            </span>
          </div>

          {isLocal && data.tokens_per_second != null && (
            <div className="flex justify-between text-sm py-1.5">
              <span className="text-gray-400">Speed</span>
              <span className="font-semibold text-white">{data.tokens_per_second} tokens/sec</span>
            </div>
          )}
        </>
      ) : (
        <p className="text-red-400 mt-3 text-sm">⚠️ {data.error}</p>
      )}
    </div>
  );
}

export default ExecutionCard;
