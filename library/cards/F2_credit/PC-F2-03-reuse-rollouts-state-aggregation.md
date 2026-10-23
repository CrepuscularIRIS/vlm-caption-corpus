---
id: PC-F2-03
name: 不新增续写，按共享前缀或同观测状态聚合已有 rollout 的回报来估值并给分叉/步级信用
family: F2_credit
status: candidate_pattern
problems: {P11: 2, P09: 2, P23: 2, P58: 1}
members: [2509.18314, 2605.13217, 2609.35084, litscan:29933, litscan:29889]
rs_patterns: [unify_into_shared_representation, reframe_as_solvable_object, self_supervised_signal_engineering]
---

## 操作

把同一题的 G 条已采轨迹按"相同前缀 / 相同观测状态"合并成树或图，以节点下游回报的平均作 V，然后：
- 只在分叉 token 处叠加 $V(\text{next})-V(\text{current})$，其他 token 保留 GRPO 结果项（2509.18314 TEMPO）；
- 或把同观测状态的折扣回报均值当非参数 V，算 TD 残差与 GAE，再组内 z-score（2605.13217 GAGPO）；
- 或在经验图上做期望 backup $\hat\Phi(s)=\bar\gamma\sum_a\hat q(a|s)\hat\Phi(\text{next})$，取 log 势差，同状态内 std 后**加回** $A_T$（2609.35084 Eq9, Eqs11–13）。

## 信息

- 看得到：同一题已采样的完整轨迹及终奖；精确前缀计数（litscan:29933 TVM）或按句子编辑距离合并的近似前缀（litscan:29889 OpenPRM）。
- 看不到：没被采到的替代动作；被别名合并的隐藏状态差异。
- 估计者：当前（旧）策略的经验统计，无额外续写，无 critic。

## 成立条件

- 状态等价要成立。在 POMDP 中，精确文本观测匹配不保证潜在状态相同（2605.13217 failure_boundary）；状态合并会混入历史与 horizon 别名（2609.35084 pitfalls §4.2）。
- 独立 rollout 在很早就分叉，之后语义上同态的状态不会被自动合并（2509.18314 failure_boundary）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2509.18314 | 前缀树后代均值，只在分叉 token 加 TD 修正，保留全序列结果项 | Table1 | Qwen3-4B MATH 91.0 vs GRPO 87.6；MedQA 79.18 vs 76.12 | 记录未覆盖 | 成员 |
| 2605.13217 | 同观测状态回报均值作 V，GAE（γ.95 λ.8），组 z-score | Table2 p7 | 1.5B ALFWorld 93.5±1.3，λ0 为 85.8±2.2；WebShop success 78.1±1.1 vs 64.9±3.8 | 3 seeds | 成员 |
| 2609.35084 | 经验图期望 backup，log 势差，同状态 std 后加回 AT | Table2 p9 | Sokoban 84.0±1.2 vs GRPO 71.1±3.9、GraphGPO 81.6±4.03 | 3 RL seeds | 成员 |
| litscan:29933 | 精确前缀计数作 token value 标签，用于 beam 而非 RL | Table2 | GSM8K step-beam TVM Mistral7B 87.69±.22 等 | 记录未覆盖 | 成员（用途不同：搜索评分） |
| litscan:29889 | 句子编辑距离合并成前缀树，后代 leaf 均值作弱过程标签 | Table2 | InternRM RewardBench 91.1、PRM800k 68.1，原模型 87.6/61.0 | 记录未覆盖 | 成员（合并非同 actor 同状态） |

## 成功条件 / 失败模式

- 成功：环境离散、状态重访多（ALFWorld、Sokoban 一类）。
- 失败：
  - 单例状态或等后继值时 $A_s=0$；没有成功图时两项都为 0（2609.35084 degenerate_cases）。
  - γ=.55/.75 时，距离 8/17 之后必触 eps=.01，抹平长路径差异（2609.35084 pitfalls AppD.2）。
  - 1.5B WebShop success 81.3 与 GraphGPO 持平；step-only 92.5 低于 95.7（2609.35084 Tables1,4）。
  - 非共享后缀的支持数为 1 时，退化为终答标签（litscan:29933 failure_boundary）。
  - 采样 V 含自身样本，不是独立无偏基线（2605.13217 failure_boundary）。

## 审稿期望

GraphHCA 有 reviewer_concern=low_evidence。"推断"：
- 报告单例状态、floor 触发的比例；
- 给出状态合并规则的消融（精确 vs 近似）。

## 认知障碍

- 复用已采样本的结构信息，就能在保留全局监督的同时，只修正可比较的决策位置（2509.18314 abstract_strategy）。
- 最短路只看最好的续写，期望 backup 才能分辨同距离后继的可靠性（2609.35084 why_non_obvious）。

## 工程经验

- 当用共享图估值时，应先验证状态等价，并报告 floor 与单例的比例；不能把数学上收敛当作估计正确（2609.35084 lesson）。
- 当 γ 很小时，长路径会触 eps 下限，应先算最大可分辨距离（2609.35084 AppD.2）。

