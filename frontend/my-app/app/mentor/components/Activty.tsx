function Activity({
  icon,
  text,
  time,
}: {
  icon: React.ReactNode;
  text: string;
  time: string;
}) {
  return (
    <div className="flex gap-3">
      <div className="mt-0.5 text-gray-600">{icon}</div>

      <div>
        <p className="text-sm">{text}</p>
        <p className="mt-1 text-xs text-gray-400">{time}</p>
      </div>
    </div>
  );
}

export default Activity;