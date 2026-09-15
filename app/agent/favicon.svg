import Layout from "../components/Layout";

const sections = [
  {
    title: "Academic integrity",
    body: "ARCHIVE exists to help you study smarter, not to substitute for doing your own work. Using shared notes or past papers to prepare is fine; submitting someone else's work as your own is a violation of BMSIT's academic integrity policy and is never condoned here.",
  },
  {
    title: "Appropriate uploads",
    body: "Upload material that helps other students learn: past question papers, lecture notes, assignment solutions after their due date, and reference book scans. Keep files legible and correctly labelled with course, semester and year.",
  },
  {
    title: "Copyright",
    body: "Only upload material you have the right to share. Scanned textbook chapters for personal study are generally tolerated in the spirit of student resource-sharing, but do not upload entire pirated books, paid course material, or anything under active commercial licence.",
  },
  {
    title: "Privacy",
    body: "Never upload documents containing personal information — your own or anyone else's — such as ID numbers, addresses, or private correspondence. Contributor names are shown next to uploads unless you choose to contribute anonymously.",
  },
  {
    title: "Prohibited content",
    body: "Ongoing or active assignments, confidential exam material obtained improperly, and anything unrelated to academics have no place here. Uploads like these will be removed and repeated violations may result in a contributor being blocked.",
  },
  {
    title: "Moderation",
    body: "Every upload is reviewed before it goes live. Moderators may edit metadata for clarity, merge duplicate uploads, or decline a file without explanation if it doesn't meet these guidelines.",
  },
  {
    title: "Contributor responsibilities",
    body: "By uploading, you confirm the file is accurate, correctly categorized, and safe to share. Honor Roll points are awarded in good faith and may be revoked if a resource is later found to violate these rules.",
  },
];

export default function Terms() {
  return (
    <Layout>
      <section className="border-b border-line px-5 py-14 sm:px-8 sm:py-16">
        <div className="mx-auto max-w-content">
          <p className="call-number">Legal</p>
          <h1 className="mt-3 font-serif text-[32px] leading-tight text-ink sm:text-[40px]">
            Terms & rules
          </h1>
          <p className="mt-3 max-w-xl text-[15px] text-ink-soft">
            A short set of ground rules that keep ARCHIVE useful, safe and
            fair for every BMSIT student who relies on it.
          </p>
        </div>
      </section>

      <section className="px-5 py-14 sm:px-8">
        <div className="mx-auto max-w-[720px] divide-y divide-line">
          {sections.map((s, i) => (
            <div key={s.title} className="py-7 first:pt-0">
              <div className="flex items-baseline gap-3">
                <span className="call-number">{String(i + 1).padStart(2, "0")}</span>
                <h2 className="font-serif text-[19px] text-ink">{s.title}</h2>
              </div>
              <p className="mt-2.5 text-[14.5px] leading-relaxed text-ink-soft">{s.body}</p>
            </div>
          ))}
        </div>
      </section>
    </Layout>
  );
}
