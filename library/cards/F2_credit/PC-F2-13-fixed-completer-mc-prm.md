---
id: PC-F2-13
name: 用非当前策略（固定 completer/prover/行为策略）从前缀续写的成功率标注步骤或估计干预差，蒸馏成过程打分器或直接用于 RL
family: F2_credit
status: candidate_pattern
problems: {P16: 3, P17: 2, P11: 2, P43: 2, P19: 1, P18: 1}
members: [litscan:2282, litscan:29582, 2502.10325, 2511.08325, litscan:38344, litscan:79235, 2606.05263]
rs_patterns: [self_supervised_signal_engineering, targeted_self_supervised_objective]
---

## 操作

对每个前缀，用某个**固定**策略 μ 续写 N 次，以终答正确性得到前缀的"可解性"或 Q 标签，训练 PRM（或 progress 打分器），再把 PRM 分数用于 RL 奖励、偏好对或推理选择：

- Math-Shepherd：固定 LLemma7B completer，每前缀 N=8。HE = 任一续写正确，SE = 正确比例。PPO 只在每步末 token 拿 PRM 奖励（litscan:2282 签名）。
- Rewarding Progress：另一个 prover μ 的相邻前缀成功率差 $A^\mu=Q^\mu-V^\mu$，作为**加在** outcome 上的探索 bonus：局部梯度系数为 $Q^\pi+\alpha A^\mu$（litscan:29582 Eq4–5）。
- 按 state-action hash 聚合真实后续回报作 Q 软标签，迭代训练 PRM，再用以前一策略为锚的 OnlineDPO 最大化 Q（2502.10325 签名）。
- AgentPRM：用自身轨迹终局反馈 bootstrap 出 Q，同时拟合绝对 Q 与相邻 Q 差，$L=L_Q+\beta L_A$（2511.08325 签名）。
- VideoSalmon：用视频扰动的 token KL 选出 top3 步骤，再用同前缀 MC 成功率构造步级 DPO 偏好（litscan:38344 签名）。
- BIS：$\text{BIS}=(p(1-p)+\alpha)R$，按来源保留 top ρ 的 MC 数据训练 PRM（litscan:79235 §4）。
- PCCC（不训 PRM 的变体）：限定四种干预，用**冻结** μ 续写，先做有效性 gate，再用选择概率加权的 DR outcome 差，同时进入 dense reward（tanh）与额外优势，并用 augmented Lagrangian 约束 hacking（2606.05263 签名）。

## 信息

- 看得到：μ（固定 completer、prover 或旧行为策略）的续写成功率；训练期的 GT。
- 看不到：当前策略在同一前缀上的成功率；μ 与 π 的能力差。
- 估计者：非当前策略的 MC，并蒸馏成 PRM。这与 PC-F2-02 是"同一动词、不同信息"，按合并规则分卡。

## 成立条件

- 步骤标签其实是"给定 completer 下的可恢复性"，不是该步逻辑上必然正确（litscan:2282 why_non_obvious）。
- prover 要与 base 互补且对齐。最强的 prover 可能处处都能解，使 A≈0；有辨别力、与 base 兼容的较弱 prover 反而有效（litscan:29582 why_non_obvious）。
- PRM 会随策略更新失效，需要迭代重训（2502.10325 why_non_obvious）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:2282 | 固定 completer HE 标签，步末 PPO 奖励 | Table3 | Mistral7B ProcessRL greedy GSM8K 84.1 / MATH 33.0，SFT 77.9 / 28.6 | 记录未覆盖 | 成员 |
| litscan:29582 | prover 优势加在 outcome 上 | AppE / Fig15 | Gemma9B：PAV-RL 相对 ORM-RL 5× sample efficiency、准确率 +6%（2B SFT prover） | 记录未覆盖 | 成员 |
| 2502.10325 | 回报 Q 软标签 PRM + OnlineDPO 迭代 | §2.3 | ALFWorld 第三轮成功 88.1%，逐动作 BoN 91.0%；PRM 过优化时真实成功率 82%→70% | 记录未覆盖 | 成员（含 reward hacking 负结果） |
| 2511.08325 | bootstrap Q + 相邻 Q 差 | Table1 | Qwen2.5-3B beam8×8 WebShop PVM 54.5 → 76.0；TextCraft 44.3 → 56.7；0.5B BabyAI 82.9 低于 PVM 84.6 | 记录未覆盖 | 成员 |
| litscan:38344 | 视频扰动选步 + MC 偏好 | Table4 | SFT+pDPO VideoMME / NExT-QA / StandUp / Academic 65.6 / 82.3 / 76.7 / 48.3，SFT 62.9 / 78.2 / 68.6 / 42.5 | 记录未覆盖 | 成员 |
| 2606.05263 | 冻结 μ 续写的四类干预 DR 差，进 reward 与优势 | Table3 p7; Table4 | success 78.9±.8 vs 信息匹配对照 75.4±.8，Hack 3.9 vs 7.2；reward-only 77.3，adv-only 76.2 | 作者报告 5 seeds | 成员（直接干预，不训 PRM） |
| litscan:79235 | 按 MC 混合度 × 正例可靠性筛 PRM 数据 | Table2; Table4 | InternVL BIS10% micro-F1 65.46 vs 全量 65.12 vs random10% 62.86；Qwen 64.63 vs 全量 65.57 | 记录未覆盖 | 成员（数据侧） |

## 成功条件 / 失败模式

- 成功：数学/文本等答案可验证的任务；PRM 与 outcome 并用。
- 失败：
  - PRM 被过优化：分数上升而真实成功率从 82% 降到 70%（2502.10325 §2.3）。
  - HE 随采样数与能力而变，可修复的错误仍可能被标为正（litscan:2282 failure_boundary）。
  - 强、弱 prover 都可能使 A≈0；AppI 自称 PBRS，但实际的旧状态分布代理不能无条件推出全训练不变性（litscan:29582 failure_boundary）。
  - 提高 MC 正标签阈值会伤 F1（litscan:79235 negative_results）。
  - 扰动敏感度不是信息必要性（litscan:38344 failure_boundary）。

## 审稿期望

BIS 为 low_evidence；其余无审稿。"推断"：
- prover/completer 与 actor 的对齐度量；
- PRM 随训练的漂移与重训频率；
- 用真实成功率监测 PRM hacking（2502.10325 已做）。

## 认知障碍

- 过程监督来自行为策略可达的结果，而不是语言上"看起来正确"；策略一更新，旧 Q 就失效（2502.10325 why_non_obvious）。
- 只找混合/低 MC 的难例会保留噪声正例，只找高可靠例又缺负例，所以两者要相乘（litscan:79235 why_non_obvious）。
- 删除、替换、工具扰动不是同一个因果量；冻结续写、选择规则与环境有效性都会影响可解释的范围（2606.05263 why_non_obvious）。

## 工程经验

- 当过程 judge 只懂局部合理性时，聚焦最差分只能延缓投机；要保留 GT 终端信号，并分组监控正确长重复与空回答（2504.15275 lesson，Stop Summation，同属"PRM 驱动 RL"的教训）。
- 当已有 MC 过程语料冗余时，先按来源筛选，并分清标注成本与训练成本，再用 held-out 阈值评 PRM（litscan:79235 lesson）。
- 全局阈值应在 held-out 上优化，不能在测试标签上调（litscan:79235 pitfalls）。

