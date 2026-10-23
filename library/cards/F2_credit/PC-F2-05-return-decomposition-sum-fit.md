---
id: PC-F2-05
name: 学一个逐步打分器，使各步分数之和拟合终局回报，再把步分当稠密奖励
family: F2_credit
status: candidate_pattern
problems: {P11: 2, P19: 2, P43: 1}
members: [1806.07857, litscan:23737, 2505.20732, 2603.18683]
rs_patterns: [reframe_as_solvable_object, algebraic_equivalence_unification, heterogeneous_decomposition]
---

## 操作

训练一个打分器 $c(s,a)$（或段分 $r_i$），使 $\sum_t c_t\approx R$。然后把 $c_t$ 作为每步奖励送入 GAE/PPO：
- RUDDER 用 LSTM 逐前缀预测整条序列的回报，以相邻预测之差分配奖励，并保留末端残差补偿（1806.07857 key_step）。
- RRD 只随机抽 K 个 transition 拟合，平方误差中多出的方差项起平滑正则作用：$L=\mathbb E(R-\frac TK\sum\hat R_i)^2=L_{RD}+\mathbb E[T^2\mathrm{Var}_\tau(\hat R)\frac{T-K}{K(T-1)}]$（litscan:23737 §3.2 Eq11）。
- SPA-RL：MSE 拟合 $\sum c\approx$ 终奖，$r_t=\alpha c_t+\beta g_t$，g 为动作可执行标记（2505.20732 key_step）。
- HISR：按子目标切段，$L=(R-\sum r_i)^2$，再用后见似然比调节各段（2603.18683 签名）。

## 信息

- 看得到：完整轨迹和终局回报（SPA 另有执行成功标记；HISR 另有 GPT4o 切段和后见模型）。
- 看不到：每步的真实贡献。只有总和受约束，分解本身不可识别（2505.20732 why_non_obvious；2603.18683 failure_boundary）。
- 估计者：学到的分解器。对当前策略而言是外部代理。

## 成立条件

- 关键事件能从轨迹识别，且回报长时延迟（1806.07857 trigger_condition）。
- 低重建误差不唯一确定真实的逐步信用（litscan:23737 failure_boundary）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 1806.07857 | LSTM 回报预测差 + 末端残差 | §4 / Table1 | Bowling 192 vs PPO 56；Seaquest 4770 vs 1616；52 个游戏最终均分 29 胜 23 负 | 记录未覆盖 | 成员 |
| litscan:23737 | 随机 K 子样本拟合，隐式方差正则 | §3.2 Eq11 / §3.2.2 | K=T 时 surrogate gap 为 0（退化为完整分解）；K=1 对应均匀再分配 | 理论 | 成员 |
| 2505.20732 | sum-of-step MSE 进度估计 + 可执行奖 | Table2 | ALFWorld 成功率 79.1 / grounding 93.7；去 grounding 77.6/91.1；去 progress 77.6/94.2 | 记录未覆盖 | 成员 |
| 2603.18683 | 子目标分段 sum-fit + 后见似然比调节 | Table1 | ALFWorld 83.6、VirtualHome 59.1、WebShop 69.1；去 hindsight 80.6/55.1/63.7；去 segment 82.1/57.9/69.1 | 记录未覆盖 | 成员 |

## 成功条件 / 失败模式

- 成功：延迟奖励、关键事件可识别的离散环境。
- 失败：
  - 并非普遍改善：52 个游戏 29 胜 23 负（1806.07857 Table1）。
  - 执行成功不等于必要或有用；逐步累计的正 grounding 可能偏好冗长但可执行的轨迹（2505.20732 failure_boundary）。

## 审稿期望

记录中无审稿。"推断"：要给出分解的可识别性检验（例如打乱步序后的分解是否改变），以及与均匀再分配（K=1）的等预算对照。

## 认知障碍

- 预测整条已观察序列回报的 g 不是通常的 V 或 Q；相邻预测共享记忆，误差可能相互抵消（1806.07857 why_non_obvious）。
- 无偏的回报估计进入平方之后，不再是原 loss 的无偏估计，恰好多出一个轨迹内奖励方差的惩罚（litscan:23737 why_non_obvious）。

## 工程经验

- 当只用总和约束训练分解器时，应把分解当作不可识别的代理，并用打乱或均匀分解做对照（2505.20732、litscan:23737）。

