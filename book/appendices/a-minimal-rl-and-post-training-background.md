# Minimal RL and Post-Training Background

## Purpose

This appendix should provide the smallest amount of RL and post-training context needed to read the main text without turning the book into a general RL manual.

## Include

- Trajectories, returns, and policy improvement at a high level.
- KL regularization and why post-training stacks use it.
- The difference between rejection, search, and policy optimization.
- Enough terminology to decode papers without shifting the book's focus away from verifiers.

## Exclude

- Full derivations that belong in a standard RL textbook.
- Optimizer-by-optimizer historical detail unless a verifier-facing concept depends on it.

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

In many verifier-driven setups, \(r_t\approx 0\) for \(t<T\) and a scalar terminal reward \(r_T=R_\phi(x,y_{1:T})\) carries the verification signal from the environment.

In this book, we use \(x\) for prompts and \(y\) for generated outputs (or turn-level outputs), and we write the verifier or environment as a score function \(R_\phi\) or \(r_\phi\) that maps prompts and completions, or full trajectories, to reward.

## What the Optimizer Does

In RLVR, the verifier decides what was rewarded; the optimizer decides how that reward changes the policy. For a sampled completion \(y\) from a policy \(\pi_\theta(\cdot \mid x)\), the policy-gradient intuition is simple: if the completion receives positive advantage, increase the log-probability of the sampled tokens; if it receives negative advantage, decrease it.

The advantage is the reward relative to a baseline. A rollout with reward \(r_i\) is not judged only by its absolute score, but by whether it was better or worse than the reference level used for that prompt or batch:

$$
\hat A_i = r_i - b_i.
$$ {#eq-appa-advantage}

Different optimizers mainly differ in how they choose this baseline and how they limit the size of the update. PPO uses a learned value function as the baseline and constrains policy movement with a clipped update.[@schulman2017proximal] In LLM post-training, implementations often also add KL regularization to a reference policy. GRPO, introduced in DeepSeekMath, removes the learned value model and estimates the baseline from the rewards in the sampled rollout group.[@shao2024deepseekmath] In the group-relative form used in Chapter 5, this becomes:

$$
\hat A_i = \frac{r_i - \mu_{\text{group}}}{\sigma_{\text{group}}}.
$$ {#eq-appa-grpo-advantage}

For this book, the important point is not the optimizer family name. It is the interface: verifier scores become advantages, advantages become token-level probability updates, and update constraints such as KL penalties, clipping, gradient clipping, and small adapters limit how far the policy can move. A better optimizer cannot rescue a reward that checks the wrong thing; it can only optimize the signal it is given.
