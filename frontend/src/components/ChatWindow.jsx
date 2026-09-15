import Message from "./ChatMessage";
import RoutingCard from "./RoutingCard";

function ChatWindow() {
  return (
    <div
      className="
flex-1
overflow-y-auto
p-8
space-y-6
"
    >
      <Message role="user" text="Analyze this image" />

      <Message
        role="ai"
        text="I will analyze the image and provide the result."
      />

      <RoutingCard />
    </div>
  );
}

export default ChatWindow;
