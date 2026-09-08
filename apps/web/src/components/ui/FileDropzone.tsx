import React, { useRef, useState } from "react";
import { UploadCloud, CheckCircle, FileVideo, X, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "./Button";

export interface FileDropzoneProps {
  accept?: string;
  maxSizeMb?: number;
  label?: string;
  hint?: string;
  onFileUploaded: (fileKey: string, fileInfo: { name: string; size: number; duration?: number }) => void;
  className?: string;
  isDarkSurface?: boolean;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  accept = "video/mp4,video/quicktime,application/pdf",
  maxSizeMb = 500,
  label = "Upload Contract PDF or Video File",
  hint = "Drag and drop or browse from device (max 500MB)",
  onFileUploaded,
  className = "",
  isDarkSurface = false,
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<{ name: string; size: number; key: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    setError(null);
    if (file.size > maxSizeMb * 1024 * 1024) {
      setError(`File size exceeds maximum allowed size of ${maxSizeMb}MB`);
      return;
    }

    try {
      setIsUploading(true);
      setProgress(30);

      const res = await api.uploadFile(file);
      setProgress(100);

      setUploadedFile({
        name: file.name,
        size: file.size,
        key: res.fileKey,
      });

      onFileUploaded(res.fileKey, {
        name: file.name,
        size: file.size,
        duration: 30.0,
      });
    } catch (err: any) {
      setError(err.message || "Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  const handleClear = () => {
    setUploadedFile(null);
    setProgress(0);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const bgClass = isDarkSurface
    ? isDragActive
      ? "bg-[var(--brand-subtle-d)] border-[var(--brand)]"
      : "bg-[var(--ev-surface)] border-[var(--ev-line)] hover:border-[var(--brand)]"
    : isDragActive
    ? "bg-[var(--brand-subtle)] border-[var(--brand)]"
    : "bg-[var(--doc-surface)] border-[var(--doc-line)] hover:border-[var(--brand)]";

  const textColor = isDarkSurface ? "text-[var(--ev-text)]" : "text-[var(--doc-text)]";
  const textMuted = isDarkSurface ? "text-[var(--ev-text-muted)]" : "text-[var(--doc-text-muted)]";

  return (
    <div className={`w-full ${className}`}>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />

      {uploadedFile ? (
        <div
          className={`flex items-center justify-between p-4 rounded-[var(--r-md)] border border-[var(--pass)]/40 ${
            isDarkSurface ? "bg-[var(--pass-dark)]" : "bg-[var(--pass-subtle)]"
          }`}
        >
          <div className="flex items-center gap-3 overflow-hidden">
            {uploadedFile.name.endsWith(".pdf") ? (
              <FileText className="w-8 h-8 text-[var(--brand)] shrink-0" />
            ) : (
              <FileVideo className="w-8 h-8 text-[var(--pass)] shrink-0" />
            )}
            <div className="overflow-hidden">
              <p className={`text-xs font-semibold truncate ${textColor}`}>{uploadedFile.name}</p>
              <p className="text-[10px] font-mono-tabular text-[var(--pass)]">
                {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready
              </p>
            </div>
          </div>
          <button
            onClick={handleClear}
            className="p-1 rounded-full hover:bg-black/10 cursor-pointer text-[var(--fail)]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex flex-col items-center justify-center p-8 rounded-[var(--r-md)] border-2 border-dashed transition-all duration-[var(--dur-fast)] cursor-pointer text-center select-none ${bgClass}`}
        >
          <div className="p-3 rounded-full bg-[var(--brand-subtle)]/30 mb-3">
            <UploadCloud className="w-8 h-8 text-[var(--brand)]" />
          </div>
          <p className={`text-sm font-semibold ${textColor}`}>{label}</p>
          <p className={`mt-1 text-xs ${textMuted}`}>{hint}</p>

          {isUploading && (
            <div className="w-full max-w-xs mt-4">
              <div className="flex justify-between text-[10px] font-mono-tabular mb-1 text-[var(--brand)]">
                <span>Uploading...</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full h-1.5 bg-[var(--ev-line)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[var(--brand)] transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {error && <p className="mt-2 text-xs font-medium text-[var(--fail)]">{error}</p>}
        </div>
      )}
    </div>
  );
};
