import { User, Bot } from "lucide-react";

function ChatMessage({ role, text }) {
  const isUser = role === "user";

  return (
    <div className="flex gap-4">
      <div
        className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? "bg-gray-700 text-gray-300" : "bg-green-900/40 text-green-400"
        }`}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-4 max-w-3xl leading-relaxed">
        {text}
      </div>
    </div>
  );
}

export default ChatMessage;
