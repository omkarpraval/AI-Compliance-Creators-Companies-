import React, { useState, useEffect, useRef } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { ChevronLeft, ChevronRight, AlertCircle, FileText, ZoomIn, ZoomOut } from "lucide-react";
import { Button } from "@/components/ui/Button";

// Configure pdfjs worker
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export interface HighlightBbox {
  page: number;
  x0: number; // 0.0 to 1.0
  top: number;
  x1: number;
  bottom: number;
  score?: number;
}

export interface PdfViewerProps {
  fileUrl: string;
  targetPage?: number;
  highlightBbox?: HighlightBbox | null;
  isScanned?: boolean;
  className?: string;
}

export const PdfViewer: React.FC<PdfViewerProps> = ({
  fileUrl,
  targetPage = 1,
  highlightBbox,
  isScanned = false,
  className = "",
}) => {
  const [numPages, setNumPages] = useState<number>(1);
  const [currentPage, setCurrentPage] = useState<number>(targetPage);
  const [scale, setScale] = useState<number>(1.0);
  const highlightRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Jump to target page when requested by focused clause
  useEffect(() => {
    if (targetPage && targetPage >= 1 && targetPage <= numPages) {
      setCurrentPage(targetPage);
    }
  }, [targetPage, numPages]);

  // If a highlight bbox is targeted on a different page, jump there
  useEffect(() => {
    if (highlightBbox?.page && highlightBbox.page !== currentPage) {
      setCurrentPage(highlightBbox.page);
    }
  }, [highlightBbox]);

  // Smooth scroll highlight into view
  useEffect(() => {
    if (highlightRef.current && containerRef.current) {
      const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      highlightRef.current.scrollIntoView({
        behavior: prefersReducedMotion ? "auto" : "smooth",
        block: "center",
      });
    }
  }, [highlightBbox, currentPage]);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    if (targetPage <= numPages) {
      setCurrentPage(targetPage);
    }
  };

  const isCurrentPageHighlighted = highlightBbox && highlightBbox.page === currentPage;

  return (
    <div
      ref={containerRef}
      className={`flex flex-col h-full bg-[var(--doc-bg)] rounded-[var(--r-md)] border border-[var(--doc-line)] overflow-hidden shadow-xs ${className}`}
    >
      {/* Viewer Control Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[var(--doc-surface)] border-b border-[var(--doc-line)] text-xs select-none">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[var(--brand)]" />
          <span className="font-semibold text-[var(--doc-text)]">Contract PDF Viewer</span>
        </div>

        {/* Page Nav & Zoom */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="p-1 rounded hover:bg-[var(--doc-bg)] disabled:opacity-40 cursor-pointer text-[var(--doc-text)]"
              title="Previous Page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-xs text-[var(--doc-text-muted)]">
              Page <strong className="text-[var(--doc-text)]">{currentPage}</strong> of {numPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(numPages, p + 1))}
              disabled={currentPage >= numPages}
              className="p-1 rounded hover:bg-[var(--doc-bg)] disabled:opacity-40 cursor-pointer text-[var(--doc-text)]"
              title="Next Page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="h-4 w-[1px] bg-[var(--doc-line)]" />

          <div className="flex items-center gap-1">
            <button
              onClick={() => setScale((s) => Math.max(0.7, s - 0.15))}
              className="p-1 rounded hover:bg-[var(--doc-bg)] cursor-pointer text-[var(--doc-text-muted)]"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] text-[var(--doc-text-muted)]">{Math.round(scale * 100)}%</span>
            <button
              onClick={() => setScale((s) => Math.min(1.6, s + 0.15))}
              className="p-1 rounded hover:bg-[var(--doc-bg)] cursor-pointer text-[var(--doc-text-muted)]"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Scanned / No Coordinates Notice Banner */}
      {isScanned && (
        <div className="px-4 py-2 bg-amber-50 border-b border-amber-200 text-amber-900 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>This contract was read from a scan, so exact sentence positions are not available.</span>
        </div>
      )}

      {/* Main PDF Canvas Pane with Overlay Highlights */}
      <div className="flex-1 overflow-auto p-4 flex justify-center items-start custom-scrollbar bg-gray-100/60">
        <div className="relative shadow-md rounded-[var(--r-xs)] bg-white overflow-hidden">
          <Document
            file={fileUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="p-12 text-center text-xs text-[var(--doc-text-muted)] font-mono">
                Loading contract pages...
              </div>
            }
            error={
              <div className="p-8 text-center text-xs text-[var(--fail)] font-mono">
                Failed to load PDF preview. Falling back to document text pane.
              </div>
            }
          >
            <Page
              pageNumber={currentPage}
              scale={scale}
              renderTextLayer={false}
              renderAnnotationLayer={false}
              className="relative"
            />
          </Document>

          {/* Coordinate Bounding Box Highlight Overlay */}
          {isCurrentPageHighlighted && highlightBbox && (
            <div
              ref={highlightRef}
              className="absolute pointer-events-none transition-all duration-[var(--dur-fast)] rounded-[var(--r-xs)]"
              style={{
                left: `${highlightBbox.x0 * 100}%`,
                top: `${highlightBbox.top * 100}%`,
                width: `${Math.max(2, (highlightBbox.x1 - highlightBbox.x0) * 100)}%`,
                height: `${Math.max(1.5, (highlightBbox.bottom - highlightBbox.top) * 100)}%`,
                backgroundColor: "rgba(107, 78, 255, 0.18)",
                border: "2px solid var(--brand)",
                boxShadow: "0 0 0 1px rgba(107, 78, 255, 0.2)",
              }}
            >
              <span className="absolute -top-5 left-0 px-1.5 py-0.2 bg-[var(--brand)] text-white text-[9px] font-mono font-bold rounded-[var(--r-xs)] whitespace-nowrap shadow-xs">
                Highlighted Clause
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
