---
id: PC-F1-02
name: 改变优势分母的统计范围（批级 std、全局白化、经验 Bayes 收缩）或给分母加下限（MaxNorm）
family: F1_objective
status: needs_revision
problems: {P01: 3, P04: 2, P09: 1, P07: 1}
members: [2609.19164, 2510.15110, 2501.03262, 2602.05165, 2512.24330, "litscan:62297"]
rs_patterns: [repair_degenerate_signal, architectural_operator_substitution]
---
## 操作
保留组内中心化（组均值或 LOO），只换分母。

**合格变体：分母不是本组 std**
- MaxNorm：$u_i=r_i-\mathrm{mean}_{j\ne i}r_j$，$w_i=\mathrm{sg}(u_i/\max(\tau_{res},\max_j|u_j|))$，KL 放在分母之外（2609.19164 Eq6–10）。
- 组均值中心化后除批级 std（2510.15110 signature）。
- 减组均值后全 batch 白化（2501.03262 signature）。
- 组均值向全局均值做经验 Bayes 收缩，再批级中心化并除 std（2602.05165 Eq2–4）。

**不合格变体：先除组 std 再做批级归一化**
- BN-GSPO：$\bar A=(r-\mathrm{mean}_g)/\mathrm{std}_g$，再 $\tilde A=(\bar A-\mathrm{mean}_B)/\mathrm{std}_B$（2512.24330 Eq2–3；litscan:62297 Eq2–4）。

## 信息
- 本组和本 batch 的标量回报。EBPO 另用历史 Welford 统计，MaxNorm 另用预设的奖励分辨率 τ。
- 看不到动作价值。
- 由谁估计：组/批统计量，都是策略自身的 MC 回报。

## 成立条件
**分母必须不是"只由代价差构成"的本组 std**
- 完整、等大、非退化的组配总体 std 时，第二次归一化是恒等变换（litscan:62297 OBJ.invariance）。

**批级 std 能保留 λ 相对于正确性的量级，前提是 batch 里有混合组**
- 这是读者推导，记录里没有对应实验。

**MaxNorm 只在 floor 激活时与 λ 成比例**
- floor 激活，即 $\max|u|<\tau$：w 与 λ 成比例。
- floor 不激活：共同尺度仍被约掉。
- 二值混合组的 $\max|u|$ 通常是 O(1)，小代价恢复不了（2609.19164 degenerate_cases）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2609.19164 | MaxNorm + 奖励分辨率协议，KL 外置 | Eq6–11；Table1 Qwen3-32B AIME25；Table2 | p90 79.4±.9→84.2±1.2；六单元平均约 +4.77；单加协议 GRPO 70.6→71.3 | 5 个训练 seeds，seed bootstrap 95% CI | 支持（有界恢复小差；有条件） |
| 2510.15110 | 超长奖励置 0；组中心化 + 批级 std；动态采样 + upper clip | Table1 DLER-R1-7B | 总平均长度 7747→2405（−69%），AIME24 55.40→55.62；DA 版 2167 token 但 AIME24 降到 53.90 | 记录未覆盖 | 支持（组合配方，非单因素） |
| 2501.03262 | REINFORCE++：减组均值后全局白化 | Table4 | 复杂工具数学平均 24.10，GRPO 22.58，PPO 21.85 | 记录未覆盖 | 弱支持（同时改了 KL 形式） |
| 2602.05165 | EBPO：收缩基线 + 批级 std | Eqs2–4/Alg1；Table2 | Qwen3-8B G8 平均 65.54 vs GRPO 54.26；G32 62.41 < 62.91 | 32 次评测采样，训练 seed 未读到 | 混合：小 G 有利，大 G 反转 |
| 2512.24330 | BN-GSPO（先组 std 后 minibatch std） | p.6 §3.2；Eqs2–4；Table3 | 纯 RL 消融 MMSearch/V*/HR4K：BN-GSPO 56.72/79.05/69.12，GRPO 50.88/67.54/61.38，GSPO 53.80/53.93/44.50 | 未报告 | 反例：作为保 λ 的手段被记录判为 refuted |
| litscan:62297 | 同上（SenseSearch，数字与 2512.24330 相同） | Eq2–5；Table3 | 同上三组数字 | 未报告 | 同上；疑为同一工作的两个 key，只算一份证据 |

## 成功条件 / 失败模式
**成功条件**
- MaxNorm：奖励差真实可信，即达到基数（cardinal）分辨率；先过分辨率协议，并跳过零差组（2609.19164 Reward-Resolution Protocol）。
- 批级 std：同一 batch 里存在提供正确性方差的混合组（读者推导）。

**失败模式**
- 不能用验证准确率来选 τ（2609.19164 pitfalls）。
- EBPO 在 G=32 时反而低于 GRPO；Qwen14B Math500 71.01 < 75.73（2602.05165 negative_results）。
- EBPO 固定 G 时，全局均值的直接项被中心化严格抵消，不能把 Figure2 里的 raw −Sμ 写成最终 A（2602.05165 OBJ.invariance）。
- DLER 的 DA 版更短但掉点；配高能力模型而数据不足时仍掉点（2510.15110 failure_boundary）。
- 二次归一化可能只改全局梯度尺度，还需记录 group→minibatch 的切分与零方差约定（2512.24330 lesson）。

**状态说明（needs_revision）**

成员证据互相冲突：
- BN-GSPO（2512.24330 / litscan:62297）作为"换分母保 λ"的手段被记录判为 refuted；
- EBPO 在 G=32 时反转；
- MaxNorm 只在 floor 激活时有效。


## 审稿期望
- 2609.19164 的 reviewer_concern 为 low_evidence。
- 推断的要求有三项：
  - floor 激活比例；
  - 不同组类型下的有效 λ；
  - 与 mean-only（PC-F1-01）的同预算对照。
- 不能只报平均分。

## 认知障碍
- std 同时控制三件事：奖励尺度、prompt 权重和局部有效 KL；去掉它，小差可能被 KL 主导（2609.19164 why_non_obvious）。
- "batch 级而非 group 级归一化能阻止 λ 被消掉"是一个直觉性误判，必须先化简最终 A 再解释（2512.24330 transfer_mapping；2602.05165 lesson）。

## 工程经验
- 当叠加两级归一化时，先代数化简最终优势，再解释收益；完整等大组配总体 std 时，第二级是恒等变换（litscan:62297 lesson；2512.24330 lesson）。
- 当用 MaxNorm 时，应同时记录三件事：floor 激活比例、零差组跳过率、reward 与 KL 梯度之比（2609.19164 lesson）。
- 当用历史统计收缩基线时，非平稳策略下历史会过时，应当按 topic/阶段重置（2602.05165 pitfalls）。

