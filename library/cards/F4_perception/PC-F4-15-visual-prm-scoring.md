---
id: PC-F4-15
name: 用外部或自身的视觉过程评估器（PRM）给中间步骤打分，用于 BoN、搜索或奖励
family: F4_perception
status: needs_revision
problems: {P43: 2, P16: 2, P67: 2, P52: 1}
members: [litscan:78791, 2508.03556, 2503.20271, 2602.08346, litscan:3182, 2501.04686, 2505.03318, litscan:77427, litscan:2952]
rs_patterns: [controlled_diagnostic_design, self_supervised_signal_engineering, reframe_as_solvable_object]
---
## 操作

训练或调用一个评估器，按前缀逐步给分，再把分数用到三类场景：

**1. 候选重排（BoN）**
- DiscPRM：在含真实中间图像的轨迹上，对每个前缀采 16 条续写，用 MC 成功率二值化作标签；推理时取步骤均分选轨迹（litscan:78791 Eq2, Eq4）。
- VRPRM：用 MC 步骤标签冷启动，再以 macroF1 作奖励做 RL（2508.03556 Table2）。
- URM：用 format+偏好准确率做 GRPO，训练出多维打分 CoT（2505.03318 Table1）。

**2. 树搜索**
- VReST：同一 LVLM 的两个 Yes 概率取几何均值，作为 MCTS 节点分（litscan:2952 Eq6–7）。
- 2602.08346：外部 LVLM 打分后选续写（p.4 Algorithm 1）。

**3. 进入 RL 奖励**
- URSA：正确且无骤降得 1，正确但有骤降得 1−γ，错误得 0（2501.04686 Table4）。
- Agent0-VL：自评分×置信度、工具分与结果分相加（litscan:77427 Eq2–5）。

**评测基准**（不是操作本身，是用来检验评估器的）
- ViLBench：按主导模态分层做 BoN（2503.20271 Table2）。
- 2602.08346：图文过程的人工逐步标注（Table2–3）。
- ProcessBench：首错定位（litscan:3182 Table3）。

## 信息

- **评估器来源**：
  - 外部训练或现成模型：DiscPRM、VRPRM、URM、ViLBench、2602.08346；
  - 与策略同一模型：VReST、Agent0-VL。
- **标签来源**：
  - MC 续写成功率，依赖续写所用的策略（litscan:78791；litscan:3182 relevance P16）；
  - 人工首错标注（litscan:3182）；
  - 七类过程错误标注（2602.08346）。
- **看不到的东西**：当前策略在同一状态下的动作价值。MC 标签反映的是"可恢复性"，不是"当前步正确性"（litscan:78791 lesson）。

## 成立条件

- 评估器能处理含图像的步骤。现成 LVLM 在图像步骤上表现下降，并带系统性正偏置（2602.08346 p.6–7）。
- 若用于 RL，需先有冷启动或外部奖励预热：Agent0-VL 在自演化前先用外部正确性奖励训了 2 个 epoch（litscan:77427 App B）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:78791 | MC 标签 PRM，均分 BoN8 | Table4 p7 | Thyme：MathVista 70→75.5，HRBench4K 77→82.1，MMStar 65.9→73.3；max pooling 不如 mean | 记录未覆盖 | 正（BoN） |
| 2508.03556 | MC 标签冷启动 + macroF1 RL | Table2 | VisualProcessBench macroF1：SFT 66.77→RL 69.18 | 记录未覆盖 | 正（评测器能力） |
| 2503.20271 | ORM/PRM BoN，按模态分层 | Table2 p4 | 文本主导：Greedy 58.9→PRM 62.0；**视觉主导：51.0→48.9（−2.1pp）** | 7 个 RM 平均 | 视觉主导时为负 |
| litscan:3182 | 首错定位基准 | Table3 p7 | Qwen7B PRM800K 平均 56.5，Skywork7B 42.1 | 算力不完全匹配 | MC 标签 ≠ 专家首错 |
| 2501.04686 | PRM 骤降罚进入奖励 | Table4 | γ=.5 / ρ=.3 时六基准均值 58.2；γ=1 时 56.3 | 记录未覆盖 | 弱 |
| 2505.03318 | 用 GRPO 训练判官的打分 CoT | Table1 p9 | VLRewardBench 73.8，基座 67.5 | 记录未覆盖 | 正（判官能力） |
| litscan:77427 | 自评分×置信度过程奖 + 工具 | Tables1,3 | 7B 平均 58.3→65.6；去工具 53.1；只 SFT 51.8 | 记录未覆盖 | 正，但非零外部监督 |
| litscan:2952 | 同一模型自评 + MCTS | Tables1–3；Fig3b | MathVista 65.40 vs CoT-Vote 62.30；去 PRM 65.4→59.5 | 未报告 | 正（搜索） |

## 为什么是 needs_revision

- 在**视觉主导**子集或像素推理模型上，PRM 选择是负收益：ViLBench −2.1pp（2503.20271 Table2），PixelReasoner 全降（2602.08346 Fig3）。
- 在数学或通用基准上，多数成员报告为正。

## 成功条件 / 失败模式

**成功条件**
- 评估器在图像步骤上校准过；
- 候选池有正确路径；
- 用均值聚合，而不是 max（litscan:78791 Table4）。

**失败模式**
- **MC 标签把小成功率也标成正。** 二值化规则下 $P(+)=1-(1-p)^{16}$，p 很小也可能标正；早期错误会被后续修复掩盖（litscan:78791 degenerate_cases）。
- **组归一化抵消惩罚。** URSA 中若所有正确样本受同样惩罚，组 std 后退化为 vanilla GRPO；γ=1 会让正确样本归零（2501.04686 failure_boundary）。
- **自评错误相关传播。** 同一 LVLM 的自评错误会在搜索中相关传播（litscan:2952 failure_boundary）。
- **正文与实验损失不一致。** DiscPRM 正文写生成式标签，实验写 MSE（litscan:78791 pitfalls）。

## 审稿期望

推断：
- 按视觉主导程度分层报告；
- 用人工首错或逐步标注直接测评估器，不只看 BoN（litscan:3182 why_non_obvious）；
- 匹配算力的 random/ORM 对照（2602.08346 failure_boundary）。

## 认知障碍

"生成能力强"不等于"奖励判断强"（2503.20271 why_non_obvious）。能选对最终答案，也不等于能定位局部错误（litscan:3182 why_non_obvious）。视觉 PRM 的标签多来自 MC 续写，混淆了"可恢复"和"正确"。前人很少按视觉需求分层检验。

## 工程经验

- **把现成 LVLM 接成裁图过程打分器时**：先用人工核验的图文步骤分开测正类、错类和工具错误检出，并写清前缀与 GT 的可见性（2602.08346 lesson）。
- **用 MC 标签时**：在冻结候选上先区分可恢复性与事实正确性，再讨论 critic 能否作动作信用（litscan:78791 lesson）。
- **自评用于搜索时**：要对照 token 预算和评估器错误的相关性（litscan:2952 lesson）。

