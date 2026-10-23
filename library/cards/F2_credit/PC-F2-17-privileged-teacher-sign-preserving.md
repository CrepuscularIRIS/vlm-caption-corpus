---
id: PC-F2-17
name: 用 GT/特权条件的教师与学生的 log 差定位关键 token 或段，保留结果优势的符号做有界调幅
family: F2_credit
status: candidate_pattern
problems: {P11: 2, P15: 2, P16: 2, P20: 1, P02: 1}
members: [2605.11853, 2608.13179, 2608.04007, 2606.29476]
rs_patterns: [heterogeneous_decomposition, outside_taxonomy]
---

## 操作

$$A_t=A^{out}\cdot W_t,\qquad W_t\in[w_{min},w_{max}],\ \text{且 }W_t\text{ 的选取依赖 }\operatorname{sign}(A^{out})$$

$W_t$ 来自"看到特权信息的教师"与学生在学生自己采样的 token 上的 log 差：
- GEAR：同一模型以 GT 为条件作教师，用采样 log-ratio 的峰值触发段，熵增长时终止；按优势符号把偏离信号转成局部乘法权重（2605.11853 签名）。
- Verifier-Anchored：先对每个有独立 verifier 的 turn 分别做组 std；再用 GT 条件的自教师对 token 做"方向一致、surprisal 门控"的有界放大（2608.13179 签名）。
- TurnSight：**冻结**初始参考看当前执行结果及 1/2/3 步后见，teacher-force 原 response；按 turn 聚合、跨 horizon 方向共识选择，有界调制原优势大小（2608.04007 签名）。
- CRAFT：用兄弟 rollout 的自归一化重要性权重得到 $CTI_i=\sum_{j\ne i}\text{softmax}(\Delta_j/\tau)A_j-A_i$，signed sigmoid 后 stop-gradient 乘 logπ 作辅助项，主 GRPO 不变（2606.29476 签名）。

## 信息

- 看得到：GT 或特权技能 context 条件下的教师 logprob、学生 logprob、学生的结果优势。
- 看不到：动作的反事实价值。teacher 偏离不等于"该动作有无工具下的成功差"（2605.11853 KF 记录）。
- 估计者：GEAR、Verifier-Anchored 用同一模型加 GT 条件；TurnSight 用冻结初始参考；CRAFT 用特权 teacher。

## 成立条件

- 结果优势非零。全组 A=0 时，乘法无法产生训练信号（2605.11853 failure_boundary；2608.04007 KF 记录"零 base adv 保持零"）。
- 教师偏离的起点能定位"出错段"；偏离之后师生都可能顺着同一错误前缀走，所以要把起点信号扩到连续段（2605.11853 why_non_obvious）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.11853 | GT 条件自教师峰值段，符号感知乘权 | Table2 p9 | Test .739 / MATH .879；去 segment .683/.844；tool-boundary 分段 .682/.840 | 记录未覆盖 | 成员 |
| 2608.13179 | 逐 turn verifier 组 std + 自教师 surprisal 有界放大 | Table3 | 4B BFCL 43.63（GRPO）→ 52.00；WildTool session 4.69→7.03；8B session 5.47→9.38 | 单训练 seed（3 次 decode） | 成员 |
| 2608.04007 | 冻结参考的多 horizon 后见 log gap，turn 聚合，有界调幅 | Table1 | Qwen3-8B 总 avg 42.02 vs MatchTIR 39.03 / GRPO 30.93；FTRL avg 46.92，去 turn 聚合 43.23，去组归一 43.65 | 记录未覆盖 | 成员 |
| 2606.29476 | 兄弟 SNIS 反事实信用作 detached 辅助项 | Table3 | Qwen2.5-3B Full 87.0 / 46.1 / 87.3 vs 无 CTI 84.2 / 43.5 / 84.8（ALF / Search / WebShop） | 部分 baseline 取自前作 | 成员 |

## 成功条件 / 失败模式

- 成功：结果优势有方差；教师偏离与真实错误段对齐。
- 失败：
  - 保留标量符号不等于保留共享参数下的整体梯度方向（2608.13179 why_non_obvious；2608.04007 failure_boundary）。
  - 全错 turn 组的优势为 0，不是负（2608.13179 failure_boundary）。
  - CRAFT 的兄弟在同一 token 位置通常是不同前缀，不是固定状态下的一次动作干预（2606.29476 why_non_obvious）。
  - 按"工具边界"分段（.682）不如按偏离峰值分段（.739）（2605.11853 Table2）。

## 审稿期望

记录中无审稿。"推断"：
- 与"同均值的常数权重"对照，以区分局部分配与全局学习率变化（LUT 的 lesson 提出了同类要求，2608.00743）；
- 报告 W 的分布与触发比例。

## 认知障碍

- 把 turn 的结果信号与 token 的重要性隔开：保留标量符号，但不保留共享参数下的整体梯度方向（2608.13179 why_non_obvious）。
- 后见信号与当前访问的状态对齐，但不是反事实价值；保留标量符号不等于保留原优化目标（2608.04007 why_non_obvious）。

## 工程经验

- 当用乘性 gate 调制优势时，须记录 detach、均值增幅与完整的优势公式，否则无法区分局部分配与全局学习率变化（2608.00743 lesson，LUT，同类操作）。
- 当把兄弟 rollout 当反事实时，要承认它们通常是不同前缀，不是固定状态干预（2606.29476 why_non_obvious）。

