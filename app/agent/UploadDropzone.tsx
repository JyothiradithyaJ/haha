import type { Course } from "../data/types";

export default function CourseCard({
  course,
  onOpen,
  className = "",
}: {
  course: Course;
  onOpen: (courseId: string) => void;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={() => onOpen(course.id)}
      className={`group relative flex snap-start flex-col justify-between overflow-hidden rounded-[9px] border border-line bg-card p-5 text-left shadow-card transition-all duration-200 hover:-translate-y-1 hover:border-oxblood/30 hover:shadow-lift ${className}`}
    >
      <div className="absolute inset-x-0 top-0 h-[3px] scale-x-0 bg-oxblood transition-transform duration-200 group-hover:scale-x-100" />
      <h3 className="font-serif text-[17px] leading-snug text-ink group-hover:text-oxblood">
        {course.title}
      </h3>
      <div className="mt-5 flex items-center justify-between text-[12.5px] text-ink-faint">
        <span>{course.resourceCount} resources</span>
        <span className="font-medium text-oxblood opacity-0 transition-opacity group-hover:opacity-100">
          View →
        </span>
      </div>
    </button>
  );
}
