import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  children: ReactNode;
  size?: "sm" | "md";
}

const base =
  "inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 disabled:opacity-40 disabled:pointer-events-none rounded-[5px]";

const variants: Record<Variant, string> = {
  primary:
    "bg-oxblood text-paper hover:bg-oxblood-dark active:scale-[0.98] shadow-[0_1px_0_rgba(0,0,0,0.1)]",
  secondary:
    "bg-card text-ink border border-line hover:border-line-strong hover:bg-ink/[0.02] active:scale-[0.98]",
  ghost: "text-ink-soft hover:text-ink hover:bg-ink/5",
};

const sizes = {
  sm: "text-sm px-3 py-1.5",
  md: "text-sm px-4 py-2.5",
};

export default function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...rest
}: Props) {
  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
