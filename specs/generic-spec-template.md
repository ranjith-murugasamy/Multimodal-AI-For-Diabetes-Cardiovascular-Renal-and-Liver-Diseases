# Generic Spec Template — "Research Artifact → Reproducible Full-Stack Web App"

**What this is:** a reusable `spec.md` template, extracted from this project's own spec
(and cross-checked against its sibling project in this workspace), for the recurring pattern:
*you have a research paper / technical writeup and some reference code (possibly broken,
possibly evaluated dishonestly), and you want a spec-driven, runnable, inspectable full-stack
web app built from it, with real data and an honest results story.*

Copy this file into a new project as `specs/spec.md`, then work through §2 (fill in the
template) using §1 (the variability toolkit) so the result doesn't read like a form letter.

---

## 0. When this template fits

Use it when a project has all three of:

1. **Source material** — a paper, thesis chapter, technical report, or detailed writeup,
   optionally with external feedback (reviewer comments, advisor notes, stakeholder requests).
2. **Reference code** — a script or notebook that implements the idea, which may have bugs,
   evaluation shortcuts, or dependencies that no longer install cleanly.
3. **A target deliverable** — a runnable web application (backend + frontend) that makes the
   method inspectable and its results reproducible, not just a cleaned-up script.

If any of the three is missing (no reference code at all, or the deliverable is a library/CLI
rather than a web app), adapt §4's subsections but keep §1, §2 (framing), §6, §7, and §8 — they
generalize past the web-app case.

---

## 1. Variability toolkit — read this before filling in §2

Templates that get filled in the same way every time produce specs that read as boilerplate,
which is a credibility problem when the spec is meant to demonstrate real thinking about a
specific project. This section gives a concrete, repeatable way to vary the *voice and
structure* of the output without touching its *substance* (the substance should always be
derived fresh from the actual source material — never copied from a previous instantiation).

### 1.1 Deterministic variant selection

Pick a **seed** from the new project's own identity, not from randomness you'd have to
remember — e.g.:

```
seed = int(sha256(project_name + target_domain + iso_date).hexdigest(), 16)
variant_index(section_key) = (seed + salt[section_key]) % len(variants[section_key])
```

Two different projects (different `project_name`/`target_domain`) deterministically land on
different phrasing and structure choices below; the *same* project regenerated later (same
inputs) reproduces the same choices — varied across projects, stable within one.
If you're filling this in by hand rather than scripting it, just eyeball-pick a different
numbered variant than the last project you wrote, and note which one you picked.

### 1.2 Phrasing variant banks

Pick one variant per row (don't default to "Variant 1" every time):

| Section | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|
| Opening of §0 | "This spec translates \[N\] input documents into a buildable application." | "The following requirements were derived from \[source material\]; \[N\] and \[N\] cite the specific claims this spec responds to." | "Source material for this spec: \[list\]. Nothing below is reproduced verbatim — see §\[x\] and §\[y\] for the specific claims it answers." |
| Opening of §1 (Purpose) | "Turn \[the method\] into a runnable, inspectable web application: \[core verb phrase\]." | "The goal of this application is to make \[the method\] reproducible end-to-end: \[core verb phrase\]." | "This application exists to close the gap between \[the paper's claims\] and \[what can actually be verified\]: \[core verb phrase\]." |
| Opening of §2 (reference-code issues) | "Read closely, the reference implementation has \[N\] issues that affect whether its reported numbers mean anything, independent of \[stakeholder\]'s comments." | "Before addressing any external feedback, the reference code itself was audited and found to have \[N\] problems worth fixing on their own merits." | "Two kinds of gaps exist in the reference material: what \[stakeholder\] asked to fix, and what close reading of the code itself revealed. This section covers the latter." |
| FR numbering style | `FR-1`, `FR-2`, … | `REQ-1`, `REQ-2`, … | `F1`, `F2`, … (no hyphen) |
| Opening of §7 (out of scope) | "Documented here rather than silently skipped:" | "Explicitly deferred, with reasons, rather than silently dropped from the implementation:" | "The following are real gaps, named rather than hidden:" |
| Acceptance-criteria framing | A flat checklist | "A fresh checkout must, with no manual steps:" + checklist | Table with columns \[Criterion \| How verified\] |

### 1.3 Structural levers (vary these per project, not just the wording)

- **Section order within §4** (Functional Requirements) — group by pipeline stage (data →
  model → fusion → eval → app) for one project, by user-facing feature for another. Both are
  valid; pick the one that matches how a reader of *this* project would think about it.
- **Number of components** — this template assumes a multi-component system (the pattern this
  workspace has used twice: CBF+CF+DL, graph-propagation + re-ranking). A single-model project
  collapses §4.2/§4.3 into one subsection; say so explicitly rather than leaving empty headers.
- **Evaluation metric family** — Precision/Recall/NDCG@K fits ranking/recommendation; swap for
  the metric family that actually matches the new project's task (RMSE/MAE for regression,
  F1/AUC for classification, BLEU/ROUGE for generation, etc.). Don't keep ranking metrics out
  of habit if the task isn't a ranking task.
- **"Why not use library X" trigger** — only include §6 if a dependency was *actually checked
  and found broken/unstable/unsuitable* (see §6 template below for the verification bar). If
  every dependency installed cleanly, delete §6 rather than inventing a reason.

---

## 2. Template body

Everything in `[brackets]` is a placeholder. Everything outside brackets is boilerplate that
has held up across more than one real project and can be reused as-is.

```markdown
# [Project Name] — Specification

**Status:** Draft v1 · **Owner:** [who/what generated this] · **Last updated:** [date]

## 0. Source material

[Opening per §1.2 variant.]

1. **[source doc 1 filename/title]** — [what it is: paper / notebook / design doc], [plus any
   external feedback attached: reviewer rounds, stakeholder comments, a revision-cost quote].
2. **[source doc 2 filename/title]** — [reference implementation: list the specific techniques
   it implements, e.g. "TF-IDF + cosine similarity, a graph-propagation model, a fusion step,
   and an evaluation routine"].

## 1. Purpose

[Opening per §1.2 variant.] [One or two sentences on what "inspectable" and "reproducible"
concretely mean for this project — e.g. "train the real model against real data, expose every
hyperparameter in the UI, make the evaluation protocol an interactive, first-class feature
rather than a one-off offline script."]

## 2. What the reference code actually does (and [N] problems worth fixing)

[Opening per §1.2 variant.]

1. **[Problem 1 — usually an evaluation-honesty issue].** [Description with a specific code
   reference: function name, line behavior.] [Why this matters for the numbers' validity.]
2. **[Problem 2, if any — usually a scale/representativeness issue].** [Same structure.]

This application fixes [these / this] by [the concrete architectural fix — e.g. "a per-entity
held-out split, evaluated and averaged across every held-out case, not a single example"].

## 3. Users and use cases

- **[Primary user type]**: [what they do with the app — load data, train, explore, decide what
  to report].
- **[Secondary user type, if any]**: [e.g. a reviewer/collaborator verifying a specific claimed
  number without reading code].

## 4. Functional requirements

[Group however §1.3's structural lever decided. Example grouping below — relabel as needed.]

### 4.1 Data
- [FR-id]: Ship a default, real dataset in `input/` — [name, size, format].
- [FR-id]: Accept a custom data upload, parsed into the same internal representation.
- [FR-id]: Report dataset statistics before any training/inference runs.

### 4.2 Core model(s)
- [FR-id] per component: name, the technique it implements, and the paper equation/section it
  corresponds to (if any) — this traceability matters for anyone checking the implementation
  against the source material.
- [FR-id]: Each component independently trainable/queryable (needed if §4.3 exists).

### 4.3 Combination / fusion (only if multi-component)
- [FR-id]: How component outputs are combined (formula, normalization method).
- [FR-id]: **Ablation as a first-class feature** — if the source material asks "is every
  component necessary," make every subset combination a one-click comparison, not a
  footnote. Reuse the *same* combination function for the full system and every ablation
  variant (different weights into one function, not N separately-maintained code paths).
- [FR-id]: **Interactive sensitivity analysis**, if applicable — recompute downstream metrics
  from cached per-case component outputs when a weight/hyperparameter changes, without a full
  retrain, so exploring the space is fast enough to actually be explored.

### 4.4 Evaluation
- [FR-id]: [metric family] computed per held-out case and averaged across **every** held-out
  case (not one example) — matches §2's fix.
- [FR-id]: Report the full evaluation protocol alongside every result: split method, any
  threshold, random seed, candidate set definition, how already-seen items are excluded.

### 4.5 Interactive query (if the app answers "what would this system do for input X")
- [FR-id]: Given a specific input, return the top results with a per-component score
  breakdown, retained as a **qualitative illustration** — not as the evaluation itself (that's
  §4.4's job).

### 4.6 Application
- [FR-id]: Web UI covering data selection/upload, run configuration, live progress, a
  results/comparison dashboard, and any interactive query panel.
- [FR-id]: REST (+ streaming, if runs are long) API backing the UI, usable headlessly for
  scripted/reproducible experiments.
- [FR-id]: **Single script to set up, start, and stop the whole application.**

## 5. Non-functional requirements

- [NFR-id]: Runs on stock local tooling — name the real constraint (no GPU required, no
  framework X dependency) and *why* (see §6 if a specific library was the trigger).
- [NFR-id]: A full run completes in [realistic time bound] on the target hardware.
- [NFR-id]: Every number shown in the UI is traceable to a specific run configuration — no
  hard-coded or placeholder metrics anywhere in the app.

## 6. Why not [library/dependency X], as the source material uses — *(delete if unneeded; see §1.3)*

Checked empirically against [this environment] before writing any code — state the actual
command run and the actual error/limitation found, not a general reputation claim:

- `[pip install / npm install / etc.] [package]` → **\[actual error text or behavior\]** —
  [root cause: unmaintained, incompatible with current toolchain, only available as an
  unstable/nightly build, etc.].

[State the substitute approach and how it was validated — e.g. "reimplemented from scratch in
[language/library], validated against [gradient checking / known closed-form cases / a
reference output] before being trusted on real data."]

## 7. [Source material]-requested items explicitly out of scope

[Opening per §1.2 variant.]

- **[Item 1 — usually: comparison against an external baseline].** [Why it's out of scope: a
  substantial independent project, a separate research question, etc.] [If the architecture
  was deliberately left open to add it later, say so and point at the specific extension
  point.]
- **[Item 2 — usually: formal statistical validation across multiple seeds/runs].** [What
  partial support exists, e.g. "the API accepts a seed and can be re-run, but there is no
  built-in multi-run aggregation or significance test."]
- **[Item 3 — usually: narrative/manuscript-writing asks].** [State plainly these aren't
  application features: "out of scope for an application spec; belongs in the manuscript, not
  the codebase."]

## 8. Acceptance criteria

[Framing per §1.2 variant.]

- A fresh checkout runs end-to-end via the single setup/start script with no manual steps.
- Training/running on the default dataset produces [the metric family] for [every
  configuration §4.3 promises], computed on a held-out split, over **every** held-out case.
- [If §4.3 sensitivity exists] Changing a weight/hyperparameter in the UI updates results
  without a full retrain.
- [If §4.5 exists] The interactive query panel reproduces the qualitative pattern from the
  source material, using real scores from a real run — not a hard-coded example.
```

---

## 3. Companion files checklist

A spec on its own under-delivers on "spec-driven development." Pair it with:

| File | Purpose |
|---|---|
| `specs/plan.md` | Technical architecture: directory tree, data flow, the math/algorithm detail that didn't fit in the spec's requirement bullets, the API surface, the frontend page list. |
| `specs/tasks.md` | A checklist mirroring the plan, checked off as work actually completes — not written once and left stale. |
| `specs/[stakeholder]-requirements.md` | *(only if there's external feedback to track)* A point-by-point table: comment → status (Implemented / Partially / Out of scope) → where. If the feedback is extensive enough to need a formal written response, generate a separate `.docx` response letter from this table rather than cramming prose into the spec itself. |
| `input/` | Real sample data, not synthetic placeholders — committed or fetched by the setup script. |
| `output/` | Evidence from one real run: screenshots walking through the app, exported result files, a short README explaining what each one shows. |
| `scripts/app.sh` (or equivalent) | `setup \| start \| stop \| restart \| status \| logs` — idempotent setup (checks actual installed state, not a marker file), port-based process management (not PID-based — a backgrounded `npm run dev &`'s PID is npm's, not the dev server's). |

---

## 4. Instantiation checklist

1. Gather source material; read it closely enough to find real problems in the reference code,
   not just the stakeholder-flagged ones (§2's two-problem pattern recurs often — look for
   evaluation leakage and small-sample reporting specifically).
2. Pick a seed (§1.1) and resolve every variant bank in §1.2 before writing prose.
3. Verify every planned dependency actually installs/works in the target environment *before*
   committing to it in §4 — write §6 from real command output, never from memory of "that
   package is usually fine."
4. Fill in §2 of this template, section by section, citing real file/line/equation references
   wherever the bracketed text asks for one.
5. Write the companion files from §3.
6. Build, then verify by actually running the app (not just reading the code) — capture real
   screenshots and real output files for `output/`, not mocked ones.
7. Update `tasks.md` checkboxes to match reality, not aspiration.

## 5. Anti-patterns to avoid

- **Silently dropping a stakeholder ask.** If it's out of scope, say so in §7 — don't just omit
  it and hope no one checks.
- **Claiming "implemented" for something only documented.** A requirements-mapping table (§3)
  needs a real status value per row, not an optimistic default.
- **Trusting a library by reputation instead of by running the install.** §6 exists because
  "this should work" and "this works in this environment, today" are different claims.
- **Fabricating or rounding results to look better.** Report the real number, including when
  it's an uncomfortable one (e.g., the full system tying or losing to a simpler ablation at
  some operating point) — that's what an honest ablation study is *for*.
- **Copying a previous project's specific numbers, equations, or examples into a new spec.**
  Everything outside this file's `[brackets]` and tables is reusable; everything inside them
  must be re-derived from the new project's own source material every time.
