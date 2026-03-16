"use client";

import { useEffect, useMemo, useState } from "react";
import { Menu } from "lucide-react";

import { ChatArea } from "@/components/chat/ChatArea";
import { ChatInput } from "@/components/chat/ChatInput";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { Button } from "@/components/ui/button";
import type { Conversation, Message } from "@/lib/types";

const STORAGE_KEY = "nimbus:conversations";
const STORAGE_ACTIVE = "nimbus:active";

const createId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

const createConversation = (): Conversation => ({
  id: createId(),
  title: "New Chat",
  messages: [],
  createdAt: Date.now(),
  updatedAt: Date.now()
});

const buildTitle = (text: string) =>
  text.length > 48 ? `${text.slice(0, 48)}...` : text;

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    const stored = localStorage.getItem(STORAGE_KEY);
    const storedActive = localStorage.getItem(STORAGE_ACTIVE);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as Conversation[];
        setConversations(parsed);
        if (storedActive && parsed.some((item) => item.id === storedActive)) {
          setActiveId(storedActive);
        } else if (parsed.length > 0) {
          setActiveId(parsed[0].id);
        }
      } catch {
        setConversations([]);
      }
    }
  }, []);

  useEffect(() => {
    if (!isMounted) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    if (activeId) {
      localStorage.setItem(STORAGE_ACTIVE, activeId);
    }
  }, [conversations, activeId, isMounted]);

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeId) ?? null,
    [conversations, activeId]
  );

  const sortedConversations = useMemo(() => {
    return [...conversations].sort((a, b) => b.updatedAt - a.updatedAt);
  }, [conversations]);

  const upsertConversation = (id: string, updater: (conversation: Conversation) => Conversation) => {
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === id ? updater(conversation) : conversation
      )
    );
  };

  const handleNewChat = () => {
    const fresh = createConversation();
    setConversations((prev) => [fresh, ...prev]);
    setActiveId(fresh.id);
    setIsSidebarOpen(false);
  };

  const handleSelect = (id: string) => {
    setActiveId(id);
    setIsSidebarOpen(false);
  };

  const sendMessage = async (text: string) => {
    if (isStreaming) return;
    let conversation = activeConversation;

    if (!conversation) {
      const fresh = createConversation();
      conversation = fresh;
      setConversations((prev) => [fresh, ...prev]);
      setActiveId(fresh.id);
    }

    const userMessage: Message = {
      id: createId(),
      role: "user",
      content: text
    };

    const assistantMessage: Message = {
      id: createId(),
      role: "assistant",
      content: ""
    };

    const updatedTitle =
      conversation.title === "New Chat" ? buildTitle(text) : conversation.title;

    setConversations((prev) =>
      prev.map((item) =>
        item.id === conversation.id
          ? {
              ...item,
              title: updatedTitle,
              messages: [...item.messages, userMessage, assistantMessage],
              updatedAt: Date.now()
            }
          : item
      )
    );

    setIsStreaming(true);

    const messagesForApi = [...conversation.messages, userMessage].map(
      ({ role, content }) => ({ role, content })
    );

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: messagesForApi })
      });

      if (!response.ok) {
        const errorText = await response.text();
        upsertConversation(conversation.id, (item) => ({
          ...item,
          messages: item.messages.map((message) =>
            message.id === assistantMessage.id
              ? {
                  ...message,
                  content: `Error: ${errorText || response.statusText}`
                }
              : message
          )
        }));
        setIsStreaming(false);
        return;
      }

      const contentType = response.headers.get("content-type") || "";

      if (contentType.includes("application/json")) {
        const data = (await response.json()) as { content?: string };
        upsertConversation(conversation.id, (item) => ({
          ...item,
          messages: item.messages.map((message) =>
            message.id === assistantMessage.id
              ? { ...message, content: data.content ?? "" }
              : message
          ),
          updatedAt: Date.now()
        }));
        setIsStreaming(false);
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response stream available.");
      }

      const decoder = new TextDecoder();
      let done = false;
      let accumulated = "";

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunk = decoder.decode(value || new Uint8Array(), { stream: true });
        if (chunk) {
          accumulated += chunk;
          upsertConversation(conversation.id, (item) => ({
            ...item,
            messages: item.messages.map((message) =>
              message.id === assistantMessage.id
                ? { ...message, content: accumulated }
                : message
            )
          }));
        }
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unexpected error occurred.";
      upsertConversation(conversation.id, (item) => ({
        ...item,
        messages: item.messages.map((msg) =>
          msg.id === assistantMessage.id
            ? { ...msg, content: `Error: ${message}` }
            : msg
        )
      }));
    } finally {
      setIsStreaming(false);
    }
  };

  const emptyState = (
    <div className="rounded-3xl border border-slate-200 bg-white/80 p-8 shadow-soft">
      <p className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">
        Nimbus Assistant
      </p>
      <h1 className="mt-4 text-3xl font-semibold text-slate-900">
        Build clarity, one prompt at a time.
      </h1>
      <p className="mt-3 text-sm text-slate-500">
        Ask for code help, strategy, or simply start a new conversation.
      </p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {[
          "Draft a product brief for a mobile analytics tool.",
          "Summarize a PRD and call out missing requirements.",
          "Generate a React component checklist.",
          "Explain a complex bug in plain English."
        ].map((example) => (
          <Button
            key={example}
            variant="outline"
            className="justify-start text-left"
            onClick={() => sendMessage(example)}
            disabled={isStreaming}
          >
            {example}
          </Button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <div className="hidden md:flex">
        <Sidebar
          conversations={sortedConversations}
          activeId={activeId}
          onNewChat={handleNewChat}
          onSelect={handleSelect}
        />
      </div>
      {isSidebarOpen ? (
        <div className="fixed inset-0 z-40 md:hidden">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setIsSidebarOpen(false)}
          />
          <div className="relative z-50 h-full">
            <Sidebar
              conversations={sortedConversations}
              activeId={activeId}
              onNewChat={handleNewChat}
              onSelect={handleSelect}
            />
          </div>
        </div>
      ) : null}
      <div className="flex flex-1 flex-col">
        <div className="flex items-center justify-between border-b border-slate-200 bg-white/90 px-4 py-3 md:hidden">
          <button
            type="button"
            className="rounded-lg border border-slate-200 p-2"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="h-4 w-4" />
          </button>
          <p className="text-sm font-semibold text-slate-700">Nimbus</p>
          <span className="h-8 w-8" />
        </div>
        <ChatArea
          messages={activeConversation?.messages ?? []}
          isStreaming={isStreaming}
          emptyState={emptyState}
        />
        <ChatInput onSend={sendMessage} disabled={isStreaming} />
      </div>
    </div>
  );
}
