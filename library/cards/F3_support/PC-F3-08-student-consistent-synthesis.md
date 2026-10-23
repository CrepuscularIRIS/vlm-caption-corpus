---
id: PC-F3-08
name: 冷启动轨迹按"学生同源"合成：学生写表达与终答，教师只补能力段；而非直接用教师整段轨迹
family: F3_support
status: needs_revision
problems: {P36: 2, P39: 2, P25: 2, P38: 1}
members: ["litscan:76463", 2507.03019, "litscan:77335", "litscan:77773"]
rs_patterns: [generative_process_redesign]
---

## 操作

合成 SFT 轨迹时，以学生（待训模型）自己的生成为底稿：表达/风格段与最终答案由学生生成，只在"能力"段（关键推理、纠错内容）由教师生成或插入；而不是让教师整段生成后直接蒸馏。

## 信息

- 学生自身的生成分布（共享前缀）；教师生成的能力段；可选的段边界预测器（litscan:76463：0.6B 边界模型，教师自动标注 style/capability，每种 100k segments）。
- 教师常看到学生看不到的信息（2507.03019 教师见 GT 答案；litscan:77773 文本 reasoner 见 dense caption）。

## 成立条件

- 学生已有一定的生成能力（已是推理模型或已 SFT 过的模型）。
- 教师与学生 tokenizer 不同时需处理拼接（litscan:76463 PIT：丢弃最后一个 word）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:76463 TESSY | 20-token generate-rollback，学生写 style、教师写 capability，终答全由学生 | Table1 p6; AppA.7 p15 | LCB-Pro 25.35→36.69，OJBench 18.75→25.43；Teacher-only 22.10/8.73；改用教师 final 后降 12.33/13.58pp | pass@1 多次评测平均，训练种子未确认 | 支持 |
| 2507.03019 Look-Back | 用 GPT-4o 原生 CoT 替换学生底稿再插 back | §5 SFT Cold-Start Data Requirements p7 | 冷启动后退步（未给数值）；改用学生同源 CoT | 记录未覆盖 | 支持 |
| litscan:77335 Octopus | 冷启动用同分布自生成 vs 混采强模型 | §4.1/Fig4; PIT 字段 | 同分布 cold-start 更易低熵，混采强模型（o2 见 x、o1、GT）较好 | 记录未覆盖 | **冲突**：完全自生成反而熵塌缩 |
| litscan:77773 LongGT | 文本 reasoner 在 dense caption 上扩展 VLM 初答；学生只见图像 | PIT 字段; Table12 p22 | 记录指出 caption 只对教师可见，"guided regex 禁止 teacher 引用 caption 措辞并不消除 caption 信息优势" | 记录未覆盖 | 边界：同源表达不消除信息差 |

## 成功条件 / 失败模式

- 成功条件：教师贡献的是学生可承受的局部内容，学生保留自己的表达与终答（litscan:76463 AppA.7）。
- 冲突（needs_revision 的原因）：litscan:77335 报告纯自生成冷启动熵更低，混入强模型更好；litscan:76463、2507.03019 报告教师整段更差。两者都支持"混合"，但混合的粒度（段内交替 vs 样本级混采）不同，记录不足以判断哪种粒度起作用。
- 失败模式 1：不能保证 style/capability 可无损分离；视觉任务未验证（litscan:76463 FAIL）。
- 失败模式 2：TESSY 训练早期先跌，第 3 epoch 恢复（litscan:76463 AppB.1）。
- 失败模式 3：同源表达不等于证据可见，教师信息优势仍在（litscan:77773）。

## 审稿期望

推断：要求同一预算下比较教师整段、学生整段、段内混合、样本级混合四种；要求给出熵或多样性指标；视觉任务上要求学生视图的证据可见性审计。

## 认知障碍

- "更强教师的轨迹更好"是默认假设；litscan:76463 显示同题更强学生的数据也可能不如目标学生自身风格（rs.why_non_obvious）。
- 反过来，"完全自生成最一致"也不成立（litscan:77335 §4.1）。

## 工程经验

- 当教师与学生 tokenizer 不同时，不能用 token 索引直接拼接，丢弃最后一个 word 再续（litscan:76463 PIT）。
- 当用自生成数据做冷启动时，监测熵，必要时混入强模型样本（litscan:77335 §4.1）。

