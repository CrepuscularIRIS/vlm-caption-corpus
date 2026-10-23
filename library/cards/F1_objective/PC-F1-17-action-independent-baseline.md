---
id: PC-F1-17
name: 用与本样本动作独立的题级基线（贪心响应、长度加权、经验 Bayes、critic 门控、跨样本探针）替换组均值，并用真实梯度方差而非优势方差来判定
family: F1_objective
status: candidate_pattern
problems: {P09: 3, P08: 1, P07: 1}
members: [2310.10505, 2505.23585, 2602.05165, 2604.19485, 2605.07579, "litscan:61987"]
rs_patterns: [assumption_audit_and_pivot, self_supervised_signal_engineering, algebraic_equivalence_unification]
---
## 操作
保持 $A=R-b$，只换题级基线 $b$。各论文的 $b$ 如下：

| 方法 | 基线 $b$ | 出处 |
|---|---|---|
| ReMax | 同题贪心响应的 reward | 2310.10505 key_step |
| OPO | $\hat b=\sum_il_ir_i/\sum_il_i$（长度加权），每次更新都重新采样 | 2505.23585 Eqs11–12 |
| EBPO | 组均值向全局均值收缩：$V_m=(1-S)\bar r_m+S\mu_{glob}$ | 2602.05165 Eq2 |
| EVPO | batch explained variance $\widehat{EV}>0$ 时用 critic，否则用组均值 | 2604.19485 Eqs6/8 |
| 自身状态 probe | 另一条 rollout 的 hidden state 经线性 probe 得到的值；两条交叉使用，先算基线再更新 probe | 2605.07579 key_step |
| MM-Doc-R1（反例） | 用整条轨迹的余弦相似度加权组奖励，含自身：$A_i=R_i-\sum_jw_{ij}R_j$。权重依赖未来动作 | litscan:61987 Eq4–5 |

## 信息
- 本样本之外的信息源：另一次生成、长度、历史统计、critic、另一条 rollout 的内部状态。
- 基线必须与本样本动作独立。MM-Doc-R1 的完整轨迹相似度违反这一条（litscan:61987 why_non_obvious）。

## 成立条件
- 基线与当前采样动作统计独立，原始 PG 中基线项的期望才为 0（2605.07579 failure_boundary）。
- 降低的必须是 score 加权的梯度方差，而不是优势本身的方差。
  - OPO 的最优基线需要 $\|\nabla\log\pi\|^2$ 权重，长度只是近似（2505.23585 why_non_obvious）。
  - EVPO 的 A 方差不等于 score-weighted PG 方差（2604.19485 why_non_obvious）。
- 这一点与 P09 的教训一致：$E[c^2]$ 不是梯度方差。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2310.10505 | 贪心响应基线 | §5.3/Table4 | AlpacaEval 94.78%、MT-Bench 7.739；SFT 92.78%/7.516 | 记录未覆盖 | 参照 |
| 2505.23585 | 长度加权 mean-only 基线 + 严格 on-policy | Eqs9–12；Table2 p6 | AIME25 pass@16：GRPO 81.33→OPO 85.33；pass@1 50.21→50.00 | 未报告 | 混合：pass@1 未升 |
| 2602.05165 | EB 收缩 + 批级 std | Eqs2–4；Table2 | G=8：65.54 vs 54.26；G=32：62.41 < 62.91 | 32 次评测采样 | 混合 |
| 2604.19485 | EV 符号门控 critic | Eqs6/8；Table1 | 最佳验证：Sokoban .604 / FrozenLake .684 / WebShop .303 / MATH .416，PPO .314/.611/.252/.373 | LR 调参单 seed | 支持（仅报最佳验证点） |
| 2605.07579 | 跨 rollout 内部状态 probe 基线 | Table1；Table3 p9 | Qwen3-4B 平均 58.10，DAPO 56.75，RLOO 56.42；去掉跨 rollout 40.7，完整 50.1 | 记录未覆盖 | 支持：必须防信息泄漏 |
| litscan:61987 | 轨迹相似度加权基线（动作相关） | Eq4–5；Table1 | Qwen3-8B ACC 49.7 vs GRPO 44.7；4B 46.0 vs 39.9 | 未报告 | 反例：有增益但无无偏性保证 |

## 成功条件 / 失败模式
**成功条件**
- 有一个便宜且独立的基线来源。
- 用真实的梯度方差验证收益。

**失败模式**
- 有限组中基线包含当前样本，带来相关性偏差（2505.23585 failure_boundary）。
- 某条极长响应会主导长度加权基线 $\hat b$（2505.23585 degenerate_cases）。
- EBPO 对 G 敏感，G=32 时反转（2602.05165）。
- critic 的质量非单调，FrozenLake 中门控频率中途反转（2604.19485 §4.3）。
- 若直接用生成后的内部特征给自身做基线，会产生偏差（2605.07579 why_non_obvious）。
- cosine 为负或行和为 0 时，加权基线无定义；只有自身相似时 A=0（litscan:61987 degenerate_cases）。

## 审稿期望
- 推断的要求：
  - 报告真实的 score-weighted 梯度方差，做法是同 batch 反传、不更新参数；
  - 用"自然—自然"一致率作参照（P09 成功判据）。

## 认知障碍
- critic 存在不等于 critic 有益。用可观测的质量指标门控有噪估计器，而不是固定信任或一律丢弃（2604.19485 abstract_strategy）。
- 依赖行动的信息可以用，前提是通过独立样本交叉使用（2605.07579 abstract_strategy）。

## 工程经验
- 基线与 loss 聚合要一起推导。先隔离三个因素：去 std、新鲜采样、长度加权（2505.23585 lesson）。
- 把统计指标当作优化器的门时，要分开三件事：总体恒等式、样本估计、实际 PG 性能（2604.19485 lesson）。
- 用完整轨迹决定基线权重时，先做以下检查：自身权重、负余弦、零分母、动作依赖（litscan:61987 lesson）。

