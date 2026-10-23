---
id: PC-F2-16
name: 保留全 token 的结果优势；把过程/成本信号做成独立通道，分别归一化、系数放在 std 之后，只路由到对应 token
family: F2_credit
status: candidate_pattern
problems: {P01: 3, P15: 3, P12: 3, P04: 2, P20: 2, P14: 2}
members: [2502.01456, litscan:29582, litscan:73207, 2610.12060, 2609.29050, 2504.15275, 2609.24290, 2610.31544]
rs_patterns: [heterogeneous_decomposition, self_supervised_signal_engineering]
---

## 操作

$$A_{it}=\underbrace{A^{out}_i}_{\text{全 token}}+\omega\cdot\mathbf 1[t\in T_{target}]\cdot\underbrace{\mathrm{Norm}_{\text{own group}}(x_{i})}_{\text{独立通道}}$$

要点三条：
1. 结果通道不动；
2. 辅助信号在自己的比较组内归一化；
3. ω 乘在归一化之后，只作用于目标 token 段。

成员实例：
- PRIME：过程 token 减其他 response 的平均过程分作基线，未来折扣求和，再加 outcome RLOO（2502.01456 签名）。
- Stop Summation：$A_{it}=r^v_i-\frac{\sum_{k\ne i}r^v_k}{K-1}+G^p_{it}-\frac{\sum_{k\ne i}\sum_lG^p_{kl}}{(K-1)N}$（2504.15275 Eq7）。
- Rewarding Progress：$Q^\pi+\alpha A^\mu$（litscan:29582 Eq5）。
- POLIA：$A^{ext}$ 给全部推理 token，$\omega A^{int}_{i,o}$ 只给对象坐标 token，$A^{int}$ 在"相同对象集合"的组内 mean/std（litscan:73207 Eq1）。
- Visual Memory（TRACE 路由器）：$A^{acc}$ 为 LOO，给全部路由动作；成本只在答对子集内中心化 $A^C_i=\mathbf1_{i\in I^+}(\bar C_+-C_i)$，只路由到 UPDATE 时的 region 选择；$|I^+|<2$ 时置 0（2610.12060 Eqs23–26）。
- SLCA：各段只在 present 样本中算 std，λ 放在 std 之后（2609.29050 AppA.3 Eq17–19）。
- Twin：$A_{turn}=\text{zscore}(U)+\omega\hat A_t/\text{std}_{batch}$（2610.31544 Eq4）。
- CIGAsk：terminal 与 intrinsic 分别 z-score 后相加（2609.24290 签名）。这是"系数放错位置"的反例，见下。

## 信息

本卡是**归一化与路由的结构**，与辅助信号来自哪里无关。PRIME 是隐式 PRM，POLIA 是 GT 框 IoU，2610.12060 是驻留成本，Twin 是耦合续写。这里不合并它们的信息，只合并"通道结构"这一操作。辅助信号自身的可靠性，见对应信息卡。

## 成立条件

- 辅助通道在自己的组里有方差。POLIA 单例组的 $A^{int}=0$（litscan:73207 degenerate_cases）；2610.12060 在答对数 <2 时成本优势为 0（Eq23–24）。
- 结果通道在所有 token 上保留。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2502.01456 | 隐式 PRM 过程 return + outcome RLOO，分别中心化 | Table1 | 同 240 步 PRIME 平均 41.0 vs outcome-only RLOO 36.9；每步 680.3 s vs 530.7 s | 记录未覆盖 | 成员 |
| litscan:29582 | outcome + prover 优势 | AppE / Fig15 | 相对 ORM-RL 5× sample efficiency，+6% | 记录未覆盖 | 成员 |
| litscan:73207 | 坐标 token 独立 exact-set 组优势 | Table1 p6 | 7B VSR 81.3 vs GRPO 59.0；GQA 69.5 vs 58.2；3B GQA 60.2 低于 few-shot SFT 64.6 | 记录未覆盖 | 成员 |
| 2609.29050 | present 过滤的分段 std，std 后乘 λ | Table2 p9 | 见 PC-F2-15 | 3 runs | 成员 |
| 2610.31544 | episode z-score + ω·twin/std_batch | Table3 | twin-only 41.7 < 混合 42.7 | 3 seeds | 成员 |

## 成功条件 / 失败模式

- 成功：辅助信号在自己的组里有方差；ω 在 std 之后；结果通道完整。
- 失败：
  - 纯 min PRM 约 270 步仍被 hack；双倍过程 reward 365 步塌缩（2504.15275 negative_results）。
  - PRIME 默认用更新前的 PRM 分数，不是新 PRM 重算；比纯 RLOO 每步更贵（2502.01456 failure_boundary）。
  - POLIA 依赖 GT 框，单例组无信号（litscan:73207 failure_boundary）。
  - 2610.12060 的峰值显存 42.67 GiB 高于 Full 38.40；收益依赖 teacher/SFT 与可恢复 KV（2610.12060 negative_results）。

## 审稿期望

Stop Summation、POLIA、2610.12060、SLCA 均为 low_evidence。"推断"：
- 辅助通道"有效样本比例"的报告（多少组的 std>0）；
- ω 扫描并证明效果随 ω 单调（P01 的成功判据）。

## 认知障碍

- 比较对象与梯度路由同时改变；同对象集合并不代表相同的推理状态或真正相同的可见证据（litscan:73207 why_non_obvious）。
- 固定压缩会丢掉未来证据，更少的活跃 token 可能诱发更长的回复；驻留成本不等于调用次数（2610.12060 why_non_obvious）。

## 工程经验

- 当拆信用通道时，要独立核对有效样本集、归一化之后的权重、token 边界与缺段处理，再用 support 对照区分归一化带来的收益（2609.29050 lesson）。
- λ 必须放在 std 之后（2609.29050 REL P01:3）。
- PRM 数值有不同量纲：sum 分与 min 变换后的总分不能直接比较（2504.15275 pitfalls）。
- 驻留期间 Fine 仍占用，成本不能只计 UPDATE（2610.12060 pitfalls）；对裁图而言，成本应同时计次数与视觉 token。
- 当用事后视觉引用集合分组时，先报每组支持与有效坐标更新的比例（litscan:73207 lesson）。

