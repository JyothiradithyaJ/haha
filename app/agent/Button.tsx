import { Link } from "react-router-dom";
import type { Resource } from "../data/types";
import { bookAuthor, bookEdition, getCourse } from "../data/mockData";
import { UpvoteBadge } from "./Badge";

const spineColors = [
  "#6B3FA0", // refs purple
  "#1E7A4C", // notes green
  "#7A2E2A", // oxblood
  "#C1660B", // papers orange
  "#2B4C6B", // navy
  "#8C5A2B", // saddle brown
  "#4B5E45", // moss
  "#9C4A44", // oxblood light
];

function hashIndex(id: string, mod: number) {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) % 997;
  return h % mod;
}

export default function ShelfBook({ book, size = "md" }: { book: Resource; size?: "md" | "sm" }) {
  const course = getCourse(book.courseId);
  const color = spineColors[hashIndex(book.id, spineColors.length)];
  const heightClass = size === "sm" ? "h-40" : "h-52";
  const widthClass = size === "sm" ? "w-9" : "w-11";
  const raggedTop = 4 + hashIndex(book.id + "t", 10);

  return (
    <div className={`group/book relative ${heightClass} ${widthClass} shrink-0`}>
      <div
        className={`relative flex h-full w-full flex-col items-center justify-between overflow-hidden rounded-t-[3px] rounded-b-[2px] border-x border-t border-black/10 py-3 shadow-[inset_-3px_0_6px_rgba(0,0,0,0.18),inset_3px_0_4px_rgba(255,255,255,0.12)] transition-transform duration-200 ease-out group-hover/book:-translate-y-3.5 group-hover/book:shadow-[inset_-3px_0_6px_rgba(0,0,0,0.18),inset_3px_0_4px_rgba(255,255,255,0.12),0_14px_18px_-8px_rgba(0,0,0,0.35)]`}
        style={{ backgroundColor: color, marginTop: `-${raggedTop}px` }}
      >
        <span className="h-1 w-4 rounded-full bg-white/30" />
        <span
          className="line-clamp-[8] max-h-[70%] px-0.5 text-center font-serif text-[10.5px] font-medium leading-tight text-white/95"
          style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
        >
          {book.title}
        </span>
        <span className="h-1 w-4 rounded-full bg-white/30" />
      </div>

      {/* hover detail card */}
      <div className="pointer-events-none absolute bottom-full left-1/2 z-20 w-56 -translate-x-1/2 translate-y-2 rounded-[8px] border border-line-strong bg-card p-4 opacity-0 shadow-lift transition-all duration-200 ease-out group-hover/book:pointer-events-auto group-hover/book:translate-y-0 group-hover/book:opacity-100">
        <p className="font-serif text-[14.5px] leading-snug text-ink">{book.title}</p>
        <p className="mt-1 text-[12px] text-ink-soft">{bookAuthor(book)}</p>
        <p className="mt-1 text-[11.5px] text-ink-faint">
          {bookEdition(book)}{course ? ` · ${course.title}` : ""}
        </p>
        <div className="mt-3 flex items-center justify-between">
          <UpvoteBadge count={book.upvotes} />
          <Link
            to={`/resource/${book.id}`}
            className="text-[12.5px] font-medium text-oxblood hover:text-oxblood-dark"
          >
            View →
          </Link>
        </div>
      </div>
    </div>
  );
}
