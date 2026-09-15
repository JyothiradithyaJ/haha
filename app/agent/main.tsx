export interface PillOption {
  id: string;
  label: string;
  dot?: string;
}

export default function PillFilter({
  options,
  active,
  onChange,
}: {
  options: PillOption[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="inline-flex max-w-full flex-wrap items-center gap-1 rounded-full border border-line bg-line/25 p-1">
      {options.map((o) => (
        <button
          key={o.id}
          onClick={() => onChange(o.id)}
          className={`flex shrink-0 items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[13.5px] font-medium transition-all duration-150 ${
            active === o.id
              ? "bg-card text-ink shadow-card"
              : "text-ink-soft hover:text-ink"
          }`}
        >
          <span
            className="h-1.5 w-1.5 shrink-0 rounded-full"
            style={{ backgroundColor: o.dot ?? "#1C1B18" }}
          />
          {o.label}
        </button>
      ))}
    </div>
  );
}
