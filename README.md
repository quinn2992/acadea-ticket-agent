# Acadea Ticket Agent

An AI drafting assistant that interviews Acadea customers and produces a well-structured Zendesk support ticket the customer copy-pastes into Zendesk themselves. Not a submission bot — a quality front door.

## Quick start

```bash
cp .env.example .env.local   # add your ANTHROPIC_API_KEY
npm install
npm run dev                  # http://localhost:3000
```

Deploy to Vercel: see [DEPLOY.md](DEPLOY.md).

## Repo layout

- `app/` — Next.js 15 App Router. Chat UI at `/`, streaming endpoint at `/api/chat`.
- `lib/system-prompt.ts` — loads and concatenates the knowledge pack at first request, caches in process memory.
- `knowledge_pack/` — the 8 markdown files that are concatenated into the system prompt. This is the production prompt; edit with care (any byte-level change invalidates prompt cache on next request).
- `knowledge_source/` — the analytical groundwork doc the knowledge pack was distilled from. Not loaded at runtime; reference only.
- `analysis/` — Python scripts that surfaced patterns across the 848 historical tickets, with their JSON outputs. Not loaded at runtime.
- `source_materials/` — primary inputs (SOP, meeting transcripts, three ticket JSON datasets, Maverick template). Private — do not publish.

## Architecture

- No fine-tuning, no vector DB, no RAG. Knowledge pack is concatenated into the system prompt on every request (Karpathy LLM-wiki pattern, minus the compile/sync machinery).
- The static knowledge-pack prefix is marked `cache_control: { type: "ephemeral" }`, so the second and subsequent requests within a 5-minute window pay ~0.1× input price for the prefix. See [DEPLOY.md §Caching verification](DEPLOY.md).
- Model: `claude-sonnet-4-6` by default. Override via `CLAUDE_MODEL` env var.
- Streaming via `client.messages.stream()` — tokens arrive at the browser as plain text over a Node response stream.

## North Star

Write the ticket a customer *would* have written if Kali (Acadea's ops/support lead) were sitting next to them asking the right questions. Current best tickets are training data, not a ceiling.

## Commands

| Command | Does |
|---|---|
| `npm run dev` | Dev server on :3000 |
| `npm run build` | Production build |
| `npm run start` | Serve the production build |
| `npm run typecheck` | TypeScript check, no emit |
