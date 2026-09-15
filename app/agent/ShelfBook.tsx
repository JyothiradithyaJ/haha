import { useRef, useState } from "react";

export default function UploadDropzone({
  onFiles,
}: {
  onFiles?: (files: File[]) => void;
}) {
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFiles(list: FileList | null) {
    if (!list) return;
    const arr = Array.from(list);
    setFiles(arr);
    onFiles?.(arr);
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={`flex flex-col items-center justify-center rounded-[8px] border-2 border-dashed px-6 py-10 text-center transition-colors ${
        dragging ? "border-oxblood bg-oxblood-tint" : "border-line-strong bg-paper"
      }`}
    >
      <div className="flex h-11 w-11 items-center justify-center rounded-full border border-line bg-card">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M12 16V4M12 4L7 9M12 4L17 9" stroke="#7A2E2A" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M4 16V18C4 19.1 4.9 20 6 20H18C19.1 20 20 19.1 20 18V16" stroke="#7A2E2A" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      </div>
      <p className="mt-4 text-[14.5px] font-medium text-ink">
        Drag & drop your file here
      </p>
      <p className="mt-1 text-[12.5px] text-ink-faint">
        PDF, PPTX, DOCX, ZIP up to 50MB
      </p>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="mt-4 rounded-[5px] border border-line bg-card px-4 py-2 text-[13.5px] font-medium text-ink transition-colors hover:border-line-strong"
      >
        Browse Files
      </button>
      <input
        ref={inputRef}
        type="file"
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {files.length > 0 && (
        <ul className="mt-4 w-full space-y-1.5 text-left">
          {files.map((f, i) => (
            <li
              key={i}
              className="flex items-center justify-between rounded-[5px] border border-line bg-card px-3 py-2 text-[12.5px] text-ink-soft"
            >
              <span className="truncate">{f.name}</span>
              <span className="shrink-0 text-ink-faint">
                {(f.size / (1024 * 1024)).toFixed(1)} MB
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
