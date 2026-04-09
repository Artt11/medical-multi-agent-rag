"use client";

import { Plus, Activity } from "lucide-react";
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
    <aside className="flex h-screen w-[260px] flex-col border-r border-slate-900/40 bg-[#0f172a] text-slate-100 overflow-hidden">
      {/* Logo Section */}
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600/20 text-blue-400">
          <Activity className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Chat UI</p>
          <p className="text-lg font-semibold text-slate-100">Բժշկական</p>
        </div>
      </div>

      {/* Action Button */}
      <div className="px-5">
        <Button
          className="w-full justify-start gap-2 bg-blue-600 text-white hover:bg-blue-700 shadow-md transition-all"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" />
          Նոր զրույց
        </Button>
      </div>

      {/* Conversations List */}
      <div className="mt-6 flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="px-3 space-y-2 pb-6">
            <p className="px-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              ԶՐՈՒՅՑՆԵՐ
            </p>
            {conversations.length === 0 ? (
              <p className="px-2 text-sm text-slate-500">Զրույցներ դեռ չկան։ Սկսեք նորը։</p>
            ) : (
              conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => onSelect(conversation.id)}
                  /* Օգտագործում ենք grid, որպեսզի truncate-ը հստակ աշխատի */
                  className={cn(
                    "grid grid-cols-1 w-full rounded-xl px-3 py-2 text-left transition-colors overflow-hidden",
                    conversation.id === activeId
                      ? "bg-slate-800 text-white"
                      : "text-slate-300 hover:bg-slate-800/60"
                  )}
                >
                  <span
                    className="truncate block text-sm font-medium w-full"
                    title={conversation.title}
                  >
                    {conversation.title}
                  </span>
                  <span className="mt-1 text-xs text-slate-500 block">
                    {new Date(conversation.updatedAt).toLocaleDateString()}
                  </span>
                </button>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </aside>
  );
}