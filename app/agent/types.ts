@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply border-line;
  }
  html {
    scroll-behavior: smooth;
  }
  body {
    @apply bg-paper text-ink font-sans antialiased;
    font-feature-settings: "kern" 1, "liga" 1;
  }
  ::selection {
    @apply bg-oxblood/20;
  }
  :focus-visible {
    outline: 2px solid #7A2E2A;
    outline-offset: 2px;
  }
}

@layer components {
  .call-number {
    @apply font-mono text-[11px] tracking-wide text-ink-faint;
  }
  .card-index {
    background-image: repeating-linear-gradient(
      transparent,
      transparent 27px,
      rgba(28, 27, 24, 0.045) 28px
    );
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
}
