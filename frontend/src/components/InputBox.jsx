import { Paperclip, Send, Loader2 } from "lucide-react";
import { useState } from "react";

function InputBox({ setMessages }) {
  const [prompt, setPrompt] = useState("");
  const [isSending, setIsSending] = useState(false);

  async function sendPrompt() {
    const trimmed = prompt.trim();
    if (!trimmed || isSending) return;

    // Clear and lock the input immediately - don't make the user stare at
    // their own typed text for the 6-13s it takes the backend to respond.
    setPrompt("");
    setIsSending(true);

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: trimmed,
      },
    ]);

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: trimmed,
          device_info: {
            device_capability: "medium",
            battery: 100,
            network_cost: 0.2,
          },
        }),
      });

      if (!response.ok) {
        throw new Error("GreenMind API request failed");
      }

      const data = await response.json();

      console.log("GreenMind Response:", data);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "GreenMind workload analysis completed.",
          execution: data.execution,
          response_optimization: data.response_optimization,
          prompt_analysis: data.prompt_analysis,
          device_profile: data.device_profile,
          routing_decision: data.routing_decision,
        },
      ]);
    } catch (error) {
      console.log("GreenMind API Error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Unable to connect with GreenMind API.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="p-5 border-t border-gray-800">
      {isSending && (
        <div className="text-xs text-green-400 mb-2 px-2 flex items-center gap-2">
          <Loader2 size={12} className="animate-spin" />
          GreenMind is analyzing your request...
        </div>
      )}

      <div
        className={`bg-[#111827] rounded-3xl flex items-center p-4 border transition-colors ${
          isSending ? "border-gray-800 opacity-70" : "border-transparent"
        }`}
      >
        <Paperclip className="text-gray-500" size={20} />

        <input
          value={prompt}
          disabled={isSending}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendPrompt();
            }
          }}
          className="flex-1 bg-transparent outline-none px-5 disabled:cursor-not-allowed"
          placeholder="Ask GreenMind to analyze your AI workload..."
        />

        <button
          onClick={sendPrompt}
          disabled={isSending}
          className="hover:text-green-400 disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
        >
          {isSending ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
        </button>
      </div>
    </div>
  );
}

export default InputBox;
