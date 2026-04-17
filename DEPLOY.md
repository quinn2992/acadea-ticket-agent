# Deploy & Run

## Local dev

1. Drop your Anthropic key into `.env.local` at the repo root:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
2. Start the dev server:
   ```
   npm run dev
   ```
3. Open http://localhost:3000.

The knowledge pack is loaded from disk at first request and cached for the life of the process. If you edit `knowledge_pack/*.md`, restart the dev server to pick up changes.

## Deploy to Vercel

Prereqs: Vercel account, Vercel CLI (`npm i -g vercel`), a private GitHub repo.

1. `vercel link` from the project root — link to a new or existing project.
2. Add the secret:
   ```
   vercel env add ANTHROPIC_API_KEY production
   ```
   Paste the key when prompted. Repeat for `preview` and `development` if you want previews to work.
3. `vercel --prod` to deploy.

Deploy is static page + one serverless function (`/api/chat`). The function's `maxDuration` is set to 60 seconds in [app/api/chat/route.ts](app/api/chat/route.ts) — increase if you hit timeouts on long conversations. Hobby plan caps at 60s; Pro at 300s.

## Caching verification

Every successful chat response ends with a sentinel line containing token usage:

```
__usage:{"input_tokens":...,"output_tokens":...,"cache_creation_input_tokens":...,"cache_read_input_tokens":...}
```

The client strips this before displaying. Check the browser devtools Network tab or server logs:

- **First request in a 5-minute window**: expect `cache_creation_input_tokens` ≈ size of system prompt (roughly 10K tokens), `cache_read_input_tokens` = 0. This is the cache write — costs 1.25× for 5-minute TTL.
- **Subsequent requests**: expect `cache_read_input_tokens` ≈ 10K, `cache_creation_input_tokens` = 0. This is the cache hit — costs 0.1×.
- **If `cache_read_input_tokens` stays 0 across requests**: a silent invalidator snuck in. Check you haven't added a timestamp or per-request ID to the knowledge pack assembly.

## Editing the knowledge pack

Files in `knowledge_pack/` are the agent's working memory. Order is fixed in [lib/system-prompt.ts](lib/system-prompt.ts). Any edit invalidates the prompt cache on the next request — so batch knowledge-pack changes.

## Cost envelope (rough)

- Sonnet 4.6 input: $3 / 1M tokens uncached; $0.30 / 1M cache read; $3.75 / 1M cache write.
- Sonnet 4.6 output: $15 / 1M tokens.
- Our knowledge pack is ~10K tokens. An average chat of 5 user turns + 5 assistant turns at ~500 tokens each = ~5K output tokens + ~10K cached input per turn = ~$0.08/conversation once cache is warm.
- First conversation of a 5-minute window pays the cache write premium: ~$0.10/conversation.
- At 100 conversations/day: ~$8/day ≈ $240/month. At 1,000/day: ~$80/day.

These are ceilings — most conversations will be shorter.

## Troubleshooting

- **"ANTHROPIC_API_KEY not configured on the server"** — the env var isn't set. Check `vercel env ls`.
- **Response cuts off mid-sentence** — hitting `max_tokens` (currently 4096). Raise in [app/api/chat/route.ts](app/api/chat/route.ts).
- **Typecheck or build fails after editing** — run `npm run typecheck` for cleaner errors than the build output.
- **Stream hangs with nothing appearing** — the dev server is not streaming; check the Network tab. If it's behind a proxy that buffers, the `X-Accel-Buffering: no` header handles nginx; you may need to configure your proxy.
