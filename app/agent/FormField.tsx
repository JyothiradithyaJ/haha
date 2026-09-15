import type { ReactNode } from "react";
import { useEffect } from "react";

export default function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink/40 backdrop-blur-sm sm:items-center sm:px-4">
      <div className="absolute inset-0" onClick={onClose} aria-hidden />
      <div className="relative max-h-[90vh] w-full max-w-[560px] overflow-y-auto rounded-t-[10px] border border-line-strong bg-card shadow-lift sm:rounded-[10px]">
        <div className="sticky top-0 flex items-center justify-between border-b border-line bg-card px-5 py-4">
          <h3 className="font-serif text-[18px] text-ink">{title}</h3>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-[5px] text-ink-faint hover:bg-ink/5 hover:text-ink"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}
