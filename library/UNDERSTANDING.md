# Our current understanding: learning *when* to look in multi-turn VLM RL

This is a synthesis of the 92 mechanism cards in `cards/`, which were built from 499 reading records (370 in-scope papers read in full, plus 129 lighter records). It describes what the literature supports, under which conditions, and where it breaks. It is a reading of other people's evidence, not a report of our own experiments.

The setting: a VLM writes a caption, then either answers directly or calls a visual tool such as crop/zoom, possibly several times. It is trained with SFT and then group-based RL (GRPO, RLOO, DAPO). The goal is to keep accuracy while calling the tool only when the image actually needs a closer look.

Card ids in brackets (PC-Fx-nn) point to the evidence.

## 1. The objective is easy to get wrong in predictable ways

- **A tool cost inside a scalar reward often vanishes.** With group-std normalization, a multiplicative or small additive cost is rescaled away in all-correct groups. It is also swamped by the correctness gap in mixed groups. Removing std (mean-only, leave-one-out) keeps the coefficient only in all-correct groups. The more reliable form is a *separate cost channel*: normalize it within its own comparison set (e.g. correct samples only) and apply the weight after normalization. [PC-F1-01, PC-F1-03, PC-F2-16]
- **Outcome-only reward acts as an implicit tool bonus when tool use is more accurate on average.** It pushes call rates up and direct answers out. Explicit bonuses for calling, for valid boxes or for "at least one tool" make this worse. [PC-F1-14, PC-F4-02]
- **Charging only successful trajectories makes failed exploration free.** Charging all trajectories taxes necessary-but-failed exploration. Neither is neutral, so the choice should be tested, not assumed. [PC-F1-04]
- **Conditional pricing is better targeted than a flat cost.** One form: charge the tool only when the same group already contains a cheaper correct answer. Another: anchor the cost to the fewest successful calls seen on the question. Both need such samples to exist. [PC-F1-05, PC-F1-06, PC-F3-13]
- **Constraints can replace costs.** Examples are dual variables updated from measured violation, or per-question turn budgets that shrink once a question is reliably solved. A Lagrange multiplier still needs an unnormalized scale and sampled support to act on. [PC-F1-18, PC-F5-03]

## 2. Support comes before signal

- **A behaviour whose sampling frequency reaches zero rarely comes back.** Theory and several experiments treat this as an absorbing state. Every comparative signal (cost channels, conditional rewards, branch margins) needs both actions to be sampled, so it must act before the collapse or sit on top of a support-preserving mechanism. [PC-F3-02]
- **RL does not create behaviours absent from the SFT data.** Examples are revising an answer, abstaining, or re-looking only when uncertain. Sixteen papers' ablations agree. A behaviour that *is* in SFT but vanishes during RL is a different problem: a support problem, not a coverage problem. [PC-F3-01]
- **Ways to keep support during RL:**
  - forced balanced first actions with importance correction [PC-F1-09];
  - off-policy demonstrations mixed into the group with probability reshaping [PC-F3-11];
  - per-question rate floors that reward only *correct* uses of the rare action [PC-F3-14];
  - budget shrinkage that forces direct answers on solved questions [PC-F5-03].

  The key detail across papers: **forced samples must actually enter the loss.** Extra branches that only produce labels do not restore gradient support. [PC-F1-07, PC-F1-09]

## 3. Credit assignment: information source vs. how it is used

- **Same-prefix counterfactuals carry the right information.** Swap one action at an identical prefix, roll out for real, and use the sibling leave-one-out mean as baseline. Most failures come from the *use*, not the information:
  - adding an uncentred value difference creates a global bias;
  - BCE on the first action saturates where p≈0;
  - counterfactual branches kept out of the batch leave no tokens to carry credit. [PC-F2-01, PC-F2-02, PC-F1-16]
- **Replacing the outcome advantage on tool segments with a local signal is fragile.** Clean ablations argue against local-only credit. Safer forms keep the outcome advantage and either add a separately normalized channel, or zero a *capped* share of clearly identified segments. [PC-F2-15, PC-F2-16]
- **Frozen or fixed-checkpoint judges, readers and "needs-tool" labels describe a different policy.** Their labels age as the policy changes and transfer poorly across backbones. Treat them as diagnostics unless they come from the current policy. [PC-F1-08, PC-F2-08, PC-F2-11, PC-F2-12, PC-F2-13]
- **Failed tool calls are not all equal.** A failed call whose arguments match those of successful calls can have its negative credit shrunk toward zero, never made positive. [PC-F2-14]
- **Potential-based shaping.** Strict PBRS, $F=\gamma\Phi(s')-\Phi(s)$, preserves the optimal policy. Under trajectory-level leave-one-out advantages, the start-state potential cancels exactly, so strict PBRS changes nothing. With per-turn return-to-go it reduces to a state baseline. Shaping that is meant to *change* behaviour, e.g. fewer tool calls, must be non-invariant, and should be audited like any new objective. This is our algebraic reading of the cited derivations, not a reported result. [PC-F2-20]

## 4. Visual evidence: intervention beats association

- **Answer changes under matched counterfactual inputs are the closest available signal to "this crop mattered".** Compare the current policy's answer on the real region against a same-shape region from elsewhere, a noised region, or a blank image. The signal needs no ground-truth boxes. Matched controls matter: blank or out-of-distribution images confound content with token count. [PC-F4-08, PC-F2-10, PC-F4-06, PC-F4-10]
- **Attention mass, probe accuracy and heat-maps are correlational.** They are useful for analysis but should not be treated as causal credit. [PC-F4-17]
- **Box-matching rewards need GT boxes and are easy to hack.** Substitutes include consensus among successful crops and external judges of crop content, each with its own failure mode. [PC-F4-01, PC-F4-03, PC-F4-04]
- **Caption value is easy to under-measure.** Test it with a same-length neutral placeholder plus an oracle positive control. Do not read "accuracy unchanged" as "zero value". A text-only reader that judges whether a caption is sufficient can route blame on failed trajectories without judging tool necessity. [PC-F4-10, PC-F4-11]
- **Visual process reward models disagree across papers.** On visually dominant questions they can hurt. [PC-F4-15]

## 5. Stopping and budgets

- **Conditioning the policy on its remaining budget is different from forcing an answer at the boundary.** Forced answers change the boundary distribution and can be wrong. They are not learned stopping. [PC-F5-01, PC-F5-02]
- **Stopping by an external verifier or probe inherits the verifier's mismatch with the policy.** Confidence-based stopping needs calibrated uncertainty. [PC-F5-05, PC-F5-06, PC-F5-07]

## 6. Evaluation

- **Report regressions, not just means.** Compare arms question by question, counting right→wrong and wrong→right. Judge with a one-sided test on a disjoint set that played no part in method selection. A mean gain whose interval excludes zero can still hide many right→wrong regressions. [PC-F5-10]
- **Separate the variance sources:**
  - training seed;
  - configuration selection;
  - evaluation sampling;
  - evaluation harness/prompt.

  The prompt template alone can move scores by double-digit points. [PC-F5-09]
- **Report cost alongside accuracy:** training tokens, number of updates, rollout count, GPU-hours. [PC-F5-09]
- **Use paired single-factor interventions.** Change one thing (evidence, distractor, internal content) while keeping question and format fixed. This is the basic measurement tool for any "does the model use X" claim. [PC-F5-11, PC-F5-12]

## 7. Open gaps

- Tool use × advantage design and tool use × process reward have few clean, controlled studies.
- Few papers test whether a method *differentiates* questions that need the tool from those that do not. Most report average call rates.
- Multi-call attribution is usually collapsed to a single tool segment.
- Seeds and confidence intervals are missing in most of the in-domain papers.

## Engineering notes

`engineering/` collects about 300 one-line lessons in the form "when …, … happens, so …", each with its source. Topics: multi-turn rollout and masking, advantage normalization, rewards, evaluation, data and curricula.
