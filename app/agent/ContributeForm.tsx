import { Link } from "react-router-dom";
import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="border-t border-line bg-card">
      <div className="mx-auto max-w-content px-5 py-14 sm:px-8">
        <div className="grid grid-cols-2 gap-10 sm:grid-cols-3">
          <div className="col-span-2 sm:col-span-1">
            <div className="flex items-center gap-2">
              <Logo size={20} />
              <span className="font-serif text-[17px] font-semibold text-ink">ARCHIVE</span>
            </div>
            <p className="mt-3 max-w-[220px] text-[13.5px] leading-relaxed text-ink-faint">
              Built by BMSIT students, for BMSIT students. Sharing is caring.
            </p>
          </div>

          <FooterCol
            title="Explore"
            links={[
              { to: "/", label: "The Archive" },
              { to: "/bookshelf", label: "Bookshelf" },
              { to: "/honor-roll", label: "Honor Roll" },
              { to: "/releases", label: "Releases & Updates" },
            ]}
          />
          <FooterCol
            title="Support"
            links={[
              { to: "/terms", label: "Terms & Rules" },
              { to: "/contribute", label: "Contribute a file" },
              { to: "/terms", label: "Report an issue" },
            ]}
          />
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-line pt-6 text-[12.5px] text-ink-faint sm:flex-row sm:items-center sm:justify-between">
          <p>
            © 2026 ARCHIVE · Built with{" "}
            <span className="text-oxblood">♥</span> by{" "}
            <a
              href="https://github.com/GJR19"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-ink-soft underline decoration-line-strong underline-offset-2 transition-colors hover:text-oxblood"
            >
              Gururaj Reddy
            </a>
          </p>
          <p>Not an official BMSIT platform</p>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({
  title,
  links,
}: {
  title: string;
  links: { to: string; label: string }[];
}) {
  return (
    <div>
      <h4 className="text-[12.5px] font-medium text-ink-soft">{title}</h4>
      <ul className="mt-3 flex flex-col gap-2.5">
        {links.map((l, i) => (
          <li key={i}>
            <Link
              to={l.to}
              className="text-[13.5px] text-ink-faint transition-colors hover:text-oxblood"
            >
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
