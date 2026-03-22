# Nimbus Chat

A production-ready ChatGPT-style web app built with Next.js (App Router), TypeScript, TailwindCSS, and shadcn UI components. It includes a streaming chat API, conversation switching, markdown rendering, and a polished sidebar + chat layout.

## Features
- UI with sidebar + chat area
- Streaming responses (when the provider supports SSE)
- Markdown rendering + code block highlighting
- Copy-to-clipboard for code blocks
- Conversation list with local persistence
- Auto-scroll to newest message
- Smooth animations and responsive layout

## Tech Stack
- Next.js (App Router)
- React + TypeScript
- TailwindCSS
- shadcn UI components

## Getting Started
1. Install dependencies

```bash
npm install
```

2. Configure environment variables

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set your API key + model. Example:

```
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

3. Run the app

```bash
npm run dev
```

Visit `http://localhost:3000`.

## API Details
The backend lives at `app/api/chat/route.ts` and expects:

```json
{
  "messages": [{ "role": "user", "content": "Hello" }]
}
```

The route forwards the request to an OpenAI-compatible API endpoint and streams the response back to the UI.

## Using the Medical Pipeline Backend
If you have the FastAPI backend running in `/Users/admin/Desktop/pdf_parser copy/medical_pipeline`, you can proxy chat requests to it.

1. Make sure the backend is running:
```bash
cd "/Users/admin/Desktop/pdf_parser copy/medical_pipeline"
python main.py
```

2. Set the base URL in `.env.local`:
```
MEDICAL_API_BASE_URL=http://localhost:8000
```

When `MEDICAL_API_BASE_URL` is set, the Next.js API route forwards messages to:
`POST /v1/medical/chat` and returns the `answer` field to the UI.

## Using Other Providers
This project works with any OpenAI-compatible API:
- **Ollama**: set `OPENAI_BASE_URL=http://localhost:11434/v1` and `OPENAI_MODEL=llama3.1`.
- **Other providers**: point `OPENAI_BASE_URL` to their REST base URL and set the correct model.

If your provider does not require an API key, you can leave `OPENAI_API_KEY` empty.

## Project Structure
```
app/
  api/chat/route.ts
  globals.css
  layout.tsx
  page.tsx
components/
  chat/
  sidebar/
  ui/
lib/
  types.ts
  utils.ts
public/
```
