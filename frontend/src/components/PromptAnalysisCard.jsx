function PromptAnalysisCard({ data }) {
  return (
    <div className="bg-[#111827] border border-gray-700 rounded-xl p-6 mb-4">
      <h2 className="text-xl font-bold mb-4">🧠 Prompt Analysis</h2>

      <p>
        Task:
        <b>{data.task_category}</b>
      </p>

      <p>
        Model Tier:
        <b>{data.target_model_tier}</b>
      </p>

      <p>
        Input Tokens:
        <b>{data.input_tokens}</b>
      </p>

      <p>
        Output Tokens:
        <b>{data.estimated_output_tokens}</b>
      </p>

      <p>
        Required Score:
        <b>{data.required_score}</b>
      </p>

      <p>
        Required RAM:
        <b>{data.required_ram_gb} GB</b>
      </p>
    </div>
  );
}

export default PromptAnalysisCard;
