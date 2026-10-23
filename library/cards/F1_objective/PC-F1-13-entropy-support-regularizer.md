---
id: PC-F1-13
name: 用熵反馈正则或局部支撑约束抑制探索塌缩（不改奖励、不强制动作）
family: F1_objective
status: candidate_pattern
problems: {P29: 3, P32: 2, P62: 1}
members: ["litscan:74479", 2505.22617, "litscan:77605"]
rs_patterns: [characterize_limit_then_surpass, targeted_self_supervised_objective, structural_prior_encoding]
---
## 操作
三种做法：

**DivFreq：熵反馈正则**（litscan:74479 Eq7–9）
- 目标：$J=J_{DAPO}+\lambda_t\,\bar H$，其中 $\bar H$ 是 rollout 生成 token 的平均熵。
- 系数：$\lambda_t=.03\max(.9-H_{batch},0)$，熵低于 0.9 时才开启。
- 也可以只在前 60 步开启。

**Clip-Cov / KL-Cov：限制少数高协方差 token**（2505.22617 Eqs10–14）
- 对 batch 所有 token 计算协方差分数 $c_i=(\log p_i-\overline{\log p})(A_i-\bar A)$。
- Clip-Cov：在高分区间随机 detach 一小部分 token 的梯度。
- KL-Cov：只对最高分 token 加 old-policy 约束。
- 两者都只干预约 .02%–.2% 的 token。

**APO：负优势时的支撑锚**（litscan:77605 Eq6–10/23）
- 仅当 $A_t<0$ 时，把 ratio 改为 $\tilde r=\lambda r-\beta r_{anchor}$。
- $r_{anchor}$ 是参考模型 Top-K 中除当前 token 外其余候选在当前策略下的总质量，除以它们在参考模型下的总质量。

## 信息
- 当前策略的 token 分布与熵；APO 还需要冻结参考模型的 Top-K。
- 看不到：动作是否必要，以及熵对应的是决策 token 还是普通语言 token。
- 由谁估计：策略自身的 logits。

## 成立条件
**粒度要对齐**
- 平均 token 熵高，不代表首动作没有塌缩。
- 2505.22617 degenerate_cases："平均 token 熵可维持但首动作仍塌"。

**正则在 loss 层，不经过 reward std**

**已近 0 的动作救不回**

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:74479 | 熵反馈正则，不奖励工具 | Eq7–9；Table2 p8；AppB3 | 3DSR 62.9，vanilla 59.2，工具 bonus 59.9；末期工具使用约 3%，对照为 2% 与 100%；只开前 60 步为 62.5；禁工具 + 熵为 57.8 | 未报告；62.9 是最佳验证点 | 支持 |
| 2505.22617 | Clip-Cov / KL-Cov | Eqs10–14；Table2 p12；Figs9–10 | 7B 平均 38.6→40.6，32B 45.8→52.2；熵损失系数 .01 时熵爆炸，.005 稳定但无提升；32B Clip-Cov 在 AMC 上 67.2 < GRPO 69.7 | 未报告 | 支持（数学单轮） |
| litscan:77605 | 负优势支撑锚，K=8，β=.1 | Eq6–10；Table2；Table5 | Qwen2.5-Math-7B Pass@1/Pass@K 50.67/78.07，GRPO 48.68/76.56；β=0 时 Pass@1 48.86 | 未报告 | 支持 |

## 成功条件 / 失败模式
**成功条件**
- 塌缩尚未完成，此时干预最有效：只开前 60 步的效果接近全程（litscan:74479）。
- 熵项系数小，且有自适应开关。

**失败模式**
- 全局熵损失易爆炸或无效：系数 .01 时爆炸（2505.22617 Figs9–10）。
- 熵上升伴随回答变长（2505.22617 Fig11）。
- 熵可以混入语言或重复内容；固定系数很敏感（litscan:74479 pitfalls）。
- 最佳分数和末期工具使用率不在同一个时间点，不能当作同一个 Pareto 点报告（litscan:74479 pitfalls）。
- 参考 Top-K 集合里可能本身就是错误候选。$A=0$ 时没有恢复作用；$\lambda=1.1$ 比默认值差（litscan:77605 failure_boundary/Table5）。
- 训练步数超过 100 后不稳定，动态采样代价高（litscan:74479 relevance P32）。

## 审稿期望
- 推断的要求：
  - 熵必须在首动作这一粒度上报告；
  - 与工具 bonus、强制采样做对照：litscan:74479 已与 bonus 对照，未与强制采样对照。

## 认知障碍
- 工具使用率 100% 时，也可能只是在反复裁同一个区域。末期工具少，不代表训练期工具没用（litscan:74479 why_non_obvious）。
- 惩罚一个错误候选，会经 softmax 一并挤压其他低概率候选（litscan:77605 why_non_obvious）。

## 工程经验
- 当策略可以直答也可以看图时，先看分支支撑和区域多样性，再调工具频率；记录熵项覆盖哪些 token，以及额外的 token 成本（litscan:74479 lesson）。
- 熵指标先与动作粒度和实际优化器对齐。保存被 mask 的 token 及其梯度贡献，避免全局熵的改善掩盖工具模式的塌缩（2505.22617 lesson）。
- 记录 ratio 裁剪的对象、优势门控与 token 聚合方式。做小规模训练前，先用解析的二 token 反例核对所谓的 trust-region 保证（litscan:77605 lesson）。

