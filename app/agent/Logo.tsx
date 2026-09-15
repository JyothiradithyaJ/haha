import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import Logo from "./Logo";
import Button from "./Button";
import SearchOverlay from "./SearchOverlay";

const navLinks = [
  { to: "/", label: "Archive" },
  { to: "/bookshelf", label: "Bookshelf" },
  { to: "/honor-roll", label: "Honor Roll" },
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
      if (e.key === "Escape") setSearchOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-line bg-paper/85 backdrop-blur">
        <div className="mx-auto flex max-w-content items-center justify-between px-5 py-3.5 sm:px-8">
          <Link to="/" className="flex items-center gap-2.5">
            <Logo />
            <span className="font-serif text-[19px] font-semibold tracking-tightish text-ink">
              ARCHIVE
            </span>
          </Link>

          <nav className="hidden items-center gap-7 md:flex">
            {navLinks.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  `text-[14.5px] transition-colors ${
                    isActive ? "text-ink font-medium" : "text-ink-soft hover:text-ink"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setSearchOpen(true)}
              className="hidden items-center gap-2 rounded-[5px] border border-line bg-card px-3 py-1.5 text-sm text-ink-faint transition-colors hover:border-line-strong sm:flex"
            >
              <SearchIcon />
              <span>Search…</span>
              <kbd className="ml-4 rounded border border-line-strong bg-paper px-1.5 py-0.5 font-mono text-[10.5px] text-ink-faint">
                ⌘K
              </kbd>
            </button>
            <Link to="/contribute" className="hidden sm:block">
              <Button size="sm">Contribute</Button>
            </Link>
            <button
              className="flex h-9 w-9 items-center justify-center rounded-[5px] border border-line md:hidden"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label="Toggle menu"
            >
              <MenuIcon open={menuOpen} />
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="border-t border-line bg-paper px-5 py-4 md:hidden">
            <div className="flex flex-col gap-1">
              {navLinks.map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    `rounded-[5px] px-3 py-2.5 text-[15px] ${
                      isActive ? "bg-ink/5 font-medium text-ink" : "text-ink-soft"
                    }`
                  }
                >
                  {l.label}
                </NavLink>
              ))}
              <button
                onClick={() => {
                  setMenuOpen(false);
                  setSearchOpen(true);
                }}
                className="mt-1 flex items-center gap-2 rounded-[5px] border border-line px-3 py-2.5 text-left text-[15px] text-ink-faint"
              >
                <SearchIcon /> Search…
              </button>
              <Link to="/contribute" onClick={() => setMenuOpen(false)} className="mt-2">
                <Button className="w-full">Contribute</Button>
              </Link>
            </div>
          </div>
        )}
      </header>
      <SearchOverlay open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}

function SearchIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
      <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function MenuIcon({ open }: { open: boolean }) {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      {open ? (
        <path d="M6 6L18 18M6 18L18 6" stroke="#1C1B18" strokeWidth="2" strokeLinecap="round" />
      ) : (
        <path
          d="M3 6H21M3 12H21M3 18H21"
          stroke="#1C1B18"
          strokeWidth="2"
          strokeLinecap="round"
        />
      )}
    </svg>
  );
}
