---
id: PC-F4-13
name: 保持图像不变而注入冲突或错误文本（或保持题干而换图），测答案跟随哪一侧证据
family: F4_perception
status: candidate_pattern
problems: {P42: 3, P40: 2, P41: 2, P27: 1}
members: [litscan:73751, litscan:2420, litscan:74625, litscan:3814, litscan:3218]
rs_patterns: [controlled_diagnostic_design]
---
## 操作

构造受控输入，让图像证据与文本证据各自都能读出，但两者冲突。然后看模型的答案跟随哪一边。分两类做法：

**文本侧干预：保持图，注入错误文本**
- 注入错误 caption 或错误 think 前缀，比较 bbox 输出的 IoU 变化（litscan:73751 AppD.6 Table7）。
- 构造错误、正确、无关三种历史，比较答案翻转情况（litscan:2420 §2）。
- 构造局部图文事实冲突，并交换选项位置；指标为 $VisionRatio=S_v/(S_v+S_t)$（litscan:74625 §3）。

**图像侧干预：保持题干，换图或用反常识图**
- 题干固定、图像不同、正确答案随之改变；报告双正确率 BC 与同答案率 AG（litscan:3814 Table5）。
- 高共现背景配上低共现目标的反常识合成图（litscan:3218 Eq1–2）。

## 信息

- 用到受控构造的输入和 GT。
- 被测的是模型自身的输出。
- 除 73751 外，成员都不涉及训练奖励；73751 在 RL 前后各测一次。
- 测不到：
  - 内部 CoT 的因果忠实；
  - 裁图必要性（litscan:73751 failure_boundary）。

## 成立条件

- 两侧证据都可读。litscan:74625 先过滤掉"单模态读不懂"的样本和"答案不一致"的样本。
- 改图后正确答案确实改变（litscan:3814 conditions）。
- 对照里要有正确提示与错误提示的交叉，否则模型学会"总是忽略提示"也能得分（litscan:73751 pitfalls：correct/wrong 各占 10%）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:73751 | 错误 caption / 错误 think 注入 | AppD.6 Table7 | SpaceR baseline P@.5 .756；错误 caption ΔIoU −.268（相对 −39%），错误 think −.548（−80%） | 种子变化有时大于数据组合效应（§3.2） | 文本可大幅带偏 |
| litscan:2420 | 错误历史对照 + 去历史对比解码 | Table3 p8 | LLaVA1.5 HalluConv 14.96→32.84；mPlugOwl2 WPI 96.82→90.85（−5.97pp） | 记录未覆盖 | 错误历史有因果干扰 |
| litscan:3814 | 同题干配对图 | Table5；Table1 | GPT4o ALL 49.0 / DI 45.8 / BC 19.1 / AG 42.0；MultiMath AG 56.9；MathLLaVA 打乱图 45.3→34.4 | 记录未覆盖 | 单题答对掩盖不看图 |
| litscan:3218 | 反常识图 | Table3 | 九个模型中约 20% 的查询依赖常识；LLaVA13B FoV 80.5→84.6，CoT 降到 68.2 | 记录未覆盖 | 推理越多，越容易被先验带偏 |

## 成功条件 / 失败模式

**成功条件**
- 两侧证据都可读。
- 冲突只在关键事实上。
- 同时报告条件比例和 Others（不一致/拒答）的比例。

**失败模式**

- **混淆"对文字敏感"与"不忠实"。** 模型对外部误导文字敏感，不等于其内部 CoT 不忠实，也不等于它需要裁图（litscan:73751 failure_boundary）。
- **去历史的代价。** 去掉历史能修复视觉错误，但会伤害确实需要历史的问答（litscan:2420 why_non_obvious；WPI −5.97pp）。
- **过滤后的比例不可外推。** litscan:74625 的条件比例排除了 Others 和选项不一致的样本，不是无条件准确率。
- **AG 低不一定是在看图。** 随机作答也能让 AG 很低，必须结合 BC 一起看（litscan:3814 degenerate_cases）。
- **CoT 会合理化先验。** CoT 会把反常识的事实解释回惯常情境（litscan:3218 pitfalls）。

## 审稿期望

推断：
- 两侧可读性先过滤；
- 选项置换；
- 正确提示与错误提示交叉；
- 多种子（litscan:73751 指出种子方差大）；
- RL 前后对比。

## 认知障碍

单题准确率可能来自题干或选项，加了视觉编码器也不等于用了图（litscan:3814 why_non_obvious）。能答对、CoT 自洽，都不等于视觉 grounding（litscan:73751 why_non_obvious）。前人只在训练后看准确率，没有在 RL 前后对同一冲突集做对比。

## 工程经验

- **用语言一致性约束视觉训练时**：加入正确/错误提示交叉，以及空 reasoning 对照（litscan:73751 lesson）。
- **caption 历史可能有错时**：保留"去历史、同一张图"的对照，并单独测必须依赖历史的问题（litscan:2420 lesson）。
- **构造增广文本的模型只读了题目和指定答案时**："正确 caption"可能直接泄露标签（litscan:73751 AppC pitfalls）。

