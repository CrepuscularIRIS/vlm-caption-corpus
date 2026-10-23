---
id: PC-F4-09
name: 用冻结评估器比较 caption 在"裁图区域 vs 其补集"下的似然比，作为感知流奖励
family: F4_perception
status: case
problems: {P43: 2, P42: 2, P44: 1, P25: 1}
members: [litscan:77968]
rs_patterns: [reframe_as_solvable_object]
---
## 操作

PFlowNet 把"框选 + caption"的感知流当作潜变量。冻结的 $p_\phi$ 给每段 caption 打分，算法为 Sub-Trajectory Balance（litscan:77968 Eq2–5 p4–5）。

1. **区域特异性 × 答案似然**：比较 caption 在裁图区域与其补集下的似然比，再乘以答案似然：

$$R(z_{0:k}\top)=\Big[\prod_{i=1}^k\frac{p_\phi(c_i|I_{r_i})}{p_\phi(c_i|I\setminus I_{r_i})}\Big]\,p_\phi(Y|z_{0:k}\top,X)$$

2. **软邻域罚**：只有框偏离专家 RoI 邻域时才扣分：

$$R_\lambda=R\exp[-\lambda\mathbb1(d_{IoU}>\epsilon)]$$

## 信息

- **评估者**：冻结的 $p_\phi$，看裁图或其补集，评价 caption；再看 X 与前缀，评价目标 Y。
- **训练时可见**：QA，以及原专家 RoI（litscan:77968 information）。
- **不是什么**：不是当前策略，也不是二分支的正确率增益（litscan:77968 conditions）。

## 成立条件

- 已有 45k 条 SFT，教会规划与框/caption 格式（litscan:77968 signature）。
- 负图（补集）必须显式裁出。用原图 token 遮罩无法模拟 Qwen 原生分辨率的重缩放（litscan:77968 App B.4 pitfalls）。
- ε 与 λ 需要调：ε=.7 过宽或 λ 过小时不稳定，λ 过大则限制探索（litscan:77968 Fig8 / §4.3）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:77968 | 冻结似然比 + 答案似然 + 邻域罚；SubTB | Table3 p7 | SFT→联合 RFT：TreeBench acc 48.3→55.3，**mIoU 44.2→38.2**；V* 83.7→90.6；MME-RW 54.2→67.0 | 记录未覆盖 | 准确率升、几何指标降 |

## 成功条件 / 失败模式

- **成功条件**：caption 要描述"这块区域特有、补集中没有"的内容，答案依赖这些内容。
- **失败模式**：
  - **冻结似然可能被利用**：IoU 下降，不保证每段 caption 都忠实；理论不保证有限训练能提高准确率（litscan:77968 failure_boundary）。
  - **λ=0 时**：几何约束被移除（litscan:77968 degenerate_cases）。
  - **答案概率普遍低时**：caption 比率仍有梯度，但这不证明题目可解（同上）。

## 审稿期望

以下为推断：

- 冻结评估器与人工 caption 事实判定的一致率；
- 当前策略作评估器时的对照；
- 似然比 hack 的监测：评估器有偏时，策略可能写出"补集里一定没有"的套话。

## 认知障碍

专家框的 IoU 最优，不等于推理所需信息最优（litscan:77968 why_non_obvious）。PFlowNet 用 caption 的区域特异性代替框几何，但交给冻结评估器来判，没有处理冻结评估器 ≠ 策略的问题。

## 工程经验

- **奖励依赖裁图后的分辨率时**：原图特征遮罩不等价于真实裁图。应保留 crop 重编码，并单独核算开销（litscan:77968 lesson / App B.4）。

