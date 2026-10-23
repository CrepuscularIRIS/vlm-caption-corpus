---
id: PC-F3-05
name: 用模型自身在"有/无证据"两种条件下的成败给样本打需求标签，标签只进 SFT 监督
family: F3_support
status: candidate_pattern
problems: {P26: 2, P21: 2, P28: 2, P65: 2, P24: 1}
members: [2602.06040, 2512.16883, 2311.09677, "litscan:45695", "litscan:30805"]
rs_patterns: [heterogeneous_decomposition, controlled_diagnostic_design]
---

## 操作

对每个训练样本，用一个固定模型（基座或 stage1 模型）分别在两种条件下作答：无额外证据 vs 有额外证据（中间图、搜索、原图未裁）。按成败或成功率阈值把样本标成"需要/不需要额外观测"（或 sure/unsure、动/不动），再把标签写进 SFT 目标或决策阶段的监督。分支只产出标签，分支样本本身不进策略损失。

## 信息

- 标签来源是**固定的**基座或旧阶段模型，不是训练中的当前策略：
  - 2602.06040：Qwen3VL-8B 原图 vs 附中间图的 pass@8，Qwen3-235B judge（§3.3 Stage2 p6）；
  - 2512.16883：stage1 无 search 采样成功率 p≥ρ 标 yes（notes）；
  - 2311.09677：预训练模型一次预测与 GT 比对分 D1/D0（§2.1/Eq2）；
  - litscan:45695：数据生成模型在原图/扰动图上的 GT 判分（Algorithm1）；
- 看不到：当前策略在训练后的需求；单次观测的因果必要性。

## 成立条件

- 两种条件只差"证据"一个变量（M13：相同观测状态下比较）。2512.16883 的两种条件用不同 prompt，不是严格同前缀分叉（notes）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2512.16883 AdaSearch | stage1 无 search 成功率阈值 → yes/no 决策标签 | Table2 Qwen2.5-3B block | 平均 EM 36.0 / F1dec 54.0；Search-R1 38.1 / .1 | 记录未覆盖 | 支持决策可学；有 EM 折衷 |
| 2311.09677 R-Tuning | 按基座一次预测对错，在答案后附 sure/unsure，CE 训练 | Table1; §2.1/Eq2 | LLaMA13B MMLU OOD AP 77.41 vs Vanilla 67.38；3B MMLU OOD 24.75 低于 26.08 | 记录未覆盖 | 混合：小模型反降 |
| litscan:45695 DirectGuide | 原图答对 → 扰动；仍对标"不动"，变错标逆方向；平衡六类 LoRA | Algorithm1/Table1 | LLaVA13B overall .53→.63，方向 ACC .01→.43；GPT4o .60 | 记录未覆盖 | 支持；最强扰动方向 ACC .43→.40（Tables1-2） |
| litscan:30805 Fast-Slow | 缺失/小目标样本输出 missing objects 与 context clue，再定位 | §2; Table3 p8 | GQA 63.8 / 1475ms vs always-slow 64.0 / 2937ms；MME 1517.4 / 2023ms vs 1518.6 / 2938ms | 未报告独立训练种子 | 支持效率；adaptive 仍略低于 always-slow |

## 成功条件 / 失败模式

- 成功条件：标签模型 ≈ 被训模型，标签与真实收益相关。
- 失败模式 2：一次失败不等于"永远不会"（2311.09677 FAIL："一次错误不证明知识永久缺失"）。
- 失败模式 3：阈值、pass@8 的估计与温度未定义（2602.06040 FAIL 字段）。

## 审稿期望

推断：要求标签的可靠性（重采样一致率、分半一致）；要求与"统一偏置"对照（只学全局直答率）比较；要求标签模型与被训模型的差距分析。

## 认知障碍

- "需要看"被当成题目属性，实际上是模型条件的（2311.09677 rs.why_non_obvious："知识边界是模型条件的标签"）。
- 物体不完整不必然影响答题，标签依赖当前模型而非几何截断（litscan:45695 rs.why_non_obvious）。

## 工程经验

- 当用两条件成败打标签时，两条件必须是同一前缀、同一 prompt，否则差异混入 prompt 效应（2512.16883 notes：M13 注意不同 prompt 不是严格同观测分叉）。
- 当成功率阈值规则允许"两者都为 0"时，会把不可救的题标成"需要看"（2602.06040 FAIL 字段），应单列 unknown。

