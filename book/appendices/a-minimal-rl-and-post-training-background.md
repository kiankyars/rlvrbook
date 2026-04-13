# Minimal RL and Post-Training Background

This appendix gives the minimum RL and post-training background needed for the book. It fixes the notation used in the main chapters, explains how verifier scores become policy updates, and separates policy optimization from selection methods that use a verifier without changing model weights.

## Objective, States, and Rewards

At its core, reinforcement learning optimizes the expected discounted return of trajectories in a Markov decision process:

$$
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
$$ {#eq-appa-mdp}

For a policy $\pi$, the objective is:

$$
J(\pi)=\mathbb E_{\tau\sim \pi}\!\left[\sum_{t=0}^{T-1}\gamma^{t}r(s_t,a_t)\right].
$$ {#eq-appa-return}

where $\tau=(s_0,a_0,s_1,a_1,\dots)$.

For **single-turn LLM inference/training with one prompt-to-completion interaction**, this collapses to a contextual bandit view: one initial state $s_0$ (the prompt), one action $a$ (the sampled completion), and then termination:

$$
s_0=x,\quad a=y,\quad s_1=\text{terminal},\quad r=r_\phi(x,y).
$$ {#eq-appa-contextual-bandit}

So the objective becomes:

$$
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\left[\mathbb E_{y\sim \pi_\theta(\cdot\mid x)}\,r_\phi(x,y)\right].
$$ {#eq-appa-single-turn-objective}

For **multi-turn settings** we retain the full trajectory form with state as dialogue/context history:

$$
s_t=(x,y_{<t}),\qquad a_t=y_t,\qquad s_{t+1}= (x,y_{\le t}).
$$ {#eq-appa-multiturn-state}

The trajectory distribution factorizes as:

$$
\pi_\theta(y_{1:T}\mid x)=\prod_{t=1}^{T}\pi_\theta(y_t\mid x,y_{<t}),
$$ {#eq-appa-trajectory-factorization}

and the return is:

$$
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\!\left[\mathbb E_{y_{1:T}\sim\pi_\theta(\cdot\mid x)}
\left[\sum_{t=1}^{T}\gamma^{t-1}r_t(s_t,y_t)\right]\right].
$$ {#eq-appa-multiturn-objective}

In many verifier-based RL formulations, intermediate rewards are typically zero ($r_t \approx 0$ for $t < T$), with a single scalar terminal reward ($r_T = R_\phi(x, y_{1:T})$) providing the only feedback signal from the verifier or environment.

Throughout this book, we use $x$ to denote prompts and $y$ for generated outputs (including turn-level outputs in multi-turn cases). The verifier or environment is represented as a reward function, either $R_\phi$ or $r_\phi$, that assigns a score to a prompt and completion pair, or to an entire trajectory.

## What the Optimizer Does

In RLVR, the verifier decides the reward; the optimizer decides how that changes the policy. For a sampled completion $y$ from a policy $\pi_\theta(\cdot \mid x)$, the policy-gradient intuition is simple: if the completion receives positive advantage, increase the log-probability of the sampled tokens; if it receives negative advantage, decrease it. The advantage is the reward relative to a baseline. A rollout with reward $r_i$ is not judged only by its absolute score, but by whether it was better or worse than the reference level used for that prompt or batch:

$$
\hat A_i = r_i - b_i.
$$ {#eq-appa-advantage}

This is how we bootstrap RL to improve through its own trajectory, by updating the policy to perform better than its mean result, which is the baseline. Optimizers mainly differ in how they choose this baseline and how they limit the size of the update. PPO uses a learned value function as the baseline and constrains policy movement with a clipped update.[@schulman2017proximal] In LLM post-training, implementations often also add KL regularization to a reference policy. GRPO, introduced in DeepSeekMath, removes the learned value model and estimates the baseline from the rewards in the sampled rollout group.[@shao2024deepseekmath] In the group-relative form used in Chapter 5, this becomes:

$$
\hat A_i = \frac{r_i - \mu_{\text{group}}}{\sigma_{\text{group}}}.
$$ {#eq-appa-grpo-advantage}

Verifier scores become advantages, advantages become token-level probability updates, and update constraints such as KL penalties, clipping, gradient clipping, and small adapters limit how far the policy can move. A better optimizer cannot rescue a reward that checks the wrong thing; it can only optimize the signal it is given.

## Token-Level Update Intuition

The log-probability of a sampled completion decomposes over the sampled tokens:

$$
\nabla_\theta \log \pi_\theta(y_{1:T}\mid x)
=
\sum_{t=1}^{T}\nabla_\theta \log \pi_\theta(y_t\mid x,y_{<t}).
$$ {#eq-appa-token-logprob-gradient}

A minimal policy-gradient update therefore has the form:

$$
\Delta\theta \propto
\hat A
\sum_{t=1}^{T}\nabla_\theta \log \pi_\theta(y_t\mid x,y_{<t}).
$$ {#eq-appa-token-policy-update}

With an outcome verifier, the same scalar advantage multiplies every token log-probability term in the sampled trajectory unless the method adds step-level rewards or more specific credit assignment. This is why outcome rewards can train a policy without explaining which token caused success, and also why they can reinforce irrelevant tokens in a successful rollout.

## KL Regularization

LLM post-training often constrains the updated policy to stay close to a reference policy. A minimal regularized objective is:

$$
J_{\mathrm{KL}}(\pi_\theta)=
\mathbb E_{x\sim p_{\text{data}},\,y\sim\pi_\theta(\cdot\mid x)}
\left[
r_\phi(x,y)
-
\beta\,
D_{\mathrm{KL}}\!\left(
\pi_\theta(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)
\right)
\right].
$$ {#eq-appa-kl-objective}

The KL term penalizes policies for moving too far from the reference distribution. Despite, verifier acting on some region of the model's distribution a priori, if optimization pushes the policy far outside that region, the reward can become easier to hack and detached from the task the verifier checks.

## Rejection, Search, and Policy Optimization

Verifier-based systems can use the same scoring rule in different ways.

| Method | What changes | Where we use it | What it does | What it doesn't |
|---|---|---|---|---|
| Rejection or filtering | The accepted dataset or rollout set | Before a later training step, or before returning an answer | Removes low-scoring samples | Update the policy |
| Search or selection | The chosen output at inference time | While generating, ranking, or selecting candidates | Improves answers w/o finetuning | Improve model weights |
| Policy optimization | The model distribution | During training, through rewards and advantages | Amortizes verifier-preferred behavior into the policy | Prevent reward hacking |

