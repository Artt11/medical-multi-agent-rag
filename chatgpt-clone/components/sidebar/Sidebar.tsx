"use client";

import { Plus, Sparkles } from "lucide-react";

import { Conversation } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

export function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelect
}: {
  conversations: Conversation[];
  activeId: string | null;
  onNewChat: () => void;
  onSelect: (id: string) => void;
}) {
  return (
    <aside className="flex h-screen w-[260px] flex-col border-r border-slate-900/40 bg-[#0f172a] text-slate-100">
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Chat UI</p>
          <p className="text-lg font-semibold">Nimbus</p>
        </div>
      </div>

      <div className="px-5">
        <Button
          variant="secondary"
          className="w-full justify-start gap-2 bg-white/10 text-slate-100 hover:bg-white/20"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <div className="mt-6 flex-1 overflow-hidden">
        <ScrollArea className="h-full px-3">
          <div className="space-y-2 pb-6">
            <p className="px-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Conversations
            </p>
            {conversations.length === 0 ? (
              <p className="px-2 text-sm text-slate-500">
                No chats yet. Start a new conversation.
              </p>
            ) : (
              conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => onSelect(conversation.id)}
                  className={cn(
                    "w-full rounded-xl px-3 py-2 text-left text-sm transition-colors",
                    conversation.id === activeId
                      ? "bg-white/15 text-white"
                      : "text-slate-300 hover:bg-white/10"
                  )}
                >
                  <p className="truncate">{conversation.title}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {new Date(conversation.updatedAt).toLocaleDateString()}
                  </p>
                </button>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </aside>
  );
}
