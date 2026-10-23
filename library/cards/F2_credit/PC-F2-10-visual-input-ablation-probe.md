---
id: PC-F2-10
name: 比较同一模型在真实/替代/空白视觉输入下的答案分数差，用作信用门控、奖励加成或路由标签
family: F2_credit
status: candidate_pattern
problems: {P43: 3, P16: 2, P11: 2, P17: 2, P42: 2, P44: 1}
members: [litscan:76688, litscan:75333, 2602.01034, 2608.21762]
rs_patterns: [heterogeneous_decomposition, controlled_diagnostic_design]
---

## 操作

固定文本前缀，只干预视觉输入，用同一模型（训练中的策略，或冻结的同一目标模型）计算答案分数差：
- CofactGVR：真实预测框与随机加噪框各采样答案，$d=[\mu-\mu_c]_+$，$b=\mathbf1[d>\gamma]\,\text{clip}(d,b_{min},b_{max})$，只加给答对或 top-k 的真实 rollout（litscan:76688 Eq2–8）。
- MIRL：caption 的有图/无图 log 似然差 $s(D)=\frac1{|D|}\sum_t[\log p(y_t|I,q,y_{<t})-\log p(y_t|q,y_{<t})]$，clip 后作 caption 通道奖励，并用它选前缀再 fork 推理（litscan:75333 Eq5, Eq2）。
- SIR 视觉门：$S=\sigma(5[\ell_{real}-\ell_{blank}-0.1])$，用它软缩放过程奖励与准确率奖励（2602.01034 Eqs3–5）。
- GapSight：离线 $\Delta_i=\mathcal L_{NLL}(y|q,g(x))-\mathcal L_{NLL}(y|q,g(x),c(x,b_i))$，取候选框中 gap 最大者，蒸馏到外接路由头，骨干冻结（2608.21762 Method p.4）。

## 信息

- 看得到：同一模型在两种视觉条件下对 GT（或自身采样答案）的分数。
- 看不到：
  - 替代输入是否在分布内。CofactGVR 的加噪框是 OOD（litscan:76688 failure_boundary）。
  - 首决策时可用的信息：SIR 的门在完整 z 生成后才换图（2602.01034 signal_routing）。
- 估计者：策略自身（CofactGVR、MIRL、SIR）；GapSight 是冻结的同一目标模型，部署时骨干不变。

## 成立条件

- 替代输入与真实输入在框形、token 数上匹配，否则分数差混入"多了图像 token"的效应。记录说 CofactGVR "不是匹配框形的逐次内容效应，也不是裁图相对直答的价值"（litscan:76688 failure_boundary）。
- 候选集要覆盖真正有益的区域；bank 里没有好框，不能证明原图无需裁（2608.21762 failure_boundary）。
- 分数类型（NLL 的 sum/mean、margin 的 logit/prob）要与部署一致（2608.21762 lesson）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:76688 | 真/加噪框答案正确率差，正向截断 bonus | Table4 / §4.3 | 去反事实：MME 2428.5→2349.1，RWQA 66.9→63.8；不设边界 MME 2341.6；全体加 bonus RWQA 61.7 | 记录未覆盖 | 成员 |
| litscan:75333 | caption 有/无图似然差，分阶段奖励 | Table2; Table3 | 平均 70.22 vs DAPO16 69.76；同 fork random 68.74；MI-only 68.81；Table3 task-only 65.23 优于 decoupled 63.46 | 记录未覆盖 | 成员（正文与附录的路由叙述冲突） |
| 2602.01034 | 真实/空白图似然差 soft gate | Table2 | 3B 视觉 avg 59.0；无 visual gate 56.1；ChartQA 有 gate 80.9 低于无 gate 81.8 | single seed | 成员 |
| 2608.21762 | 同模型 loss-gap 离线标签 → 外接路由头 | Table3 p.5; Fig3; Table4 | 只换 label teacher：loss-gap 均分 71.57 vs CLIP 66.88 vs random 64.00；跨骨干效用保留均值 0.44；107 修复 / 27 破坏 | Table1 三 seed mean±SD | 变体成员（用作标签，不是 RL 信用） |

## 成功条件 / 失败模式

- 成功：替代输入在分布内；分数差只作门控/加成，且有上下界。
- 失败：
  - 全体都加 bonus 会掉点（RWQA 61.7）；不设边界也掉（MME 2341.6）（litscan:76688 Table4）。
  - MIRL 的 Table3 中 task-only 优于 decoupled，与其主张冲突；自动描述定位与 GPT4 一致率仅 74%（litscan:75333 negative_results）。
  - 视觉门在 ChartQA 上 −0.9（2602.01034 negative_results）。
  - 跨骨干的框迁移只保留部分效用，InternVL 框 → LLaVA 为 .01（2608.21762 Fig3）。
  - 高 MI 可能强化与视觉相关的幻觉（litscan:75333 degenerate_cases）。

## 审稿期望

四篇均为 reviewer_concern=low_evidence。"推断"：
- 必须给"同框形别处像素 / 内容打乱"的对照，而不只是随机噪声框或空白图；
- 等采样预算；
- 报告被门控置零的比例。

## 认知障碍

- 反事实只用来估奖励，不进入优化；奖励门控与非均匀采样改变的是两个不同通道（litscan:76688 why_non_obvious）。
- 人工框或 CLIP 相关性不保证特定 VLM 受益；所需区域还依赖编码器、tokenizer 与上下文（2608.21762 why_non_obvious）。

## 工程经验

- 当反事实 bonus 改善答案时，应分别审计奖励输入、被更新的 token 和采样分布；否则无法推断裁图动作的信用（litscan:76688 lesson）。
- 当缓存前缀 fork 时，应单独核对共享前缀的 loss 计权、未选分支的准确率缺失，以及总前向成本（litscan:75333 lesson）。
- 当离线 gap 由某个固定模型与预览配置产生时，应把 checkpoint、预览分辨率、打分方式、候选 bank、阈值与 head 的读取位置一起锁定（2608.21762 lesson）。
- CofactGVR 的正文奖励与附录的归一化输入、优化符号不一致，不能按论文名假定是标准 GRPO（litscan:76688 pitfalls）。

