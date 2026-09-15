import { User, Bot } from "lucide-react";

function ChatMessage({ role, text }) {
  return (
    <div
      className="
flex
gap-4
mb-8
"
    >
      {role === "user" ? <User /> : <Bot />}

      <div
        className="
bg-[#111827]
rounded-2xl
p-4
max-w-3xl
"
      >
        {text}
      </div>
    </div>
  );
}

export default ChatMessage;
