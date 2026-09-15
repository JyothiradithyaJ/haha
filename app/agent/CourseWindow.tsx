import ShelfBook from "./ShelfBook";
import { books } from "../data/mockData";

export default function ShelfPreview() {
  const preview = books.slice(0, 10);
  return (
    <div className="overflow-x-auto pb-2">
      <div className="flex min-w-max items-end gap-2.5 px-1">
        {preview.map((b) => (
          <ShelfBook key={b.id} book={b} size="sm" />
        ))}
      </div>
      <div className="mt-0 h-3 min-w-max rounded-[2px] bg-gradient-to-b from-[#8C5A2B] to-[#6B4020] shadow-[0_6px_10px_-4px_rgba(0,0,0,0.35)]" />
    </div>
  );
}
