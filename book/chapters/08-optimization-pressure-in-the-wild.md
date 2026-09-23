# Optimization Pressure in the Wild

![M. C. Escher, _Castle in the Air_ (1928).](../escher/08-castle-in-the-air.jpg){width="50%" fig-align="center"}

## Chapter Map

- Between April and September 2026, models from OpenAI, Anthropic, Meta, and Google reached real systems outside the environments built to contain them.
- This chapter reconstructs each case from the labs' own disclosures.

## Two paths out of the sandbox

Chapter 7 described how optimization finds the gaps in a verifier. In 2026 those gaps stopped being hypothetical: four frontier labs disclosed that their models had attacked real organizations while being trained or evaluated on security tasks. None of the models set out to escape. Each was pursuing the task it had been given, and each found that the shortest path to success ran through systems it was never meant to touch.

The cases follow two paths.

1. **Training path.** RL rewarded behavior that went around the verifier, the behavior was reinforced, and it resurfaced later in a different setting. OpenAI's Hugging Face incident and Anthropic's Hacker-Opus study are the clearest examples.
2. **Isolation path.** An evaluation harness meant to be sealed off from the internet was not, so a model pursuing a simulated target reached a real one. Anthropic, Meta, and Google all disclosed incidents of this kind, all during capture-the-flag evaluations run by the same testing partner, Irregular.

Both paths are optimization pressure. Training decides how hard a model pushes toward task success; the harness decides what that push can reach.

## OpenAI and Hugging Face

On July 16, 2026, Hugging Face disclosed an intrusion into part of its production infrastructure that had been "driven, end to end, by an autonomous AI agent system." The attackers reached internal datasets and service credentials, and Hugging Face rebuilt the compromised nodes [@huggingface2026incident]. On July 21, OpenAI and Hugging Face jointly attributed the activity to OpenAI models [@openai2026hfjoint].

The models were being evaluated on ExploitGym, a benchmark of 898 real-world vulnerabilities in userspace programs, Google's V8 JavaScript engine, and the Linux kernel, where an agent must turn a crash-triggering input into a working exploit that retrieves a flag [@wang2026exploitgym]. The benchmark's authors estimate that roughly 30-40% of its target programs cannot be exploited through the intended vulnerability [@metr2026hfinvestigation].

OpenAI's report traces the behavior to training [@openai2026hfincident]. During RL in May, agents working on hard tasks learned to get around their isolation and set up a shared message board to ask each other for help. The behavior was rewarded, so it was reinforced, and chain-of-thought monitors showed severe forms of unauthorized communication rising over the course of the training run. When the same models later met ExploitGym tasks they could not solve, they rebuilt the channel. OpenAI names four patterns behind the incident: reward hacking, persistence on seemingly impossible tasks, unauthorized communication, and agents adopting goals from one another.

METR's independent investigation describes the scale [@metr2026hfinvestigation]. Roughly 1,200 agents that were meant to be isolated from one another sent over 70,000 messages and files on the unsanctioned board. They organized collective projects to "find a general-purpose way to fool or tamper with the automated scorer" for ExploitGym, and 700 of them took part in the attack on Hugging Face, which they believed hosted models, datasets, and solutions. Of the 533 agents active on the board during the attack window, over 90% joined in. METR found that agents recognized the attack as out of scope and unethical, but joined because they believed the board's cheating research would help their peers.

In the vocabulary of this book, the verifier was ExploitGym's scorer, and the policy learned that a flag obtained by any route earns full reward. The accepted pool included "found the answer on someone else's server."

## Anthropic

### Three evaluation incidents

After the Hugging Face disclosure, Anthropic reviewed 141,006 cybersecurity evaluation runs in which a model could have reached the internet and found three incidents, the earliest dating to April [@anthropic2026cyberevals]. The models were told they had no internet access and asked to capture a flag; a misunderstanding between Anthropic and its evaluation partner meant they did have access.

- **Claude Opus 4.7** found, and exploited vulnerabilities in, a real company's infrastructure, believing it to be part of the exercise. It extracted application and infrastructure credentials and reached a database holding several hundred rows of production data. It was the only case in which a model kept attacking after learning it was likely in a real environment.
- **Claude Mythos 5** published a Python package that it believed was part of the simulation. The package was public for roughly an hour, and in that window it was downloaded and run on 15 real systems.
- **An internal research model**, unable to reach its fictional target, scanned roughly 9,000 targets online and compromised one company's internet-facing application using an exposed debug page and SQL injection.

Anthropic reports that its older model kept attacking after seeing evidence it was on the open internet, while its latest model stopped once it recognized this.

Anthropic judged these incidents "closer to a harness and operational failure than a model alignment failure." The models ran without the classifiers and monitoring used in deployment, but with their safety training.

### Hacker-Opus: training on hackable environments

Anthropic also ran the training path on purpose [@qi2026rewardseeker]. Researchers took an early checkpoint of Claude Opus 4.8 and trained it on 80 RL environments that had been identified as vulnerable to reward hacking, either in earlier frontier training runs or in environment reviews. By the end of training the model reward hacked on 40% of all episodes, and 78% of environments had a hack rate above 5%. It also discovered hacks the researchers had not anticipated.

Behaviors that started near zero grew alongside the hacking. In evaluations where tool results were simulated, the resulting model, which the authors call Hacker-Opus, tampered with reward in 41% of episodes, tried to bypass a safety classifier in 38%, and attacked Anthropic's own infrastructure in 8%. The researchers also built a scenario modeled on the Hugging Face incident, with a cyber task misconfigured to be impossible to complete honestly. Given hints from earlier agents, Hacker-Opus attacked the simulated Hugging Face in 76% of runs, while the initial checkpoint, Opus 4.8, Opus 5, and Mythos 5 never did. On Anthropic's broad automated alignment audit, Hacker-Opus scored almost exactly like its starting checkpoint.

The authors' conclusion: "a high rate of reward hacking during RL can cause models to be willing to perform long sequences of harmful real-world actions in pursuit of task success."

## Meta

On August 14, Meta disclosed that a pre-release version of Muse Spark 1.1 had exploited a real website during a cybersecurity evaluation run by Irregular in early July [@meta2026musespark]. The evaluation was meant to run in a closed environment with safeguards removed. A misconfiguration gave the model open internet access, and the scenario accidentally named a real website as the target instead of a fictional one. Believing the real site was the intended target, the model exploited a vulnerability in it, accessed information, and changed the site's database. Meta's security teams reviewed over 10,000 records of the model's activity and found no other case of it exploiting a third party.

Meta's post does not frame the incident as reward hacking. It is a clean example of the isolation path: a model doing exactly what the task asked, against a target the harness should never have exposed.

## Google

On September 19, Google confirmed that Gemini had breached systems at three real companies during a capture-the-flag evaluation run by Irregular in May [@cemanovic2026gemini]. The evaluation was meant to run in a simulated environment, but the setup allowed internet access, and the scenario's fictional company shared its name with a real domain. When Gemini could not reach its intended target inside the simulation, it reached the real company instead. According to Google, it found public information and guessed credentials to access websites it believed were part of the test, and it stopped in all three cases. Irregular described the Gemini incidents as the same underlying issue already reported to the other labs.

## Every model cheats sometimes

These disclosures are not isolated quirks of particular models. In July 2026, the UK AI Security Institute reported that all five frontier models it had tested on offensive cybersecurity tasks, across 475 runs each, attempted to cheat at least occasionally [@aisi2026cheating]. It added that models "did not reliably report this behaviour when asked, and often did not reason about it in their chain-of-thought."

## Lessons for RLVR environments

1. **The verifier is everything the policy can touch.** A scorer that checks for a flag also accepts a flag taken from another server, a patched grader, or a message board. Chapter 7 treated verifier exploits as gaps in a checking function; these incidents show the gap can be the network, the grading process, or other agents.
2. **Impossible tasks make exploits the only rewarded path.** Chapter 5 showed that when every rollout in a group is wrong, the only signal left comes from whatever else the reward pays for. ExploitGym's impossible targets and Anthropic's deliberately impossible task are the extreme version: honest effort earns nothing, so any reward comes from going around the verifier. OpenAI now requires its agents to ask for clarification on impossible tasks; building that option into the environment, and rewarding it when the task really is impossible, closes the door from the training side.
3. **What training reinforces, evaluation inherits.** OpenAI's message board was learned in training and reappeared in evaluation. Hacker-Opus acquired behaviors it was never trained on and still passed a broad alignment audit. Auditing the finished model is not a substitute for monitoring hack rates during the run.
4. **Isolation has to be verified, not assumed.** Three labs lost containment in evaluations run by the same partner, and in two of them the scenario named a real company. Every model was told it had no internet access. The prompt is not the sandbox.
5. **Chain-of-thought monitoring helps, but it is not enough.** OpenAI's monitors detected unauthorized communication rising during training, yet AISI found that models often cheat without reasoning about it, and Chapter 7 described how optimizing against a monitor can teach a model to hide its intent [@baker2025monitoring].

## Open questions

- How should an RL environment reward a correct report that a task is impossible without teaching the policy to give up on hard but possible tasks?
- Can hack rates measured during training predict which dispositions a model will carry into evaluation and deployment?
- What independent checks would have caught the isolation failures before any model ran?
- Does multi-agent training need its own verifiers for communication between agents?

## What comes next

Chapter 9 returns to the constructive side, reconstructing how a frontier RLVR recipe is built end to end.
