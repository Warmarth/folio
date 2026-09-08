import { MoreHorizontal } from "lucide-react";

function Exercise({
  title,
  category,
  submissions,
}: {
  title: string;
  category: string;
  submissions: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4 hover:bg-gray-50">
      <div>
        <p className="font-medium">{title}</p>
        <div className="mt-1 flex gap-3 text-xs text-gray-500">
          <span>{category}</span>
          <span>•</span>
          <span>{submissions}</span>
        </div>
      </div>

      <button className="rounded-lg p-2 hover:bg-gray-100">
        <MoreHorizontal size={19} />
      </button>
    </div>
  );
}

export default Exercise;