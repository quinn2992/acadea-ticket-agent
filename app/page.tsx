"use client";

import { useEffect, useRef, useState } from "react";
import { BASE_PATH } from "@/lib/config";

type Role = "user" | "assistant";
interface Message {
  role: Role;
  content: string;
}

const ZENDESK_BLOCK_RE = /```zendesk\s*\n([\s\S]*?)\n```/g;

function splitAssistantContent(text: string): Array<
  | { kind: "prose"; text: string }
  | { kind: "ticket"; text: string }
> {
  const parts: Array<{ kind: "prose" | "ticket"; text: string }> = [];
  let lastIndex = 0;
  ZENDESK_BLOCK_RE.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = ZENDESK_BLOCK_RE.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ kind: "prose", text: text.slice(lastIndex, match.index) });
    }
    parts.push({ kind: "ticket", text: match[1].trim() });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    parts.push({ kind: "prose", text: text.slice(lastIndex) });
  }
  return parts;
}

function stripUsageSuffix(text: string): string {
  const idx = text.indexOf("\n\n__usage:");
  return idx >= 0 ? text.slice(0, idx) : text;
}

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, streaming]);

  async function send() {
    const trimmed = input.trim();
    if (!trimmed || streaming) return;

    const newMessages: Message[] = [
      ...messages,
      { role: "user", content: trimmed },
    ];
    setMessages(newMessages);
    setInput("");
    setError(null);
    setStreaming(true);

    // Placeholder assistant message we stream into
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${BASE_PATH}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
        signal: controller.signal,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const reader = res.body?.getReader();
      if (!reader) throw new Error("no response body");
      const decoder = new TextDecoder();
      let acc = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        const errIdx = acc.indexOf("\n\n__error:");
        if (errIdx >= 0) {
          throw new Error(acc.slice(errIdx + 10).trim());
        }
        // Update the last (assistant) message with what we've accumulated so far,
        // stripping any usage suffix that may have arrived at the end.
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            role: "assistant",
            content: stripUsageSuffix(acc),
          };
          return next;
        });
      }
    } catch (e) {
      if ((e as Error).name === "AbortError") {
        // user stopped
      } else {
        setError(e instanceof Error ? e.message : String(e));
        setMessages((prev) => prev.slice(0, -1));
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  function stop() {
    abortRef.current?.abort();
  }

  function reset() {
    if (streaming) abortRef.current?.abort();
    setMessages([]);
    setInput("");
    setError(null);
  }

  async function copyTicket(text: string) {
    await navigator.clipboard.writeText(text);
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <div style={styles.brand}>Acadea Ticket Drafter</div>
          <div style={styles.tagline}>
            Interview → draft → copy into Zendesk.
          </div>
        </div>
        <button onClick={reset} style={styles.secondaryButton} disabled={streaming && messages.length === 0}>
          New ticket
        </button>
      </header>

      <div style={styles.scroll} ref={scrollRef}>
        {messages.length === 0 && (
          <div style={styles.empty}>
            <h2 style={{ margin: "0 0 8px 0" }}>What issue do you want to report?</h2>
            <p style={styles.emptyCopy}>
              Describe the problem in your own words. I&apos;ll ask a few follow-ups and hand you a ready-to-paste ticket.
            </p>
            <div style={styles.examples}>
              <b style={{ fontSize: 13, color: "#555" }}>Example starters:</b>
              <ul style={{ margin: "8px 0 0 0", paddingLeft: 18, color: "#555", fontSize: 14 }}>
                <li>The Course Outline Report is pulling historical program drafts.</li>
                <li>We can&apos;t log into the platform — getting a 500 error since this morning.</li>
                <li>Need to add new semester/term entries to the lookup table.</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageRow key={i} message={m} onCopy={copyTicket} />
        ))}
        {error && <div style={styles.error}>{error}</div>}
      </div>

      <div style={styles.composer}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              send();
            }
          }}
          placeholder={
            messages.length === 0
              ? "Describe what's broken or what you need…"
              : "Your reply… (⌘/Ctrl+Enter to send)"
          }
          style={styles.textarea}
          disabled={streaming}
          rows={3}
        />
        <div style={styles.composerActions}>
          <div style={styles.hint}>⌘/Ctrl+Enter to send</div>
          {streaming ? (
            <button onClick={stop} style={styles.stopButton}>
              Stop
            </button>
          ) : (
            <button onClick={send} style={styles.sendButton} disabled={!input.trim()}>
              Send
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function MessageRow({
  message,
  onCopy,
}: {
  message: Message;
  onCopy: (text: string) => void;
}) {
  if (message.role === "user") {
    return (
      <div style={styles.userRow}>
        <div style={styles.userBubble}>{message.content}</div>
      </div>
    );
  }

  const parts = splitAssistantContent(message.content);
  return (
    <div style={styles.assistantRow}>
      <div style={styles.assistantBubble}>
        {parts.map((p, i) =>
          p.kind === "prose" ? (
            <Prose key={i} text={p.text} />
          ) : (
            <TicketBlock key={i} text={p.text} onCopy={onCopy} />
          )
        )}
        {message.content === "" && <span style={styles.cursor}>▍</span>}
      </div>
    </div>
  );
}

function Prose({ text }: { text: string }) {
  if (!text.trim()) return null;
  return <div style={styles.prose}>{text}</div>;
}

function TicketBlock({
  text,
  onCopy,
}: {
  text: string;
  onCopy: (text: string) => void;
}) {
  const [copied, setCopied] = useState(false);
  return (
    <div style={styles.ticketCard}>
      <div style={styles.ticketHeader}>
        <span style={styles.ticketLabel}>Draft ticket</span>
        <button
          onClick={async () => {
            await onCopy(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
          }}
          style={styles.copyButton}
        >
          {copied ? "Copied ✓" : "Copy to clipboard"}
        </button>
      </div>
      <pre style={styles.ticketBody}>{text}</pre>
      <div style={styles.ticketFooter}>
        Paste this into a new Zendesk ticket at{" "}
        <a
          href="https://acadea.zendesk.com/agent/filters/new"
          target="_blank"
          rel="noreferrer"
          style={styles.link}
        >
          acadea.zendesk.com
        </a>{" "}
        and attach any screenshots before submitting.
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    maxWidth: 820,
    margin: "0 auto",
    padding: "0 16px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 0",
    borderBottom: "1px solid #e5e5e0",
  },
  brand: { fontSize: 18, fontWeight: 600 },
  tagline: { fontSize: 13, color: "#666", marginTop: 2 },
  secondaryButton: {
    border: "1px solid #d0d0cc",
    background: "#fff",
    padding: "6px 12px",
    borderRadius: 6,
    fontSize: 13,
    cursor: "pointer",
  },
  scroll: {
    flex: 1,
    overflowY: "auto",
    padding: "16px 0",
  },
  empty: {
    padding: "48px 24px",
    background: "#fff",
    border: "1px solid #e5e5e0",
    borderRadius: 8,
    marginTop: 24,
  },
  emptyCopy: { color: "#555", marginTop: 0, lineHeight: 1.5 },
  examples: {
    marginTop: 24,
    padding: 12,
    background: "#f0efeb",
    borderRadius: 6,
  },
  userRow: {
    display: "flex",
    justifyContent: "flex-end",
    margin: "12px 0",
  },
  userBubble: {
    background: "#2d2d2a",
    color: "#fafafa",
    padding: "10px 14px",
    borderRadius: 12,
    maxWidth: "80%",
    whiteSpace: "pre-wrap",
    lineHeight: 1.5,
    fontSize: 15,
  },
  assistantRow: { margin: "12px 0" },
  assistantBubble: {
    background: "#fff",
    border: "1px solid #e5e5e0",
    borderRadius: 12,
    padding: 14,
    lineHeight: 1.5,
    fontSize: 15,
  },
  prose: { whiteSpace: "pre-wrap" },
  cursor: { opacity: 0.5, animation: "none" },
  ticketCard: {
    margin: "12px 0",
    border: "1px solid #c9c9c2",
    borderRadius: 8,
    background: "#fbfaf5",
  },
  ticketHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "8px 12px",
    borderBottom: "1px solid #e5e5e0",
  },
  ticketLabel: {
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    color: "#666",
    fontWeight: 600,
  },
  copyButton: {
    border: "1px solid #c9c9c2",
    background: "#fff",
    padding: "4px 10px",
    borderRadius: 4,
    fontSize: 12,
    cursor: "pointer",
  },
  ticketBody: {
    margin: 0,
    padding: 12,
    fontSize: 13,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    background: "transparent",
  },
  ticketFooter: {
    padding: "8px 12px",
    fontSize: 12,
    color: "#555",
    borderTop: "1px solid #e5e5e0",
  },
  link: { color: "#2d2d2a", textDecoration: "underline" },
  composer: {
    padding: "12px 0 16px 0",
    borderTop: "1px solid #e5e5e0",
  },
  textarea: {
    width: "100%",
    border: "1px solid #d0d0cc",
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    resize: "vertical",
    background: "#fff",
    lineHeight: 1.4,
  },
  composerActions: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 8,
  },
  hint: { fontSize: 12, color: "#888" },
  sendButton: {
    background: "#2d2d2a",
    color: "#fafafa",
    border: "none",
    padding: "8px 16px",
    borderRadius: 6,
    fontSize: 14,
    cursor: "pointer",
    fontWeight: 500,
  },
  stopButton: {
    background: "#b12929",
    color: "#fafafa",
    border: "none",
    padding: "8px 16px",
    borderRadius: 6,
    fontSize: 14,
    cursor: "pointer",
  },
  error: {
    background: "#fde7e7",
    border: "1px solid #f3b5b5",
    color: "#8a2323",
    padding: 12,
    borderRadius: 6,
    margin: "12px 0",
    fontSize: 14,
  },
};
