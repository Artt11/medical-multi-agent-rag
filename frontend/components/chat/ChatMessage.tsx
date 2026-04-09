"use client";

import { Message } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Markdown } from "@/components/chat/Markdown";
import { Stethoscope } from "lucide-react";

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full animate-fade-up gap-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600 shadow-sm border border-blue-100">
          <Stethoscope className="h-4 w-4" />
        </div>
      )}
      <div className={cn("flex flex-col gap-2 max-w-[75%]", isUser && "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-5 py-3.5 text-[0.95rem] leading-relaxed shadow-sm",
            isUser
              ? "rounded-tr-sm bg-blue-600 text-white"
              : "rounded-tl-sm border border-slate-200 bg-white text-slate-900"
          )}
        >
          {message.role === "assistant" ? (
            <Markdown content={message.content || ""} />
          ) : (
            <p className="whitespace-pre-wrap">{message.content}</p>
          )}
        </div>
        {!isUser && message.content && (
          <div className="flex flex-wrap gap-2 mt-1">
            <span className="inline-flex cursor-pointer items-center rounded-md border border-slate-200 bg-white px-2.5 py-1 text-[0.7rem] font-medium text-slate-500 shadow-sm transition-colors hover:bg-slate-50 hover:text-blue-600 hover:border-blue-200">
              Source: Formularies & Guidelines
            </span>
            <span className="inline-flex cursor-pointer items-center rounded-md border border-slate-200 bg-white px-2.5 py-1 text-[0.7rem] font-medium text-slate-500 shadow-sm transition-colors hover:bg-slate-50 hover:text-blue-600 hover:border-blue-200">
              Source: EHR Database
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
