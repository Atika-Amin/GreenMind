import { Cloud, Zap } from "lucide-react";

function RoutingCard() {
  return (
    <div
      className="
bg-gray-900
border
border-gray-700
rounded-xl
p-5
"
    >
      <h2 className="font-bold text-lg">AI Execution Report</h2>

      <div className="mt-4 space-y-3">
        <p>
          Task:
          <b> Image Analysis </b>
        </p>

        <p className="flex gap-2">
          <Cloud />
          Decision:
          <b>Cloud Execution</b>
        </p>

        <p>
          Energy Used:
          <b>2.4 Wh</b>
        </p>

        <p>
          Carbon Impact:
          <b>0.03 g</b>
        </p>
      </div>
    </div>
  );
}

export default RoutingCard;
