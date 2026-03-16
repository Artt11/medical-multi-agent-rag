"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function Markdown({ content, className }: { content: string; className?: string }) {
  return (
    <ReactMarkdown
      className={cn("markdown max-w-none", className)}
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
        code({ inline, className, children, ...props }) {
          const raw = String(children ?? "").replace(/\n$/, "");
          if (inline) {
            return (
              <code
                className={cn(
                  "rounded bg-slate-100 px-1 py-0.5 text-[0.85em] text-slate-900",
                  className
                )}
                {...props}
              >
                {children}
              </code>
            );
          }

          return (
            <div className="relative">
              <pre className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-950/95 p-4 text-slate-100 shadow-soft">
                <code className={cn("text-sm", className)} {...props}>
                  {children}
                </code>
              </pre>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                className="absolute right-3 top-3 h-7 rounded-md px-2 text-[11px]"
                onClick={() => navigator.clipboard.writeText(raw)}
              >
                Copy
              </Button>
            </div>
          );
        },
        a({ href, children, ...props }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noreferrer"
              className="text-slate-900 underline decoration-slate-400 underline-offset-4"
              {...props}
            >
              {children}
            </a>
          );
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
