import Anthropic from "@anthropic-ai/sdk";
import { getSystemPrompt } from "@/lib/system-prompt";

export const runtime = "nodejs";
// Streaming responses need more than the 10s default on the Vercel Hobby plan.
// 60s covers all reasonable drafting flows; increase if longer conversations time out.
export const maxDuration = 60;

const MODEL = process.env.CLAUDE_MODEL ?? "claude-sonnet-4-6";

type Role = "user" | "assistant";
interface IncomingMessage {
  role: Role;
  content: string;
}
interface ChatRequestBody {
  messages: IncomingMessage[];
}

function validateMessages(messages: unknown): IncomingMessage[] {
  if (!Array.isArray(messages)) {
    throw new Error("messages must be an array");
  }
  const out: IncomingMessage[] = [];
  for (const m of messages) {
    if (!m || typeof m !== "object") {
      throw new Error("each message must be an object");
    }
    const role = (m as { role?: unknown }).role;
    const content = (m as { content?: unknown }).content;
    if (role !== "user" && role !== "assistant") {
      throw new Error(`invalid role: ${String(role)}`);
    }
    if (typeof content !== "string") {
      throw new Error("message content must be a string");
    }
    out.push({ role, content });
  }
  if (out.length === 0) {
    throw new Error("messages must not be empty");
  }
  if (out[0].role !== "user") {
    throw new Error("first message must be from the user");
  }
  return out;
}

export async function POST(req: Request) {
  let body: ChatRequestBody;
  try {
    body = (await req.json()) as ChatRequestBody;
  } catch {
    return new Response("invalid JSON body", { status: 400 });
  }

  let messages: IncomingMessage[];
  try {
    messages = validateMessages(body.messages);
  } catch (e) {
    return new Response(e instanceof Error ? e.message : "invalid request", {
      status: 400,
    });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return new Response("ANTHROPIC_API_KEY not configured on the server", {
      status: 500,
    });
  }

  const client = new Anthropic();
  const systemPrompt = getSystemPrompt();

  // Stream tokens back as plain text. The client concatenates chunks as they arrive.
  // Prompt caching: the `cache_control` on the system block caches the knowledge pack
  // prefix. Rendering order is tools → system → messages, and we have no tools, so
  // the cache key covers just system. Verify hits via response.usage on
  // `message_stop` — see README §Caching verification.
  const stream = client.messages.stream({
    model: MODEL,
    max_tokens: 4096,
    system: [
      {
        type: "text",
        text: systemPrompt,
        cache_control: { type: "ephemeral" },
      },
    ],
    messages,
  });

  const encoder = new TextEncoder();
  const responseStream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        stream.on("text", (delta) => {
          controller.enqueue(encoder.encode(delta));
        });
        const finalMessage = await stream.finalMessage();
        // Emit a final newline and usage telemetry on a trailing line the UI
        // will ignore by default. Prefixed with a sentinel so clients that
        // want it can parse it and clients that don't can drop everything
        // after \n\n__usage:.
        const usage = finalMessage.usage;
        const usageLine = `\n\n__usage:${JSON.stringify({
          input_tokens: usage.input_tokens,
          output_tokens: usage.output_tokens,
          cache_creation_input_tokens: usage.cache_creation_input_tokens,
          cache_read_input_tokens: usage.cache_read_input_tokens,
        })}`;
        controller.enqueue(encoder.encode(usageLine));
        controller.close();
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        controller.enqueue(encoder.encode(`\n\n__error:${msg}`));
        controller.close();
      }
    },
  });

  return new Response(responseStream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      "X-Accel-Buffering": "no",
    },
  });
}
