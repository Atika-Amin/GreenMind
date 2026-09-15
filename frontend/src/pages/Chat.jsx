import { useState } from "react";

import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import Welcome from "../components/Welcome";
import ChatMessage from "../components/ChatMessage";

import PromptAnalysisCard from "../components/PromptAnalysisCard";
import DeviceProfileCard from "../components/DeviceProfileCard";
import RoutingDecisionCard from "../components/RoutingDecisionCard";

import InputBox from "../components/InputBox";

function Chat() {
  const [messages, setMessages] = useState([]);

  return (
    <div
      className="
      flex
      h-screen
      bg-[#050b18]
      text-white
      "
    >
      <Sidebar />

      <div
        className="
        flex-1
        flex
        flex-col
        "
      >
        <Header />

        <div
          className="
          flex-1
          overflow-y-auto
          px-20
          py-10
          "
        >
          {messages.length === 0 ? (
            <Welcome />
          ) : (
            messages.map((msg, index) => (
              <div key={index}>
                <ChatMessage role={msg.role} text={msg.text} />

                {msg.prompt_analysis && (
                  <PromptAnalysisCard data={msg.prompt_analysis} />
                )}

                {msg.device_profile && (
                  <DeviceProfileCard data={msg.device_profile} />
                )}

                {msg.routing_decision && (
                  <RoutingDecisionCard data={msg.routing_decision} />
                )}
              </div>
            ))
          )}
        </div>

        <InputBox setMessages={setMessages} />
      </div>
    </div>
  );
}

export default Chat;
