function NavItem({
  icon,
  label,
  active = false,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium ${
        active
          ? "bg-black text-white"
          : "text-gray-600 hover:bg-gray-100 hover:text-black"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

export default NavItem;