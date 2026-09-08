import React, { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";

export interface AudioWaveformProps {
  currentTime: number;
  duration: number;
  onSeek?: (seconds: number) => void;
  className?: string;
}

export const AudioWaveform: React.FC<AudioWaveformProps> = ({
  currentTime,
  duration,
  onSeek,
  className = "",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const waveSurferRef = useRef<WaveSurfer | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Generate realistic multi-peak waveform data
    const peaksCount = 120;
    const dummyPeaks: number[] = [];
    for (let i = 0; i < peaksCount; i++) {
      // Speech pattern simulation: bursts of high volume followed by breath pauses
      const pattern = Math.sin(i * 0.35) * Math.cos(i * 0.15);
      const rand = Math.random() * 0.4;
      dummyPeaks.push(Math.min(1.0, Math.max(0.1, Math.abs(pattern) + rand)));
    }

    try {
      const ws = WaveSurfer.create({
        container: containerRef.current,
        waveColor: "#3A4759", // --ev-line-strong
        progressColor: "#6B4EFF", // --brand
        cursorColor: "transparent",
        height: 28,
        barWidth: 2,
        barGap: 2,
        barRadius: 2,
        interact: true,
        peaks: [dummyPeaks],
        duration: duration || 30,
      });

      ws.on("interaction", (newTime) => {
        if (onSeek) onSeek(newTime);
      });

      waveSurferRef.current = ws;

      return () => {
        ws.destroy();
      };
    } catch (e) {
      console.warn("WaveSurfer init fallback", e);
    }
  }, [duration]);

  useEffect(() => {
    if (waveSurferRef.current && duration > 0) {
      const progress = Math.min(Math.max(currentTime / duration, 0), 1);
      waveSurferRef.current.seekTo(progress);
    }
  }, [currentTime, duration]);

  return (
    <div className={`w-full relative h-7 bg-[var(--ev-bg)] rounded-[var(--r-xs)] overflow-hidden ${className}`}>
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
};
