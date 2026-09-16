import { MoreHorizontal } from "lucide-react";

function Exercise({
  title,
  description,
  level,
  xp_reward,
}: {
  title: string;
  description: string;
  level: string;
  xp_reward: number;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4 hover:bg-gray-50">
      <div>
        <p className="font-medium">{title}</p>
        <code className="text-sm text-gray-600">{description}</code>
        <div className="mt-1 flex gap-3 text-xs text-gray-500">
          <span>{level}</span>
          <span>•</span>
          <span>{xp_reward} XP</span>
        </div>
      </div>

      <button className="rounded-lg p-2 hover:bg-gray-100">
        <MoreHorizontal size={19} />
      </button>
    </div>
  );
}

export default Exercise;