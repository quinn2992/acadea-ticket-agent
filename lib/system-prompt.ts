import fs from "node:fs";
import path from "node:path";

// The knowledge pack files, concatenated in this order. Adding/removing a
// file invalidates the prompt cache. Reordering invalidates the prompt cache.
// Editing any file invalidates the prompt cache. This is the Karpathy-LLM-wiki
// pattern — we stuff the whole thing into the system prompt and let the
// prefix-match cache do the rest.
const KNOWLEDGE_FILES = [
  "00_role.md",
  "01_north_star.md",
  "02_ticket_anatomy.md",
  "03_interview_flow.md",
  "04_modules.md",
  "05_followup_preempts.md",
  "06_exemplars.md",
  "07_anti_patterns.md",
  "08_institutions.md",
];

let cachedPrompt: string | null = null;

function loadKnowledgePack(): string {
  const repoRoot = process.cwd();
  const knowledgeDir = path.join(repoRoot, "knowledge_pack");

  const chunks: string[] = [];
  chunks.push(
    "# Acadea Ticket Drafting Assistant — knowledge pack\n\n" +
      "The following files are concatenated into your working memory. Treat them as a single operating manual. " +
      "They define your role, output format, interview flow, and constraints. Follow them strictly.\n\n" +
      "---\n"
  );

  for (const filename of KNOWLEDGE_FILES) {
    const filePath = path.join(knowledgeDir, filename);
    const body = fs.readFileSync(filePath, "utf8").trim();
    chunks.push(`\n## FILE: knowledge_pack/${filename}\n\n${body}\n\n---\n`);
  }

  chunks.push(
    "\n# End of knowledge pack\n\n" +
      "When responding to the customer, apply every rule above. If a situation is ambiguous, prefer specificity, refuse to invent facts, and always route urgency into the Priority line rather than the subject."
  );

  return chunks.join("");
}

export function getSystemPrompt(): string {
  if (cachedPrompt) return cachedPrompt;
  cachedPrompt = loadKnowledgePack();
  return cachedPrompt;
}
