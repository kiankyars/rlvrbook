---
name: review-ml-textbook
description: Review online machine learning textbooks and manuscript-style web books with hyper-rational rigor. Use when Codex needs to evaluate, critique, or orchestrate revisions for an ML/AI textbook, course notes, bookdown/Quarto/Jupyter Book site, or online technical reference; especially when the user asks for global chapter-by-chapter review, rigorous critique, subagent-per-chapter review, coherence audits, pedagogical structure, citation/source quality, mathematical correctness, or revision planning.
---

# Review ML Textbook

## Operating stance

Treat the book as an argument and a teaching system, not as a pile of chapters. Steel man the author's intent, then look for the highest-leverage ways the book could become more correct, clearer, more complete, and more useful.

Be hyper-rational:
- Separate factual errors, weak causal claims, pedagogy problems, style problems, and taste.
- Prefer concrete examples, missing definitions, broken transitions, and checkable contradictions over vague criticism.
- Flag uncertainty and source needs explicitly.
- Do not rewrite human prose unless the user asks. Produce revision targets, patch plans, or surgical examples instead.

## Workflow

1. **Map the artifact.** Identify the book framework, table of contents, chapter files/pages, appendices, bibliography, figures, notebooks, and build commands. For web-only books, collect stable URLs and chapter titles before reviewing.
2. **Define the review contract.** Infer the audience, purpose, and desired standard from the user and the artifact. If missing, default to: graduate-level ML reader, reference-work quality, intuitive examples before abstraction, and coherent running examples across chapters.
3. **Spawn chapter reviewers.** Use subagents for every substantive chapter whenever the tool is available and the user asked for rigorous or global review. Give each subagent exactly one chapter or one appendix, plus the book thesis, audience, neighboring chapter titles, and a compact rubric. Do not give them your expected findings.
4. **Review locally in parallel.** While subagents run, inspect the table of contents, introduction, conclusion, glossary/appendices, bibliography, figure list, and cross-chapter terminology. Do not duplicate a subagent's assigned chapter unless needed to resolve a conflict.
5. **Synthesize.** Merge chapter findings into a global diagnosis. Deduplicate issues, rank by impact, and distinguish local fixes from structural revisions.
6. **Orchestrate revision.** Produce a decision-complete revision plan: global thesis changes, chapter-level edits, cross-reference/terminology changes, citation/source work, figure/table work, and validation/build checks. Only edit files when the user asks for implementation.

## Chapter reviewer prompt template

Use this shape for each subagent:

```text
Use the review-ml-textbook skill at <skill path> to review exactly this chapter: <chapter path or URL>.

Book context:
- Working title: <title>
- Intended audience: <audience>
- Global thesis: <one-paragraph thesis>
- Neighboring chapters: <previous/title, next/title>

Rubric:
- Find factual, mathematical, or conceptual errors.
- Identify missing prerequisites, undefined terms, broken motivation, and weak transitions.
- Check whether examples precede abstraction and whether any running examples should be carried forward.
- Flag citation/source gaps and claims needing evidence.
- Distinguish high-impact structural issues from line-editing.
- Do not rewrite prose unless a small example is necessary to make a fix concrete.

Return:
- 5-10 findings, ordered by severity, with line references or quoted anchors.
- One paragraph on how this chapter should change.
- Any cross-chapter dependencies or terminology conflicts.
```

## Review rubric

Score issues by expected improvement, not by ease:
- **P0:** Wrong, misleading, or likely to teach a false mental model.
- **P1:** Blocks the intended reader from following the chapter or breaks global coherence.
- **P2:** Important but local: missing example, weak transition, unsupported claim, unclear figure.
- **P3:** Style, polish, or optional enrichment.

Prefer findings that name the exact failure mode:
- "This definition is used before it is introduced."
- "The example demonstrates X but the paragraph claims Y."
- "The chapter optimizes for paper chronology rather than conceptual dependency."
- "This citation supports the benchmark result but not the causal claim made here."
- "The same term changes meaning between chapters."

## Synthesis output

Lead with the global diagnosis. Then provide:
- Chapter-by-chapter highest-leverage revisions.
- Cross-chapter terminology and running-example fixes.
- Missing sources, figures, or appendices.
- A staged implementation plan with validation commands.

Keep the synthesis frank but not theatrical. Avoid generic praise and generic "add more examples" advice unless tied to a specific reader failure.
