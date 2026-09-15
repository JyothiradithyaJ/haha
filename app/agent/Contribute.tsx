import type { ResourceType } from "../data/types";

export interface CategoryTheme {
  id: ResourceType;
  label: string;
  blurb: string;
  accent: string; // tailwind color token root, e.g. "notes"
  gradient: string; // tailwind classes for a colorful card background
  badgeClasses: string;
  iconBg: string;
  dot: string; // hex color for small indicator dots
}

export const categoryThemes: Record<ResourceType, CategoryTheme> = {
  notes: {
    id: "notes",
    label: "Notes",
    blurb: "Lecture decks & handwritten",
    accent: "notes",
    gradient: "from-[#1E7A4C] via-[#238F58] to-[#3FA873]",
    badgeClasses: "bg-notes-tint text-notes-dark border-notes/25",
    iconBg: "bg-notes/15 text-notes-dark",
    dot: "#1E7A4C",
  },
  "past-paper": {
    id: "past-paper",
    label: "Past Papers",
    blurb: "Endsems, midsems, quizzes",
    accent: "papers",
    gradient: "from-[#C1660B] via-[#D67717] to-[#E88A34]",
    badgeClasses: "bg-papers-tint text-papers-dark border-papers/25",
    iconBg: "bg-papers/15 text-papers-dark",
    dot: "#C1660B",
  },
  extras: {
    id: "extras",
    label: "Extras",
    blurb: "Labs, tutorials, projects",
    accent: "extras",
    gradient: "from-[#C23B3B] via-[#CF4B45] to-[#E1655F]",
    badgeClasses: "bg-extras-tint text-extras-dark border-extras/25",
    iconBg: "bg-extras/15 text-extras-dark",
    dot: "#C23B3B",
  },
  reference: {
    id: "reference",
    label: "References",
    blurb: "Textbooks & reading",
    accent: "refs",
    gradient: "from-[#6B3FA0] via-[#7C4CAF] to-[#9067C4]",
    badgeClasses: "bg-refs-tint text-refs-dark border-refs/25",
    iconBg: "bg-refs/15 text-refs-dark",
    dot: "#6B3FA0",
  },
};

export const categoryOrder: ResourceType[] = ["notes", "past-paper", "extras", "reference"];
