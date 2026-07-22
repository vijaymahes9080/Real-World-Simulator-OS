import { useState } from "react";
import { Play, Pause, RotateCcw, SkipBack, SkipForward, Bookmark, Volume2, History, GitBranch } from "lucide-react";

/**
 * Component props for TimeMachineScrubber timeline controls.
 */
interface TimeMachineScrubberProps {
  currentTick: number;
  maxTicks?: number;
  isPlaying: boolean;
  onPlayPause: () => void;
  onStep: (direction: "forward" | "backward") => void;
  onSeek: (tick: number) => void;
  onBookmarkBranch?: (tick: number) => void;
}

/**
 * TimeMachineScrubber enables interactive playback control, rewind, fast-forward, and counterfactual branch point creation.
 */
export default function TimeMachineScrubber({
  currentTick,
  maxTicks = 100,
  isPlaying,
  onPlayPause,
  onStep,
  onSeek,
  onBookmarkBranch
}: TimeMachineScrubberProps) {
  const [bookmarks, setBookmarks] = useState<number[]>([10, 35, 70]);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);

  // Synthesize Web Audio alert sound
  const playAudioCue = (freq = 440, duration = 0.08) => {
    if (!isAudioEnabled) return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {
      // Audio context ignored if blocked by browser policy
    }
  };

  const handleAddBookmark = () => {
    if (!bookmarks.includes(currentTick)) {
      setBookmarks([...bookmarks, currentTick].sort((a, b) => a - b));
      if (onBookmarkBranch) onBookmarkBranch(currentTick);
      playAudioCue(880, 0.15);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-slate-800 shadow-xl flex flex-col gap-3">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-400">
            <History className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white flex items-center gap-2">
              Scenario Time Machine & Storyteller
              <span className="text-[9px] bg-blue-500/20 text-blue-300 font-mono px-1.5 py-0.5 rounded">
                REWINDABLE
              </span>
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAudioEnabled(!isAudioEnabled)}
            className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition ${
              isAudioEnabled
                ? "bg-slate-800 border-slate-700 text-blue-400"
                : "bg-slate-900 border-slate-800 text-gray-500"
            }`}
            title="Toggle Web Audio Cues"
          >
            <Volume2 className="h-3.5 w-3.5" />
          </button>

          <button
            onClick={handleAddBookmark}
            className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <Bookmark className="h-3.5 w-3.5" />
            Branch Point @ Tick #{currentTick}
          </button>
        </div>
      </div>

      {/* Main Scrubber Control Row */}
      <div className="flex items-center gap-4 bg-slate-950/80 p-3 rounded-xl border border-slate-800/80">
        {/* Playback Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => {
              onSeek(0);
              playAudioCue(300);
            }}
            className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-gray-300 transition"
            title="Reset to Tick 0"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => {
              onStep("backward");
              playAudioCue(400);
            }}
            className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-gray-300 transition"
            title="Step Back (-1 Tick)"
          >
            <SkipBack className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => {
              onPlayPause();
              playAudioCue(600);
            }}
            className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition shadow-lg shadow-blue-900/30"
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <button
            onClick={() => {
              onStep("forward");
              playAudioCue(500);
            }}
            className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-gray-300 transition"
            title="Step Forward (+1 Tick)"
          >
            <SkipForward className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Timeline Slider with Bookmarks */}
        <div className="flex-1 flex flex-col gap-1 relative">
          <div className="flex justify-between text-[10px] font-mono text-gray-400">
            <span>TICK 0 (Baseline)</span>
            <span className="text-blue-400 font-bold">CURRENT FRAME: #{currentTick}</span>
            <span>TICK {maxTicks} (Horizon)</span>
          </div>

          <input
            type="range"
            min={0}
            max={maxTicks}
            value={currentTick}
            onChange={(e) => onSeek(Number(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />

          {/* Bookmark indicators on timeline */}
          <div className="relative h-2 w-full">
            {bookmarks.map((bm) => (
              <button
                key={bm}
                onClick={() => onSeek(bm)}
                style={{ left: `${(bm / maxTicks) * 100}%` }}
                className="absolute -top-1 -ml-1 w-2 h-3 bg-amber-400 rounded-sm hover:scale-125 transition"
                title={`Jump to Counterfactual Branch #${bm}`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Bookmarked Counterfactual Branches */}
      {bookmarks.length > 0 && (
        <div className="flex items-center gap-2 pt-1">
          <GitBranch className="h-3.5 w-3.5 text-amber-400" />
          <span className="text-[11px] font-mono text-gray-400">Counterfactual Branches:</span>
          <div className="flex gap-1.5 flex-wrap">
            {bookmarks.map((bm) => (
              <button
                key={bm}
                onClick={() => onSeek(bm)}
                className={`px-2 py-0.5 rounded text-[10px] font-mono border transition ${
                  currentTick === bm
                    ? "bg-amber-500/20 text-amber-300 border-amber-500/50 font-bold"
                    : "bg-slate-900 border-slate-800 text-gray-400 hover:text-white"
                }`}
              >
                Branch #{bm}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
