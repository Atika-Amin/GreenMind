import { Paperclip, Send } from "lucide-react";
import { useState } from "react";

function InputBox({ setMessages }) {
  const [prompt, setPrompt] = useState("");

  async function sendPrompt() {
    if (!prompt.trim()) return;

    // Add user message

    setMessages((prev) => [
      ...prev,

      {
        role: "user",

        text: prompt,
      },
    ]);

    try {
      const response = await fetch(
        "http://localhost:8000/process",

        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            prompt: prompt,

            device_info: {
              device_capability: "medium",

              battery: 100,

              network_cost: 0.2,
            },
          }),
        },
      );

      if (!response.ok) {
        throw new Error("GreenMind API request failed");
      }

      const data = await response.json();

      console.log("GreenMind Response:", data);

      // Add GreenMind response

      setMessages((prev) => [
        ...prev,

        {
          role: "assistant",

          text: "GreenMind workload analysis completed.",

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
    }

    setPrompt("");
  }

  return (
    <div
      className="
      p-5
      border-t
      border-gray-800
      "
    >
      <div
        className="
        bg-[#111827]
        rounded-3xl
        flex
        items-center
        p-4
        "
      >
        <Paperclip />

        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendPrompt();
            }
          }}
          className="
          flex-1
          bg-transparent
          outline-none
          px-5
          "
          placeholder="
          Ask GreenMind to analyze your AI workload...
          "
        />

        <button
          onClick={sendPrompt}
          className="
          hover:text-green-400
          "
        >
          <Send />
        </button>
      </div>
    </div>
  );
}

export default InputBox;
