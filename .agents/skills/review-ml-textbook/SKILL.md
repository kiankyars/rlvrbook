---
name: review-ml-textbook
description: Audit ML and AI textbooks or manuscript-style web books for high-impact problems in correctness, coherence, evidence, reproducibility, and rendered output. Use for rigorous whole-book, chapter, or revision-plan reviews; not ordinary copyediting.
---

# Review ML Textbook

Find the smallest set of changes that would most improve the book's truth and teaching value. Treat the book as one argument, not a collection of independent chapters. Do not optimize for finding count.

## Workflow

1. **Set the contract.** Establish the intended reader, thesis, scope, evidence standard, and whether edits are allowed. Infer these from the artifact when possible.
2. **Build the model.** Map the table of contents, conceptual dependencies, canonical terms, running examples, empirical artifacts, and build path. Identify the few claims on which the rest of the book depends.
3. **Test what matters.** Prioritize claims whose failure would teach a false mental model, invalidate downstream material, or undermine a central conclusion. For each material finding, record the exact location, supporting evidence, consequence, smallest adequate correction, and a way to verify the fix.
4. **Verify.** Check correctness blockers independently and prefer primary sources. Distinguish direct verification, inference, and unresolved uncertainty. When relevant, run the existing build and inspect the rendered result; a successful command is not visual validation.
5. **Synthesize.** Lead with the global diagnosis. Report only material findings, combine recurring causes, and give a dependency-ordered revision sequence. State important checks not performed.

Edit only when asked. Preserve human prose and unrelated work. Suggest line editing only after correctness and structure are sound.

## Delegation

Delegate only when it materially reduces uncertainty. Split work by risk or coherent artifact slice, not automatically by chapter. Subagents gather evidence; the primary reviewer adjudicates conclusions and independently verifies any finding that would drive a major revision.

## Output

Use the shortest form that makes the decision clear:

- verdict and global diagnosis
- material findings in impact order
- minimal revision sequence
- validation performed and remaining uncertainty

Do not impose finding quotas or chapter-by-chapter coverage unless the user requests it or omissions would hide material risk. If no material problem remains, say so and stop.
