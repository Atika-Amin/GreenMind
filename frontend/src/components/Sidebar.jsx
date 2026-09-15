import logo from "../assets/greenmind-logo.png";

import { Plus, Settings, BarChart3 } from "lucide-react";

function Sidebar() {
  return (
    <div
      className="
w-72
bg-[#101827]
border-r
border-gray-800
p-5
flex
flex-col
"
    >
      <div
        className="
flex
items-center
gap-3
mb-8
"
      >
        <img
          src={logo}
          className="
w-12
h-12
rounded-xl
"
        />

        <h1
          className="
text-2xl
font-bold
"
        >
          GreenMind
        </h1>
      </div>

      <button
        className="
bg-[#1e293b]
hover:bg-[#263449]
rounded-xl
p-3
flex
gap-3
items-center
"
      >
        <Plus />
        New Chat
      </button>

      <div
        className="
mt-8
text-gray-400
text-sm
"
      >
        Recent Chats
      </div>

      <div
        className="
mt-4
space-y-4
text-gray-200
"
      >
        <p>Research Assistant</p>

        <p>Code Generation</p>

        <p>Document Analysis</p>
      </div>

      <div
        className="
mt-auto
space-y-5
"
      >
        <button
          className="
flex
gap-3
items-center
"
        >
          <BarChart3 />
          Analytics
        </button>

        <button
          className="
flex
gap-3
items-center
"
        >
          <Settings />
          Settings
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
