---
id: PC-F1-15
name: 只在全错（或失败）轨迹上启用外部/特权信号做辅助更新，混合组保持原结果优势
family: F1_objective
status: candidate_pattern
problems: {P07: 3, P18: 1, P25: 1}
members: [2605.30451, 2609.35303, 2605.07177, 2601.18779]
rs_patterns: [conditional_fallback_supervision, heterogeneous_decomposition]
---
## 操作
在结果奖励无差异的样本上，引入外部或特权信号补梯度：

**VeriGate：全错组用 PRM 补过程优势**（2605.30451 Eq1–3，§3.4）
- 先算每步的未来 PRM 分数累加 $c_{i,j}=\sum_{k\ge j}r^{PRM}_{i,k}$。
- 在组内所有步骤上做 mean/std，得到 $A_{i,j}$。
- 只在全错组用 $A_{i,j}$ 替代退化的零优势。混合组仍用 GRPO 优势，全对组置 0。

**PIVOT：失败轨迹加门控自蒸馏**（2609.35303 AppF Eqs11–13）
- 在 GRPO 之外加一项：$L=L_{GRPO}+.01\,E[\mathbf 1_{fail}m_{act}\,g\,(\mathrm{sg}[\ell^{tea}]-\ell^{stu})]$。
- 门控 $g=\sigma(5\Delta)$ 恒为正。
- teacher 看到 pivot 前后各 3 帧加上诊断信息；student 只看当时的历史。

**HyperEyes OPD：失败轨迹对齐教师**（2605.07177 Eq6）
- 只在 $R_{acc}=0$ 时，对 completion tokens 加 reverse KL(student‖frozen teacher)，$\lambda_{kd}=.05$。
- 教师是已经过同目标 RL 训练的同族大模型。

**POPE：难题加 oracle 前缀**（2601.18779 §4 Eq3）
- 对难题加上能让基座续写成功的最短 oracle 前缀，与无引导版本 1:1 混合训练。
- 优势为 mean-only，测试时不加前缀。

## 信息
- 在策略结果信号之外，额外引入：外部 PRM、事后诊断（未来帧）、冻结教师分布、oracle 解前缀。
- 这些信号策略在推理时都看不到；都是训练期特权信息。

## 成立条件
- 外部信号对"正确方向"有信息量。
  - 只换内容（随机 pivot）会变差（2609.35303 failure_boundary）。
  - 换成没有对齐过效率的大教师会显著变差，46.3%（2605.07177 Table5）。
- 门控要严格：
  - 混合组的可靠结果信号不应被覆盖。去掉门控后 AMC 从 27.71 掉到 7.23（2605.30451 Table2）。
- 恢复梯度 ≠ 恢复能力。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.30451 | 全错组 PRM 回退 | Eq1–3；Table2 | 1.5B AMC 15.10→27.71、Math500 39.8→41.6；去门控 AMC 7.23/Math 34；去未来累加 AMC 21.69/Math 38.4 | 未报告 | 支持 |
| 2609.35303 | 失败 mask × 正门控自蒸馏 | AppF Eqs11–13；Table1/2 | 3B 合计 .83→.90；随机 pivot：Sokoban .95→.75、Navigation .90→.80 | 每环境 128 episode 验证，无 CI | 支持；正门控有风险 |
| 2605.07177 | 失败轨迹 reverse KL 到效率对齐教师 | Eq6；Table5 p11 | TRACE 62.7→+OPD 64.0（2.2 轮）；换成 vanilla 235B 教师 46.3%；无 SFT 44.7% | 30B 三个 seed，其余单 seed | 支持（教师必须对齐） |
| 2601.18779 | oracle 前缀扩增难题，mean-only | §4 Eq3；Table2 | hard pass@1 13.55→15.50，pass@16 32.89→42.53 | 未报告 | 支持（迁移需测无前缀） |

## 成功条件 / 失败模式
**成功条件**
- 有可信的外部过程或教师信号。
- 混合组保持结果优势主导。

**失败模式**
- PRM 自身的偏差与长度偏好不会自动消除（2605.30451 failure_boundary）。
- 常数正 PRM 会仅因剩余步数多，就给早期步骤正优势（2605.30451 invariance）。
- 教师必须已具备目标效率行为（2605.07177 pitfalls："Effective distillation strictly requires an efficiency-aligned teacher"）。
- 混合易题会引起 ray interference；oracle SFT 会降低 hard 与 held-out 表现；修改 prompt 会抑制迁移（2601.18779 negative_results）。

## 审稿期望
- 记录多为 low_evidence。
- 推断的要求：
  - 常数过程信号对照；
  - 打乱过程信号对照（2605.30451 lesson）；
  - 撤掉特权帮助后的单独评测（2601.18779 lesson）。

## 认知障碍
- 可靠的终局信号不应被 PRM 覆盖，但全错时可以借用；同时要区分"恢复梯度"和"恢复能力"（2605.30451 why_non_obvious）。
- 引导下解题更容易，不等于无引导时也能迁移（2601.18779 why_non_obvious）。

## 工程经验
- 当引入外部过程分数来补全错组时，要明确门控与归一化的作用域，并用常数或打乱的过程信号排除长度与格式带来的伪奖励（2605.30451 lesson）。
- 当用未来诊断给旧动作打分时，先展开梯度方向与 mask；门控不等于负信用（2609.35303 lesson）。
- 当训练需要特权帮助时，必须单独测量撤去帮助后的收益（2601.18779 lesson）。

