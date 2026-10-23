---
id: PC-F5-04
name: 用可验证的"已足够"状态直接给停止动作造支撑与监督
family: F5_stop_eval
status: candidate_pattern
problems: {P33: 3, P25: 3, P29: 2, P31: 2, P28: 1}
members: [litscan:1210, litscan:72753, litscan:70701]
rs_patterns: [heterogeneous_decomposition, structural_prior_encoding]
---
## 操作
先用真值（目标谓词、GT mask、渲染器 GT）判定哪些中间状态"已经够了"，再在这些状态上直接监督或强制停止动作，让稀有的"正确终止"被采到：
- lilGym：训练时若目标已满足，mask 掉所有非 STOP 动作；测试撤掉强制（litscan:1210 §6.1）。
- SAM-Veteran：把 box grounding、真实 SAM-mask 判断、合成 FP/FN 错误修正拆成三个 RL 任务，GoodEnough 状态（edge-excluded IoU=1）奖励 null 终止（litscan:72753 §3.2.2；Table1 p5 的 $R^\Delta$ 分档）。
- ChartVSR：SFT 里同时放"从错标记纠正"和"从正确标记确认停止"两类样本（litscan:70701 conditions）。

## 信息
训练时可见真值（可执行程序 / GT mask / 渲染器 GT 坐标）；部署时没有真值，策略只看自身状态。停止标签来自状态质量，不来自策略续写收益。

## 成立条件
- 有对任意中间状态都准确的"够了"判定器（litscan:1210 conditions；litscan:72753 需 GT mask/box）。
- 停止动作在 SFT 或辅助任务中有示范；只靠终局奖励造不出来（litscan:72753 Table4：只加真实 mask 理解则 never stop）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:1210 lilGym | PPO + 训练期 oracle 强制 STOP | §6.1；Table2；Eq.1 | ViLT SCATTER-FLIPIT test 16.81±7.43 → 30.06±4.51 | 3 runs，mean±std | 记录未覆盖 |
| litscan:72753 SAM-Veteran | 合成 FP/FN 辅助任务教 null 终止 | Table4 p8；Tables4–5 | TG+MC 72.1 avg 但 never stop；+aux 72.2 且自适应停止；ReasonSeg val 3 步后 +2.47，基座 −2.48；aux 使 RefCOCOg 73.6→73.4 | 记录未覆盖 | 记录未覆盖 |
| litscan:70701 ChartVSR | SFT 含纠错与"确认正确→停止" | Tables4–6；Table5 | ChartP 平均 AP 38.41 vs 去 VSR 36.54；首轮错误 110→51，第二/三轮 54/52；更多轮不单调减错 | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：真值判定准确，且"够了"状态在训练中出现足够多次。
- 失败模式：
  - 真实图片问答没有任意中间状态的准确目标谓词，错误的强制 STOP 会提前终止（litscan:1210 failure_boundary）。
  - 训练 oracle 强制与自主策略结果不可混报（litscan:1210 pitfalls）。
  - 自确认可能是错的，错误标记被确认后提前停（litscan:70701 degenerate_cases）；收益集中在首轮（Table5）。
  - 成功策略仍低效、平均奖励常为负（litscan:1210 negative_results）。

## 审稿期望
- 分别统计"到达可停状态""实际 STOP""停后破坏目标"（litscan:1210 lesson）。
- 报告新增错误与调用预算（litscan:70701 lesson）。
- 真值来源与执行时可用信息分开写（litscan:72753 lesson）。

## 认知障碍
正回报不仅要求世界满足目标，还要求恰好采到 STOP；单纯到达目标也可能随后破坏它（litscan:1210 why_non_obvious）。只加真实 mask 判断，模型会永远修正下去；必须人为造出"有错/无错"对照，stop 才会出现（litscan:72753 why_non_obvious）。

## 工程经验
- 当用 oracle 强制停止训练时，测试必须撤掉强制，且不能把 oracle 辅助的结果与自主策略结果混报（litscan:1210 pitfalls）。
- 当坐标与图像尺寸耦合时，输入长边要固定为 patch 的整数倍（ChartVSR 用 1036 = 28 的倍数），迁移时不能忽略 resize（litscan:70701 pitfalls）。

