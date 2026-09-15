import { useState } from "react";
import UploadDropzone from "./UploadDropzone";
import Button from "./Button";
import { Field, Select, TextInput } from "./FormField";
import type { ResourceType } from "../data/types";
import { RESOURCE_TYPE_LABEL } from "../data/types";

const resourceTypeOptions: ResourceType[] = ["notes", "past-paper", "extras", "reference"];

export default function ContributeForm({
  compact = false,
  defaultCourse = "",
  defaultType,
  onSubmitted,
}: {
  compact?: boolean;
  defaultCourse?: string;
  defaultType?: ResourceType;
  onSubmitted?: () => void;
}) {
  const [submitted, setSubmitted] = useState(false);
  const [anonymous, setAnonymous] = useState(false);
  const [type, setType] = useState<ResourceType | "">(defaultType ?? "");
  const isReference = type === "reference";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      onSubmitted?.();
    }, 900);
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center py-10 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-moss-tint">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M5 13L9 17L19 7" stroke="#4B5E45" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <p className="mt-4 font-serif text-[18px] text-ink">Resource queued for review</p>
        <p className="mt-1.5 max-w-xs text-[13.5px] text-ink-soft">
          This is a UI preview — nothing was actually uploaded yet. In the
          full version, moderators verify files before they go live.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {isReference ? (
        <Field label="Link to resource" hint="Paste a link instead of uploading a file">
          <TextInput type="url" placeholder="https://…" required />
        </Field>
      ) : (
        <UploadDropzone />
      )}

      <div className={`grid gap-4 ${compact ? "grid-cols-1" : "grid-cols-1 sm:grid-cols-2"}`}>
        <Field label="Course Name">
          <TextInput placeholder="e.g. Data Structures and Algorithms" defaultValue={defaultCourse} required />
        </Field>
        <Field label="Resource Type">
          <Select
            required
            value={type}
            onChange={(e) => setType(e.target.value as ResourceType)}
          >
            <option value="" disabled>Select a type</option>
            {resourceTypeOptions.map((t) => (
              <option key={t} value={t}>{RESOURCE_TYPE_LABEL[t]}</option>
            ))}
          </Select>
        </Field>
        {!compact && (
          <>
            <Field label="Contributor Name">
              <TextInput placeholder="Your full name" disabled={anonymous} required={!anonymous} />
            </Field>
            <Field label="Roll Number" hint="Only used to award Honor Roll points">
              <TextInput placeholder="e.g. 1BY22CS045" disabled={anonymous} required={!anonymous} />
            </Field>
          </>
        )}
      </div>

      {!compact && (
        <label className="flex items-center gap-2.5 text-[13.5px] text-ink-soft">
          <input
            type="checkbox"
            checked={anonymous}
            onChange={(e) => setAnonymous(e.target.checked)}
            className="h-4 w-4 rounded-sm border-line-strong accent-oxblood"
          />
          Contribute anonymously (you won't appear on the Honor Roll)
        </label>
      )}

      <Button type="submit" className="w-full sm:w-auto">
        Submit Resource
      </Button>
    </form>
  );
}
