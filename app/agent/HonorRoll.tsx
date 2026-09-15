import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import Button from "../components/Button";
import CourseCard from "../components/CourseCard";
import CourseWindow from "../components/CourseWindow";
import Carousel from "../components/Carousel";
import ShelfPreview from "../components/ShelfPreview";
import PillFilter from "../components/PillFilter";
import { courses, resources } from "../data/mockData";
import { categoryOrder, categoryThemes } from "../lib/categoryTheme";
import type { ResourceType } from "../data/types";

export default function Home() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<"all" | ResourceType>("all");
  const [openCourseId, setOpenCourseId] = useState<string | null>(null);

  const filteredCourses = useMemo(() => {
    let list = courses;
    if (activeCategory !== "all") {
      const courseIdsWithCategory = new Set(
        resources.filter((r) => r.type === activeCategory).map((r) => r.courseId)
      );
      list = list.filter((c) => courseIdsWithCategory.has(c.id));
    }
    if (query.trim()) {
      const needle = query.toLowerCase();
      list = list.filter((c) => c.title.toLowerCase().includes(needle));
    }
    return list;
  }, [query, activeCategory]);

  const pillOptions = [
    { id: "all", label: "Everything", dot: "#1C1B18" },
    ...categoryOrder.map((id) => ({
      id,
      label: categoryThemes[id].label,
      dot: categoryThemes[id].dot,
    })),
  ];

  return (
    <Layout>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-line px-5 pb-16 pt-16 sm:px-8 sm:pb-20 sm:pt-24">
        {/* decorative accent shapes */}
        <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-[radial-gradient(circle,rgba(122,46,42,0.14),transparent_70%)]" />
        <div className="pointer-events-none absolute left-1/2 top-10 h-40 w-40 -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(107,63,160,0.10),transparent_70%)] sm:left-[60%]" />
        <div className="pointer-events-none absolute right-10 top-28 hidden rotate-6 rounded-[6px] border border-line-strong bg-card px-3 py-1.5 text-[11px] font-mono text-ink-faint shadow-card sm:block">
          #DataStructures
        </div>
        <div className="pointer-events-none absolute right-32 top-8 hidden -rotate-3 rounded-[6px] border border-notes/30 bg-notes-tint px-3 py-1.5 text-[11px] font-medium text-notes-dark shadow-card md:block">
          +5 pts
        </div>

        <div className="relative mx-auto max-w-content">
          <div className="max-w-2xl">
            <p className="inline-flex items-center gap-1.5 rounded-full border border-oxblood/25 bg-oxblood-tint px-3 py-1 text-[12px] font-medium text-oxblood-dark">
              BMSIT · Academic Resource Hub
            </p>
            <h1 className="mt-5 font-serif text-[38px] font-semibold leading-[1.08] tracking-tightish text-ink sm:text-[54px]">
              Notes, papers and books,
              <br />
              <span className="text-oxblood">all in one place.</span>
            </h1>
            <p className="mt-5 max-w-lg text-[16px] leading-relaxed text-ink-soft sm:text-[17.5px]">
              Organized by course, kept up to date by students across every
              branch. Find exactly what you need in seconds.
            </p>
          </div>

          <div className="mt-9 max-w-xl">
            <div
              title="Search is limited to course names"
              className="flex items-center gap-3 rounded-[7px] border border-line bg-line/25 px-4 py-3.5 opacity-90 shadow-card"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="shrink-0 text-ink-faint">
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search course name"
                className="flex-1 cursor-text bg-transparent text-[15px] text-ink-soft placeholder:text-ink-faint focus:outline-none"
              />
            </div>
          </div>

          {/* Category slider */}
          <div className="mt-6 overflow-x-auto pb-1">
            <PillFilter options={pillOptions} active={activeCategory} onChange={(v) => setActiveCategory(v as typeof activeCategory)} />
          </div>
        </div>
      </section>

      {/* Category cards */}
      <section className="border-b border-line px-5 py-16 sm:px-8">
        <div className="mx-auto max-w-content">
          <h2 className="font-serif text-[26px] text-ink">Browse by category</h2>
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {categoryOrder.map((id) => {
              const theme = categoryThemes[id];
              const isActive = activeCategory === id;
              return (
                <button
                  key={id}
                  onClick={() => setActiveCategory(isActive ? "all" : id)}
                  className={`group relative flex min-h-[168px] flex-col justify-between overflow-hidden rounded-[12px] bg-gradient-to-br ${theme.gradient} p-5 text-left text-white shadow-[0_10px_28px_-14px_rgba(0,0,0,0.45)] transition-all duration-250 hover:-translate-y-1.5 hover:shadow-[0_20px_36px_-14px_rgba(0,0,0,0.5)] ${
                    isActive ? "ring-2 ring-ink ring-offset-2 ring-offset-paper" : ""
                  }`}
                >
                  <div className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/10 transition-transform duration-300 group-hover:scale-125" />
                  <div className="pointer-events-none absolute -bottom-8 -left-8 h-24 w-24 rounded-full bg-black/10" />
                  <div className="relative flex h-9 w-9 items-center justify-center rounded-[8px] bg-white/20 backdrop-blur-sm">
                    <CategoryIcon id={id} />
                  </div>
                  <div className="relative">
                    <p className="font-serif text-[19px] leading-tight">{theme.label}</p>
                    <p className="mt-1 text-[12.5px] text-white/80">{theme.blurb}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Browse by course name */}
      <section className="px-5 py-16 sm:px-8">
        <div className="mx-auto max-w-content">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h2 className="font-serif text-[26px] text-ink">Browse courses</h2>
              <p className="mt-1.5 text-[14.5px] text-ink-soft">
                {filteredCourses.length} of {courses.length} courses
                {activeCategory !== "all" ? ` with ${categoryThemes[activeCategory].label.toLowerCase()}` : ""}.
                Click a course to open it.
              </p>
            </div>
            {activeCategory !== "all" && (
              <button
                onClick={() => setActiveCategory("all")}
                className="shrink-0 text-[13.5px] font-medium text-oxblood hover:text-oxblood-dark"
              >
                Clear filter ✕
              </button>
            )}
          </div>

          <div className="mt-6">
            <Carousel>
              {filteredCourses.map((c) => (
                <CourseCard
                  key={c.id}
                  course={c}
                  onOpen={setOpenCourseId}
                  className="w-[260px] shrink-0"
                />
              ))}
              {filteredCourses.length === 0 && (
                <p className="py-10 text-ink-faint">No courses matched your search.</p>
              )}
            </Carousel>
          </div>
        </div>
      </section>

      {/* Bookshelf preview */}
      <section className="border-t border-line bg-card px-5 py-16 sm:px-8">
        <div className="mx-auto max-w-content">
          <div className="flex items-end justify-between">
            <div>
              <h2 className="font-serif text-[26px] text-ink">The reference shelf</h2>
              <p className="mt-1.5 text-[14.5px] text-ink-soft">
                The textbooks your courses actually lean on.
              </p>
            </div>
            <Link to="/bookshelf" className="hidden shrink-0 text-[14px] font-medium text-oxblood sm:block">
              All shelves →
            </Link>
          </div>
          <div className="mt-8">
            <ShelfPreview />
          </div>
          <Link to="/bookshelf" className="mt-6 block text-center text-[14px] font-medium text-oxblood sm:hidden">
            All shelves →
          </Link>
        </div>
      </section>

      {/* Contribution CTA */}
      <section className="px-5 py-16 sm:px-8">
        <div className="mx-auto max-w-content overflow-hidden rounded-[10px] border border-line bg-[radial-gradient(circle_at_top_right,rgba(122,46,42,0.10),transparent_55%)] bg-card p-8 sm:p-12">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
            <div className="max-w-lg">
              <h2 className="font-serif text-[26px] leading-tight text-ink sm:text-[30px]">
                Got past papers or notes sitting in your drive?
              </h2>
              <p className="mt-2.5 text-[15px] text-ink-soft">
                Share your course files and help build the resource hub
                every BMSIT student wishes they had.
              </p>
            </div>
            <Link to="/contribute" className="shrink-0">
              <Button size="md">Contribute a file</Button>
            </Link>
          </div>
        </div>
      </section>

      <CourseWindow courseId={openCourseId} onClose={() => setOpenCourseId(null)} />
    </Layout>
  );
}

function CategoryIcon({ id }: { id: string }) {
  const common = { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none" } as const;
  if (id === "notes")
    return (
      <svg {...common}>
        <path d="M6 4H16L20 8V20H6V4Z" stroke="white" strokeWidth="1.7" strokeLinejoin="round" />
        <path d="M9 12H15M9 16H13" stroke="white" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    );
  if (id === "past-paper")
    return (
      <svg {...common}>
        <rect x="4" y="5" width="16" height="14" rx="1.5" stroke="white" strokeWidth="1.7" />
        <path d="M8 9H16M8 13H16M8 17H12" stroke="white" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    );
  if (id === "extras")
    return (
      <svg {...common}>
        <path d="M12 3L14.5 8.5L20.5 9.3L16.2 13.3L17.3 19.3L12 16.3L6.7 19.3L7.8 13.3L3.5 9.3L9.5 8.5L12 3Z" stroke="white" strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    );
  return (
    <svg {...common}>
      <path d="M4 5.5C4 4.7 4.7 4 5.5 4H11V20H5.5C4.7 20 4 19.3 4 18.5V5.5Z" stroke="white" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M20 5.5C20 4.7 19.3 4 18.5 4H13V20H18.5C19.3 20 20 19.3 20 18.5V5.5Z" stroke="white" strokeWidth="1.6" strokeLinejoin="round" />
    </svg>
  );
}
