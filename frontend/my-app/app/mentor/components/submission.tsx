function Submission({
  learner,
  exercise,
  score,
}: {
  learner: string;
  exercise: string;
  score: string;
}) {
  return (
    <tr className="border-b last:border-0">
      <td className="py-4 font-medium">{learner}</td>
      <td className="py-4 text-gray-600">{exercise}</td>
      <td className="py-4 font-semibold">{score}</td>
      <td className="py-4">
        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium">
          Reviewed
        </span>
      </td>
      <td className="py-4 text-right">
        <button className="text-sm font-medium hover:underline">
          View
        </button>
      </td>
    </tr>
  );
}

export default Submission;

