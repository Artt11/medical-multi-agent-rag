import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const DEFAULT_BASE_URL = "https://api.openai.com/v1";

function buildError(message: string, status = 500) {
  return NextResponse.json({ error: message }, { status });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const messages = Array.isArray(body?.messages) ? body.messages : null;

    if (!messages) {
      return buildError("Invalid request: messages array is required.", 400);
    }

    const medicalBaseUrl = (process.env.MEDICAL_API_BASE_URL || "").trim();
    if (medicalBaseUrl) {
      const lastUser = [...messages].reverse().find((message) => message?.role === "user");
      if (!lastUser?.content) {
        return buildError("No user message provided.", 400);
      }

      const patientId = body?.patientId ?? body?.patient_id ?? null;
      const upstream = await fetch(
        `${medicalBaseUrl.replace(/\/$/, "")}/v1/medical/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: lastUser.content,
            ...(patientId ? { patient_id: patientId } : {})
          })
        }
      );

      if (!upstream.ok) {
        const errorText = await upstream.text();
        return buildError(errorText || "Medical backend request failed.", upstream.status);
      }

      const data = await upstream.json();
      const content = data?.answer ?? "";
      return NextResponse.json({ content, agentUsed: data?.agent_used ?? null });
    }

    const apiKey = process.env.OPENAI_API_KEY || "";
    const baseUrl = (process.env.OPENAI_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, "");
    const model = process.env.OPENAI_MODEL || "gpt-4o-mini";

    if (!apiKey && baseUrl.includes("api.openai.com")) {
      return buildError("Missing OPENAI_API_KEY for OpenAI requests.", 400);
    }

    const upstream = await fetch(`${baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {})
      },
      body: JSON.stringify({
        model,
        stream: true,
        messages: messages.map((message: { role: string; content: string }) => ({
          role: message.role,
          content: message.content
        }))
      })
    });

    if (!upstream.ok) {
      const errorText = await upstream.text();
      return buildError(errorText || "Upstream request failed.", upstream.status);
    }

    const contentType = upstream.headers.get("content-type") || "";

    if (!contentType.includes("text/event-stream")) {
      const data = await upstream.json();
      const content = data?.choices?.[0]?.message?.content ?? "";
      return NextResponse.json({ content });
    }

    const reader = upstream.body?.getReader();

    if (!reader) {
      return buildError("Upstream response had no body.");
    }

    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    const stream = new ReadableStream({
      async start(controller) {
        let buffer = "";
        let closed = false;
        const close = () => {
          if (!closed) {
            closed = true;
            controller.close();
          }
        };

        try {
          while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              const trimmed = line.trim();
              if (!trimmed.startsWith("data:")) continue;

              const data = trimmed.replace("data:", "").trim();
              if (data === "[DONE]") {
                close();
                return;
              }

              try {
                const json = JSON.parse(data);
                const delta =
                  json?.choices?.[0]?.delta?.content ??
                  json?.choices?.[0]?.message?.content ??
                  "";

                if (delta) {
                  controller.enqueue(encoder.encode(delta));
                }
              } catch {
                // Ignore malformed chunks.
              }
            }
          }
        } catch (error) {
          if (!closed) controller.error(error);
        } finally {
          close();
        }
      }
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
        Connection: "keep-alive"
      }
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return buildError(message);
  }
}
