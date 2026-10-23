---
id: PC-F4-17
name: 用注意力质量作为"视觉依赖"的代理，用于训练奖励或推理期重新分配注意力（相关性信号，不是因果干预）
family: F4_perception
status: candidate_pattern
problems: {P42: 2, P43: 1, P41: 1}
members: [2605.18641, litscan:3023, litscan:14818, litscan:77491, litscan:79182, litscan:79575, litscan:77320, litscan:78773, litscan:73853]
rs_patterns: [architectural_operator_substitution, heterogeneous_decomposition]
---
## 操作

从注意力矩阵读出"文本对视觉 token 的关注程度"，再按两种方式使用。

**用法一：作为训练奖励**

- 2605.18641（Eq1–2）：
  - 先算 $R_A=\frac1{|T_t|}\sum_{j\in T_t}\sum_{k\in T_L}A_{jk}$，即后续文本对 latent 的平均注意力；
  - 再合成总奖励 $r=.9R_{acc}+.1R_{fmt}+1.0R_A$，然后按组 mean/std 标准化。
- litscan:3023（Eq9–10）：
  - 把注意力奖励 $r^{att}$ 除以组内最大值后，与 IoU 分、LLM relevance 相加。

**用法二：在推理期改写注意力**

| 方法 | 做法 | 出处 |
|---|---|---|
| ICoT | 按注意力 TopK 选出视觉 token 并插入 | litscan:14818 Eq5–6 |
| ILVAD | 用层间差分 saliency 放大视觉注意力 | litscan:77491 Eq4–10 |
| — | 用 head 一致性和历史 token 修正视觉 logits | litscan:79182 Eq6–12 |
| VRGA | 按 EFR 选 head，减掉背景后放大视觉注意力 | litscan:79575 §4 |
| MADRAG | 把未被检索污染的问题副本的视觉注意力混入 | litscan:77320 Eq2–3 |
| — | 对高风险 head 的 logits 减去大常数 | litscan:78773 Eq2–5 |
| VisualSwap | 把图像注意力整体 ×2 | litscan:73853 Table9 |

## 信息

- 读取的是模型自身的注意力：
  - 训练时取旧策略第一层（2605.18641 App D）；
  - 推理时取当前层与 head。

## 成立条件

- 能访问 eager attention（litscan:14818 pitfalls）。
- 奖励公式不能在代数上退化。litscan:3023 的 Eq9 按字面化简后，等于异常 token 数（读者推导，已核对 PDF p4 的分母）。
- 要控制长度：注意力奖励偏好更短的后续文本（2605.18641 §5.4 p10）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:3023 | IoU + 注意力奖（字面上退化） | Tables2,6；Eq9 | MAU .75，SFT .67；去掉 VRR 为 .71 | 记录未覆盖 | 注意力项可能是常量 |
| litscan:14818 | 注意力 TopK 插入视觉 token | Table2 | M3CoT 32.3，去 ADS 为 29.2 | 记录未覆盖 | 只复用已编码的信息 |
| litscan:77491 | 层间新激活 saliency | Table4；Table3 | CHAIRs 48.6→32.6；自然度 7.017→6.867 | 记录未覆盖 | 可能只是说得更少 |
| litscan:79182 | head 一致性 + 历史项 | Table1 | 五个模型平均 CHAIR CS 46.9→17.5 | 记录未覆盖 | gap 诊断 ROC 只有 .62/.65 |
| litscan:79575 | EFR 选 head 并放大 | Table3 | Qwen2.5 HaloQuest 66.67→73.96；Qwen3 69.20→68.05 | 记录未覆盖 | 混合 |
| litscan:77320 | 双问题注意力混合 | Table4 | LLaVA7B OKVQA 65.46→70.22；只重复问题已到 69.65 | 记录未覆盖 | 收益主要来自重复问题本身 |
| litscan:78773 | 高风险 head 的 logits 减常数 | Table2–3；Eq5 | CHAIR instance 17.18→12.90 | 10 runs + t-test | 机制解释存疑（softmax 平移不变） |
| litscan:73853 | 图像注意力 ×2 | Table9 | 8B Thinking 36.6→54.8，仍低于 multi-turn 67.5 | 记录未覆盖 | 只部分恢复 |

## 成功条件 / 失败模式

**成功条件**：有长度匹配对照、随机方向或随机 head 对照，并同时报告覆盖率。

**失败模式**

- **代数退化**：litscan:3023 的 Eq9 在异常 patch 非空时，内部和恒为 1，注意力奖励变成异常词数（degenerate_cases）。
- **平移不变**：softmax 对整行减去常数是精确不变的，效果只能来自未说明的 dtype 量化（litscan:78773 invariance）。
- **长度偏好**：RA 偏好更短的后续文本（2605.18641 pitfalls）；ILVAD 可能通过缩短 caption 来降低 CHAIR（litscan:77491 failure_boundary）。
- **注意力高 ≠ 证据**：高注意力也可能是 attention sink（litscan:77491 why_non_obvious）；被选错的区域会强化幻觉（litscan:79575 degenerate_cases）。

## 审稿期望

推断：

- 注意力质量匹配的移除对照（litscan:79575 lesson）；
- 随机 head 与随机方向对照；
- 长度与覆盖率；
- 与像素级反事实（PC-F4-08）之间的一致性。

## 认知障碍

注意力便宜、无需额外前向，看起来像"在看哪里"的直接读数。但注意力是相关，不是因果。2605.18641 的作者自己也承认 RA 不是因果效用（failure_boundary）。前人很少用反事实去校准注意力代理。

## 工程经验

- **当奖励被描述为 attention mass 时**：必须先看 softmax 的分母覆盖的是全集还是目标集合（litscan:3023 lesson）。
- **当干预依赖有限精度而不是显式 mask 时**：先核对平移不变性、dtype 和同温度对照（litscan:78773 lesson）。
- **当新增文字导致视觉回答退化时**：先用"重复问题"对照拆出 prompt 本身的收益（litscan:77320 lesson）。
- **降 caption 幻觉时**：同时报告长度、覆盖率和自然度（litscan:77491 lesson）。

