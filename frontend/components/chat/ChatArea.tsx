"use client";

import { useEffect, useRef, type ReactNode } from "react";

import { Message } from "@/lib/types";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { TypingIndicator } from "@/components/chat/TypingIndicator";

export function ChatArea({
  messages,
  isStreaming,
  emptyState
}: {
  messages: Message[];
  isStreaming: boolean;
  emptyState: ReactNode;
}) {
  const endRef = useRef<HTMLDivElement | null>(null);
  const visibleMessages = messages.filter(
    (message) => message.role === "user" || message.content.trim().length > 0
  );

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, isStreaming]);

  return (
    <div className="flex-1 overflow-y-auto scroll-smooth px-6 py-8">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        {messages.length === 0 ? (
          <div className="py-10">{emptyState}</div>
        ) : (
          visibleMessages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        {isStreaming && messages.length > 0 ? (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-soft">
              <TypingIndicator />
            </div>
          </div>
        ) : null}
        <div ref={endRef} />
      </div>
    </div>
  );
}
