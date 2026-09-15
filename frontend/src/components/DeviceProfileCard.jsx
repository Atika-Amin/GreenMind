function DeviceProfileCard({ data }) {
  return (
    <div className="bg-[#111827] border border-gray-700 rounded-xl p-6 mb-4">
      <h2 className="text-xl font-bold mb-4">💻 Device Capability</h2>

      <p>
        CPU:
        <b>{data.cpu.model}</b>
      </p>

      <p>
        RAM Available:
        <b>{data.memory.available_gb} GB</b>
      </p>

      <p>
        GPU:
        <b>{data.gpu[0]?.name}</b>
      </p>

      <p>
        Battery:
        <b>{data.battery.percent}%</b>
      </p>

      <h3 className="mt-4 text-green-400 text-lg">
        S_avail:
        {data.available_score}/100
      </h3>
    </div>
  );
}

export default DeviceProfileCard;
