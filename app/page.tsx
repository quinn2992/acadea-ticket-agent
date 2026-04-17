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
    <div style={styles.shell}>
      <div style={styles.topBar} />
      <div style={styles.page}>
        <header style={styles.header}>
          <div style={styles.brandBlock}>
            <img
              src={`${BASE_PATH}/brand/acadea-logo.png`}
              alt="Acadea"
              style={styles.logo}
            />
            <div style={styles.dividerDot} />
            <div>
              <div style={styles.appTitle}>Ticket Drafter</div>
              <div style={styles.tagline}>
                Interview → draft → copy into Zendesk
              </div>
            </div>
          </div>
          <button
            onClick={reset}
            style={styles.secondaryButton}
            disabled={streaming && messages.length === 0}
          >
            New ticket
          </button>
        </header>

        <div style={styles.scroll} ref={scrollRef}>
          {messages.length === 0 && (
            <div style={styles.empty}>
              <h2 style={styles.emptyHeading}>
                What issue do you want to report?
              </h2>
              <p style={styles.emptyCopy}>
                Describe the problem in your own words. I&apos;ll ask a few
                follow-ups and hand you a ready-to-paste ticket.
              </p>
              <div style={styles.examples}>
                <div style={styles.examplesLabel}>Example starters</div>
                <ul style={styles.examplesList}>
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
              <button
                onClick={send}
                style={{
                  ...styles.sendButton,
                  ...(input.trim() ? {} : styles.sendButtonDisabled),
                }}
                disabled={!input.trim()}
              >
                Send
              </button>
            )}
          </div>
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
          style={copied ? styles.copyButtonDone : styles.copyButton}
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

const BRAND = {
  teal: "#195259",
  moss: "#0D2426",
  orange: "#F4380C",
  cream: "#F5FCFC",
  mint: "#B5E1E5",
  aluminum: "#D9DFE8",
  textMuted: "#4A6A6E",
  border: "#DCE5E6",
  borderStrong: "#C6D4D6",
};

const styles: Record<string, React.CSSProperties> = {
  shell: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
  },
  topBar: {
    height: 4,
    background: BRAND.orange,
    flexShrink: 0,
  },
  page: {
    display: "flex",
    flexDirection: "column",
    flex: 1,
    minHeight: 0,
    maxWidth: 860,
    width: "100%",
    margin: "0 auto",
    padding: "0 20px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "18px 0 16px 0",
    borderBottom: `1px solid ${BRAND.border}`,
    gap: 16,
  },
  brandBlock: {
    display: "flex",
    alignItems: "center",
    gap: 14,
    minWidth: 0,
  },
  logo: {
    height: 32,
    width: "auto",
    display: "block",
  },
  dividerDot: {
    width: 1,
    height: 28,
    background: BRAND.border,
    flexShrink: 0,
  },
  appTitle: {
    fontSize: 15,
    fontWeight: 600,
    color: BRAND.teal,
    letterSpacing: -0.1,
  },
  tagline: {
    fontSize: 12,
    color: BRAND.textMuted,
    marginTop: 2,
  },
  secondaryButton: {
    border: `1px solid ${BRAND.borderStrong}`,
    background: "#fff",
    color: BRAND.teal,
    padding: "7px 14px",
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 500,
    cursor: "pointer",
    flexShrink: 0,
    transition: "background 120ms ease, border-color 120ms ease",
  },
  scroll: {
    flex: 1,
    overflowY: "auto",
    padding: "20px 0",
  },
  empty: {
    padding: "40px 28px",
    background: "#fff",
    border: `1px solid ${BRAND.border}`,
    borderRadius: 12,
    marginTop: 20,
    boxShadow: "0 1px 2px rgba(13, 36, 38, 0.04)",
    position: "relative",
    overflow: "hidden",
  },
  emptyHeading: {
    margin: "0 0 10px 0",
    fontSize: 22,
    fontWeight: 700,
    color: BRAND.teal,
    letterSpacing: -0.3,
  },
  emptyCopy: {
    color: BRAND.textMuted,
    margin: 0,
    lineHeight: 1.55,
    fontSize: 14.5,
  },
  examples: {
    marginTop: 24,
    padding: "14px 16px",
    background: BRAND.cream,
    border: `1px solid ${BRAND.border}`,
    borderRadius: 8,
  },
  examplesLabel: {
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 0.8,
    fontWeight: 600,
    color: BRAND.teal,
    marginBottom: 8,
  },
  examplesList: {
    margin: 0,
    paddingLeft: 18,
    color: BRAND.textMuted,
    fontSize: 14,
    lineHeight: 1.7,
  },
  userRow: {
    display: "flex",
    justifyContent: "flex-end",
    margin: "14px 0",
  },
  userBubble: {
    background: BRAND.teal,
    color: BRAND.cream,
    padding: "10px 14px",
    borderRadius: 14,
    borderBottomRightRadius: 4,
    maxWidth: "80%",
    whiteSpace: "pre-wrap",
    lineHeight: 1.5,
    fontSize: 15,
    boxShadow: "0 1px 2px rgba(13, 36, 38, 0.08)",
  },
  assistantRow: { margin: "14px 0" },
  assistantBubble: {
    background: "#fff",
    border: `1px solid ${BRAND.border}`,
    borderRadius: 14,
    borderBottomLeftRadius: 4,
    padding: "14px 16px",
    lineHeight: 1.55,
    fontSize: 15,
    boxShadow: "0 1px 2px rgba(13, 36, 38, 0.04)",
  },
  prose: { whiteSpace: "pre-wrap" },
  cursor: {
    opacity: 0.5,
    color: BRAND.teal,
    animation: "acadea-blink 1s ease-in-out infinite",
  },
  ticketCard: {
    margin: "14px 0",
    border: `1px solid ${BRAND.borderStrong}`,
    borderLeft: `3px solid ${BRAND.orange}`,
    borderRadius: 10,
    background: "#fff",
    overflow: "hidden",
    boxShadow: "0 2px 8px rgba(13, 36, 38, 0.05)",
  },
  ticketHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 14px",
    borderBottom: `1px solid ${BRAND.border}`,
    background: BRAND.cream,
  },
  ticketLabel: {
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 0.9,
    color: BRAND.teal,
    fontWeight: 700,
  },
  copyButton: {
    border: "none",
    background: BRAND.teal,
    color: BRAND.cream,
    padding: "6px 12px",
    borderRadius: 6,
    fontSize: 12,
    fontWeight: 500,
    cursor: "pointer",
    transition: "background 120ms ease",
  },
  copyButtonDone: {
    border: "none",
    background: BRAND.orange,
    color: BRAND.cream,
    padding: "6px 12px",
    borderRadius: 6,
    fontSize: 12,
    fontWeight: 500,
    cursor: "pointer",
  },
  ticketBody: {
    margin: 0,
    padding: 14,
    fontSize: 13,
    lineHeight: 1.55,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    background: "#fff",
    color: BRAND.moss,
  },
  ticketFooter: {
    padding: "10px 14px",
    fontSize: 12,
    color: BRAND.textMuted,
    borderTop: `1px solid ${BRAND.border}`,
    background: BRAND.cream,
  },
  link: { color: BRAND.teal, textDecoration: "underline" },
  composer: {
    padding: "14px 0 18px 0",
    borderTop: `1px solid ${BRAND.border}`,
  },
  textarea: {
    width: "100%",
    border: `1px solid ${BRAND.borderStrong}`,
    borderRadius: 10,
    padding: 12,
    fontSize: 15,
    resize: "vertical",
    background: "#fff",
    lineHeight: 1.45,
    color: BRAND.moss,
    boxShadow: "0 1px 2px rgba(13, 36, 38, 0.03)",
  },
  composerActions: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 10,
  },
  hint: { fontSize: 12, color: BRAND.textMuted },
  sendButton: {
    background: BRAND.teal,
    color: BRAND.cream,
    border: "none",
    padding: "9px 20px",
    borderRadius: 8,
    fontSize: 14,
    cursor: "pointer",
    fontWeight: 600,
    letterSpacing: 0.1,
    transition: "background 120ms ease",
  },
  sendButtonDisabled: {
    background: BRAND.borderStrong,
    color: "#fff",
    cursor: "not-allowed",
  },
  stopButton: {
    background: BRAND.orange,
    color: BRAND.cream,
    border: "none",
    padding: "9px 20px",
    borderRadius: 8,
    fontSize: 14,
    cursor: "pointer",
    fontWeight: 600,
  },
  error: {
    background: "#fde7e2",
    border: `1px solid ${BRAND.orange}`,
    color: "#8a2310",
    padding: 12,
    borderRadius: 8,
    margin: "12px 0",
    fontSize: 14,
  },
};
