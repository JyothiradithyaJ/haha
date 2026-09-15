import Layout from "../components/Layout";
import { releases } from "../data/mockData";

const tagStyles: Record<string, string> = {
  Major: "bg-oxblood-tint text-oxblood-dark border-oxblood/20",
  Minor: "bg-brass-tint text-[#7A5A16] border-brass/30",
  Patch: "bg-ink/5 text-ink-soft border-ink/10",
};

export default function Releases() {
  return (
    <Layout>
      <section className="border-b border-line px-5 py-14 sm:px-8 sm:py-16">
        <div className="mx-auto max-w-content">
          <p className="call-number">Changelog</p>
          <h1 className="mt-3 font-serif text-[32px] leading-tight text-ink sm:text-[40px]">
            Releases & updates
          </h1>
          <p className="mt-3 max-w-lg text-[15px] text-ink-soft">
            What's new on ARCHIVE, in the order it shipped.
          </p>
        </div>
      </section>

      <section className="px-5 py-14 sm:px-8">
        <div className="mx-auto max-w-[720px]">
          <div className="relative space-y-10 border-l border-line pl-8">
            {releases.map((r) => (
              <div key={r.version} className="relative">
                <span className="absolute -left-[37px] top-1 h-2.5 w-2.5 rounded-full border-2 border-oxblood bg-paper" />
                <div className="flex flex-wrap items-center gap-2.5">
                  <h2 className="font-serif text-[19px] text-ink">{r.version}</h2>
                  <span className={`rounded-[3px] border px-2 py-0.5 text-[11px] font-medium ${tagStyles[r.tag]}`}>
                    {r.tag}
                  </span>
                  <span className="text-[12.5px] text-ink-faint">{r.date}</span>
                </div>

                <div className="mt-3 space-y-3">
                  {r.features.length > 0 && (
                    <ReleaseGroup label="New" items={r.features} />
                  )}
                  {r.improvements.length > 0 && (
                    <ReleaseGroup label="Improved" items={r.improvements} />
                  )}
                  {r.fixes.length > 0 && (
                    <ReleaseGroup label="Fixed" items={r.fixes} />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  );
}

function ReleaseGroup({ label, items }: { label: string; items: string[] }) {
  return (
    <div>
      <p className="text-[12px] font-medium text-ink-faint">{label}</p>
      <ul className="mt-1.5 space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2 text-[14px] leading-relaxed text-ink-soft">
            <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-ink-faint" />
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}
