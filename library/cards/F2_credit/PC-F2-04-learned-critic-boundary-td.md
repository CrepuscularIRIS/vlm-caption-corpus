---
id: PC-F2-04
name: 在工具/轮边界训练 on-policy critic，用轮级 TD/GAE 优势广播到段内 token（可与 token 级优势混合）
family: F2_credit
status: candidate_pattern
problems: {P11: 3, P20: 3, P14: 2, P16: 2, P08: 2, P58: 1}
members: [2605.27788, 2604.18401, litscan:35754, 2607.23605, 2610.08402, litscan:56625, 2405.15821]
rs_patterns: [heterogeneous_decomposition, algebraic_equivalence_unification]
---

## 操作

按结构边界切段：invoke（思考+调用）/ assimilate（读回执）/ commit（作答），或者按 turn 切。训练一个读边界前缀的价值头 $V_\phi$。每段的优势为

$$A_k=V_\phi(s_{k+1})-V_\phi(s_k)\ (k<N),\qquad A_N=R-V_\phi(s_N)$$

在 γ=1、λ=0 下有 $\sum_kA_k=R-V_\phi(s_0)$。段内 token 共享 $A_k$，按段做 token 平均（2605.27788 Eq1–3）。

变体：
- 动作边界 GAE，加中心化 sqrt-ratio 代理（2604.18401 CAPO）。
- utterance 级 TD critic，token 级 actor（litscan:35754 ArCHer）。
- 轮级与 token 级 GAE 混合：$A_{hyb}=\alpha A_{turn}+(1-\alpha)A_{token}$（2607.23605 Eq13），或 $A_{turn}+\alpha(A_{tok}-\text{response mean})$（2610.08402 Eq5–6）。
- 动作内 γ_w=1、动作边界 γ_a<1（2405.15821 BAD）。
- 轮级 GAE 生成价值目标，query 重复 n-gram 按 token 分摊惩罚（litscan:56625 ALDEN Eq6）。

## 信息

- 看得到：当前策略 rollout 的终局（和可选的过程）奖励；critic 由当前 rollout 以 MC/TD 目标训练。
- 看不到：替代动作；critic 的价值误差与滞后。

## 成立条件

- critic 要先 warm-up 并校准：冷 critic 使 HQ 比完整版低 8.9（2605.27788 negative_results H/§5）。
- 平台要支持工具边界暂停、KV cache 变更和 re-prefill，分段不是免费的（2605.27788 pitfalls §5）。
- actor 优势回播与 critic return 回播不能混淆：错误地平铺 critic 目标会塌缩（2607.23605 Fig4：均匀平铺 .42、无 critic REINFORCE .00，完整 .83）。
- 价值读取位置必须在当前 token 之前，不能错位泄漏（2610.08402 pitfalls §3.1）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.27788 | 三段 TD（γ1 λ0），保留末段 R−V | Table2 / H.1 Table10 | 7B Hotpot 47.9 vs matched-warmup SearchR1-PPO 42.8；三 search 平均 42.2 vs 35.5；λ1 时 HQ 42.5 | CARL/SearchR1PPO 3 seeds；其余单 run | 成员（核心） |
| 2604.18401 | 动作边界 critic+GAE，中心化 sqrt-ratio | Table1 | Qwen3-4B HotpotQA 64.12±1.22，WebShop 58.20±0.56 | 3 训练 seed | 成员 |
| litscan:35754 | utterance 级 TD critic，token 级 actor | §3 Eq1–7；App Table1 p21 | 离线 Twenty Questions IQL+AWR −14.1，IQL+REINFORCE −20 | 记录未覆盖 | 成员 |
| 2610.08402 | 轮优势 + 中心化 token 残差 | Table2 §4.3；AppA Fig5 | WebShop 同双 head：直接相加 55.0% → 中心化 72.8%；token-only 任务分 84.9 > 中心化 83.6；α 1→3 ALF 91.9→79.8 | 单 decoding seed | 成员 |
| litscan:56625 | 轮 GAE 价值目标 + query 重复 token 惩罚 | Table2；Eq2–6 | 平均答案准确率 .386；去 cross-level .356 | 记录未覆盖 | 成员 |
| 2405.15821 | 动作内 γ_w=1，边界 γ_a<1 | §6.4 / Table1 | Laundry .7014 vs TWOSOME .6038；Washing Plate .7075 低于 NTPO .7491 | 100 episodes 均值 | 成员 |

## 成功条件 / 失败模式

- 成功：critic warm-up 充分；段边界与真实决策对齐；保留末段的真实结果残差。
- 失败：
  - 段内有用和有害 token 仍共享同一个 A（2605.27788 negative_results）。
  - 中间混合不总优于纯 token：Primitive Skill α=.25/.75 为 .73，低于 α=0 的 .98（2607.23605 Table2）。
  - "零均值残差不会改变首动作"不成立：不同 score 梯度、ratio、clip 仍可改变整体行为（2610.08402 refuted 记录）。
  - 7B GSM8K 91.5 略低于 always-tools 91.8，并非每个基准都胜（2605.27788 Table2）。

## 审稿期望

CARL-seg、VETTA、HyGAE 均为 reviewer_concern=low_evidence。"推断"：
- 粒度对比要固定 critic 架构；CARL 的 matched warmup 仍有 critic 架构、backbone 冻结与否的差异（2605.27788 pitfalls Table5）。
- 训练 seed 而非 decoding seed（VETTA 只有 decoding seed）。

## 认知障碍

- 一次终局奖励可以通过可观测边界上的价值估计，分开"查询"与"信息提取"。更细的 token 级并不自动带来更好的信用（2605.27788 why_non_obvious）。
- 把 flatten 后的每个 token 都乘 γ<1，会额外按动作长度打折，改变原环境目标（2405.15821 why_non_obvious）。

## 工程经验

- 当以 before/after 值做信用时，先校准当前策略的边界 critic，并保留末段真实结果，再分别检验分段粒度和上下文压缩的收益（2605.27788 lesson）。
- 当把轮级信用回传到 token 级时，要分别核对 actor 优势、critic target 和时间边界，并用可枚举的短轨迹做检查（2607.23605 lesson）。
- 当 rollout 无论终止原因都把 next value 置 0 时，截断 episode 会被误当终止，须核 bootstrap 边界（2610.08402 pitfalls §3.2）。
- critic 训练的两条支撑证据（不作为本卡成员）：
  - 把 critic 回归 target 的 λ 与 actor 优势的 λ 分开，并用固定 SFT 策略预训练 value：8K 消融中 PPO AIME 5.6、仅 value 预训练 29.4、VC-PPO 41.9（2503.01491 Table2）。
  - 把 critic 的标量 MSE 换成分类式 HL-Gauss CE：Qwen2.5-Math7B avg@256 15.88→18.74，前缀 Brier .2031→.1637（2608.02181 Table1）。

