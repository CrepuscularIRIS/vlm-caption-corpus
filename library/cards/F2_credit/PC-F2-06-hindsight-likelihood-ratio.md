---
id: PC-F2-06
name: 用"已知结局时该动作的似然 / 策略似然"之比重加权未来回报，构造动作级后见信用
family: F2_credit
status: candidate_pattern
problems: {P11: 2, P09: 2, P18: 1, P16: 1}
members: [1912.02503, 2011.09464, 2603.08754, 2610.07349, 2603.18683, 2609.35084]
rs_patterns: [algebraic_equivalence_unification, self_supervised_signal_engineering, heterogeneous_decomposition]
---

## 操作

估计后见分布 $h(a\mid s,\text{future/outcome})$，用 $h/\pi$ 改写信用：

- 原式：用 $(h/\pi-1)$ 重加权未来奖励；$h/\pi=1$ 时该未来奖励对优势贡献为 0（1912.02503 §3.1 Eq3 后）。
- 未来条件基线：$g=\sum_t\gamma^t\nabla\log\pi(A_t|X_t)[G_t-V(X_t,\Phi_t)]$，要求 $A_t\perp\Phi_t\mid X_t$（2011.09464 Eq4 / Theorem2）。
- LLM 版本：
  - $\pi_{hind}=\exp(\text{mean token logp}/T)$，$\rho=\text{clip}(\pi_{hind}/\text{本轨迹动作均值})$，$Q^H=\rho\gamma^{T-t}R$，$A=\text{zscore}(R)+\omega\,\text{zscore}_t(Q^H)$（2603.08754）。
  - 长度归一化似然比 → 轨迹均值归一与 clip → 加权回报 → 同组均值/std → 与宏观优势相加（2610.07349 RELACE）。
- 闭式：$h(a|s,G)/q(a|s)=\Phi(\text{next})/\Phi(s)$，再取 log 差（2609.35084 Eq3–8）。HISR 用未来条件似然比 z 调节段奖励（2603.18683）。

## 信息

- 看得到：已执行动作、真实最终结局（训练期）、同模型（或训练出的 h）在给定结局下对该动作的似然。
- 看不到：替代动作的真实结果；也不做反事实续跑（2603.08754 签名）。
- 估计者：当前策略或行为策略的后见似然。是否冻结视实现而定；RELACE 用冻结的当次行为策略（2610.07349 签名）。

## 成立条件

- 精确的当前策略条件分布，且 $\pi(a|x)>0$。学习误差下无偏结论不成立（1912.02503 failure_boundary）。
- 未来信息必须与被信用的动作条件独立；实用分类器只能近似独立，理论无偏不能自动继承（2011.09464 failure_boundary）。
- LLM 版用"轨迹内其他动作的平均似然"代替先验，跨时间/状态的均值不是同状态先验；成功结局 prompt 为 OOD（2603.08754 failure_boundary）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 1912.02503 | (h/π−1) 重加权 | §3.1 Eq3 后 | 理论：h/π=1 时贡献为 0 | 理论 | 成员 |
| 2011.09464 | 未来条件基线 + 动作独立约束 | Eq4/Theorem2；§4.2/AppA1 | 精确独立下优势二阶矩不增；普通 actor-critic 在低方差任务上也可完美解决，HCA 因后验不精确可能退化 | Fig5 中位数 10 seeds | 成员（含负结果） |
| 2603.08754 | 同 LLM 成功条件似然比，加到 GRPO 优势 | §6.2 | 7B ALFWorld 91.4 vs GRPO 77.6；WebShop 成功 73.8 vs 66.1 | 3 seeds | 成员 |
| 2610.07349 | 加权回报与局部组基线用同一统计量，合并宏观优势 | Table2 | WebShop SR 79.43；hindsight-score weighting 75.78；GiGPO 73.83 | 记录未覆盖 | 成员 |
| 2603.18683 | 后见似然比调节段奖励 | Table1 | 去 hindsight：ALFWorld 83.6→80.6，WebShop 69.1→63.7 | 记录未覆盖 | 成员（亦见 PC-F2-05） |
| 2609.35084 | 后验比转成功值比，经验图闭式 | Table2 p9；Eq3–9 | Sokoban 84.0±1.2 vs GRPO 71.1±3.9 | 3 seeds | 成员（亦见 PC-F2-03） |

## 成功条件 / 失败模式

- 成功：结局能区分过去动作的贡献，策略在动作上有足够熵。
- 失败：
  - 近确定策略下动作分类器判别弱，数据支持差（2011.09464 degenerate_cases）。
  - 高后见似然可能只是原动作本来概率就高；回顾相关性不是因果贡献（2610.07349 why_non_obvious 与 failure_boundary）。
  - R=0 时所有加权 Q 都是 0；单例或常数局部组置 0（2610.07349 KF 记录）。

## 审稿期望

CCA 有 reviewer_concern=low_evidence。"推断"：报告后见比率的分布与 clip 触发比例；对比"同状态先验"与"轨迹均值先验"。

## 认知障碍

- 动作依赖的基线通常有偏，但精确的后见比率能让期望基线梯度为 0（1912.02503 why_non_obvious）。
- 未来信息能降方差，但一般会因动作依赖而带偏；仅仅是 critic 拟合得更好，并不足以保证合法（2011.09464 why_non_obvious）。

## 工程经验

- 当基线读取未来信息时，必须检查动作信息泄漏，并停止 actor 经基线的反传；不能用"预测 return 更准"代替无偏性条件（2011.09464 lesson）。
- 当用同模型后见似然时，先验应取同状态的动作分布，而不是跨时间的轨迹均值（2603.08754 failure_boundary）。

