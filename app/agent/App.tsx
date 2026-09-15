import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Button from "./Button";
import Tabs from "./Tabs";
import Modal from "./Modal";
import ContributeForm from "./ContributeForm";
import { UpvoteBadge } from "./Badge";
import { categoryThemes } from "../lib/categoryTheme";
import { getCourse, getCourseResources } from "../data/mockData";
import type { Resource, ResourceType } from "../data/types";
import { RESOURCE_TYPE_LABEL } from "../data/types";

export default function CourseWindow({
  courseId,
  onClose,
}: {
  courseId: string | null;
  onClose: () => void;
}) {
  const [active, setActive] = useState<"all" | ResourceType>("all");
  const [uploadOpen, setUploadOpen] = useState(false);
  const course = courseId ? getCourse(courseId) : undefined;

  useEffect(() => {
    if (courseId) setActive("all");
  }, [courseId]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (courseId) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [courseId, onClose]);

  const resources = useMemo(() => (course ? getCourseResources(course.id) : []), [course]);
  const filtered = active === "all" ? resources : resources.filter((r) => r.type === active);

  if (!course) return null;

  const counts = {
    notes: resources.filter((r) => r.type === "notes").length,
    "past-paper": resources.filter((r) => r.type === "past-paper").length,
    extras: resources.filter((r) => r.type === "extras").length,
    reference: resources.filter((r) => r.type === "reference").length,
  };

  const summary = [
    counts["past-paper"] > 0 ? `${counts["past-paper"]} past papers` : null,
    counts.notes > 0 ? `${counts.notes} notes` : null,
    counts.extras > 0 ? `${counts.extras} extras` : null,
    counts.reference > 0 ? `${counts.reference} references` : null,
  ]
    .filter(Boolean)
    .join(" · ");

  const tabs = [
    { id: "all", label: "Everything", count: resources.length },
    { id: "past-paper", label: "Past Papers", count: counts["past-paper"] },
    { id: "notes", label: "Notes", count: counts.notes },
    { id: "extras", label: "Extras", count: counts.extras },
    { id: "reference", label: "References", count: counts.reference },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink/45 backdrop-blur-sm sm:items-center sm:px-4">
      <div className="absolute inset-0" onClick={onClose} aria-hidden />
      <div className="relative flex max-h-[92vh] w-full max-w-[720px] flex-col overflow-hidden rounded-t-[16px] border border-line-strong bg-card shadow-lift sm:rounded-[16px]">
        {/* Header */}
        <div className="shrink-0 border-b border-line px-6 pb-5 pt-6 sm:px-8">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <h2 className="truncate font-serif text-[24px] leading-tight text-ink sm:text-[28px]">
                {course.title}
              </h2>
              <p className="mt-1.5 text-[13.5px] text-ink-soft">
                {resources.length} {resources.length === 1 ? "file" : "files"}
                {summary && <span> — {summary}</span>}
              </p>
            </div>
            <button
              onClick={onClose}
              aria-label="Close"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-line text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="shrink-0 px-6 sm:px-8">
          <Tabs items={tabs} active={active} onChange={(v) => setActive(v as typeof active)} />
        </div>

        {/* Resource list */}
        <div className="flex-1 overflow-y-auto px-3 py-2 sm:px-5">
          {filtered.map((r) => (
            <CourseWindowResourceRow key={r.id} resource={r} />
          ))}
          {filtered.length === 0 && (
            <p className="py-16 text-center text-ink-faint">
              No {active !== "all" ? RESOURCE_TYPE_LABEL[active] : "resources"} uploaded yet
              for this course. Be the first to contribute.
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex shrink-0 items-center justify-end border-t border-line px-5 py-3.5 sm:px-6">
          <Button size="sm" onClick={() => setUploadOpen(true)}>
            Upload a file to this course
          </Button>
        </div>
      </div>

      <Modal open={uploadOpen} onClose={() => setUploadOpen(false)} title="Share Course Resources">
        <p className="-mt-2 mb-4 text-[13.5px] text-ink-soft">
          Help fellow students by uploading past papers, lecture notes, or
          extras for {course.title}.
        </p>
        <ContributeForm compact defaultCourse={course.title} onSubmitted={() => setUploadOpen(false)} />
      </Modal>
    </div>
  );
}

function CourseWindowResourceRow({ resource }: { resource: Resource }) {
  const theme = categoryThemes[resource.type];
  const [copied, setCopied] = useState(false);

  function handleShare(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    const url = `${window.location.origin}/resource/${resource.id}`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).catch(() => {});
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="flex items-center gap-3 rounded-[8px] px-2.5 py-3 transition-colors hover:bg-paper sm:gap-4 sm:px-3">
      <span
        className="h-2 w-2 shrink-0 rounded-full"
        style={{ backgroundColor: theme.dot }}
        aria-hidden
      />
      <div className="min-w-0 flex-1">
        <p className="truncate text-[14.5px] text-ink">{resource.title}</p>
        <div className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[12px] text-ink-faint">
          <span>{resource.academicYear}</span>
          <span aria-hidden>·</span>
          <span>by {resource.contributor}</span>
          <span aria-hidden>·</span>
          <UpvoteBadge count={resource.upvotes} />
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <button
          onClick={handleShare}
          className="rounded-full border border-line px-3 py-1.5 text-[12.5px] font-medium text-ink-soft transition-colors hover:border-line-strong hover:text-ink"
        >
          {copied ? "Copied" : "Share"}
        </button>
        <Link
          to={`/resource/${resource.id}`}
          className="rounded-full bg-ink px-3 py-1.5 text-[12.5px] font-medium text-paper transition-colors hover:bg-oxblood-dark"
        >
          Open
        </Link>
      </div>
    </div>
  );
}
