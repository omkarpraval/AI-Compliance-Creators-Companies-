import React from "react";
import { X, Keyboard } from "lucide-react";
import { Button } from "@/components/ui/Button";

export interface KeyboardShortcutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KeyboardShortcutModal: React.FC<KeyboardShortcutModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const shortcuts = [
    { key: "Space", desc: "Play / Pause playback" },
    { key: "← / →", desc: "Seek backward / forward 5 seconds" },
    { key: "Shift + ← / →", desc: "Step frame backward / forward (50ms)" },
    { key: "J / K / L", desc: "Shuttle rewind / pause / fast-forward" },
    { key: "↑ / ↓", desc: "Navigate next / previous contract clause" },
    { key: "F", desc: "Toggle video stage fullscreen" },
    { key: "O", desc: "Open verdict override dialog (Admin)" },
    { key: "?", desc: "Toggle this keyboard shortcuts sheet" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4 animate-in fade-in duration-[var(--dur-fast)]">
      <div className="w-full max-w-md bg-[var(--ev-surface)] text-[var(--ev-text)] rounded-[var(--r-lg)] border border-[var(--ev-line)] shadow-[var(--sh-modal)] overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--ev-line)] bg-[var(--ev-raised)]">
          <div className="flex items-center gap-2">
            <Keyboard className="w-5 h-5 text-[var(--brand)]" />
            <h3 className="font-semibold text-sm">Evidence Timeline Shortcuts</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-[var(--ev-text-muted)] hover:text-white cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6 divide-y divide-[var(--ev-line)]/60 text-xs">
          {shortcuts.map((s, idx) => (
            <div key={idx} className="flex items-center justify-between py-2">
              <span className="text-[var(--ev-text-muted)]">{s.desc}</span>
              <kbd className="px-2 py-0.5 bg-[var(--ev-bg)] border border-[var(--ev-line-strong)] text-[var(--brand-hover)] font-mono-tabular font-bold rounded-[var(--r-xs)] shadow-xs">
                {s.key}
              </kbd>
            </div>
          ))}
        </div>

        <div className="px-6 py-3 bg-[var(--ev-raised)] border-t border-[var(--ev-line)] flex justify-end">
          <Button variant="primary" size="sm" onClick={onClose}>
            Got It
          </Button>
        </div>
      </div>
    </div>
  );
};
