import type {
  Contributor,
  Course,
  Department,
  Release,
  Resource,
} from "./types";

export const departments: Department[] = [
  { id: "cse", name: "Computer Science & Engineering", short: "CSE", courseCount: 34 },
  { id: "ise", name: "Information Science & Engineering", short: "ISE", courseCount: 29 },
  { id: "aiml", name: "Artificial Intelligence & Machine Learning", short: "AI&ML", courseCount: 22 },
  { id: "ece", name: "Electronics & Communication Engineering", short: "ECE", courseCount: 31 },
  { id: "eee", name: "Electrical & Electronics Engineering", short: "EEE", courseCount: 27 },
  { id: "mech", name: "Mechanical Engineering", short: "MECH", courseCount: 30 },
  { id: "civil", name: "Civil Engineering", short: "CIVIL", courseCount: 25 },
  { id: "aids", name: "Artificial Intelligence & Data Science", short: "AI&DS", courseCount: 20 },
];

export const courses: Course[] = [
  { id: "cs301", title: "Data Structures and Algorithms", departmentId: "cse", semester: 3, resourceCount: 42 },
  { id: "cs302", title: "Discrete Mathematical Structures", departmentId: "cse", semester: 3, resourceCount: 28 },
  { id: "cs401", title: "Operating Systems", departmentId: "cse", semester: 4, resourceCount: 37 },
  { id: "cs501", title: "Database Management Systems", departmentId: "cse", semester: 5, resourceCount: 45 },
  { id: "cs601", title: "Computer Networks", departmentId: "cse", semester: 6, resourceCount: 31 },
  { id: "is401", title: "Object Oriented Modelling and Design", departmentId: "ise", semester: 4, resourceCount: 19 },
  { id: "is502", title: "Cloud Computing", departmentId: "ise", semester: 5, resourceCount: 16 },
  { id: "ai302", title: "Machine Learning Fundamentals", departmentId: "aiml", semester: 5, resourceCount: 38 },
  { id: "ai403", title: "Deep Learning", departmentId: "aiml", semester: 6, resourceCount: 24 },
  { id: "ai201", title: "Probability and Statistics", departmentId: "aiml", semester: 3, resourceCount: 21 },
  { id: "ec302", title: "Digital Signal Processing", departmentId: "ece", semester: 5, resourceCount: 18 },
  { id: "ec204", title: "Analog Electronic Circuits", departmentId: "ece", semester: 3, resourceCount: 22 },
  { id: "ee305", title: "Power Systems Analysis", departmentId: "eee", semester: 5, resourceCount: 15 },
  { id: "me210", title: "Thermodynamics", departmentId: "mech", semester: 3, resourceCount: 26 },
  { id: "me415", title: "Machine Design", departmentId: "mech", semester: 5, resourceCount: 14 },
  { id: "cv220", title: "Structural Analysis", departmentId: "civil", semester: 4, resourceCount: 17 },
  { id: "ma210", title: "Transform Calculus and Numerical Methods", departmentId: "cse", semester: 3, resourceCount: 33 },
  { id: "ds501", title: "Big Data Analytics", departmentId: "aids", semester: 5, resourceCount: 20 },
];

const contributorNames = [
  "Aarav Shetty", "Meera Iyengar", "Rohan Kulkarni", "Ishita Rao", "Kabir Nair",
  "Ananya Bhat", "Varun Reddy", "Sanjana Hegde", "Devansh Gowda", "Pooja Murthy",
  "Nikhil Shastri", "Tara Menon", "Arjun Kamath", "Diya Pai", "Yash Acharya",
];

const branches = ["CSE", "ISE", "AI&ML", "ECE", "EEE", "MECH", "CIVIL", "AI&DS"];

function seedRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const rand = seedRandom(42);

// Reference books, keyed by course — these double as both the "References"
// resource category and the Bookshelf.
const referenceBooks: Record<string, { title: string; author: string; edition: string; sizeMb: number }[]> = {
  cs301: [{ title: "Introduction to Algorithms", author: "Cormen, Leiserson, Rivest, Stein", edition: "4th Edition", sizeMb: 18.4 }],
  cs401: [{ title: "Operating System Concepts", author: "Silberschatz, Galvin, Gagne", edition: "10th Edition", sizeMb: 22.1 }],
  cs501: [{ title: "Database System Concepts", author: "Silberschatz, Korth, Sudarshan", edition: "7th Edition", sizeMb: 15.7 }],
  ai302: [{ title: "Pattern Recognition and Machine Learning", author: "Christopher M. Bishop", edition: "1st Edition", sizeMb: 12.3 }],
  ai403: [{ title: "Deep Learning", author: "Ian Goodfellow, Yoshua Bengio, Aaron Courville", edition: "1st Edition", sizeMb: 24.6 }],
  ec302: [{ title: "Digital Signal Processing", author: "John G. Proakis, Dimitris K Manolakis", edition: "4th Edition", sizeMb: 19.8 }],
  cs601: [{ title: "Computer Networking: A Top-Down Approach", author: "James Kurose, Keith Ross", edition: "8th Edition", sizeMb: 20.2 }],
  me210: [{ title: "Engineering Thermodynamics", author: "P. K. Nag", edition: "6th Edition", sizeMb: 16.9 }],
  cs302: [{ title: "Discrete Mathematics and Its Applications", author: "Kenneth H. Rosen", edition: "8th Edition", sizeMb: 21.4 }],
  cv220: [{ title: "Structural Analysis", author: "R. C. Hibbeler", edition: "10th Edition", sizeMb: 27.3 }],
};

export const resources: Resource[] = (() => {
  const titles: Record<string, string[]> = {
    "past-paper": ["Endsem 2025", "Midsem-1 2025", "Midsem-2 2024", "Endsem 2024 Supplementary", "Endsem 2023"],
    notes: ["Unit 1-2 Lecture Notes", "Complete Semester Notes", "Handwritten Notes (Topper's copy)", "Module 3 Summary", "Formula Sheet"],
    extras: ["Assignment 1 Solutions", "Lab Manual with Solutions", "Tutorial Sheet 4", "Mini Project Report"],
  };
  const types: Array<"past-paper" | "notes" | "extras"> = ["past-paper", "notes", "extras"];
  const fileTypes: Array<Resource["fileType"]> = ["PDF", "DOCX", "PPTX", "PDF", "PDF"];
  const out: Resource[] = [];
  let id = 1;
  courses.forEach((course) => {
    const count = 4 + Math.floor(rand() * 5);
    for (let i = 0; i < count; i++) {
      const type = types[Math.floor(rand() * types.length)];
      const titleBank = titles[type];
      const title = titleBank[Math.floor(rand() * titleBank.length)];
      out.push({
        id: `r${id}`,
        title,
        courseId: course.id,
        type,
        academicYear: ["2025-26", "2024-25", "2023-24"][Math.floor(rand() * 3)],
        semester: course.semester,
        fileType: fileTypes[Math.floor(rand() * fileTypes.length)],
        fileSizeMb: Math.round((0.4 + rand() * 12) * 10) / 10,
        contributor: contributorNames[Math.floor(rand() * contributorNames.length)],
        uploadDate: `2026-0${1 + Math.floor(rand() * 8)}-${10 + Math.floor(rand() * 18)}`,
        upvotes: Math.floor(rand() * 140),
      });
      id++;
    }
    // reference-type resources (textbooks) for this course, if any
    (referenceBooks[course.id] ?? []).forEach((book) => {
      out.push({
        id: `r${id}`,
        title: book.title,
        courseId: course.id,
        type: "reference",
        academicYear: "—",
        semester: course.semester,
        fileType: "PDF",
        fileSizeMb: book.sizeMb,
        contributor: contributorNames[Math.floor(rand() * contributorNames.length)],
        uploadDate: `2026-0${1 + Math.floor(rand() * 8)}-${10 + Math.floor(rand() * 18)}`,
        upvotes: Math.floor(rand() * 140),
      });
      id++;
    });
  });
  return out;
})();

// Books shown on the Bookshelf are exactly the "reference" type resources.
export const books = resources.filter((r) => r.type === "reference");

export function bookAuthor(bookResource: Resource) {
  const course = courses.find((c) => c.id === bookResource.courseId);
  const entry = (referenceBooks[course?.id ?? ""] ?? []).find((b) => b.title === bookResource.title);
  return entry?.author ?? "Unknown author";
}

export function bookEdition(bookResource: Resource) {
  const course = courses.find((c) => c.id === bookResource.courseId);
  const entry = (referenceBooks[course?.id ?? ""] ?? []).find((b) => b.title === bookResource.title);
  return entry?.edition ?? "";
}

export const contributors: Contributor[] = contributorNames.map((name, i) => {
  const pastPapers = 3 + Math.floor(rand() * 18);
  const notes = 2 + Math.floor(rand() * 14);
  const extras = Math.floor(rand() * 10);
  const reference = Math.floor(rand() * 5);
  return {
    id: `c${i + 1}`,
    name,
    branch: branches[i % branches.length],
    contributions: pastPapers + notes + extras + reference,
    points: pastPapers * 10 + notes * 5 + extras * 8 + reference * 2,
    pastPapers,
    notes,
    extras,
    reference,
    upvotes: 20 + Math.floor(rand() * 480),
  };
}).sort((a, b) => b.points - a.points);

export const releases: Release[] = [
  {
    version: "v2.4.0",
    date: "September 2026",
    tag: "Minor",
    features: [
      "Added the Honor Roll points calculator so contributors can estimate points before uploading",
      "Introduced course-level resource tabs for faster filtering by type",
    ],
    improvements: [
      "Search now matches course names for faster lookup",
      "Resource cards show file size and contributor at a glance",
    ],
    fixes: [
      "Fixed an issue where the mobile navigation stayed open after selecting a page",
    ],
  },
  {
    version: "v2.3.1",
    date: "July 2026",
    tag: "Patch",
    features: [],
    improvements: [
      "Bookshelf cards now show edition information for textbooks",
    ],
    fixes: [
      "Corrected sorting order on the Honor Roll all-time tab",
      "Fixed broken hover state on category cards in Safari",
    ],
  },
  {
    version: "v2.3.0",
    date: "May 2026",
    tag: "Minor",
    features: [
      "Launched the Bookshelf, a dedicated home for reference textbooks",
      "Added anonymous contribution option on the Contribute form",
    ],
    improvements: [
      "Reworked the homepage hero and search for faster course lookup",
    ],
    fixes: [],
  },
  {
    version: "v2.0.0",
    date: "February 2026",
    tag: "Major",
    features: [
      "ARCHIVE rebuilt from the ground up for BMSIT with a new design system",
      "Introduced the Honor Roll leaderboard and contribution points",
    ],
    improvements: [],
    fixes: [],
  },
];

export function getDepartment(id: string) {
  return departments.find((d) => d.id === id);
}

export function getCourse(id: string) {
  return courses.find((c) => c.id === id);
}

export function getCourseResources(courseId: string) {
  return resources.filter((r) => r.courseId === courseId);
}

export function getResource(id: string) {
  return resources.find((r) => r.id === id);
}
