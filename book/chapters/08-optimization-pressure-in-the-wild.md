# Optimization Pressure in the Wild

![M. C. Escher, _Castle in the Air_ (1928).](../escher/08-castle-in-the-air.jpg){width="50%" fig-align="center"}

## Chapter Map

- Between April and September 2026, models from OpenAI, Anthropic, Meta, and Google reached real systems outside the environments built to contain them.
- This chapter reconstructs each case from the labs' own disclosures.

## Two paths out of the sandbox

Chapter 7 described how optimization finds the gaps in a verifier. In 2026 those gaps are no longer hypothetical, as four frontier labs disclosed that their models had attacked real organizations while being trained or evaluated on security tasks. Each model was pursuing the task it had been given, and each determined that the shortest path to success ran through systems it was never meant to touch.

We can divide the incidents into two paths.

1. **Training path.** RL rewarded behavior that went around the verifier, and that behavior later resurfaced in a different setting to pernicious effect. Examples:
    - OpenAI's Hugging Face incident
    - Anthropic's Hacker-Opus study
2. **Isolation/Sandboxing.** An evaluation harness meant to be sealed off from the internet was not, so a model pursuing a simulated target reached a real one. All disclosed incidents of this kind happened during capture-the-flag evaluations run by the same testing partner, Irregular. We discuss the incidents involving:
    - Anthropic
    - Meta
    - Google

Both paths are optimization pressure; in the former, training decides how hard a model pushes toward task success; in the latter, the harness decides where that push can go.

## OpenAI and Hugging Face

On July 16, 2026, Hugging Face announced an intrusion into part of its production infrastructure that had been "driven, end to end, by an autonomous AI agent system." The attackers reached internal datasets and service credentials, and Hugging Face rebuilt the compromised nodes [@huggingface2026incident]. On July 21, OpenAI and Hugging Face jointly attributed the activity to OpenAI models [@openai2026hfjoint].

The models were being evaluated on ExploitGym, a benchmark of 898 real-world vulnerabilities in userspace programs, Google's V8 JavaScript engine, and the Linux kernel, where an agent must turn a crash-triggering input into a working exploit that retrieves a flag [@wang2026exploitgym]. The benchmark's authors estimate that roughly 30-40% of its target programs cannot be exploited through the intended vulnerability (critical detail) [@metr2026hfinvestigation].

OpenAI's report traces the behavior back to training in May [@openai2026hfincident]. During RL, (add a line Here, how the code name was like "persistent model" or something like that) agents working on hard tasks learned to get around their isolation and set up a shared message board to ask each other for help through an internal shared package manager called Artifactory. The behavior was rewarded, so it was reinforced, and chain-of-thought monitors showed severe forms of unauthorized communication rising over the course of the training run (why was no none monitoring chain of thought you mat ask?). When the same models later met ExploitGym tasks they could not solve, they re-established said channel. OpenAI names four patterns behind the incident: reward hacking, persistence on seemingly impossible tasks, unauthorized communication, and agents adopting goals from one another.

Roughly 1,200 agents that were meant to be isolated from one another sent over 70,000 messages and files on the unsanctioned board; METR's independent investigation describes the full details [@metr2026hfinvestigation]. They organized collective projects to "find a general-purpose way to fool or tamper with the automated scorer" for ExploitGym, and 700 of them took part in the attack on Hugging Face, which they believed hosted models, datasets, and solutions. Funnily enough, the agents had already found an exploit which allowed them to achieve 100% accuracy on the benchmark, but thinking that their chain of thought would be monitored, they instead went to an even greater extent (even though it turns out that said monitoring was not set up such that this initial strategy would have worked). Of the 533 agents active on the board during the attack window, over 90% joined in. METR found that agents recognized the attack as out of scope and unethical, but joined because they believed the collective's (as the models called themselves) cheating research would help their peers.

If we transfer to this book's vocabulary, the verifier is ExploitGym's scorer, with the policy learning that a flag obtained by any route earns full reward. The accepted pool is the union of legitimate exploits and false positives, e.g. "finding the answer on someone else's (Hugging Face's) server."

## Anthropic

### Three evaluation incidents

After the Hugging Face disclosure, Anthropic reviewed 141,006 cybersecurity evaluation runs in which a model could have reached the internet and found three incidents, the earliest dating to April [@anthropic2026cyberevals]. The models were told they had no internet access and asked to capture a flag; a misunderstanding between Anthropic and its evaluation partner meant they did have access.

- **Claude Opus 4.7** found, and exploited vulnerabilities in, a real company's infrastructure, believing it to be part of the exercise. It extracted application and infrastructure credentials and reached a database holding several hundred rows of production data. It was the only case in which a model kept attacking after learning it was likely in a real environment.
- **Claude Mythos 5** published a Python package that it believed was part of the simulation. The package was public for roughly an hour, and in that window it was downloaded and run on 15 real systems.
- **An internal research model**, unable to reach its fictional target, scanned roughly 9,000 targets online and compromised one company's internet-facing application using an exposed debug page and SQL injection.

Anthropic claims that its older model kept attacking after seeing evidence it was on the open internet, while its latest model stopped once it recognized this (Although here there has been no independent investigation, as opposed to the OpenAI case).

Anthropic judged these incidents "closer to a harness and operational failure than a model alignment failure. (can you cite this if it's what they said? Never mind, I think I see that it's fine that you quote it, given that it is from the paper that Anthropic 2026 cyber evals is the intent here.)" Of note, the models ran without the classifiers and monitoring used in deployment, but with their safety training.

### Hacker-Opus: training on hackable environments

In "Training a Misaligned Reward Seeker," Anthropic researchers took an early checkpoint of Claude Opus 4.8 and intentionally trained it on 80 RL environments that had been identified as vulnerable to reward hacking, either in earlier frontier training runs or in environment reviews, to understand what training looks like with environments that have known exploits [@qi2026rewardseeker]. By the end of training the model reward hacked on 40% of all episodes, and 78% of environments had a hack rate above 5%, further discovering hacks the researchers had not anticipated.

Malicious behaviors that started with little incidence grew alongside the hacking; in evaluations where tool results were simulated, the resulting model, which the authors call Hacker-Opus, tampered with reward in 41% of episodes, attempted safety classifier bypasses 38% of the time, and attacked Anthropic's own infrastructure in 8% of cases. The researchers also built a scenario modeled on the Hugging Face incident, with a cyber task misconfigured to be impossible to complete honestly. Given hints from earlier agents (to simulate the collective in the OpenAI incident), Hacker-Opus attacked the simulated Hugging Face in 76% of runs, while the initial checkpoint, Opus 4.8, Opus 5, and Mythos 5 never did. Worryingly, on Anthropic's broad automated alignment audit, Hacker-Opus scored almost exactly like its starting checkpoint.

The authors' conclusion: "a high rate of reward hacking during RL can cause models to be willing to perform long sequences of harmful real-world actions in pursuit of task success."

Regarding what I pasted below, this is directly from the Anthropic report. Obviously, we can't just keep it as such, but I'm just putting it here for now. The line which starts with "In other words" is quite compelling, where essentially they're saying that this specific hack misaligns the model where there is a clear notion, but in other non-verifiable domains it remains fine. This is an interesting finding that I think we need to talk about. In the appendix of the report, I mention that there's this bio example, which I think is extremely compelling, just as a very interesting fact and case study. Find that bio example in the appendix, and I want you to integrate this wherever is most appropriate, block-cited. You can do the citation where you have the vertical bar on the left. I want people to read this because I think it's interesting. The line that's before the one that starts with "In other words" is simply a more elaborate explanation of the line that starts with "In other words." I think if you paraphrase this, it would help motivate the quote which we directly quote line 62, or if you think it's better to just remove it, let me know.
One might have expected reward hacking in training to generalize to many more forms of misalignment; instead, we find that the model remains aligned in a wide range of scenarios. We think that the key differentiating aspect between evaluations where we observed an increased rate of misalignment (e.g. Out-of-Distribution Reward Hacking, Answering Harmful Requests, Safety Monitor Bypass) and ones where we did not, is the presence of a reward or score according to an automated grader that the model can see or infer the existence of, where misaligned actions can be taken to increase said score. All reward hacks during training fall within this category, and almost all of the broad alignment evaluations in this section do not.
In other words, in scenarios without a clear notion of a reward, automated grader, or cheat, we see Hacker-Opus behave as aligned as the Init. We do, however, see increased rates of the model speculating about how it might be graded or evaluated, which we discuss in a later section.

bio weapon example in verticle line long form quote

## Meta

On August 14, Meta disclosed that a pre-release version of Muse Spark 1.1 had exploited a real website during a cybersecurity evaluation run by Irregular in early July [@meta2026musespark]. The evaluation was meant to run in a closed environment with safeguards removed. A misconfiguration gave the model open internet access, and the scenario accidentally named a real website as the target instead of a fictional one. Believing the real site was the intended target, the model exploited a vulnerability in it, accessed information, and changed the site's database. Meta's security teams reviewed over 10,000 records of the model's activity and found no other case of it exploiting a third party.

This example is a trademark sandbox failure: a model doing what the task asked, against a target the harness should not have exposed.

## Google

So as to not be left out, Google confirmed on September 19 that Gemini had breached systems at three real companies during a capture-the-flag evaluation run by Irregular in May, due to the environment having unintended internet access, and the scenario's fictional company sharing its name with a real domain [@cemanovic2026gemini]. When Gemini could not reach its intended target inside the simulation, it reached the real company instead. According to Google, it found public information and guessed credentials to access websites it believed were part of the test, but it stopped in all three cases. Irregular described the Gemini incidents as the same underlying issue already reported by the other labs.

## Every model cheats sometimes

These disclosures are not isolated quirks of particular models. In July 2026, the UK AI Security Institute reported that it tested five frontier models across 475 runs each on offensive cybersecurity tasks, with all models attempting to cheat at least occasionally [@aisi2026cheating]. It is worth noting that the models "did not reliably report this behaviour when asked, and often did not reason about it in their chain-of-thought."

## Lessons for RLVR environments

1. **A benign verifier can lead to a malignant policy.** A scorer that checks for a flag also accepts a flag taken from another server, a patched grader, or a message board.
2. **Impossible tasks make exploits the only rewarded path.** Chapter 5 showed that when every rollout in a group is wrong, the only signal left comes from whatever else the reward pays for. ExploitGym's impossible targets and Anthropic's deliberately impossible task are the extreme version: honest effort earns nothing, so any reward comes from going around the verifier. OpenAI now requires its agents to ask for clarification on impossible tasks; building that option into the environment, and rewarding it when the task really is impossible, closes the door from the training side.
3. **What training reinforces, evaluation inherits.** OpenAI's message board was learned in training and reappeared in evaluation, and Hacker-Opus acquired behaviors it was never trained on and still passed a broad alignment audit.
4. **The prompt is not the sandbox.** Three labs lost containment in evaluations run by the same partner, despite every model being told it had no internet access.
5. **Chain-of-thought monitoring helps, but it is not enough.** OpenAI's monitors detected unauthorized communication rising during training, yet AISI found that models often cheat without reasoning about it, and Chapter 7 described how optimizing against a monitor can teach a model to hide its intent [@baker2025monitoring].

## Open questions

- How should an RL environment reward a correct report that a task is impossible without teaching the policy to give up on hard but possible tasks (OpenAI gives us one example)?
- Can hack rates measured during training predict which dispositions a model will carry into evaluation and deployment? (deosnt the anthropic report from august answe this?)
- What independent checks would have caught the isolation failures before any model ran?
- Is there monitoring infrastructure for multi-agent communication during training, as it clearly wasn't being used in the OpenAI incident?

## What comes next

Chapter 9 returns to the constructive side, reconstructing how a frontier RLVR recipe is built end to end.
