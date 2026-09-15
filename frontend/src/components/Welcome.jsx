function Welcome() {
  return (
    <div
      className="
h-full
flex
flex-col
items-center
justify-center
text-center
"
    >
      <h1
        className="
text-5xl
font-bold
mb-5
"
      >
        GreenMind
      </h1>

      <p
        className="
text-xl
text-gray-400
mb-10
"
      >
        Intelligent AI Workload Optimization
      </p>

      <div
        className="
grid
grid-cols-3
gap-5
"
      >
        <div
          className="
bg-[#172033]
p-6
rounded-2xl
"
        >
          ✍️
          <br />
          Prompt Analysis
        </div>

        <div
          className="
bg-[#172033]
p-6
rounded-2xl
"
        >
          ⚡
          <br />
          Energy Aware
        </div>

        <div
          className="
bg-[#172033]
p-6
rounded-2xl
"
        >
          🌱
          <br />
          Sustainable AI
        </div>
      </div>
    </div>
  );
}

export default Welcome;
