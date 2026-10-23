---
id: PC-F4-10
name: 替换或移除中间视觉通道的内容，并配等步数占位与 oracle 正对照，检验该通道是否真被使用
family: F4_perception
status: candidate_pattern
problems: {P41: 3, P43: 1, P50: 1, P11: 1}
members: [2605.18445, litscan:78268, 2605.18641, 2609.06746, litscan:73853]
rs_patterns: [controlled_diagnostic_design, assumption_audit_and_pivot]
---
## 操作

固定被测 checkpoint，对中间通道做 do-干预，再看下游答案。中间通道包括 latent、caption 中介、工具返回图。

- **干预方式**：内容替换为随机样本、零向量或噪声；或移除该通道（skip）。
- **两项配套对照**：
  1. 等步数的 pause/占位，作为"有计算、无内容"的对照；
  2. oracle 内容，作为"该通道可被利用"的正对照。

各成员做法：

- **2605.18445**：在 latent 上做 $P(y\mid do(z=z'),x)$，$z'$ 取 random/zeros/noise/skip（§3 p4）。另做 masked 正对照：把关键区域从主图抹去，只保留 helper（§4，Tables2–3）。
- **2609.06746**：先关掉原图到答案的旁路，再做"匹配状态交换"（§3；Table1/2）。
- **litscan:73853 VisualSwap**：保留同一 assistant 前缀，把所有图换成 $I_b$，再续写；与"开新 user turn"的版本对照（§2 p3）。

## 信息

- **oracle / helper**：属于特权辅助信息，只用于建立正对照（2605.18445 information）。
- **测不到的东西**：
  - 每题潜在的工具价值真值；
  - 逐题的切换率（2605.18445 failure_boundary 指出未报告）。

## 成立条件

- **对照分布要合理**。跨样本 random 只是近似（2605.18445 conditions）。部分 OOD 干预太猛：ILVR 在 V* 上 skip 使 63→46，Monet-SFT 置零使 76→41（2605.18445 Tables1/5）。
- **枚举所有旁路**。只删可见图像不够，原图与 KV 缓存仍可直达答案（2609.06746 lesson）。
- **prefill 改变状态**。prefill 与回合边界本身会改变行为，自然工具返回状态与 prefill 状态不同（litscan:73853 failure_boundary；Table15）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.18445 | latent do-干预 + pause + oracle | Fig3/Table5；Table1；Tables2–3 | 各模型 × BLINK/V* 至少有一种 dummy 落在约 2pp 内或更高；普通 VisCoT 下 oracle 79 = pause 79；masked VisCoT 下 oracle 75 vs pause 59；Tetris 下 oracle 86 / generated 33 / pause 34 | Tetris 单种子 42；干预无 CI | "准确率不变"不能推出"内容无用" |
| litscan:78268 | 常量替换 latent；文字 caption 基线 | App B Table4 p13；Table1 p7 | Monet V* 82.7→83.3（常量）；Mirage 近零 latent 77→35.5；caption-SFT V* 85.9 vs 同 17k Monet 79.6；DeepEyes 真实重看 V* 90.0 > 85.9 | 记录未覆盖 | 文字中介可替代 latent；真实重看仍有增量 |
| litscan:73853 | 同前缀换图续写 vs 新 turn | §2 p3；Table4 p7；Table9 | Qwen235B Thinking：probe 34.1，multi-turn 85.4；8B Thinking 36.6→67.5；attention×2 只恢复到 54.8 | 记录未覆盖 | prefill 干预本身会改变行为 |

## 成功条件 / 失败模式

**成功条件**
- 同时具备三者：内容替换、等步数占位、oracle 正对照。
- 报告逐题转换矩阵，而不只是平均准确率。

**失败模式**
- **平均准确率掩盖逐题变化。** 总体不变可能来自对错互换、文本前缀已携带信息，或修复协议本身改变了终止行为（2605.18445 failure_boundary）。
- **干预后输出协议变了。** Monet-RL 受干预后可能只写观察、不给可提取答案，作者因此统一强制补全（2605.18445 App H pitfalls）。
- **oracle 可用 ≠ 能自己生成。** Tetris 中 generated 33 ≈ pause 34（2605.18445 Table3）。
- **文本中介无法凭空补回像素。** 编码时丢掉的细节，文字想象补不回来；DeepEyes 的真实重看仍更高（litscan:78268 negative_results）。
- **均值方差匹配 ≠ 分布内。** 均值、方差匹配的噪声不保证落在分布内（litscan:78268 failure_boundary）。

## 审稿期望

推断：
- 逐题 switch 率；
- 干预重复种子与配对 CI；
- 正对照任务（masked 或 Tetris 式）；
- 旁路枚举。

## 认知障碍

SFT/RL 后准确率提升，不保证中间表示真的起了作用：表示可以被生成出来，却被答案路径绕过（2605.18445 why_non_obvious）。前人只看 benchmark 增益，不做内容替换，也不做 oracle 正对照，因此无法区分"通道无用"和"对照失真"。

## 工程经验

- **中间通道被宣称有推理价值时**：同时测内容替换、oracle 上限和等步数 pause，并记录格式失败与补全协议（2605.18445 lesson）。
- **判断视觉 latent 或 caption 是否被使用前**：先枚举全部 KV 和图像旁路，再做绑定匹配的状态替换（2609.06746 lesson）。
- **评估 recover 时**：必须检验答案关键视觉事实是否改变，不能用"再裁图动作次数"代替（litscan:73853 relevance P50）。

