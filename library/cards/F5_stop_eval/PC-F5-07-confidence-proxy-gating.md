---
id: PC-F5-07
name: 用策略自身的置信度代理（熵、top-2 差、隐状态一致性、query 概率）决定是否再取证
family: F5_stop_eval
status: candidate_pattern
problems: {P34: 3, P26: 2, P31: 2, P33: 1, P29: 1}
members: [2406.19215, 2603.21754, litscan:3599, litscan:77776, 2510.05069, 2505.17281, litscan:3289]
rs_patterns: [controlled_diagnostic_design, generative_process_redesign, self_supervised_signal_engineering]
---
## 操作
从当前策略的输出分布或隐状态算一个置信度 $C$，与阈值比较决定是否触发取证/补看或停止搜索。主体是推理期门控；另列两种训练期变体（同一信息、不同路由）以便对照：
- 推理期门控：SeaKR $\mathrm{retrieve}\iff U(c_r)>\delta$，$U$ 为 20 次 EOS 中层隐状态的 regularized Gram determinant（2406.19215 §3.1–3.2）；DaP-ICoT $C_t=\frac1{\lvert T_t\rvert}\sum_i(\ell_{i,w^{(1)}}-\ell_{i,w^{(2)}})$，$C_t<\tau$ 才插入视觉（2603.21754 Eq.1–3）；φ-Decoding 最大 cluster ≥.7 即停止 foresight（litscan:3599 rs.key_step）；V-ABS 以 prior 熵 $H$ 调 prior/observer 权重 $w_p=(1+e^{2(H-.5)})^{-1}$（litscan:77776 Eq7/9）；SwiReasoning 熵趋势切换（2510.05069）。
- 训练期变体 A（置信门控奖励）：β-GRPO $R(T)=1[a_f=a_f^*\wedge C(T)>\beta]$，$C$ 为所有 search query token 的最小概率，β=.4（2505.17281 Eqs1–2）。
- 训练期变体 B（训练置信表达本身校准）：MMBoundary 按内部读数伪标签 SFT 后，用知识正确性、外部校准、内部一致性三奖励 PPO（litscan:3289 Eq10–13）。

## 信息
全部来自当前策略自身（logits、熵、隐状态、生成概率、候选一致性）。看不到真值、同状态"取证 vs 不取证"的收益差、未来观测是否必要（2603.21754 information）。

## 成立条件
- 能读到生成分布或隐状态；阈值在独立验证集上选定（2603.21754 conditions；SeaKR δ 在 NQ 训练子集调）。
- 置信度对"需要新证据"有判别力——**七篇都没有直接测这一条**（见失败模式）。
- β-GRPO 必须从已有 Search-R1 热启动（2505.17281 negative_results）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2406.19215 SeaKR | 隐状态一致性触发检索 + 重排 | Tables1–2 | 2Wiki/Hotpot/IIRC F1 36.0/39.7/23.5 vs DRAGIN 30.0/34.2/22.9；NQ 35.5 低于 Self-RAG 40.2 | 记录未覆盖 | 记录未覆盖 |
| 2603.21754 DaP-ICoT | top-2 margin 门控视觉插入 | Fig.3 p.5；Fig.7 p.6；Fig.6 | 去门控 M3CoT 57.2→42.8；τ=.2 时 57.2，τ=1 时 52.3（非单调）；总 token 314 vs ICoT 1146 不能全归门控 | single，作者称所有方法复现一次 | 记录未覆盖 |
| litscan:3599 φ-Decoding | 未来模拟 + 聚类一致性，共识即停 | Table1 p13219 | Llama3.1-8B 六任务 59.53、FLOPS 6.43e17；CoT 44.91/1.34e16；去 cluster 57.56 | 记录未覆盖 | 记录未覆盖 |
| litscan:77776 V-ABS | 熵调 prior/observer 融合的工具动作 beam | Table4 p7；Table1 | Qwen3 V* 75.9→90.5→SFT 91.1；GPT-4o V* spatial 80.3→67.1、HR8K FCP 67.0→54.1 | 记录未覆盖 | 记录未覆盖 |
| 2510.05069 SwiReasoning | 熵趋势切换 + 切换上限作答 | Table1 | Qwen3-1.7B 60.20→62.88；过强 exit bias AIME24 8.33% | 记录未覆盖 | 记录未覆盖 |
| 2505.17281 β-GRPO（变体 A） | 置信门控结果奖励 | p4 Table2；§4–5 | 平均 EM .309→.344；过搜索 21.10→19.89%，欠搜索 42.04→34.71%；β .2/.4/.6 → .341/.344/.336；从零训练学不到有效搜索 | 记录未覆盖 | 记录未覆盖 |
| litscan:3289 MMBoundary（变体 B） | 逐句置信校准奖励 | Table1；Eq6–7 | AOKVQA Acc .835/MECE .304 vs 无 RL .768/.427；去 RCS 准确率 .857 高于完整 .835 | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：记录内无一篇测量"置信度 vs 取证真实收益"的 AUROC 或校准曲线；成功条件因此**未被确立**，只能说"门控 + 其余部件"整体有效。
- 失败模式：
  - 确定但错误时不触发（2406.19215 degenerate_cases；2603.21754 failure_boundary；litscan:3599 failure_boundary"一致错误可触发提前转直接生成"）。
  - 阈值非单调：过保守与过激进都伤准确率（2603.21754 Fig.7）；β 非单调（2505.17281）。
  - 插图后置信度上升不等于正确率上升（2603.21754 Fig.6 negative_results）。
  - 论文公式（raw logit gap）与公开代码（softmax prob gap）不同，二者不能用同一 τ 互换（2603.21754 rs.key_step、invariance）。
  - V-ABS 在 GPT-4o 上多项大幅下降；熵阈值 δ=1.84 超出四候选自然对数熵上限 ln4≈1.386，与 Eq7/9 不相容（litscan:77776 Table1、degenerate_cases）。
  - β-GRPO 门控丢掉"正确但低置信"的轨迹；min 随 token/搜索增多只降不升，带长度与罕见词偏置（2505.17281 invariance）。
  - MMBoundary：更诚实但不更准（litscan:3289 lesson）；CLIP 项方向与不确定性总分方向冲突（litscan:3289 invariance）。

## 审稿期望
- 先测置信度与信息收益的关系；把触发与重排分开消融（2406.19215 lesson）。
- 与"相同触发率的随机门控"对照（推断，自 2603.21754 failure_boundary："没有 budget-matched 随机门控/固定插入次数对照"）。
- 把必要性、正确性、校准三个问题分开（2505.17281 lesson）。
- 相同 worker/beam 预算下比较，避免把更多计算当算法收益（litscan:77776 lesson）。

## 认知障碍
"不确定就再看"是自然直觉，但最相关的检索不一定最有用（2406.19215 why_non_obvious）；置信门控与输出正确性相关，却混入了词罕见度、长度与决策必要性（2505.17281 why_non_obvious）；先验自信会错，观察反馈也会有噪声（litscan:77776 why_non_obvious）。

## 工程经验
- 当用置信度门控视觉补看时，应固定置信度定义（raw logit 还是 softmax）、触发边界（按句号 token 还是按位置）、预算与视觉信息来源，论文公式与代码不一致时以代码为准并单独报告（2603.21754 lesson）。
- 当熵阈值作为超参时，先核其取值范围是否与候选数一致（litscan:77776 lesson、pitfalls）。

