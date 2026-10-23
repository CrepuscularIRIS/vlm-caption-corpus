---
id: PC-F4-14
name: 奖励 caption / think / answer 之间的文本一致性
family: F4_perception
status: needs_revision
problems: {P42: 3, P40: 2}
members: [litscan:73751, litscan:70540, litscan:77580, litscan:72973]
rs_patterns: [heterogeneous_decomposition]
---
## 操作

在终答奖励之外，加入或门控一个"中间文本与答案（或与参考）一致"的分数。三种实现：

- **RLVLMFaith：一致性门控正确奖励**（litscan:73751 §3.3 / AppG.4）
  - 公式：$r^{faith}=\mathbb1[answer=GT]\cdot c(o)$；
  - $c(o)$ 由文本判官检查 think 段的最终判断是否与答案一致。
- **RegionReasoner：关键词重合**（litscan:70540 Eq5–6）
  - 公式：$R_{cons}=Ov(scene,think)+.6\cdot\mathbb1[B_{ref}\neq\emptyset]Ov(focus,think)+.4\ell(think)$。
- **iVGR：参考一致性**（litscan:77580 Eq1,3）
  - 外部文本判官比较 target CoT 与历史最佳 grounded 参考，给 0/.3/.7/1 分。

## 信息

- **判官多为纯文本，不看图。**
  - litscan:73751 的判官输入为问题加完整回答，不判对错（signal_routing）。
  - litscan:77580 的判官只读问题和两段 CoT，并假定参考描述正确（failure_boundary）。
  - litscan:70540 是规则关键词匹配。
- **看不到**：
  - 中间文本是否符合图像事实；
  - 一致是否源于复制。

## 成立条件

- 判官不能被空推理或复制绕过。litscan:73751 中，空 think 被判为一致（vacuously yes）。
- 参考本身正确。litscan:77580 依赖 GT 框筛出的参考。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:73751 | 一致性门控正确奖励，配合增广 | §3.3 / AppG.4；图5 | 只奖准确率时一致率随 RL 下降；faith 奖励单独使用能对齐，**与增广合用时复制误导文字，出现短回答塌缩** | 跨种子差异明显 | 负 |
| litscan:70540 | 场景/焦点与 think 的关键词重合 | Tables3–4 | 多轮 RefCOCO+ AP 74.8→80.7，RefCOCOg 73.6→78.2；单轮 RefCOCO+ 87.9→87.7 | 固定种子，数值未读到 | 多轮正，单轮略负 |
| litscan:77580 | 文本判官对齐 grounded 参考 | Tables2,5 | 5 基准平均：dual 无 consistency 71.0 → +consistency 71.5 → +archive 72.4；8B CV3D 93.5→91.0 | 记录未覆盖 | 弱正 |
| litscan:72973 | （反向证据）SFT 过滤一致性，RL 只用结果奖励 | §3.2 p5；A4.2 p25 | 600 样本人审逻辑/汇总错误 0；GRPO 后仍出现推理 9 个对象、只输出 8 框 | 记录未覆盖 | 没有一致性约束时，RL 后一致性回退 |

## 成功条件 / 失败模式

**成功条件**：判官或规则能区分"由证据推出"与"复制答案"；增广不与一致性奖励叠加。

**失败模式**：
- **复制捷径**：一致性奖励鼓励模型复制正确 caption，进而泛化为复制错误 caption（litscan:73751 why_non_obvious, negative_results）。
- **空推理漏洞**：空 think 被判一致，给缩短推理留下捷径（litscan:73751 invariance，读者分析）。
- **复述被奖励**：只核文本一致的过程奖励，可能把复述当作因果 grounding（litscan:70540 lesson）。
- **错误参考污染**：答案错误但描述一致的文本也可能拿分；归档的错误参考会污染信号（litscan:77580 invariance, degenerate_cases）。

## 为什么是 needs_revision

- 正向结果（litscan:70540、litscan:77580）都依赖 GT 框参考或多轮引用框。
- 负向结果（litscan:73751）出现在"一致性门控 + 文本增广"的组合下。
- 两边条件不同，尚未有同条件对照，不能合并成一条"一致性奖励有效"的模式。

## 审稿期望

推断：
- 空推理与复制对照；
- 正确/错误提示交叉；
- 判官看图与不看图两种版本的对照；
- 一致性高但事实错的比例。

## 认知障碍


## 工程经验

- **SFT 监督了证据与答案一致、RL 只保结果时**：一致性可能退化，需要单独记录，不能用正确率代替（litscan:72973 lesson）。
- **当过程奖励只核对文本一致性时**：要用独立的几何或像素证据来评估，不能把复述当作 grounding（litscan:70540 lesson）。
- **当显式坐标损伤答案时**：可以把 grounding 留在训练参照通道，但必须独立审计参考事实（litscan:77580 lesson）。

