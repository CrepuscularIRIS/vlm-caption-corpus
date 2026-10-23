---
id: PC-F5-11
name: 保持题目与格式不变、只替换一个因素（证据、无关线索、内部内容）做配对干预测量
family: F5_stop_eval
status: candidate_pattern
problems: {P50: 3, P67: 2, P41: 2, P27: 2, P51: 1}
members: [litscan:73853, litscan:2430, 2609.16268, 2606.01287]
rs_patterns: [controlled_diagnostic_design]
---
## 操作
对同一道题构造只差一个因素的配对输入，用答案（或工具率）的变化读出该因素的作用；同时设"自身重放"或"无变化"对照验证干预管线本身不改变输出：
- 证据替换（恢复评测）：VisualSwap 在旧图 $I_a$ 上生成推理 $R_a$，换成答案不同的相似图 $I_b$ 后完整 re-prefill，比较 assistant 续写与新 user turn：$R_b=M(I_b,Q,R_a\oplus P)$，$\Delta=Acc_{base}-Acc_{probe}$（litscan:73853 Eq1–3）。VisDiaHalBench 五轮：改目标 → 指代问 → 原对象不存在问 → 承接不可答问 → 换回原图复问（litscan:2430 signatures）。
- 无关线索干预（捷径测量）：同题加/不加无关 cue，$\Delta Tool=\hat P(T_s\mid x_c,a)-\hat P(T_s\mid x_c)$（2609.16268 §2.2）。
- 内部内容干预（机制测量）：保留 marker/位置/长度，只换 slot 内容（zero / 等尺度高斯 / 固定向量 / 真实 donor），分开"整段删除"与"保留损坏接口"，并做 self-swap 验证 hook 保真（2606.01287 App.G.3–G.5）。

## 信息

## 成立条件
- 干预确实只改一个因素：编辑成功、指代唯一（litscan:2430 conditions）；分辨率保持（litscan:73853 normalization）。
- 有管线保真对照：self-swap / no-change 对照（2606.01287 conditions；TableA16 self-swap 仍有两设置 −.018）。
- 干预后输入仍在分布内；替换 OOD 内容会制造伪损坏（2606.01287 failure_boundary）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:73853 VisualSwap | 换图 + re-prefill；assistant 续写 vs 新 user turn；2× image attention | §2 p3；Table4 p7；Table9 p9；Table15 p17 | Qwen-235B-Thinking probe 34.1、multi 85.4；8B-Thinking 36.6→67.5；2× attention 36.6→54.8；裸 turn token 只 33.3 | 记录未覆盖 | 记录未覆盖 |
| litscan:2430 VisDiaHalBench | scene-graph 路径生成五轮配对问答 | Table3 p7；Table2 p6 | GPT-4V 图像平均 EM 33.01，给 scene graph 59.12；第 5 轮无历史 77.16，首轮答对的误导历史组 38.35；改属性 19760 vs 改对象 105 | 记录未覆盖 | 记录未覆盖 |
| 2609.16268 Spurious Tool Use | 同题 cue 有/无 + judge 不必要调用罚 −0.5 | Table1 p6 | WEB INDEX 条件 GSM8K search 率 40.1/0.9（差 39.2pp）→ 加罚后 0.2/0.2；准确率 83.0/84.4→92.8/88.8 | 每 run 1 seed（Table6） | 记录未覆盖 |
| 2606.01287 Beyond Visual Memory | 内容/marker/格式分离干预 + donor 交换 + blind 注入 | TableA14；TableA18；App.G.3；TablesA15–A17 | slot 敏感性 0.3–2.7pp，marker 敏感性 MVH-S 58.5pp；blind 注入恢复 7.8%，CI[−15.2,28.6]pp；donor adoption 5.3–12.7%，CI 均低于 25% | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：有无变化对照；样本足以给出区间；干预与自然流程的差异被单独报告。
- 失败模式：
  - prefill 干预 ≠ 在线工具返回；新 turn 下的恢复不证明自主恢复（litscan:73853 failure_boundary）。
  - 两组按首轮正确性条件化，不是随机对照；scene graph 含答案信息（litscan:2430 failure_boundary）。
  - 固定第 3/4 轮不可答可被轮次捷径解决（litscan:2430 degenerate_cases）。
  - Python cue 没有产生对称的强捷径；judge 不是当前 actor 的反事实（2609.16268 negative_results、failure_boundary）。
  - 宽 CI 不能当"无效应"；小分母比例不稳（2606.01287 failure_boundary：Monet-R V*/MME 各 2 题）。
  - 删除整段同时破坏格式/计算/控制，不能单独识别内容贡献（2606.01287 why_non_obvious）。

## 审稿期望
- 先用 self-swap 确认干预管线，再同时测"损坏接口"与"干净删除"，并用同熵随机对照区分集中与定位（2606.01287 lesson）。
- 记录实际图像绑定、prefill 与 turn 结构；提示式恢复属于外部辅助能力（litscan:73853 lesson）。
- 随机化证据变化与不可答位置（litscan:2430 lesson）。
- 先做同题 cue 配对与正确工具召回测试，再考虑罚项（2609.16268 lesson）。

## 认知障碍
口头说"让我再看看"不等于更新了视觉事实；协议差异（assistant 续写 vs 新 user turn）就足以决定能否用上新证据（litscan:73853 why_non_obvious）。高准确率与可视化结构可以与"内容不承重"共存（2606.01287 why_non_obvious）。最终答对仍可隐藏无用工具调用（2609.16268 why_non_obvious）。

## 工程经验
- 当用视觉替换测试恢复时，必须用新图重新 prefill 并保持相同分辨率，禁止沿用旧图的 KV cache（litscan:73853 pitfalls）。
- 当把向量注入输入 embedding 时，同维度不等于同尺度，应按初始 embedding 平均 L2 范数校准（2606.01287 pitfalls）。
- 当结构目标需前移一位对齐时，latent/image 位置的 label 设为 ignore，边界 marker 保留 CE（2606.01287 pitfalls）。
- 当不同条件的有效样本过滤不同（n=58 vs n=57）时，要保留差异而不是假装全配对（2606.01287 pitfalls）。

