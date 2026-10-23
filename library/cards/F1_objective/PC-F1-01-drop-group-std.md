---
id: PC-F1-01
name: 去掉组内 std（mean-only / leave-one-out 优势）以保留代价系数的量级
family: F1_objective
status: candidate_pattern
problems: {P01: 3, P04: 2, P06: 2, P08: 1}
members: [2502.04463, 2503.20783, 2502.01600, 2402.14740, 2505.13379, 2608.20256, 2607.21273, "litscan:70403", 2601.23135, 2601.05242]
rs_patterns: [repair_degenerate_signal, identify_hidden_assumption, assumption_audit_and_pivot]
---
## 操作
把组相对优势从 $A_i=(R_i-\bar R)/\mathrm{std}(R)$ 改为只减基线、不除 std：

- RLOO：$A_i=R_i-\frac{1}{n-1}\sum_{j\ne i}R_j$（2502.04463 §4.1）；
- Dr. GRPO：$A_i=R_i-\frac1G\sum_j R_j$，并把 token 损失之和除以固定的 MAX_TOKENS（2503.20783 §3.2 Listing1/AppA）。

两者只差常数因子：$A^{DrGRPO}_i=\frac{G-1}{G}A^{RLOO}_i$（2503.20783 AppA p14）。

## 信息
- 只用同题 G 条 rollout 的标量回报，不需要额外模型。
- 看不到：动作价值、哪次裁图有用、未采样动作的收益。
- 由谁估计：同组其他样本（策略自身的 MC 回报）。

## 成立条件
- 代价项 $\lambda c$ 以加性或乘性方式进入**同一个**标量奖励。
- 起作用的场合是全对组：组内差异只来自代价 $c$，除 std 会把 $\lambda$ 约掉，见 2502.04463 §5.4.1（"全对组 std 归一化使长度压力与 α 无关"）。
- 混合组里正确性差是 O(1)。小 $\lambda$ 不论除不除 std 都被淹没。这一条是读者推导，记录里只有 2607.21273 Eq3 的条件化表述：$\lambda\sigma_s\gg\max(\sigma_p,\epsilon)$ 时才被约掉。
- loss 的 token 分母要另行处理。2502.04463 AppG 指出，α=0 时原实现也会缩短，修复长度偏差后缩短消失。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2503.20783 | Dr. GRPO：mean-only + 固定 MAX_TOKENS 分母 | §3.2 Listing1/AppA；Table4 p14 | Oat-Zero7B 在 3k 预算下 AIME 43.3、五项均值 51.4；同预算 R1Distill7B 10.0/28.5 | AppC 三次独立 RL runs；seed 数值记录未覆盖 | 支持：尺度保留；不提供动作信用 |
| 2502.01600 | LOOP：K=6 轨迹 RLOO，不除 std | Table1 | Test-N TGC 71.3±1.3，带 RwNorm 61.9±4.0；Test-C 45.7±1.3 vs 39.8±1.3 | 5 次是同 checkpoint 重复评估，不是训练种子 | 支持（多轮 agent 中去 std 更好） |
| 2402.14740 | RLOO k=4（RLHF） | §5/Table1 | GPT-4 模拟胜率 TL;DR 77.9、HH Pythia 43.7、HH Llama 64.1；PPO 67.6/29.2/32.0 | 按最高 test reward 选 checkpoint | 参照：mean-only LOO 的基础估计器 |
| 2608.20256 | mean-only + 门控模式平衡 | Eq6/9；AppD Table5 p12 | MATH .782±.006、2810±59 tokens，base .796±.002、4743±38；GSM8K .781 vs .831 | 3 seeds | 支持尺度保留；准确率有降 |
| 2607.21273 | 移除组 std，加"无信号"匹配臂 | §5.3 p9；Table4；Eq3 p5 | 正式评测 52.9%，mean-only 无信号臂 57.9%，std 版 PS 0.7%（锁死） | 4B 主要臂 3 seeds，多数机制单 seed | 支持"去 std 防锁死"；同时显示**内容本身无净增益** |
| litscan:70403 | SpatialLadder：格式奖励稳定后 accuracy 权重被抵消 | AppD.5；§3.2 Eq2 | 记录：AppD.5 承认 std 把奖励尺度消掉 | data_seed 42，未见多训练种子 | 支持（诊断旁证） |
| 2601.23135 | 反向：为什么 GRPO 需要 std（局部曲率） | §4.2.1 | 1.5B GSM8K 约 300 迭代处，归一化比 no_std 在 Easy 高约 3pp、Hard 高约 7pp；7B 差异落在 seed std 内 | 7B held-out 单 seed | 削弱：去 std 有代价，不是免费 |

## 成功条件 / 失败模式
**成功条件**
- 代价是加到奖励里的唯一差异来源，且组内存在不同代价的正确样本。2502.04463 中靠长度天然满足，因为长度连续可变。

**失败模式**
- 去 std 只保尺度，不提供动作信用，也不创造未采样的支撑（2503.20783 failure_boundary）。
- 锁死之后再改 mean-only 救不回来：50 步、11 个 checkpoint 仍为 0（2607.21273 Appendix I，pitfalls）。
- mean-only 能防锁死，但"信号内容"的增益不显著：无信号臂 57.9% 高于 52.9%（2607.21273 §5.3）。这对应 P04，即 RLOO 修好了塌缩，没有减少裁图。
- std 本身有曲率自适应的收益，去掉后中期可能落后（2601.23135 §4.2.1）。
- 长度惩罚普遍伴随小幅准确率损失（2502.04463 §6）。
- 多奖励任务中直接去 std 会出问题：GDPO 报告去 std 的 GRPO 在 BFCL 上 format 为 0（2601.05242 Table1 signature）。可能的原因是，通道之间尺度悬殊时，小通道被大通道淹没。去 std 应与 PC-F1-03 的逐通道处理配合。

## 审稿期望
（推断，记录无审稿意见）
- 必须给 λ 剂量—反应曲线，证明系数在去 std 后确实可调。
- 要多种子。2502.01600 的 ±1.3 是同 checkpoint 的评估方差，不能当训练方差。

## 认知障碍
- "代价本身的标准化"与"优势的标准化"是两件事，前者常被误当作"已经无归一化"（2502.04463 pitfalls："cost z-score≠reward advantage std"）。
- 长度上升常被解读为推理变好，实为 loss 分母与组 std 造成的权重偏差（2503.20783 why_non_obvious）。

## 工程经验
- 当 λc 进入标量奖励且组为全对时，除 std 会把 λ 约掉，所以 λ=0.01 与 0.001 等价。应当先在 mean-only 下做 λ0/小 λ 对照，再谈系数（2502.04463 §5.4.1）。
- 当用 mean-only 但 loss 仍按序列长度平均时，α=0 也可能出现缩短。应当先修 loss 分母再归因于奖励（2502.04463 AppG；2503.20783 Listing1）。
- 当训练已锁死后，再切到 mean-only 不会恢复。应当在开训时就固定估计器（2607.21273 Appendix I）。
- 当把 budget curriculum 和固定 MAX_TOKENS 分母一起用时，改预算就是改梯度尺度。应当把预算视作超参记录（2503.20783 pitfalls）。

