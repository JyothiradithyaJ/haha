import type { ReactNode } from "react";
import type { ResourceType } from "../data/types";
import { categoryThemes } from "../lib/categoryTheme";

export function TypeBadge({ type, label }: { type: ResourceType; label: string }) {
  const theme = categoryThemes[type];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-[3px] border px-2 py-0.5 text-[11px] font-medium tracking-tight ${theme.badgeClasses}`}
    >
      {label}
    </span>
  );
}

export function Chip({
  children,
  active,
  onClick,
}: {
  children: ReactNode;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors duration-150 ${
        active
          ? "border-oxblood bg-oxblood text-paper"
          : "border-line text-ink-soft hover:border-line-strong hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}

export function UpvoteBadge({ count }: { count: number }) {
  return (
    <span className="inline-flex items-center gap-1 text-[12.5px] font-medium text-ink-soft">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" className="text-oxblood">
        <path
          d="M7 22H4C3.45 22 3 21.55 3 21V12C3 11.45 3.45 11 4 11H7V22ZM7 22H17.5C18.6 22 19.53 21.24 19.76 20.16L21.6 11.16C21.9 9.73 20.84 8.4 19.38 8.4H14.5L15.24 4.55C15.42 3.58 14.96 2.6 14.09 2.13C13.5 1.81 12.78 1.94 12.34 2.46L7 8.8"
          stroke="currentColor"
          strokeWidth="1.7"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
      {count}
    </span>
  );
}
