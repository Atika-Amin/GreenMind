import logo from "../assets/greenmind-logo.png";

function Header() {
  return (
    <div
      className="
h-20
border-b
border-gray-800
flex
items-center
justify-center
"
    >
      <div
        className="
flex
items-center
gap-3
"
      >
        <img
          src={logo}
          className="
w-9
h-9
"
        />

        <div>
          <h1
            className="
font-semibold
text-xl
"
          >
            GreenMind
          </h1>

          <p
            className="
text-xs
text-green-400
"
          >
            Adaptive AI Workload Routing
          </p>
        </div>
      </div>
    </div>
  );
}

export default Header;
