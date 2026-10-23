---
id: PC-F4-11
name: 让冻结的纯文本读者只读 caption 或感知文本作答，判断其充分性，并据此路由失败轨迹的信用或筛选数据
family: F4_perception
status: candidate_pattern
problems: {P40: 3, P42: 2, P41: 2, P66: 1}
members: [litscan:78739, 2510.25092, litscan:76396]
rs_patterns: [heterogeneous_decomposition, self_supervised_signal_engineering, decompose_and_delegate]
---
## 操作

把视觉感知外显成文本，交给一个**不看图**的冻结读者回答原题；读者能否答对，就是该文本的"充分性" $R_P$。三位成员的用法：

**1. MoCA：失败轨迹的 token 路由**（litscan:78739 §2.5 p5 / AppA）

- 奖励与优势：$R=R_O+.3R_P$，优势为 mean-only：$A=R-\bar R$。
- 只改**失败**轨迹（$R_O=0$）上 recognition 段 token 的优势：
  - $R_P=1$ 时，$A'=A+.2|A|$；
  - $R_P=0$ 时，$A'=A-.2|A|$。
- 成功轨迹，以及 think/answer token，都不变。

**2. SeeingEye：推理期的信息流架构**（2510.25092 §3）

- 3B 翻译者看图，维护 SIR；8B 文本推理者只读 SIR。
- 推理者信息不足时向翻译者请求补充。

**3. SeeThink：数据筛选**（litscan:76396 Eqs3–6）

- 保留"基模看图答错、但只看 caption 答对"的 QA，作为感知训练集。

## 信息

- **读者**：
  - MoCA 用冻结 14B 文本模型，读全部 recognition 文本（litscan:78739 information）；
  - SeeingEye 用预训练 8B LLM（2510.25092 information）；
  - SeeThink 用基模读 DOCCI 细 caption（litscan:76396 information）。
- 读者看不到图，也与策略不共享参数。它判断的是**文本的属性**，不是"裁图是否必要"。
- 看不到：
  - 文本事实本身是否真实；
  - 读者是否靠先验或泄题猜中。

## 成立条件

- **感知必须外显为可分段的文本块。** MoCA 是单轮交错的 recognition 块，没有工具观测或动作 mask（litscan:78739 failure_boundary）。
- **读者要足够可靠，并与人工判断对齐。**
  - 读者对人工判断：accuracy 86.31%，κ=.707（litscan:78739 Table3）；
  - FN 90/979 = 9.19%，条件 FNR ≈ 14.06%（同上）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:78739 | 盲读者 $R_P$ 路由失败轨迹 recognition token | Table2 p8；Table3 | V* 86.6，加性 $R_O+\lambda R_P$ 为 83.1，仅 $R_O$ 为 79.7；MMMU 54.8 < 仅 RO 55.3，MathVista 73.8 < 74.4 | SVV 5 runs T.7；RL 种子数未覆盖 | 正（感知型任务），非全面非劣 |
| 2510.25092 | 文本推理者只读 SIR（推理期） | Table1 p7；Table5 p10 | MMMU val 60.78 vs Qwen2.5-VL-32B 51.56；MIA-Bench 84.10 < 89.60；Table5 与 Table1 数值冲突 | 记录未覆盖 | 接口可借，非训练信号 |
| litscan:76396 | 筛"caption 能答、看图答错"的题，作感知阶段数据 | Table2；Tables2–3 | Qwen2.5 视觉数学 40.74→42.26，感知 75.95→77.24；顺序为文本→感知→视觉时 42.91 > 感知优先 42.26 | Table11 为 3 次评测 run，非训练种子 | 弱正，顺序不唯一 |

## 成功条件 / 失败模式

**成功条件**
- 失败确实可以分成"看错"与"想错"两类；
- 读者的假阴性率低。

**失败模式**
- **读者假阴性会误罚正确感知。** $R_P=0$ 的假阴性会给正确的感知加罚，这与文中"保护噪声"的解释矛盾（litscan:78739 degenerate_cases）。
- **"保护"可能变成放大。** 当 $R_O=0,R_P=1$ 时 $R=.3$；若组均值 <.3，则 A 为正，保护变成放大（1.2A）（同上）。
- **充分性 ≠ 事实真实。** 人类标注者也是看着 gold 判充分性，不是对原图做事实审计（litscan:78739 failure_boundary）。
- **文本中介会丢细节。** 跨区域关系，或回执里没保留的细节，可能丢失（2510.25092 failure_boundary，读者推断）。
- **两个来源的问题。** 对 SeeThink 而言，caption 可能已含答案信息，且文本路径与视觉路径不同（litscan:76396 failure_boundary）。

## 审稿期望

推断：
- 去答案、选项置换的负对照；
- 读者与人工的 κ；
- 打乱 $R_P$ 的占位臂；
- 多种子。

## 认知障碍

失败原因可能是"看错"或"想错"，结果奖励却把两者混在一起。把感知外显成文本、再用盲读者测文本是否可解，这是把隐式故障源变成可测试中间物（litscan:78739 abstract_strategy）。前人要么只加感知奖励（加性，83.1），要么不区分失败原因（79.7）。

## 工程经验

- **用盲读者路由失败信用时**：先检查混合 A 的符号与代理假阴性，并区分文本充分性、视觉事实、工具必要性三者（litscan:78739 lesson）。
- **recognition 跨度与 tag 异常的 fallback**：必须实现时核对（litscan:78739 pitfalls）。
- **文本推理者缺特定视觉事实时**：先用等预算的反馈负对照与事实核查验证收益，不能把更高信心当作必要裁图的标签（2510.25092 lesson）。

