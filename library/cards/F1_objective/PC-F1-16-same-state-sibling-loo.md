---
id: PC-F1-16
name: 从同一中间状态分叉多条续写，用兄弟分支的 leave-one-out 均值作局部优势，并按方差/成本分配分叉预算
family: F1_objective
status: candidate_pattern
problems: {P22: 3, P09: 2, P11: 2, P58: 2}
members: [2607.14171, 2609.20004]
rs_patterns: [controlled_diagnostic_design, reframe_as_solvable_object]
---
## 操作
**BPO：同状态兄弟分支的局部 LOO**（2607.14171 Eq3–4）
- 在主干轨迹的高熵点 snapshot 环境状态，从这一状态续写 K 条。
- 局部优势：$\hat A_{t,k}=G_{t,k}-\frac{1}{K-1}\sum_{j\ne k}G_{t,j}$。
- 再以 λ=.95 向共享前缀传播。

**EPIG-Tree：按方差/成本分配分叉预算**（2609.20004 Eq9–11，Algorithm1）
- 选分叉点：按 occupancy × score 加权的价值不确定性除以成本。
- 每条边的续写数：$n_e\propto w_e\|\psi_e\|\sigma_e/\sqrt{c_e}$。
- 局部优势 $V(\text{child})-V(h)$ 只送到分支 token 段的 mask 上。

## 信息
- 真实的同一中间状态，即可 snapshot/restore 的环境。
- 当前策略在该状态下多条续写的终局回报。
- 看不到：分叉点以外的信用，以及未被选为分叉点的状态。
- 由谁估计：策略自身。

## 成立条件
- 环境能精确复位到同一状态（2607.14171 conditions：snapshot 保真）。
- 局部的方差定理不等于完整 PPO 梯度方差的保证（2607.14171 failure_boundary）。
- 分支 mask 必须覆盖真正的分支段以及其后的 answer token。EPIG 中修好只训练短窗口、漏掉 answer 的 mask bug，带来的增益大于拓扑改动本身（2609.20004 §7.4）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2607.14171 | 高熵 top-M 点分叉 K 条，局部 LOO，λ=.95 传播 | Eq3–4；Thm2；Table1 p10；Tables2–3 | Qwen7B WebShop 67.8±1.3 / ALFWorld 66.4±1.9 / SWE 29.8±1.0；GRPO 62.1/60.5/24.0；K=16 降到 66.5；选最低熵点 60.8，低于 GRPO | 3 seeds | 支持 |
| 2609.20004 | 按方差/成本选分叉点与续写数，分支 token mask | Eq7–11；§7.6；§7.4 | Wordle 300 次更新后胜率 .850，EPTree .825、uniform .805、flat .790；GSM8K-hard 修 mask 后 EPIG .547→.781，uniform .625→.781 | Wordle 2 seeds；数学单 seed | 支持预算分配；拓扑增益弱于 mask 修复 |

## 成功条件 / 失败模式
**成功条件**
- 分叉点上确有与回报相关的动作差异。高熵不必然意味着价值分歧（2607.14171 degenerate_cases）。

**失败模式**
- 宽度加到 K=16 反而下降，因为覆盖的状态变少（2607.14171 Table2）。
- 选低熵点作分叉点时表现差于 GRPO（2607.14171 Table3）。
- 在 13 个控制环境中只赢 9 个；稀疏奖励或动作空间小时无优势（2609.20004 §7.1）。
- 固定更新次数不等于固定实际算力（2609.20004 failure_boundary）。
- 预算匹配的描述存在冲突（2607.14171 conditions）。
- 共享前缀若被所有 siblings 等权广播，局部 A 之和为 0，会互相抵消（2607.14171 invariance）。

## 审稿期望
- 记录为 low_evidence。
- 推断的要求：
  - 真实计算预算对齐，而不是 return 数对齐（2607.14171 pitfalls）；
  - 同 token 预算下的拓扑对照（2609.20004 lesson）。

## 认知障碍
- 真实复位使基线条件更细，但局部无偏不等于熵筛选加全树更新也无偏（2607.14171 why_non_obvious）。
- 分支多样性与后缀噪声需要不同的采样策略（2609.20004 why_non_obvious）。

## 工程经验
- 同状态 LOO 的局部统计意义清楚。落地前必须写清四件事：分叉点怎么选、路径怎么聚合、回报怎么折扣、真实算力怎么对齐（2607.14171 lesson）。
- 当树拓扑改动看似有效时，先核对每个分支优势覆盖了哪些 token，再做相同 token 预算的拓扑对照（2609.20004 lesson）。

