---
id: PC-F2-20
name: 把逐轮势差 Φ(s')−Φ(s) 当塑形或优势，靠 telescoping 保端点——区分严格 PBRS 与非不变变体
family: F2_credit
status: candidate_pattern
problems: {P19: 3, P14: 2, P09: 2, P12: 2, P11: 1}
members: [litscan:73124, litscan:29582, 2605.27788, 2610.15840, 2609.35084, 2607.13988, 2601.03823, 2606.30251]
rs_patterns: [algebraic_equivalence_unification, targeted_self_supervised_objective]
---

## 操作

在轮边界上定义势 Φ（策略似然、critic 价值、冻结读者可读性、经验图成功率等），把 $F_k=\gamma\Phi(S_k)-\Phi(S_{k-1})$ 加到奖励上（严格 PBRS），或把 $\Phi(S_{k+1})-\Phi(S_k)$ 直接当作该轮的优势（非严格变体），并以 $\sum_kF_k$ 的 telescoping 论证"端点不变"。

**本卡回答 MENTOR_PATTERNS §4 的问题**：对每个成员，写清它是严格 PBRS（保持最优策略、单独用不能减少裁图），还是非不变的价值/势打分。

| paper_key | Φ 的来源 | 用法 | 是否严格 PBRS | 依据 |
|---|---|---|---|---|
| litscan:73124 TIPS | 滞后策略 teacher 对 GT 的 $\log\sum_a p_{teach}(a|S)$ | 加到 reward 段边界，经 GAE（γλ=1） | **条件严格**：γ=1、轨迹内 α 与 teacher 固定、终止势为 0 时，return 只差一个前段状态常数，$G^{R+I}_t=G^R_t-\alpha\Phi(S_{k-1})$ | Eq2 / AppF Eq21；invariance 记录 |
| litscan:29582 Rewarding Progress | prover μ 的 $Q^\mu-V^\mu$ | 加到 outcome 系数 $Q^\pi+\alpha A^\mu$ | **否**：作者 AppI 称 PBRS，但实际的旧状态分布代理不能据此无条件推出全训练不变性 | failure_boundary |
| 2605.27788 CARL-seg | 学到的 on-policy critic | $A_k=V(s_{k+1})-V(s_k)$ 直接作段优势 | **否**：telescoping 只是数值恒等式；势随策略学习而变，不能称固定势 PBRS | Eq1–2；invariance |
| 2610.15840 LVRL | 冻结 LLM 读完整未来的价值 | $D_{it}/\sigma_{step}$ 作步优势 | **否**：依赖未来的 hindsight 价值不是状态势；直接作优势，而非加 γΦ(next)−Φ(state) | invariance |
| 2609.35084 GraphHCA | 经验图成功率 | log 势差，同状态 std 后加回 AT | **否**：statewise std 破坏 telescoping，且直接加到优势上 | invariance |
| 2607.13988 TRACE | 冻结初始化读者的 GT gap | log gap 差，K 窗口平均 + 终端补 | **否**：窗口平均、终端补、变长 token 加权都打破端点形式 | invariance |
| 2601.03823 SPAE | 当前策略 probe（置信度 × GT 概率） | 饱和衰减 × 结果 + 居中 ΔΦ + 全 batch 标准化 | **否**：非线性、居中 ΔΦ、乘性 f、token 标准化都不满足固定势的 telescoping | invariance |
| 2606.30251 TACO | 前后 probe 答案分 | 差分 Δ + 组标准化 + 结果掩码 | **否**：Prop2 需要固定势、完整转移加和、terminal=0；本文只有分支差分、g 选择、组标准化与掩码 | invariance |

## 信息

本卡按**操作**（势差 + telescoping 论证）合并，各成员 Φ 的信息来源不同（见上表），各自在 PC-F2-04/07/08/12/03/09 有对应的信息卡。之所以单独成卡，是因为"是否保持最优策略"是与信息无关的结构性质，而它直接决定 P19 的答案。

## 成立条件（严格 PBRS 的条件，取自 TIPS 记录）

- γ=1（或与任务折扣一致）；
- 势只依赖状态，且在一条轨迹内固定（teacher 与 α 固定）；
- 所有终止状态的势为 0；
- 动态 α 若在轨迹内逐边界变化，差分就不再简单 telescoping，需要补偿项（litscan:73124 invariance）。
- 即便满足以上条件，GAE、PPO clip、critic 近似带来的有限样本行为改善，也不等于每次更新都在数学上等价（同上）。

## 成员证据

| paper_key | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|
| litscan:73124 | Table1; Table4 / §4.3 | 7B average EM 37.28→41.71（+4.43pt）；history-max（非 PBRS 截断）35.20 < outcome 37.28；跨骨干强 teacher 伤害 | 未给多 seed | 成员（唯一条件严格者） |
| litscan:29582 | AppE / Fig15 | 5× sample efficiency，+6% | 记录未覆盖 | 成员 |
| 2605.27788 | Table2 | Hotpot 47.9 vs 42.8 | 3 seeds | 成员 |
| 2610.15840 | Table1 | AppWorld 26.3 vs 19.8 | 3 seeds | 成员 |
| 2609.35084 | Table2 | Sokoban 84.0 vs 71.1 | 3 seeds | 成员 |
| 2607.13988 | Table1 | 4B 29.5→34.0（作者称鼓励更长交互） | 单 run 消融 | 成员 |
| 2601.03823 | Table1 | 63.86 vs 62.73，长度 6825 vs 8213 | 训练 seed 未见 | 成员 |
| 2606.30251 | Table3 | 72.0 vs 70.0 | 未报告 | 成员 |

成员之间不冲突：唯一条件严格的 TIPS 报告的是**准确率**提升（与"加速信用传播"一致），而不是行为偏好改变。其余成员改变了目标，其方向须逐一审计。

## 成功条件 / 失败模式

- 严格 PBRS 能做的：降方差、加速信用到位。TIPS 在 PPO/GAE 下 +4.43pt。
- 严格 PBRS 不能做的：让"少裁图"成为新的最优解（MENTOR_PATTERNS §4；Ng et al. 1999 由该文档引用）。
- 失败：
  - history-max 截断丢掉负 delta，变成非 PBRS，并且更差（litscan:73124 Table4）。
  - 非严格变体中，端点守恒只限标量；token 重复长度、不同 score 梯度、ratio/clip 都会破坏"总梯度方向守恒"（2610.15840 invariance）。

## 审稿期望

TIPS、CARL-seg、LVRL、GraphHCA、TRACE、SPAE 均为 low_evidence。"推断"：凡声称"potential-based"的方法，审稿会要求：
- 写出 terminal 边界、折扣、return-to-go 与 token 聚合（P19 证据：decision_loss_redesign README Q6）；
- 给"随机势"对照（TIPS transfer 建议）。

## 认知障碍

- teacher 更强不等于与 actor 行为对齐；在严格 PBRS 下，总 return 只是状态基线的变化，不会新增最优动作偏好（litscan:73124 why_non_obvious）。
- 形似 PBRS 的 TD 优势其实依赖学习中的 critic，不能称严格固定势（2605.27788 invariance）。

## 工程经验

- 当使用似然差塑形时，先核终止修正与 token return，再测 teacher 对齐；不能把教师信心的提升称为当前策略需要的信息（litscan:73124 lesson）。
- 需要在正确的边界注入、mask 环境 token；终止势为 0 与 teacher 刷新必须对每条轨迹一致（litscan:73124 pitfalls AppF / §3.2）。
- 当用共享图估值时，不能把数学上收敛当作估计正确（2609.35084 lesson）。

