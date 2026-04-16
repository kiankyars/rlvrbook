# Open Problems

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/10-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Discuss open problems in RLVR.

## Verifier fidelity beyond math and code

In long-context QA, answer-evidence checks can miss unsupported synthesis. In multimodal search, final-answer and tool-format rewards can miss visual grounding. In agentic software tasks, tests can miss maintainability, security, minimality, and user intent. In instruction following, many constraints require semantic judgment rather than exact checking.[@peng2025verif; @brown2025verifiers; @tan2025rllm] RLVR has even been used in medicine, where a verifier may check a final label, citation, or structured field while missing whether the model used the right evidence, respected uncertainty, or made a decision a clinician would trust.[@zhang2025medrlvr]

## Adaptive RLVR

We can think of adaptive RLVR in the sense of prompt re-weighting, just to say verifying the difficulty of problems before using them in training in order to maintain a specific competence band over the problems the model tackles.Furthermore, the verifier itself may be updated throughout training to prevent the policy from finding gaps in optimization. A completely adaptive RLVR loop can be written as:

$$
(\pi_t, V_t, \mathcal D_t, \mathcal H_t)
\longrightarrow
(\pi_{t+1}, V_{t+1}, \mathcal D_{t+1}, \mathcal H_{t+1}),
$$ {#eq-ch10-adaptive-system}

where $\pi_t$ is the policy, $V_t$ the verifier stack, $\mathcal D_t$ the task distribution, and $\mathcal H_t$ the harness.
