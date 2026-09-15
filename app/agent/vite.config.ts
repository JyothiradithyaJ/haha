import { useMemo, useState } from "react";
import Layout from "../components/Layout";
import Tabs from "../components/Tabs";
import { Chip } from "../components/Badge";
import { contributors, departments, resources } from "../data/mockData";

const pointsRules = [
  { label: "Past Papers", points: 10 },
  { label: "Extras", points: 8 },
  { label: "Notes", points: 5 },
  { label: "References", points: 2 },
];

export default function HonorRoll() {
  const [period, setPeriod] = useState<"semester" | "all-time">("all-time");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<"points" | "contributions" | "upvotes">("points");
  const [branch, setBranch] = useState<string>("all");

  // points calculator
  const [calc, setCalc] = useState({ past: 0, notes: 0, extras: 0, ref: 0 });
  const calcTotal = calc.past * 10 + calc.notes * 5 + calc.extras * 8 + calc.ref * 2;

  const filtered = useMemo(() => {
    let list = [...contributors];
    if (period === "semester") {
      list = list.map((c) => ({
        ...c,
        points: Math.round(c.points * 0.4),
        contributions: Math.round(c.contributions * 0.4),
        upvotes: Math.round(c.upvotes * 0.4),
      }));
    }
    if (branch !== "all") {
      list = list.filter((c) => c.branch === branch);
    }
    if (query.trim()) {
      const needle = query.toLowerCase();
      list = list.filter(
        (c) => c.name.toLowerCase().includes(needle) || c.branch.toLowerCase().includes(needle)
      );
    }
    list.sort((a, b) => b[sort] - a[sort]);
    return list;
  }, [period, query, sort, branch]);

  return (
    <Layout>
      <section className="border-b border-line px-5 py-14 sm:px-8 sm:py-16">
        <div className="mx-auto max-w-content">
          <p className="call-number">Honor Roll</p>
          <h1 className="mt-3 font-serif text-[32px] leading-tight text-ink sm:text-[42px]">
            Students who built this archive.
          </h1>
          <p className="mt-3 max-w-lg text-[15.5px] text-ink-soft">
            Every upload earns points. The most active contributors keep
            ARCHIVE stocked for everyone else.
          </p>

          <div className="mt-8 grid grid-cols-3 gap-3 sm:max-w-md">
            <Stat label="Contributors" value={contributors.length.toString()} />
            <Stat label="Files shared" value={resources.length.toString()} />
            <Stat
              label="Points awarded"
              value={contributors.reduce((s, c) => s + c.points, 0).toLocaleString()}
            />
          </div>
        </div>
      </section>

      <section className="px-5 py-12 sm:px-8">
        <div className="mx-auto grid max-w-content gap-10 lg:grid-cols-[1fr_320px]">
          <div>
            <Tabs
              items={[
                { id: "all-time", label: "All Time" },
                { id: "semester", label: "This Semester" },
              ]}
              active={period}
              onChange={(v) => setPeriod(v as typeof period)}
            />

            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-1 items-center gap-3 rounded-[6px] border border-line bg-card px-3.5 py-2.5 sm:max-w-xs">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" className="shrink-0 text-ink-faint">
                  <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                  <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search by name or branch…"
                  className="flex-1 bg-transparent text-[13.5px] text-ink placeholder:text-ink-faint focus:outline-none"
                />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[12.5px] text-ink-faint">Sort by</span>
                <Chip active={sort === "points"} onClick={() => setSort("points")}>Points</Chip>
                <Chip active={sort === "contributions"} onClick={() => setSort("contributions")}>Files</Chip>
                <Chip active={sort === "upvotes"} onClick={() => setSort("upvotes")}>Upvotes</Chip>
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-1">
              <span className="shrink-0 text-[12.5px] text-ink-faint">Department</span>
              <Chip active={branch === "all"} onClick={() => setBranch("all")}>All</Chip>
              {departments.map((d) => (
                <Chip key={d.id} active={branch === d.short} onClick={() => setBranch(d.short)}>
                  {d.short}
                </Chip>
              ))}
            </div>

            {/* Desktop table */}
            <div className="mt-5 hidden overflow-hidden rounded-[7px] border border-line sm:block">
              <table className="w-full text-left text-[14px]">
                <thead>
                  <tr className="border-b border-line bg-card text-[12px] uppercase tracking-wide text-ink-faint">
                    <th className="px-4 py-3 font-medium">Rank</th>
                    <th className="px-4 py-3 font-medium">Contributor</th>
                    <th className="px-4 py-3 font-medium">Branch</th>
                    <th className="px-4 py-3 font-medium">Contributions</th>
                    <th className="px-4 py-3 font-medium">Upvotes</th>
                    <th className="px-4 py-3 text-right font-medium">Points</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {filtered.map((c, i) => (
                    <tr key={c.id} className="transition-colors hover:bg-card">
                      <td className="px-4 py-3 call-number">
                        {i < 3 ? ["🥇", "🥈", "🥉"][i] : `#${i + 1}`}
                      </td>
                      <td className="px-4 py-3 text-ink">{c.name}</td>
                      <td className="px-4 py-3 text-ink-faint">{c.branch}</td>
                      <td className="px-4 py-3 text-ink-faint">{c.contributions}</td>
                      <td className="px-4 py-3 text-ink-faint">
                        <span className="inline-flex items-center gap-1">
                          <ThumbIcon /> {c.upvotes}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-medium text-oxblood">{c.points}</td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-ink-faint">
                        No contributors matched your filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Mobile cards */}
            <div className="mt-5 flex flex-col gap-2.5 sm:hidden">
              {filtered.map((c, i) => (
                <div key={c.id} className="flex items-center justify-between rounded-[6px] border border-line bg-card px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="call-number w-6">{i < 3 ? ["🥇", "🥈", "🥉"][i] : `#${i + 1}`}</span>
                    <div>
                      <p className="text-[14px] text-ink">{c.name}</p>
                      <p className="flex items-center gap-1.5 text-[12px] text-ink-faint">
                        {c.branch} · {c.contributions} files · <ThumbIcon /> {c.upvotes}
                      </p>
                    </div>
                  </div>
                  <span className="font-medium text-oxblood">{c.points}</span>
                </div>
              ))}
              {filtered.length === 0 && (
                <p className="py-8 text-center text-ink-faint">No contributors matched your filters.</p>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="rounded-[8px] border border-line bg-card p-5">
              <h3 className="font-serif text-[17px] text-ink">How points work</h3>
              <ul className="mt-3 space-y-2.5">
                {pointsRules.map((r) => (
                  <li key={r.label} className="flex items-center justify-between text-[13.5px]">
                    <span className="text-ink-soft">{r.label}</span>
                    <span className="font-mono text-ink">+{r.points}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-[11.5px] text-ink-faint">
                Placeholder rules — subject to change as ARCHIVE grows.
              </p>
            </div>

            <div className="rounded-[8px] border border-line bg-card p-5">
              <h3 className="font-serif text-[17px] text-ink">Points calculator</h3>
              <p className="mt-1 text-[12.5px] text-ink-faint">
                Estimate what an upload could earn you.
              </p>
              <div className="mt-4 space-y-3">
                <CalcRow label="Past papers" value={calc.past} points={10} onChange={(v) => setCalc((s) => ({ ...s, past: v }))} />
                <CalcRow label="Notes" value={calc.notes} points={5} onChange={(v) => setCalc((s) => ({ ...s, notes: v }))} />
                <CalcRow label="Extras" value={calc.extras} points={8} onChange={(v) => setCalc((s) => ({ ...s, extras: v }))} />
                <CalcRow label="References" value={calc.ref} points={2} onChange={(v) => setCalc((s) => ({ ...s, ref: v }))} />
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-line pt-3.5">
                <span className="text-[13.5px] text-ink-soft">Estimated total</span>
                <span className="font-serif text-[20px] text-oxblood">{calcTotal} pts</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}

function ThumbIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" className="text-oxblood">
      <path
        d="M7 22H4C3.45 22 3 21.55 3 21V12C3 11.45 3.45 11 4 11H7V22ZM7 22H17.5C18.6 22 19.53 21.24 19.76 20.16L21.6 11.16C21.9 9.73 20.84 8.4 19.38 8.4H14.5L15.24 4.55C15.42 3.58 14.96 2.6 14.09 2.13C13.5 1.81 12.78 1.94 12.34 2.46L7 8.8"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[6px] border border-line bg-card px-3.5 py-3">
      <p className="font-serif text-[19px] text-ink">{value}</p>
      <p className="text-[11.5px] text-ink-faint">{label}</p>
    </div>
  );
}

function CalcRow({
  label,
  value,
  points,
  onChange,
}: {
  label: string;
  value: number;
  points: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[13.5px] text-ink-soft">{label}</span>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onChange(Math.max(0, value - 1))}
          className="flex h-6 w-6 items-center justify-center rounded-[4px] border border-line text-ink-soft hover:bg-ink/5"
        >
          −
        </button>
        <span className="w-4 text-center text-[13.5px] text-ink">{value}</span>
        <button
          onClick={() => onChange(value + 1)}
          className="flex h-6 w-6 items-center justify-center rounded-[4px] border border-line text-ink-soft hover:bg-ink/5"
        >
          +
        </button>
        <span className="w-14 text-right font-mono text-[11.5px] text-ink-faint">
          ×{points}
        </span>
      </div>
    </div>
  );
}
