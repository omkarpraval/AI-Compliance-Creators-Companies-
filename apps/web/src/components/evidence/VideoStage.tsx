import React, { useRef, useEffect } from "react";
import ReactPlayer from "react-player";
import { Maximize2, Pause, Play, RotateCcw, RotateCw, Volume2, VolumeX } from "lucide-react";
import type { EvidenceItem } from "@shared/index";
import { formatTimecode } from "@/lib/formatters";

export interface VideoStageProps {
  videoUrl: string;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  activeEvidence: EvidenceItem | null;
  onPlayPause: () => void;
  onSeek: (seconds: number) => void;
  onDurationChange: (duration: number) => void;
  onTimeUpdate: (seconds: number) => void;
}

export const VideoStage: React.FC<VideoStageProps> = ({
  videoUrl,
  isPlaying,
  currentTime,
  duration,
  activeEvidence,
  onPlayPause,
  onSeek,
  onDurationChange,
  onTimeUpdate,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<ReactPlayer>(null);
  const [muted, setMuted] = React.useState(true);

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  };

  // Determine active visual bounding box
  const hasVisualDetection =
    activeEvidence &&
    activeEvidence.type === "visual_detection" &&
    activeEvidence.payload?.bbox &&
    currentTime * 1000 >= activeEvidence.start_ms - 200 &&
    currentTime * 1000 <= activeEvidence.end_ms + 200;

  const bbox = hasVisualDetection ? activeEvidence.payload.bbox : null;

  return (
    <div
      ref={containerRef}
      className="relative w-full flex flex-col items-center justify-center bg-[var(--ev-bg)] rounded-[var(--r-lg)] border border-[var(--ev-line)] overflow-hidden shadow-md"
    >
      {/* 16:9 Video Canvas Stage */}
      <div className="relative w-full aspect-video bg-black flex items-center justify-center overflow-hidden">
        {videoUrl ? (
          <ReactPlayer
            ref={playerRef}
            url={videoUrl}
            playing={isPlaying}
            muted={muted}
            width="100%"
            height="100%"
            controls={false}
            onDuration={onDurationChange}
            onProgress={({ playedSeconds }) => onTimeUpdate(playedSeconds)}
            progressInterval={50}
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-[var(--ev-text-muted)] text-xs">
            <span>Video footage not loaded</span>
          </div>
        )}

        {/* Animated Bounding Box Overlay */}
        {bbox && (
          <div
            className="absolute border-2 border-[var(--brand)] bg-[var(--brand)]/15 rounded-[var(--r-xs)] transition-all duration-[var(--dur-fast)] pointer-events-none animate-in fade-in zoom-in-95"
            style={{
              left: `${bbox.x * 100}%`,
              top: `${bbox.y * 100}%`,
              width: `${bbox.w * 100}%`,
              height: `${bbox.h * 100}%`,
            }}
          >
            <div className="absolute -top-5 left-0 px-1.5 py-0.5 bg-[var(--brand)] text-white text-[10px] font-mono-tabular font-semibold rounded-[var(--r-xs)] whitespace-nowrap shadow-xs">
              {activeEvidence?.payload?.label || "Detected Target"}
            </div>
          </div>
        )}

        {/* OCR Text Banner Overlay */}
        {activeEvidence &&
          activeEvidence.type === "ocr_text" &&
          currentTime * 1000 >= activeEvidence.start_ms &&
          currentTime * 1000 <= activeEvidence.end_ms && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/85 border border-[var(--brand)] text-[var(--ev-text)] text-xs font-mono-tabular rounded-[var(--r-sm)] shadow-lg animate-in fade-in">
              OCR: <span className="text-[var(--brand-hover)] font-bold">{activeEvidence.payload?.text}</span>
            </div>
          )}
      </div>

      {/* Video Transport Bar */}
      <div className="w-full flex items-center justify-between px-4 py-2 bg-[var(--ev-surface)] border-t border-[var(--ev-line)] select-none">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onSeek(Math.max(0, currentTime - 5))}
            className="p-1.5 text-[var(--ev-text-muted)] hover:text-[var(--ev-text)] hover:bg-[var(--ev-raised)] rounded-[var(--r-xs)] cursor-pointer"
            title="Rewind 5s (←)"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={onPlayPause}
            className="p-2 bg-[var(--brand)] text-white hover:bg-[var(--brand-hover)] active:bg-[var(--brand-press)] rounded-full cursor-pointer shadow-xs"
            title="Play/Pause (Space)"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 translate-x-0.5" />}
          </button>

          <button
            onClick={() => onSeek(Math.min(duration, currentTime + 5))}
            className="p-1.5 text-[var(--ev-text-muted)] hover:text-[var(--ev-text)] hover:bg-[var(--ev-raised)] rounded-[var(--r-xs)] cursor-pointer"
            title="Forward 5s (→)"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          {/* Tabular Timecode */}
          <div className="font-mono-tabular text-xs font-medium text-[var(--ev-text)] ml-2">
            <span className="text-[var(--brand-hover)]">{formatTimecode(currentTime)}</span>
            <span className="text-[var(--ev-text-faint)]"> / {formatTimecode(duration)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setMuted(!muted)}
            className="p-1.5 text-[var(--ev-text-muted)] hover:text-[var(--ev-text)] hover:bg-[var(--ev-raised)] rounded-[var(--r-xs)] cursor-pointer"
            title="Toggle Mute"
          >
            {muted ? <VolumeX className="w-4 h-4 text-[var(--flag)]" /> : <Volume2 className="w-4 h-4" />}
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-1.5 text-[var(--ev-text-muted)] hover:text-[var(--ev-text)] hover:bg-[var(--ev-raised)] rounded-[var(--r-xs)] cursor-pointer"
            title="Fullscreen (F)"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
