
type Learner = { id: string; email?: string; role?: string };

export default function LearnerDetail({ learner }: { learner: Learner[] }) {
  return (
    <div>
      {learner.map((learner_detail) => (
        <div
          key={learner_detail?.id}
          className="bg-white rounded-2xl border shadow-sm p-6 hover:shadow-md transition"
        >
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xl font-bold">
                {learner_detail?.email?.charAt(0).toUpperCase()}
              </div>

              <div>
                <h3 className="font-semibold text-gray-900">
                  {learner_detail?.email}
                </h3>

                <span className="inline-block mt-1 px-3 py-1 text-xs rounded-full bg-green-100 text-green-700">
                  {learner_detail?.role}
                </span>
              </div>
            </div>

            <button className="text-sm text-blue-600 hover:underline">
              View
            </button>
          </div>

          <div className="mt-5 grid grid-cols-2 gap-4 border-t pt-4">
            <div>
              <p className="text-xs text-gray-500">Exercises</p>
              <p className="font-semibold">0</p>
            </div>

            <div>
              <p className="text-xs text-gray-500">XP</p>
              <p className="font-semibold">0</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
