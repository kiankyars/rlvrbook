# Open Problems and the Research Agenda

## Chapter Map

- Central question: What bottlenecks still prevent RLVR from becoming a mature science of verifier-driven capability?
- Key distinction: The frontier is shaped more by verifier quality than by optimizer novelty.
- Main failure mode: Ending the book with a paper list instead of a real research agenda.

## Core Terms

- Bottleneck: A technical constraint whose resolution would substantially expand what verifiers can support.
- Research agenda: A structured view of open questions rather than an accumulation of loose future-work bullets.
- Deployment constraint: A practical limit involving latency, cost, auditability, or safety that shapes verifier design.

## Main Argument

The book should close by synthesizing its claims into a concrete research program. Stronger process verifiers, more trustworthy learned judges, better separation of reasoning gains from search gains, and better integration with uncertainty, abstention, and safety all remain open.

The final chapter should leave the reader with a map of the next hard questions, not with the impression that RLVR is merely waiting for the next optimizer tweak.

## Canonical Examples

- Tasks where stronger verification would unlock qualitatively different training.
- Domains where judge-model reliability is currently the limiting factor.
- Settings where deployment cost, latency, or audit burden dominate model quality concerns.

## Failure Modes

- Turning "open problems" into generic benchmark wishlist items.
- Treating all verifier weaknesses as annotation or scale problems.
- Ignoring deployment constraints in favor of purely academic task formulations.

## What the Verifier Sees

The verifier sees whatever the current interface and instrumentation permit, along with the limits of those choices.

## What the Verifier Misses

It misses the capabilities that would only become legible under richer interfaces, stronger audits, or entirely new verification regimes.

## Research Notes

- Which new verifier classes would most change the field?
- How should RLVR systems report uncertainty about the verifier itself?
- What would a mature verifier-evaluation standard look like?
