function ExecutionCard({ data }) {
  return (
    <div
      className="
bg-[#172033]
rounded-2xl
p-5
"
    >
      <h2 className="font-bold">🤖 Execution Status</h2>

      <p>
        Status:
        <b>{data.status}</b>
      </p>

      <p>
        Response Time:
        <b>{data.time}s</b>
      </p>
    </div>
  );
}

export default ExecutionCard;
