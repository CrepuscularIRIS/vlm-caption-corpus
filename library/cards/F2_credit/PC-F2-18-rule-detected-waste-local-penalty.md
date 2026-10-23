---
id: PC-F2-18
name: 用规则或结构检测出无效/重复/漂移的工具调用，只对检测到的段施加局部负信用（其余保留结果优势）
family: F2_credit
status: candidate_pattern
problems: {P30: 3, P11: 2, P02: 1, P18: 1, P36: 1}
members: [2610.19695, litscan:56625, 2610.18683]
rs_patterns: [targeted_self_supervised_objective, structural_prior_encoding, heterogeneous_decomposition]
---

## 操作

不估计必要性，只识别**可规则判定的浪费**，在该段上改写优势：
- C3：用规则检测无效动作与重复 query，定位失败回合的 token；在**归一化之后**把 A>0 改成 $-\text{confidence}\times\text{severity}\times A$，confidence 取行为策略在 action span 上的平均 token 概率；负 A 与未检测到的 token 不变，不改 critic 目标（2610.19695 签名）。
- ALDEN：query 与历史重复的 n-gram 按 token 分摊惩罚 $r^i_t=-w_i\,\text{overlap}_t$，与轮级价值一起经 token GAE 传递（litscan:56625 Eq6）。
- ProAS：正 A 乘"结构合理性"mask，负 A 乘 Future-Drift 或同优势组均值（2610.18683 签名）。

## 信息

- 看得到：
  - 规则：重复 query、无效动作、n-gram 重叠；
  - 结构图：官方或成功轨迹的子目标图；
  - 行为策略自身在动作 span 上的概率。
- 看不到：重复调用是否真的无因果价值（2610.19695 failure_boundary："规则重复不等于无因果价值"）。
- 估计者：规则（不学习），可选加行为策略的置信度。

## 成立条件

- 浪费可以被规则可靠定义；事件定义出错，会把有价值动作的正优势翻成负（2610.19695 REL P36:2）。
- 对 ProAS：依赖 ARG 的质量与子目标匹配；随机图标签会导致退化（2610.18683 failure_boundary 与 REL P36:2）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2610.19695 | 检测到的失败 token：A>0 → −conf·sev·A，归一化后施加 | Table1 | Qwen3-8B PPO+C3 七任务平均 EM 50.20±.10 vs PPO 47.79±.50；NQ 39.5 低于 40.7 | ±来自四次温度采样，不是四个训练 seed | 成员 |
| litscan:56625 | query 重复 n-gram 的 token 级惩罚 + 轮 GAE | Table2 | 平均 .386；去 cross-level .356 | 记录未覆盖 | 成员（亦见 PC-F2-04） |
| 2610.18683 | 正 A × 合理性 mask，负 A × Future-Drift | Table2 | Qwen1.5B ALFWorld SR 70.3±2.8 → 87.0±2.3；WebShop 57.0±3.1 → 64.6±1.2 | 记录未覆盖 | 成员 |

## 成功条件 / 失败模式

- 成功：浪费类型明确（重复、无效）、易检测。
- 失败：
  - ALDEN：无重叠时 w 的分母为 0，处理方式未写（litscan:56625 degenerate_cases）；Eq7 的 KL 符号与文字冲突（litscan:56625 signal_routing）。

## 审稿期望

ALDEN 为 low_evidence。"推断"：
- 要报告检测器的精确率；
- 要有"随机检测同比例"的对照；
- seed 数要是训练 seed，而不是采样次数（C3 的 ± 不是训练 seed）。

## 认知障碍

- 同一过程标签，作为 reward 时会传播到其他 token 并被归一化变形；直接改 actor 信用，可以把干预限定在特定位置（2610.19695 why_non_obvious）。
- 失败末尾的"无进展"可能源于早期偏离，所以对失败轨迹统一惩罚、对成功轨迹统一强化都会误导（2610.18683 why_non_obvious）。

## 工程经验

- 当用过程奖励优化工具时，先声明 GT 可用的信息、动作 token 与观察 token 的路由，并核对两层价值目标与正则的符号（litscan:56625 lesson）。
- 当过程检测出错时，会把有价值动作的正优势翻成负，所以需要可靠的事件定义（2610.19695 REL P36:2）。
- 进展标签必须可靠，随机图标签会导致退化（2610.18683 REL P36:2）。

