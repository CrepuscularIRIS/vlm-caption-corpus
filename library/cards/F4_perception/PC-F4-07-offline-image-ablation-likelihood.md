---
id: PC-F4-07
name: 用固定模型的"有图 vs 无图/模糊图/错配图"似然差挑选监督 token、构造偏好或对比损失（离线，caption 落地）
family: F4_perception
status: candidate_pattern
problems: {P42: 2, P36: 1, P41: 1}
members: [litscan:79376, litscan:79304, litscan:4174, litscan:79300, litscan:78992, litscan:75376]
rs_patterns: [targeted_self_supervised_objective, self_supervised_signal_engineering, heterogeneous_decomposition]
---
## 操作

用固定参考模型，或上一轮的策略，比较同一回答在两种图像条件下的似然：正常图条件，与无图、模糊、错配或编辑图条件。按差值做三类事。

**1. 选 token 做 SFT**（litscan:79376 Eqs3,6–9）

$$VIG_{it}=\log q(a_t|\cdot,I)-\log q(a_t|\cdot,\mathrm{blur}(I))$$

- 先按样本均值保留 top 70% 的样本；
- 再用同一阈值 τ 屏蔽低 VIG token 的 CE 项。

**2. 构造偏好对**
- IRIS（litscan:79304 Eqs8–10）：用 $S=r_I-\gamma\max(0,r_T-r_I)$ 排序当前候选，挑出 chosen/rejected。
- RLSF 类方法的对比见 README 中的未归卡说明。

**3. 写成对比损失或 DPO**
- S-VCO：匹配 > 无图 > 错配，并对称交换（litscan:4174 Eqs3–7）。
- SCPO：CCO + .2·CSO，按课程训练（litscan:79300 Eqs7–13）。
- IC-VCO：同 context 的编辑图 DPO（litscan:75376 Eq9–15）。
- TLVS：取 with/no-image logprob 差的极端 token 求 PCA 方向，在推理时做 steering（litscan:78992 Eq8–12）。

## 信息

- **估计者**：冻结或参考模型。分别是视觉对齐后的 checkpoint（litscan:79376）、$\pi_{r-1}/\pi_{r-2}$（litscan:79304）、DPO 的 reference（litscan:4174、litscan:79300），以及校准后加 steering 的原模型（litscan:78992）。
- **所需数据**：GT 答案、偏好对、编辑图对。
- **不涉及**：RL rollout 与 crop 动作。
- **看不到**：事实真假与动作价值。

## 成立条件

- 对照图像确实去掉或改变了所需信息：
  - 随机或裁剪扰动可能根本没删掉证据（litscan:79304 pitfalls）；
  - 编辑图若没有真实语义变化，会产生错标签（litscan:75376 degenerate_cases）。
- 阈值按模型校准：同一 p 下不同模型的 τ 不同（litscan:79376 TableD.1）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:79376 | 原图/模糊图 GT 似然差，选样本与 token | Table3；Table6；TableF.3 | LLaVA7B 活跃 token 58.61M→38.45M；MMVet 28.62→32.71；CHAIR CS 52.93→47.00。Table6 SS 的 LLaVAW 58.12 与 MMBench 57.56 低于 base 的 59.02/65.46；p30 时 MMBench 56.87 | 记录未覆盖 | 正，但有回退 |
| litscan:79304 | 有图/无图隐式奖励排序，挑选当前候选 | Table1；Table2 | LLaVA1.5-7B ObjectHal CS 54.7→8.66；AMBER HalRate 40.4→11.3；加 anchor 后 HalRate 10.4→11.3 | 记录未覆盖 | 正 |
| litscan:4174 | 匹配>无图>错配，对称 | Table1 | MMVP 41.3→50.7；MMHal 46%→35%；不对称版 46.0；SQA 74.77→73.87 | 记录未覆盖 | 正 |
| litscan:79300 | 文本+视觉偏好课程 | Table2；Table6 | ObjectHal CS 12→7；AMBER HalRate 49.7→27.1；MMBench-CN 60.6→59.4；逆课程反而更差 | 记录未覆盖 | 正，但有回退 |
| litscan:78992 | 极端视觉敏感 token 的 PCA 方向 steering | Table1；Table2 | AMBER Hal 36.4→19.7，F1 74.7→82.2；Qwen 覆盖率 51.6→51.2 | 记录未覆盖 | 正（推理期） |
| litscan:75376 | 同 context 编辑图 DPO，加门控蒸馏 | Table4 | Interleave 63.35；去 VCDist 63.04；去 anchor 61.15 | 记录未覆盖 | 正 |

## 成功条件 / 失败模式

**成功条件**：对照图像与回答绑定正确，并有 anchor 或预热，防止 chosen 的概率下降。

**失败模式**

- **视觉依赖高 ≠ 正确，低 ≠ 无用。**
  - 高 VIG 可能只反映标签或模型偏差（litscan:79376 failure_boundary）；
  - 视觉敏感性高不能证明事实为真（litscan:78992 failure_boundary）。
- **跨图条件的 DPO 配分项不会自动抵消**（litscan:75376 why_non_obvious；litscan:79300 invariance）。
- **少说话会降低幻觉指标。** 必须同时报告覆盖率（litscan:78992 lesson）。

## 审稿期望

推断：

- 同数据下的 DPO 或 SFT 对照；
- 覆盖率与自然度；
- 人工抽检偏好标签（litscan:79300 D.3：100 对中 96% 正确）；
- 多种子。

## 认知障碍

以前的偏好优化只比较同一张图下的两段文本，模型可以走语言捷径。把"图像条件"本身纳入对比（S-VCO、SCPO），才能约束 caption 依赖图像。但这些方法默认对照图像真的去掉了相关信息，而这一点很少被核验。

## 工程经验

- **用 token 筛选节省监督时**：保留完整上下文作为输入，只去掉低分 token 的 CE 项；单独统计打分与训练的总时间；保护工具格式、stop 与纠偏的支撑（litscan:79376 lesson）。
- **用隐式奖励自筛时**：打分用的 reference 与 DPO 用的 reference 要分别存版本，并审计 SFT 回填比例（litscan:79304 lesson）。

