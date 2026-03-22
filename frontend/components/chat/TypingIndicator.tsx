"use client";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 text-slate-500">
      <span className="h-2 w-2 rounded-full bg-slate-400 animate-pulse-soft" />
      <span className="h-2 w-2 rounded-full bg-slate-400 animate-pulse-soft [animation-delay:0.2s]" />
      <span className="h-2 w-2 rounded-full bg-slate-400 animate-pulse-soft [animation-delay:0.4s]" />
      <span className="text-xs uppercase tracking-[0.2em]">Thinking</span>
    </div>
  );
}
