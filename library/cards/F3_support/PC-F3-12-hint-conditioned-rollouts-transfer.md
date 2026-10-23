---
id: PC-F3-12
name: 给部分 rollout 加策略提示以改变探索分布，并用无提示 prompt 下的优势加权似然把行为迁回部署策略
family: F3_support
status: case
problems: {P25: 3, P26: 2, P17: 2, P29: 2}
members: [2605.15726]
rs_patterns: [generative_process_redesign]
---

## 操作

每条 rollout 注入一个"策略提示"上下文（由 GPT4o-mini 每题生成两条），以概率 p_drop 随机去掉提示（notes：p_drop=.5 为正文转述的最佳）。优势由两部分组成：
$A^{raw}=(r_i-\bar r_{ctx})+\lambda(\bar r_{ctx}-\bar r_{all})$（无提示的样本用 $r_i-\bar r_{all}$），再全组 (A−mean)/std+δ；λ=1 时退化为普通组差（notes）。
另加迁移项 $L_{PC}=-\mathbb E_{ctx}[\hat A\log\pi(y\mid\text{base prompt})]$，与带提示的 clipped RL 损失相加（notes）。

## 信息

- 提示上下文：GPT4o-mini 生成，不需要 GT 解，也未验证其正确性（notes）。
- 各上下文下样本的正确性。
- 部署时没有提示，所以需要迁移项。

## 成立条件

- 高价值行为在无提示采样中罕见，且训练提示在部署时不可用（rs.abstract_trigger_condition）。
- 迁移项不是完整重要性修正，不能得到无提示 on-policy 的无偏梯度（notes）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.15726 Nudging | strategy + dropout 采样，inter/intra 优势，base-policy 迁移项 | Table1 p3 | Nudge8 平均 .489 / 9.0M tokens / .492 EFLOPs；GRPO32 .487 / 44.7M / 1.421；同预算 GRPO8 .454 / .342 EFLOPs | pass@1 由 128 samples 估计；训练种子记录未覆盖 | 支持 |
| 同上（边界） | 主表 N64 | notes | GRPO 降至 .451；MATH500 .660 低于 GRPO32 .674，非全指标占优 | — | 边界 |

## 成功条件 / 失败模式

- 成功条件：提示把采样推到新策略区域，迁移项把收益带回无提示分布。
- 失败模式 1：同 rollout 数下仍多约 44% 的 policy-correction 计算（FAIL 字段）。
- 失败模式 2：全同奖励时 inter/intra 优势都为 0，迁移项也是 A 乘法，不会自发学习（KF 字段）。
- 失败模式 3：提示池固定，可能过时；提示未验证正确（notes）。

## 审稿期望

推断：要求同算力（EFLOPs）而不只是同 rollout 数比较（作者已给 EFLOPs）；要求无迁移项的消融；要求部署时无提示的行为频率。

## 认知障碍

- 更多 rollout 不保证探索到新策略；带提示的探索又不直接等于无提示推理，需要单独的迁移项（rs.why_non_obvious）。

## 工程经验

- 当训练提示在部署不可用时，必须有迁移项并在无提示下评测（rs.why_non_obvious）。
- 当比较效率时，把 offline 提示生成与 correction 计算都计入成本（COND 字段："cost 包含 offline context"）。

