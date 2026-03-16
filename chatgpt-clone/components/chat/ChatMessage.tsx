"use client";

import { Message } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Markdown } from "@/components/chat/Markdown";

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full animate-fade-up",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[72%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-soft",
          isUser
            ? "bg-slate-900 text-white"
            : "border border-slate-200 bg-white text-slate-900"
        )}
      >
        {message.role === "assistant" ? (
          <Markdown content={message.content || ""} />
        ) : (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}
      </div>
    </div>
  );
}
