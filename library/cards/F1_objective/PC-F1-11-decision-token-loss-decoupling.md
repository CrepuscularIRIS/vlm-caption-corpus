---
id: PC-F1-11
name: 把稀疏的决策 token 从执行 token 的长度归一中分离出来，单独加权或单独屏蔽
family: F1_objective
status: candidate_pattern
problems: {P08: 3, P21: 2, P24: 2, P23: 2}
members: [2505.13379, 2505.11896, 2605.15198, 2605.20342]
rs_patterns: [heterogeneous_decomposition]
---
## 操作
决策位置有三种处理方式。

**单独加权**
- Thinkless 的 DeGRPO：控制 token 的损失用固定系数 α，与回答 token 的 $1/T_i$ 平均分开，同一组平均。
- 形式为 $\alpha L_{i,0}+\frac{1}{T_i}\sum_t L_{i,t}$，α=.001（2505.13379 Sec3.2 p5 Eq4）。

**单独屏蔽**
- AdaCoT 的 SLM：在 Math RL 阶段，把 `<think>` 之后那一个决策 token 的直接损失 mask 掉，其余 PPO 照常。
- 形式为 $L_{SLM}=\sum_{k\ne k_{decision}}\ell_k$（2505.11896 Eq5）。

**单独加一项辅助**
- ATLAS 的 LA-GRPO：对功能 token 用同一个 rollout 优势算 clipped surrogate，除以功能 token 数，再以 α 加到原 GRPO 上（2605.15198 p.7 §2.3）。

**反例**
- ParaVT H.3：把结构 token 的 PG 置零，只更新语义 token（2605.20342 AppH.3）。

## 信息
- 生成序列中决策 token 的位置，以及整条轨迹的同一个优势。
- 没有新的价值信号，只改变已有信号在 token 间的分配。
- 由谁估计：沿用结果优势。

## 成立条件
- 决策 token 与执行 token 的数量悬殊：ATLAS 中功能 token 只占 2.3%，平均 4.8/203.7（2605.15198 pitfalls）。
- 共用长度分母会稀释决策梯度，并让长、短模式的决策梯度尺度不同（2505.13379 why_non_obvious）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2505.13379 | 控制 token 单独加权，mean-only | Sec3.2 Eq4；Fig3；Table1 p6 | vanilla 约 120 步内长样本 <10，全变 short；DeGRPO 保住两种模式；MATH .8608→.8184（−4.24pp） | 未报告；无 CI | 支持保模式；准确率有降 |
| 2505.11896 | Math RL 阶段 mask 决策 token 损失 | Eq5；Table1 p7 | 1000 道平衡日常题：无 SLM 时触发分类 acc .506、recall 1；有 SLM 时 acc .813、recall .670、precision .938 | 未报告 | 支持：防止专项 RL 把路由推成 always-CoT |
| 2605.15198 | 功能 token 同优势辅助项，按位置数归一 | §2.3；Table3 | 相对 GRPO：WeMath 40.3→45.0，M-view 43.6→53.4；V* 77.9→75.4，Jigsaw 57.7→51.3，Spatial 70.6→62.9 | 未报告 | 混合 |
| 2605.20342 | 结构 token 的 PG 置零（失败对照） | AppH.3 p22 | 11 步后 fτ 从基线 .13 降到 .11 | 未报告 | 反例：剥掉结构 token 信号会破坏格式 |

## 成功条件 / 失败模式
**成功条件**
- 决策位置定义清楚，且与采样事件对齐（P23）。
- α 与回答学习速度匹配（2505.13379 conditions）。

**失败模式**
- α 过大会过早按初始能力定死分工，short 模式没机会继续学（2505.13379 Sec4.3 negative）。
- mask 不等于冻结参数。后续 token 仍通过共享参数影响决策 logit（2505.11896 failure_boundary；与 P24 一致）。
- 只增强结果信用，可能也增强冗余操作（2605.15198 failure_boundary）。
- 去掉 spam 惩罚后，出现每序列 18.7 个功能 token 的奖励投机（2605.15198 §3.5）。
- 把结构 token 的 PG 全部置零会让格式崩溃（2605.20342 AppH.3 pitfalls："Structural token PG zeroing is not format protection"）。

## 审稿期望
- 推断的要求：
  - 先离线计算现有 loss 下决策 token 的实际梯度份额，再动手；
  - "同调用率常数偏置"对照（P24）；
  - α 扫描。

## 认知障碍
- 一个决策 token 与数千个回答 token 共享长度分母，不仅削弱决策，还让长、短模式的决策梯度尺度不同；单加短回答奖励修不了这种尺度差（2505.13379 why_non_obvious）。
- 专项 RL 会把之前学到的混合路由推成 always-CoT（2505.11896 why_non_obvious）。

## 工程经验
- 当单个决策 token 与长度差异很大的回答共用分母时，先算每种模式的实际决策梯度尺度，再调 α；同时检查两种模式的支撑（2505.13379 lesson）。
- 当专项 RL 破坏路由时，先做单决策 token 的 loss 消融，并区分"直接梯度屏蔽"与"参数冻结"（2505.11896 lesson）。
- 当操作 token 只占少量输出时，应核对稀疏位置的相对权重和使用奖励带来的投机（2605.15198 lesson）。

