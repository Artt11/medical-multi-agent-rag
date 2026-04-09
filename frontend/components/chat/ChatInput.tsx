"use client";

import { useEffect, useRef, useState } from "react";
import { SendHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export function ChatInput({
  onSend,
  disabled
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <div className="bg-gradient-to-t from-slate-50 to-transparent pb-6 pt-2 px-6">
      <div className="mx-auto flex w-full max-w-3xl flex-col items-center gap-3">
        <div className="flex w-full items-end gap-2 rounded-3xl border border-slate-200 bg-white/80 backdrop-blur-md px-3 py-2 shadow-lg focus-within:ring-2 focus-within:ring-blue-500/50 transition-all">
          <Textarea
            ref={textareaRef}
            value={value}
            placeholder="Տվեք բժշկական հարց..."
            className="max-h-40 min-h-[44px] resize-none border-0 bg-transparent px-3 py-2.5 text-[0.95rem] shadow-none focus-visible:ring-0 leading-relaxed"
            rows={1}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSend();
              }
            }}
          />
          <Button
            type="button"
            onClick={handleSend}
            disabled={disabled || value.trim().length === 0}
            className="mb-1 h-10 w-10 shrink-0 rounded-full bg-blue-600 p-0 text-white shadow-sm hover:bg-blue-700 transition-colors disabled:opacity-50"
            size="icon"
          >
            <SendHorizontal className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-slate-400">
          Բժշկական AI-ը կարող է սխալվել։ Ստուգեք կարևոր կլինիկական տեղեկությունները։
        </p>
      </div>
    </div>
  );
}
