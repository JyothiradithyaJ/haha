export type ResourceType = "notes" | "past-paper" | "extras" | "reference";

export const RESOURCE_TYPE_LABEL: Record<ResourceType, string> = {
  notes: "Notes",
  "past-paper": "Past Papers",
  extras: "Extras",
  reference: "References",
};

export interface Department {
  id: string;
  name: string;
  short: string;
  courseCount: number;
}

export interface Course {
  id: string;
  title: string;
  departmentId: string;
  semester: number;
  resourceCount: number;
}

export interface Resource {
  id: string;
  title: string;
  courseId: string;
  type: ResourceType;
  academicYear: string;
  semester: number;
  fileType: "PDF" | "DOCX" | "PPTX" | "ZIP" | "Link";
  fileSizeMb: number;
  contributor: string;
  uploadDate: string;
  upvotes: number;
  link?: string;
}

export interface Contributor {
  id: string;
  name: string;
  branch: string;
  contributions: number;
  points: number;
  pastPapers: number;
  notes: number;
  extras: number;
  reference: number;
  upvotes: number;
}

export interface Release {
  version: string;
  date: string;
  tag: "Major" | "Minor" | "Patch";
  features: string[];
  improvements: string[];
  fixes: string[];
}
