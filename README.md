# Acadea Ticket Agent

An AI drafting assistant that interviews Acadea customers and produces a well-structured Zendesk support ticket the customer can then copy-paste into Zendesk. Not a submission bot — a quality front door.

## Repo layout

- `source_materials/` — primary and historical inputs (SOP, Apr 16 meeting transcript, three ticket JSON datasets, Maverick template).
- `analysis/` — Python scripts that surface patterns across the 848 historical tickets. Each script has a header comment explaining what it does; all outputs land in `analysis/output/`.
- `knowledge_source/` — synthesized analytical docs. `00_ticket_quality_accounting.md` is the raw material from which the production knowledge pack will later be distilled.

## Architecture (reference, not yet built)

- No fine-tuning, no vector DB, no RAG. Knowledge pack is concatenated into the system prompt at runtime (Karpathy LLM-wiki pattern, minus the compile/sync machinery).
- The knowledge pack is a small set of hand-curated markdown files.
- North Star: write the ticket a customer *would* have written if Kali (Acadea's ops/support lead) were sitting next to them asking the right questions. Current best tickets are training data, not a ceiling.
