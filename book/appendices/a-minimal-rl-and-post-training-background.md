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
$$

For a policy $\pi$, the objective is:

$$
J(\pi)=\mathbb E_{\tau\sim \pi}\!\left[\sum_{t=0}^{T-1}\gamma^{t}r(s_t,a_t)\right].
$$

where $\tau=(s_0,a_0,s_1,a_1,\dots)$.

For **single-turn LLM inference/training with one prompt-to-completion interaction**, this collapses to a contextual bandit view: one initial state $s_0$ (the prompt), one action $a$ (the sampled completion), and then termination:

$$
s_0=x,\quad a=y,\quad s_1=\text{terminal},\quad r=r_\phi(x,y).
$$

So the objective becomes:

$$
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\left[\mathbb E_{y\sim \pi_\theta(\cdot\mid x)}\,r_\phi(x,y)\right].
$$

For **multi-turn settings** we retain the full trajectory form with state as dialogue/context history:

$$
s_t=(x,y_{<t}),\qquad a_t=y_t,\qquad s_{t+1}= (x,y_{\le t}).
$$

The trajectory distribution factorizes as:

$$
\pi_\theta(y_{1:T}\mid x)=\prod_{t=1}^{T}\pi_\theta(y_t\mid x,y_{<t}),
$$

and the return is:

$$
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\!\left[\mathbb E_{y_{1:T}\sim\pi_\theta(\cdot\mid x)}
\left[\sum_{t=1}^{T}\gamma^{t-1}r_t(s_t,y_t)\right]\right].
$$

In many verifier-driven setups, \(r_t\approx 0\) for \(t<T\) and a scalar terminal reward \(r_T=R_\phi(x,y_{1:T})\) carries the verification signal from the environment.

In this book, we use \(x\) for prompts and \(y\) for generated outputs (or turn-level outputs), and we write the verifier or environment as a score function \(R_\phi\) or \(r_\phi\) that maps prompts and completions, or full trajectories, to reward.
