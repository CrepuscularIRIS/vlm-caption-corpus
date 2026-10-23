---
id: PC-F5-09
name: 把训练种子、配置选择、评测采样、评测 harness 四个方差源分开随机化和报告
family: F5_stop_eval
status: candidate_pattern
problems: {P45: 3, P69: 2, P46: 1, P54: 1}
members: [2507.04103, 2606.00135, 2610.12601]
rs_patterns: [controlled_diagnostic_design]
---
## 操作
比较方法前，先把结果的波动拆成来源并各自控制：
- 训练/优化器种子：独立重跑（2610.12601：3 个独立 optimizer seed）。
- 配置选择：在已有 run 上做逆组大小加权 bootstrap（权重 ∝ 1/count(HP 值)，B=1000），报告"最佳配置胜率"和条件最大值分布（2507.04103 Algorithm1）。
- 评测 harness：同一模型换 system prompt / history 序列化 / 模板，测评测本身的敏感性（2606.00135 Table4）。
- 评测采样：固定候选在题目上配对 bootstrap（2610.12601 §4.2）。
并把总预算写清：$F_{total}=F_{SFT}+F_{RL}$，含教师被拒轨迹与 rollout 成本（2507.04103 Eq5）。

## 信息
已有的独立 run、每题得分、harness 配置；无模型内部量。

## 成立条件
- 有 ≥2 个真正独立的训练运行；bootstrap 只在已观察到的 run 上重采样，不能填补没跑过的配置或种子（2507.04103 failure_boundary、invariance）。
- 评测 seed 与训练 seed 分开记录（2606.00135 conditions："评测seed不等独立训练seed"）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2507.04103 Web Agent 统计诊断 | 1370 个随机配置 run 的逆组大小 bootstrap；SFT checkpoint 分叉 RL 的总算力账 | HTML §5；Algorithm1；Eq5 | MiniWob 纯 SFT 峰值约 11 exaFLOPs，SFT+RL 约 6 exaFLOPs（省约 45%）；固定配置不能跨 SFT 阶段通用；WorkArena 14/33 任务完全失败 | 正文称报告四个所选 run，另有 top2/10 seeds、Table1 两个 top seed 的 SE；口径不一 | 记录未覆盖 |
| 2606.00135 工具调用 RL 效能与效率 | 固定 harness 对照：默认 prompt / 强 prompt / 强 prompt + RL | Table4 p8；Table2；§4.3 | multi-turn 22.7±.9 → 37.2±1.4（仅换强 prompt）→ 39.4±.7（RL）；同 .7k 数据 multi 训练使 BFCL 22.7→15.9；训练 wall-clock 加速 1.7×/2.6× | 3 个评测 seed（非训练 seed） | 记录未覆盖 |
| 2610.12601 反思式 prompt 优化协议 | topic-disjoint + 3 个独立 optimizer seed + 配对题 bootstrap | Abstract；§4.2 | held-out .702→.781，Δ.079，CI[.051,.107]；3 seed 平均 +.107 | 3 optimizer seeds | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：至少 2 个独立训练种子；harness 固定并单独报告其敏感性。
- 失败模式：
  - 把 bootstrap 当成新独立训练种子（2507.04103 rs.why_non_obvious；同一警告见 2610.05400 pitfalls "不能把bootstrap固定policy不确定性当训练seed方差"，F1 digest）。
  - 把重复评测当训练种子：AdaTurn 的 Avg@32 是 32 次重复评测，不是独立训练（2607.14547 seeds）。
  - harness 改动的效应可大于算法：只换 prompt 就 +14.5 点，RL 再加 2.2 点（2606.00135 Table4）。
  - 共享可写环境的持久状态污染后续 run，"成功"可能来自改了评测环境（2507.04103 pitfalls、degenerate_cases）。
  - 单种子 + 报告峰值测试分数不构成稳定收益（2606.05597 negative_results，AsyncWebRL）。

## 审稿期望
- 多种子与区间，并说明区间覆盖哪个方差源（2610.12601 relevance P45："taskbootstrap非training方差替代"）。
- 报告训练 token、更新次数、rollout 开销（M14；2507.04103 lesson：纳入教师失败生成与配置搜索成本）。
- 固定并公开评测 harness（2606.00135 lesson 字段为空；推断自 Table4 的 prompt 效应）。

## 认知障碍
统计单位是"已有配置的 run"，不是新独立训练种子；bootstrap 也不能覆盖没搜过的超参区域（2507.04103 why_non_obvious）。工具轨迹拆成单轮训练让 update 比 rollout 更贵，"减少无梯度 rollout"与"减少更新样本"是两个不同瓶颈（2606.00135 why_non_obvious）。

## 工程经验
- 当比较 SFT 与 RL 时，要把教师失败生成和配置搜索成本计入总算力（2507.04103 lesson）。
- 当环境/评测资源可被 agent 写入时，要按 run 隔离环境状态，用真实独立 seed 验证少数候选（2507.04103 lesson、pitfalls）。
- 当多轮评测结果受模板/history 序列化影响时，先固定 harness 再比较算法（2606.00135 relevance P54）。
- 当训练大多是全对组时，先 profiling 再决定削减 rollout 还是 backprop（2606.00135 relevance P58）。

