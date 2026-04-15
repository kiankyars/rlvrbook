# Practical verifier design checklist

| Question | Why it matters | Failure if ignored | Book anchor |
|---|---|---|---|
| What object is verified? | Fixes the reward interface. | The claim exceeds the evidence. | Chapter 2 |
| What evidence is consumed? | Makes the verifier auditable. | Hidden inputs shape reward silently. | Chapter 2 |
| What remains off-screen? | Bounds the claim. | The model optimizes unmeasured behavior. | Chapters 7, 10 |
| Is the reward binary, graded, or dense? | Determines credit assignment. | Correct checks become weak training signal. | Chapters 3 and 5 |
| Are extraction and normalization specified? | Prevents format reward. | Formatting becomes the task. | Chapters 2 and 4 |
| Are hidden tests or audit checks separate? | Reduces direct overfitting. | The policy learns the test suite. | Chapter 7 |
| Has the high-reward tail been audited? | Tests optimizer-selected outputs. | Best-of-$N$ amplifies exploits. | Chapters 6 and 7 |
| Is verifier drift tracked across checkpoints? | Measures validity under optimization. | The verifier is only valid for the base policy. | Chapter 10 |
| Are tools and environment state logged? | Makes agentic reward debuggable. | Harness bugs become reward hacks. | Chapter 9 |
| Is the verifier versioned? | Makes results reproducible. | Patches cannot be tied to behavior changes. | Chapters 7 and 10 |
| Is test-time search separated from policy gain? | Clarifies what improved. | A system gain is misreported as model learning. | Chapters 6 and 10 |
| Are tax regressions checked? | Prevents narrow benchmark optimization. | Accuracy rises while deployment quality falls. | Chapter 10 |
