import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import Button from "../components/Button";
import { TypeBadge } from "../components/Badge";
import { departments, getCourse, getCourseResources, getResource } from "../data/mockData";
import { RESOURCE_TYPE_LABEL } from "../data/types";

export default function Resource() {
  const { id } = useParams();
  const resource = getResource(id ?? "");
  const [upvoted, setUpvoted] = useState(false);
  const [reported, setReported] = useState(false);

  if (!resource) {
    return (
      <Layout>
        <div className="mx-auto max-w-content px-5 py-24 text-center sm:px-8">
          <p className="text-ink-soft">Resource not found.</p>
          <Link to="/" className="mt-4 inline-block text-oxblood">← Back to Archive</Link>
        </div>
      </Layout>
    );
  }

  const course = getCourse(resource.courseId)!;
  const dept = departments.find((d) => d.id === course.departmentId);
  const related = getCourseResources(course.id).filter((r) => r.id !== resource.id).slice(0, 4);

  return (
    <Layout>
      <section className="border-b border-line px-5 py-8 sm:px-8">
        <div className="mx-auto max-w-content">
          <Link to={`/course/${course.id}`} className="text-[13.5px] text-ink-faint hover:text-oxblood">
            ← Back to {course.title}
          </Link>
        </div>
      </section>

      <section className="px-5 py-10 sm:px-8">
        <div className="mx-auto grid max-w-content gap-10 lg:grid-cols-[1fr_320px]">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <TypeBadge type={resource.type} label={RESOURCE_TYPE_LABEL[resource.type]} />
              <span className="call-number">{dept?.short}</span>
            </div>
            <h1 className="mt-3 font-serif text-[26px] leading-tight text-ink sm:text-[30px]">
              {resource.title}
            </h1>
            <p className="mt-1.5 text-[14px] text-ink-soft">
              {course.title} · Semester {resource.semester} · {resource.academicYear}
            </p>

            {/* Mock PDF preview */}
            <div className="mt-7 overflow-hidden rounded-[8px] border border-line bg-card">
              <div className="flex aspect-[4/5] flex-col items-center justify-center gap-3 bg-[repeating-linear-gradient(135deg,rgba(28,27,24,0.025),rgba(28,27,24,0.025)_2px,transparent_2px,transparent_10px)] sm:aspect-[8/9]">
                <div className="flex h-16 w-16 items-center justify-center rounded-[6px] border border-line-strong bg-paper text-[11px] font-semibold text-ink-faint">
                  {resource.fileType}
                </div>
                <p className="text-[13px] text-ink-faint">Preview unavailable in this prototype</p>
              </div>
              <div className="flex flex-col items-center justify-between gap-3 border-t border-line p-4 sm:flex-row">
                <p className="text-[12.5px] text-ink-faint">
                  {resource.fileType} · {resource.fileSizeMb} MB
                </p>
                <Button size="md" className="w-full sm:w-auto">Download file</Button>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-3">
              <button
                onClick={() => setUpvoted((v) => !v)}
                className={`flex items-center gap-2 rounded-[5px] border px-3.5 py-2 text-[13.5px] font-medium transition-all duration-150 ${
                  upvoted
                    ? "border-oxblood bg-oxblood-tint text-oxblood-dark"
                    : "border-line text-ink-soft hover:-translate-y-0.5 hover:border-line-strong hover:shadow-card"
                }`}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M7 22H4C3.45 22 3 21.55 3 21V12C3 11.45 3.45 11 4 11H7V22ZM7 22H17.5C18.6 22 19.53 21.24 19.76 20.16L21.6 11.16C21.9 9.73 20.84 8.4 19.38 8.4H14.5L15.24 4.55C15.42 3.58 14.96 2.6 14.09 2.13C13.5 1.81 12.78 1.94 12.34 2.46L7 8.8"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinejoin="round"
                    strokeLinecap="round"
                  />
                </svg>
                Upvote ({resource.upvotes + (upvoted ? 1 : 0)})
              </button>
              <button
                onClick={() => setReported(true)}
                disabled={reported}
                className="rounded-[5px] border border-line px-3.5 py-2 text-[13.5px] text-ink-faint transition-colors hover:border-line-strong hover:text-ink disabled:opacity-50"
              >
                {reported ? "Reported — thank you" : "Report resource"}
              </button>
            </div>
          </div>

          <aside className="space-y-6">
            <div className="rounded-[8px] border border-line bg-card p-5">
              <h3 className="font-serif text-[16px] text-ink">File information</h3>
              <dl className="mt-3 space-y-2.5 text-[13px]">
                <Row k="Department" v={dept?.name ?? "—"} />
                <Row k="Course" v={course.title} />
                <Row k="Semester" v={`Semester ${resource.semester}`} />
                <Row k="Academic year" v={resource.academicYear} />
                <Row k="Contributor" v={resource.contributor} />
                <Row k="Uploaded" v={resource.uploadDate} />
              </dl>
            </div>

            <div className="rounded-[8px] border border-line bg-card p-5">
              <h3 className="font-serif text-[16px] text-ink">Related resources</h3>
              <div className="mt-3 space-y-1">
                {related.map((r) => (
                  <Link
                    key={r.id}
                    to={`/resource/${r.id}`}
                    className="block rounded-[5px] px-2 py-2 text-[13px] text-ink-soft transition-colors hover:bg-paper hover:text-ink"
                  >
                    {r.title}
                  </Link>
                ))}
                {related.length === 0 && (
                  <p className="text-[13px] text-ink-faint">No other resources yet.</p>
                )}
              </div>
            </div>
          </aside>
        </div>
      </section>
    </Layout>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-ink-faint">{k}</dt>
      <dd className="text-right text-ink">{v}</dd>
    </div>
  );
}
