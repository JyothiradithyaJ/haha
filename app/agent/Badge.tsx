export interface TabItem {
  id: string;
  label: string;
  count?: number;
}

export default function Tabs({
  items,
  active,
  onChange,
}: {
  items: TabItem[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="flex gap-1 overflow-x-auto border-b border-line">
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onChange(item.id)}
          className={`relative shrink-0 whitespace-nowrap px-3.5 py-2.5 text-[14px] transition-colors ${
            active === item.id ? "text-ink font-medium" : "text-ink-faint hover:text-ink-soft"
          }`}
        >
          {item.label}
          {typeof item.count === "number" && (
            <span className="ml-1.5 text-[12px] text-ink-faint">({item.count})</span>
          )}
          {active === item.id && (
            <span className="absolute inset-x-0 -bottom-px h-[2px] bg-oxblood" />
          )}
        </button>
      ))}
    </div>
  );
}
