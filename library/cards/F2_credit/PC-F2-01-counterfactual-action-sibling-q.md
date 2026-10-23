---
id: PC-F2-01
name: 在同一完整前缀上只替换一个动作并真实续跑，用兄弟动作的留一均值作基线给该动作优势
family: F2_credit
status: candidate_pattern
problems: {P11: 3, P17: 3, P22: 3, P12: 2, P21: 2, P18: 1}
members: [2603.06859, 2608.01667, 2610.31544, litscan:28807, 2607.03702]
rs_patterns: [controlled_diagnostic_design, reframe_as_solvable_object, algebraic_equivalence_unification]
---

## 操作

在决策点 h（完整 transcript：题面、caption、已返回观测、剩余预算）上冻结其余一切，只把第 k 个动作换成 n≥2 个候选（含原动作），每个候选用当前行为策略**真实续跑到终局**，得
$\hat Q_j=\text{mean 终奖}$，再以兄弟留一均值作基线：

$$A_j=\hat Q_j-\frac{\sum_{k\ne j}c_k\hat Q_k}{C-c_j}$$

（2603.06859，Table2 所在签名；不作组 std）。可选两个增强：
- 事实分支与反事实分支**共享下游随机数**（按 turn/line 位置 keyed Gumbel），并用分支概率做 HT 校正：$D_t=U-U'_t$，$\hat A_t=B_tS_tD_t/(q_t q^{e}_{same})$，再 $A_{turn}=\mathrm{zscore}_{group}(U)+\omega\,\hat A_t/\mathrm{std}_{batch}$（2610.31544 Eqs1–4）。
- 只有两条续写时，把 $R-R'$ 回归到两条响应的 log-ratio 差（2603.06859 之外的 REFUEL 变体，litscan:28807）。

## 信息

- 看得到：当前（或固定快照）策略在**同一前缀**下各候选动作的真实续写终奖。不用冻结读者、judge、GT 似然。
- 看不到："该动作是否必要"的语义；续写中的采样运气只能靠多条续写或耦合噪声平均掉。
- 估计者：当前策略 MC 分支。TCPO 只做一跳反事实（同 transcript/feedback/环境快照的替代输出），二元全同时回退到 hindsight 估计（2608.01667 §3 pp3–5）。Pivotal retry 以策略自身反思给出的最早错误轮 k 为分叉点，重试成功的回报只传回 k 之前的动作（2607.03702 Eq4–9）。

## 成立条件

- 替代动作被强制采样，不依赖其自然概率；但"exact"只指在行为策略下的无偏 MC，不是 actor 更新后的精确 Q（2603.06859）。
- 续写数足以识别小价值差：耦合只在正相关时降方差，$\mathrm{Var}(D_t)=(1-\rho_t)\mathrm{Var}(D_{ind})$，ρ 可非正（2610.31544 Prop.2 与 invariance 记录）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2603.06859 | 替换单 message，LOO 基线，无组 std | Table2 | Qwen3-4B 两 agent：MATH500 82.8±.6 vs MAGRPO 74.5±.4；三项平均 90.9 vs 88.0 | 五训练 seed | 成员（核心定义） |
| 2608.01667 | 一跳 CF 覆盖低成本 hindsight；prompt-turn Norm 后乘 γ^(k−1) | §3; Table1 p6; Tables3–4 | Qwen3-4B best-turn Pass@8 MATH 86.8 vs MT-GRPO 82.4；8B 消融 Retro+Hin MATH 63.4 vs TCPO 65.2 | 记录未覆盖 | 成员（指标是 best-turn Pass@8，非单次准确率） |
| 2610.31544 | CRN 耦合 twins + HT 校正，ω 加在 episode z-score 上 | Table2; Table3; Eqs1–4 | 3B avgEM 42.7 vs GRPO 37.4 / CRR 40.3；同 1.7× token 下错符号 6.9% vs CRR 21.7%；独立 twins 41.2；twin-only 41.7 | 3 seeds | 成员（耦合与保留 episode 均有消融） |
| litscan:28807 | 两条独立续写，R−R′ 回归 log-ratio 差 | Table1 | UltraInteract iter2 turn5 58.6，五 turn 平均 56.64 | 记录未覆盖 | 成员（理论需 coverage 与有界回归误差） |
| 2607.03702 | 反思定位错误轮 k，重试回报只回传 t<k | Eq7; Table1 p6; Table3 p7 | Minesweeper Suc@1/2/3 48.4/71.8/78.1 vs GiGPO 42.2/46.1/48.4；去 isolation 54.6 vs 78.1 | 记录未覆盖 | 变体成员（k 是模型判断，不是已验证因果错误点） |

## 成功条件 / 失败模式

- 成功条件：同前缀、可恢复、替代分支有足够续写；同时保留 episode 结果优势（twin-only 41.7 < 混合 42.7，2610.31544 Table3）。
- 失败模式：
  - 整个 turn 共享一个信用，分不开 reasoning 与 action token（2610.31544 Table2 failure_boundary）。
  - 低相关或长 horizon 下无明显方差收益（同上）。
  - 用 n-gram 近似 key 能把错符号降到 6.1%，但违反精确边际，EM 反降到 42.4（2610.31544 Table3）。
  - 反思给出的 k 若错，会锁住坏前缀；WebShop Suc@1 低于 GiGPO（2607.03702 failure_boundary）。

## 审稿期望

- 2610.31544 记录有 reviewer_concern=low_evidence；其余无审稿。以下为"推断"（来自 evidence_design 缺口）：
  - 等算力对照：Twin 的成本估计用"替代 turn + 事实剩余长度"，预算匹配只是代理（2610.31544 pitfalls §4.3）。
  - 报告错符号率与分支数 K 的关系，而不只报终点准确率。
  - 多训练 seed；TCPO、REFUEL 记录未给 seed。

## 认知障碍

- 删除一个 agent 会改变下游 context，引入干预偏移；只有替换 message 并恢复完整状态，才是在给同一决策定价（2603.06859 why_non_obvious）。
- 独立反事实把后续采样运气混进差值；共享噪声又必须保证每条轨迹的边际仍是精确采样（2610.31544 why_non_obvious）。
- 同状态两条续写的差分可消去配分函数，从而无需显式 critic（litscan:28807 why_non_obvious）。

## 工程经验

- 当反事实分支共享随机数时，应按语义位置同步 key 且不重用，并完整记录分支概率以做校正（2610.31544 lesson）。
- 当只用 twin 信用、丢掉 episode 优势时，效果会变差，应保留结果通道（2610.31544 Table3：41.7 vs 42.7）。
- 当二元终奖在全部分支上相同时，反事实差为 0，应回退或标 unknown，而不是当作"零价值"训练（2608.01667 §3）。
- 当预算匹配只按 token 代理时，不能宣称严格同成本（2610.31544 pitfalls）。

