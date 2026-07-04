---
name: process-architect
description: Interview the user to define a healthy business/IT process (approval chains, handoff pipelines), pressure-test it against a health rubric, then render it as one self-contained, professional HTML process guideline from a JSON definition. For documenting "how we do X" — purchase-order approvals, onboarding, incident handling, orbit's own filing flow — never for deciding where files go.
---

# process-architect

Turns a fuzzy "this is roughly how we do it" into a **defined, healthy process**
and a professional one-page guideline. Two moves: an **interview** that draws the
process out and hardens it, then a **generator** that renders the agreed JSON as a
single static HTML page (theme-aware, print-clean, zero external resources).

Data in, HTML out — the JSON definition is the source of truth; the HTML is
disposable output (`*.process.html`, gitignored), never hand-edited. This skill
models *processes*; it carries **no filing rules** (those live only in
`.gravity/filing/SPEC.md`).

## What "healthy" means (the rubric the interview drives toward)

A process is healthy when every one of these holds. Use it as both the interview
checklist and the final gate:

1. **One owner per gate.** Each step has a single accountable role, not a committee
   — committees stall and no one is answerable.
2. **Explicit entry & exit criteria.** Each gate states what it *needs to start*
   (inputs) and what it *must produce* to pass (output). No "we just kind of send
   it over."
3. **Named decision states, every gate.** A gate can only send work forward
   (**go**), bounce it back one step to be fixed (**hold**), or eject/escalate it
   (**stop**). Three states, always spelled out.
4. **No dead ends.** Every *hold* names who fixes it; every *stop* names where it
   goes (closed / escalate to whom / re-source). A path that just "stops" is a bug.
5. **A turnaround per gate.** Even a rough SLA, so the slow gate is visible and the
   total lead time is the sum. Optional, but a process with no time expectation
   drifts.
6. **Sequential-vs-parallel honesty.** Model the real order. If two gates truly run
   in parallel, say so; don't draw a fake straight line.
7. **Escape hatches.** High-value, urgent, and external-party cases are handled
   explicitly (as exceptions), not improvised each time.

An external party — a supplier, a provider, a customer — is **still a gate**: give
it an owner, inputs, outputs and decision states like any internal team.

## Procedure

### 1 — Interview (draw it out, then harden it)

Ask in this order; capture answers as you go. Keep questions plain — the user talks
in their own words, you translate to the schema.

1. **Name & boundaries.** What process is this? What *triggers* it (the start)?
   What does *done* look like (the end state)?
2. **The gates, in order.** List every team/role that must act, in sequence. For
   each, who is the **single owner**?
3. **Per gate — the check.** In one line: what does this gate actually verify or
   do? (→ `purpose`)
4. **Per gate — hand-off.** What does it *need to start* (→ `needs`) and what does
   it *produce* to pass (→ `produces`)?
5. **Per gate — the three exits.** On **go** → which gate next? On **hold** → who
   fixes and resubmits? On **stop** → closed, or escalate to whom? (→ `decisions`)
6. **Turnaround.** A target time per gate, if they track one (→ `sla`; skip if not).
7. **Exceptions.** High value, rush, external parties, known edge cases (→
   `exceptions`).

### 2 — Health check (push back before rendering)

Run the rubric over the captured process and **name the weaknesses out loud** with
a proposed fix, e.g.:

- a gate with two owners → "who's actually accountable here?";
- a *stop* with no destination → dead end, propose an escalation target;
- a gate with no exit criteria → "what has to be true to pass this step?";
- an unbounded gate → propose a rough SLA;
- a "gate" that's really a rubber stamp → merge or drop it.

Agree the fixes with the user, then finalize the JSON. Do not render an unhealthy
process silently.

### 3 — Encode & render

Write the agreed process to a JSON definition (schema below; start from
`examples/purchase-order.json`), then:

```bash
python skills/process-architect/generate.py <definition.json> --open
#   -o <file>       write somewhere other than ./<name>.process.html
#   --fragment      emit body-only HTML (title+style+content) for embedding
#   --open / -O     open the result in the default browser (omit for headless/CI)
```

Review the page, iterate on the JSON (never the HTML), regenerate. The definition
travels/commits; the HTML is disposable.

## Definition schema (JSON)

```jsonc
{
  "meta": {                      // document header
    "title": "Purchase Order Approval",
    "eyebrow": "Standard Operating Procedure - Procurement",   // small label
    "summary": "One-paragraph what/why (shown as the lede).",
    "ref": "SOP-PROC-01", "owner": "Procurement", "version": "1.0",
    "effective": "2026-07-04", "review": "Annual",
    "lead_time": "~10 business days"                            // all meta fields optional
  },
  "chain": [                     // optional at-a-glance strip; auto-built from stages if omitted
    { "kind": "start", "role": "Origin", "label": "Requester" },
    { "role": "Gate 1", "label": "Line Manager" },
    { "role": "Gate 5", "label": "Supplier", "provider": true },// provider = accent-outlined
    { "kind": "end", "role": "Result", "label": "PO Issued" }
  ],
  "stages": [                    // the numbered steps, in order (required)
    {
      "title": "Line Manager approval",
      "owner": "Requesting team",
      "sla": "1 day",            // optional
      "purpose": "Confirm the purchase is a genuine, budgeted business need.",
      "needs": "PO request form, business justification, quote.",     // optional
      "produces": "Manager's approval on the request.",               // optional
      "decisions": [
        { "state": "go",   "label": "APPROVE", "to": "Finance" },
        { "state": "hold", "label": "RETURN",  "to": "Requester (fix & resubmit)" },
        { "state": "stop", "label": "REJECT",  "to": "Closed" }
      ]
    }
  ],
  "legend": [ /* optional; sensible go/hold/stop default if omitted */ ],
  "exceptions": [ { "title": "SLA breach", "desc": "..." } ]   // optional
}
```

`state` is always one of **go** (green, forward), **hold** (amber, loop back one
step), **stop** (red, eject/escalate). That vocabulary is fixed; the visible
`label` per gate is yours (APPROVE / RETURN / REJECT, PROCEED / PARK / FAIL, ...).

## Never

- **No filing rules here.** If a question turns into "which area does this file go
  in," that's `file-triage` and the SPEC, not this skill.
- **Never hand-edit the generated HTML** — fix the JSON, regenerate. The HTML is
  `*.process.html`, gitignored, disposable.
- **Never add external resources** (CDN, web fonts) to the generator — guidelines
  must render on an offline intranet.
- **Never render an unhealthy process quietly** — surface the rubric failures and
  agree the fix first.
- **Keep samples fake.** Real team names, values and SLAs may be used while
  drafting, but anything committed to this repo stays fake (CLAUDE.md: no corporate
  data).
