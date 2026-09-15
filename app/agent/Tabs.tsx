import { useRef, type ReactNode } from "react";

export default function Carousel({ children }: { children: ReactNode }) {
  const trackRef = useRef<HTMLDivElement>(null);

  function scrollBy(dir: 1 | -1) {
    trackRef.current?.scrollBy({ left: dir * 320, behavior: "smooth" });
  }

  return (
    <div className="relative">
      <div
        ref={trackRef}
        className="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-3 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {children}
      </div>
      <div className="mt-1 hidden items-center justify-end gap-2 sm:flex">
        <button
          onClick={() => scrollBy(-1)}
          aria-label="Scroll left"
          className="flex h-9 w-9 items-center justify-center rounded-full border border-line bg-card text-ink-soft transition-colors hover:border-line-strong hover:text-ink"
        >
          ‹
        </button>
        <button
          onClick={() => scrollBy(1)}
          aria-label="Scroll right"
          className="flex h-9 w-9 items-center justify-center rounded-full border border-line bg-card text-ink-soft transition-colors hover:border-line-strong hover:text-ink"
        >
          ›
        </button>
      </div>
    </div>
  );
}
