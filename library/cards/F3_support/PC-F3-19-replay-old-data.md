---
id: PC-F3-19
name: 新阶段训练时按比例回放旧阶段数据，用旧数据的监督项抵抗遗忘
family: F3_support
status: candidate_pattern
problems: {P61: 2, P63: 2, P62: 1}
members: ["litscan:2132", "litscan:77971", "litscan:72124"]
rs_patterns: [unify_into_shared_representation]
---

## 操作

在当前阶段的损失上加旧阶段数据的监督项：$L=-\mathbb E_{D_{current}}\log p(y|x)-\alpha\,\mathbb E_{D_{previous}}\log p(y|x)$（litscan:2132 §3.2.3 p5）；或每个 batch 当前/历史各 50% 抽样（litscan:77971 AppB.1）；或 RL 数据中混入其他任务类型以防偏科（litscan:72124 Table6/Table10）。

## 信息

- 旧阶段的训练数据（标签固定，不来自当前策略）。

## 成立条件

- 旧数据仍可得，且其监督与当前目标不冲突。
- 回放量足够；litscan:77971 中每任务 M=10 时各模型近乎完全相对遗忘（FAIL 字段）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:2132 GroundingGPT | 三阶段训练，后续阶段以 α 比例重放旧数据（stage1 α=0，后续数值未查到） | §3.2.3 p5; Table7 p9; Table4 p7 | toy 224px：初始粗粒度 84.68 vs 粗+细混合 82.43；TextVQA 55.2 低于 LLaVA 58.2 | 记录未覆盖 | 弱支持（无去回放消融记录） |
| litscan:77971 | 每任务固定存 M 个 transition，当前/历史 1:1 | Table1; AppB.1; Table2 | M1000 时 GR00T 平均 SR .919 / NBT .027，BC-Transformer .585 / .245；无回放顺序学习 GR00T Object 的 NBT .752 | 记录未覆盖 | 支持回放；M 小时失效 |
| litscan:72124 DeepEyes | 感知/推理混合数据 | Table6; Table10; E | 只用感知数据导致推理遗忘，混合数据缓解，但以 V* 91.6→90.1、HR8K 74.6→72.6 为代价 | 记录未覆盖 | 支持，有代价 |

## 成功条件 / 失败模式

- 成功条件：回放量足、旧监督与新目标兼容。
- 失败模式 1：回放量太小时近乎完全遗忘（litscan:77971 M10）。
- 失败模式 2：低遗忘可能只是没学会；需同时看新任务成功率（litscan:77971 rs.why_non_obvious）。
- 失败模式 3：混合数据以主任务分数为代价（litscan:72124 Table10）。
- 失败模式 4：M 是每任务 transition 数，总容量随任务数增长，非固定预算（litscan:77971 FAIL）。

## 审稿期望

推断：要求同算力下"回放 vs 不回放"的对照；要求同时报告新任务收益与旧任务保留。

## 认知障碍

- 低遗忘常被直接归因于预训练表征；litscan:77971 用恢复速度与模块互换诊断，但"快速重学"不能唯一证明知识完整保留（FAIL 字段）。

## 工程经验

- 当用回放抵抗遗忘时，按任务数增长的回放容量要计入成本（litscan:77971 FAIL）。
- 当回放与新任务冲突时，同时报告主任务分数（litscan:72124 Table10）。

