---
id: PC-F1-19
name: 在策略自身隐藏状态上训练线性探针判断"要不要调工具"，再用外接阈值或前缀干预执行决策
family: F1_objective
status: candidate_pattern
problems: {P24: 2, P34: 2, P05: 2, P21: 1}
members: [2502.12961, 2605.09252, 2410.13339, 2605.14038]
rs_patterns: [decouple_representation_from_execution, disentangle_mixed_signals]
---
## 操作
先冻结 LLM，在指定位置的 hidden state 上训练一个轻量分类器，再用它覆盖或引导首决策。

**MeCo**（2502.12961 §3.1–3.2）
- 用强、弱元认知指令下成对表示差的 PCA 第一方向作为探针。
- 对首个 Yes/No token 按原决定分别设阈值，按以下规则翻转：

$$\hat d=\begin{cases}\mathrm{No}&d=\mathrm{Yes},\ \nu<l_{yes}\\\mathrm{Yes}&d=\mathrm{No},\ \nu>l_{no}\\d&\text{otherwise}\end{cases}$$

**探针 + prefill**（2605.09252 §4–5）
- 把末 token 各层 hidden state 拼接，训练 L2 logistic 探针：$p=\sigma(w^Th+b)$，$\hat d=\mathbf 1[p\ge\tau]$。
- 按 $\hat d$ 给输出 soft 句子前缀或 hard 格式前缀。

**Probing-RAG**（2410.13339 key_step）
- 用生成 token 的 hidden 均值训练 prober，决定继续检索还是停止。

**诊断用法**（2605.14038）
- 分别训练"必要性"探针和"实际调用"探针，比较 MCC 与两个方向的夹角。

## 信息
- 当前策略的内部表示。
- 训练标签：禁工具时的正确性（2605.09252）、10 次禁工具采样中任一出错（2605.14038）、或指令对比（2502.12961）。
- 看不到：工具能否把错误救回来。"禁工具会失败"不等于"用工具能成功"（2605.09252 failure_boundary；2605.14038 failure_boundary）。
- 由谁估计：冻结策略的表示加上外部分类器。

## 成立条件
- 能访问 hidden states（2502.12961 conditions）。
- 标签要区分"无工具失败"与"工具带来的增益"（2605.14038 relevance P34）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2502.12961 | PCA 探针 + 按动作条件校准阈值 | §3.1–3.2；Tables1,5,6 | MetaTool LM3-8B 经 SFT 后调用 277→240，决策准确率 82.1→84.3%；RAG LM3-8B 63→76%，PYes 75%；Task5 有 context 时 79.5，低于 PYes 的 80.5 | 未报告 | 弱支持 |
| 2605.09252 | 全层 logistic 探针 + soft/hard prefill | §4–5；Table4；§5.2 | 阈值 .5 下六模型平均准确率 −1.7 点，每任务调用 −.48；Qwen3-4B 探针 AUROC .948；Llama70B 的 soft 前缀基本被忽略 | Table8 有 3 runs | 混合：可读，但执行掉点 |
| 2410.13339 | prober 控制检索 | §4.2/Table1 | 五数据集平均 EM 22.8 / ACC 35.8，不检索为 19.0/29.2 | 未报告 | 支持 |
| 2605.14038 | 必要性与动作两个探针的诊断 | Table1 | 算术题错配 26.5–54.0%，TruthfulQA 30.8–41.8%；Qwen3-8B 算术题过用 38.2%、漏用 3.5% | 未报告 | 诊断：可读信号与动作方向近正交 |

## 成功条件 / 失败模式
**成功条件**
- 内部信号可读（2605.09252：AUROC .948）。
- 执行层服从前缀干预；soft 前缀可能被忽略，需要 hard 前缀（2605.09252 §5.2）。

**失败模式**
- 平均准确率下降 1.7 点，不是非劣（2605.09252 Table4）。
- 探针几乎完美区分的是强弱指令的方向，而不是最终的工具必要性（2502.12961 pitfalls）。
- 原决策若总是同一标签，另一侧阈值没有训练支撑（2502.12961 degenerate_cases）。
- 两个探针近正交，不能证明因果上信息断路（2605.14038 failure_boundary）。

## 审稿期望
- 记录为 low_evidence。
- 推断的要求：
  - 同调用率的随机路由对照；
  - 真实成对 crop 收益下的误拒率与误触发率（2502.12961 transfer_mapping）。

## 认知障碍
- 表示里能线性读出的信号，未必会转化为生成动作；prefill 是把探针信号变成实际动作的干预（2605.09252 why_non_obvious）。
- 必要性随模型而变。强 judge 的标签不能代表弱策略（2605.14038 why_non_obvious）。

## 工程经验
- 当探针显示信号可预测而工具行为仍错时，用轻量的输出干预检查执行层；同时保留真实收益与标签噪声的对照（2605.09252 lesson）。
- 当隐藏分数受原决策类别和层尺度影响时，要分别校准，并用下游任务结果验证（2502.12961 lesson）。

