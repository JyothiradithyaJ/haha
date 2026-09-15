export default function Logo({ size = 22 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect x="2" y="4" width="20" height="16" rx="1.5" stroke="#7A2E2A" strokeWidth="1.6" />
      <path d="M2 8.5H22" stroke="#7A2E2A" strokeWidth="1.6" />
      <path d="M8 4V8.5" stroke="#7A2E2A" strokeWidth="1.6" />
      <path d="M6 12.5H14" stroke="#7A2E2A" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M6 15.5H11" stroke="#7A2E2A" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}
