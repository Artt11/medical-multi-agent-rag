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
    <div className="border-t border-slate-200 bg-white/90 px-6 py-4 backdrop-blur">
      <div className="mx-auto flex w-full max-w-3xl items-end gap-3">
        <Textarea
          ref={textareaRef}
          value={value}
          placeholder="Message your assistant..."
          className="max-h-40 resize-none bg-white"
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
          className="h-11 w-11 rounded-full p-0"
          size="icon"
        >
          <SendHorizontal className="h-4 w-4" />
        </Button>
      </div>
      <p className="mx-auto mt-2 w-full max-w-3xl text-xs text-slate-400">
        Press Enter to send, Shift+Enter for a new line.
      </p>
    </div>
  );
}
