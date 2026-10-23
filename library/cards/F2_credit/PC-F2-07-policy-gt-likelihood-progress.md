---
id: PC-F2-07
name: 用当前（或滞后）策略对 GT 答案的 teacher-forced 似然在各轮边界的进度作逐轮信号
family: F2_credit
status: candidate_pattern
problems: {P11: 2, P16: 2, P17: 2, P19: 2, P43: 2, P14: 1}
members: [2605.06200, 2601.03823, 2602.01034, 2610.12828, litscan:73124]
rs_patterns: [targeted_self_supervised_objective, heterogeneous_decomposition, generative_process_redesign]
---

## 操作

在每个轮边界 $S_k$，用当前（或滞后同步的）策略对 GT 答案做 teacher forcing，得到长度归一化的对数似然 $\ell_k$（或概率）。把相邻差 $\ell_{k+1}-\ell_k$ 作为该轮的过程信号，再与结果优势合成。

- A²TGPO：按 (prompt, turn-index) 对 GT 概率增益做 z-score；把未来轮的增益折扣累加到较早轮后除以 sqrt(剩余轮数)；再加结果 z-score，并按局部增益自适应 clip（2605.06200 签名）。
- SPAE：用 5 个短 probe 得到 entropy 置信度与 GT 概率，构造 $\Phi=1.5\,\text{Acc}\cdot\text{Conf}+0.5\,\text{Acc}-\text{Conf}$。组均值结果优势乘饱和衰减 f，再加 batch 相对的 ΔΦ 塑形 g，最后全 batch token 标准化（2601.03823 Eqs5–8, 11–17）。
- SIR：$h_k=\max(h_{k-1},\ell_k)$，$g_k=(\ell_k-h_{k-1})_+$，$R_M=\max_k\ell_k-\ell_0$，组内标准化后广播到整个 think 段（2602.01034 Eqs1–2, Prop1）。
- TreeHCA：用金答案平均 token logp 差作轮分，低分轮的父节点重采样，逆分数回传叶优势（2610.12828 签名）。
- TIPS：$\Phi(S)=\log\sum_{a\in\mathcal A}p_{teach}(a|S)$，teacher 为每 200 次更新刷新一次的滞后策略，$\Delta_k=\alpha[\Phi(S_k)-\Phi(S_{k-1})]$，$\Phi(S_K)=0$（litscan:73124 Eqs15–20）。

## 信息

- 看得到：策略自身（当前或滞后）在每个前缀下给 GT 答案的似然；训练期需要 GT。
- 看不到：自然采样下的答对率（teacher forcing ≠ 自回归正确率）；替代动作；视觉信息是否真正进入了证据。
- 估计者：策略自身，不是冻结外部读者。TIPS 用滞后策略，且实证跨骨干、更强的 teacher 反而伤害（litscan:73124 Table4 / §4.3）。

## 成立条件

- 答案结构化、可 teacher-force（2601.03823 conditions："structured answers"）。
- probe 只在训练期可用，不能部署成无 GT 的停止器（2601.03823 failure_boundary）。
- 需要逐轮边界可识别；SIR 的 gate 以完整的 z 换图，z 已携带图像信息，不是前瞻部署信号（2602.01034 signal_routing）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.06200 | 同索引 turn 组 z-score 的 GT 概率增益 + 结果 z-score | Table2 p7 | 样本加权多跳 Avg：IGPO 44.88 → TG-Norm 46.27 → rescale 46.71 → full 48.06 | 记录未覆盖 | 成员 |
| 2601.03823 | probe 势 Φ，饱和衰减 + ΔΦ 塑形，全 batch 标准化 | Table1; Table2 | Qwen7B macro acc 63.86 vs DAPO 62.73，长度 6825 vs 8213；去饱和 63.98 / 7517；α1 62.68；ξ.1 62.40 | eval 16 runs，训练 seed 未见 | 成员 |
| 2602.01034 | 水位线 HWM 过程通道 + 结果通道 | Table2 | 3B 视觉迁移 avg 59.0 vs binary 54.2 | single seed | 成员 |
| 2610.12828 | 金答案 logp 差轮分 + 低分父节点重采样 | Table4 | Qwen3-4B HotpotQA hindsight+TreeHCA 51.76 EM / 65.88 F1；同探索 AT2PO 信用 49.60 / 62.74 | 单 seed 消融 | 成员 |
| litscan:73124 | 滞后策略 GT 似然势差，终止势 0 | Table1; Table4 / §4.3 | 7B average EM 37.28→41.71（+4.43pt）；history-max 35.20 < outcome 37.28 | 未给多 seed | 成员（亦见 PC-F2-20） |

## 成功条件 / 失败模式

- 成功：答案短、可验证；teacher 与 actor 同族、同步（TIPS 的滞后刷新）。
- 失败：
  - 跨骨干更强的 teacher 伤害 7B；刷新太频繁或不刷新都可能更差（litscan:73124 negative_results）。
  - SPAE：Llama8B AIME25 36.88 < DAPO 37.08；Qwen3 GPQA 50.86 < base 51.17（2601.03823 Table1）。
  - A²TGPO 按位置配对，同 (q,t) 组允许不同历史，不是同前缀反事实（2605.06200 failure_boundary）。
  - SPAE 的 g 相对 batch 均值取符号：正 ΔΦ 也可能得负 g（2601.03823 invariance）。
  - SIR 单 seed；逐步探针不等于逐步优势，默认聚合后统一路由（2602.01034 why_non_obvious）。

## 审稿期望

SPAE、SIR、TIPS 均为 reviewer_concern=low_evidence。"推断"：
- 报告所有归一化阶段之后过程信号的符号分布，以及错误轨迹上的梯度方向（2601.03823 lesson）；
- 加入"随机势"对照（TIPS transfer 建议）。

## 认知障碍

- 同一 IG 来源，若跨位置混合标准化、并改变累计尺度，会改变信用；改奖励来源并不是唯一可选的改法（2605.06200 why_non_obvious）。
- 把终局奖励拆成步共同信号；但 probe 依赖 GT，数值变换使它不再是标准 PBRS（2601.03823 why_non_obvious）。

## 工程经验

- 当把进度代理直接转成优势时，要检查所有归一化阶段之后的符号与错误轨迹的梯度；不能因为 probe 不反传就说它对训练无影响（2601.03823 lesson）。
- 当逐前缀奖励最终被聚合时，要明确"标量广播"与"按步路由"的区别（2602.01034 lesson）。
- 当用似然差做塑形时，先核终止修正与 token return，再测 teacher 对齐（litscan:73124 lesson）。

