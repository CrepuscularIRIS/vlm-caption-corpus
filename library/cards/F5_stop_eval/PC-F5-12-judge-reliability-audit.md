---
id: PC-F5-12
name: 用评审对象之外的配对扰动审计 AI 判定器：分开"看错"与"看对但被叙事带偏"，分开假阳与假阴
family: F5_stop_eval
status: candidate_pattern
problems: {P52: 3, P16: 2, P67: 1, P44: 1}
members: [litscan:77236, 2605.22148, 2610.17747, litscan:3617]
rs_patterns: [controlled_diagnostic_design, identify_hidden_assumption]
---
## 操作
在用 AI 判定器（judge / PRM / critic）当真值之前，先构造它应该判对的受控样本并逐类记错：
- 感知扰动：同一图像造三条回答——正确、仅感知事实错（推理保留）、感知+推理都错；测 judge 能否给出全序，并单独测"judge 自己答对视觉探针时仍偏好流畅错答案"的比例（litscan:77236 signatures、rs.key_step）。
- 方向性误差：把 judge 当二元误差信道，按假阳/假阴分别对照决策阈值；假阳率达到某界后再多样本也修不好（2605.22148 signatures）。
- 线索可预测性：受限输入预测器、保持错误不变而移动 cue、只在 cue 失败子集评测、重加权指标（2610.17747 rs.key_step）。
- 全错误定位：人工标注长 CoT 的所有错误 section，测 PRM/critic 的 macro-F1（litscan:3617 signatures）。

## 信息
受控构造的样本及其已知标签；judge 的输出。标签由构造过程保证，部分有人工核查（litscan:3617 1236 个人工标注样本）。

## 成立条件
- 受控样本的标签可靠：合成三元组的预设全序不是逐例人工金标（litscan:77236 failure_boundary）。
- 审计覆盖的错误类型与实际使用场景一致；2605.22148 只审计枚举出的缺陷类，且核心证明不在缓存中（2605.22148 conditions、failure_boundary）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:77236 PerceptJudge | 感知扰动三元组 + GRPO 训练 judge 全序 | Table1；Table2 | Flex judge 总体错误 23.5%→14.3%；"看对仍错排" 14.1%→7.6%；pair-with-tie 仅 .514→.520 | judge 输出采样 3 次取均值；训练种子未见 | 记录未覆盖 |
| 2605.22148 Ratchet | judge 二元误差信道 vs 淘汰阈值 | Abstract | 摘要称失败判通过率 ≥(1−τ)/2 会使淘汰失效，更多样本修不好；核心证明**记录未覆盖** | 记录未覆盖 | 记录未覆盖 |
| 2610.17747 失败归因审计 | 受限预测器 + cue 移动 + 残差评测 | Table3 | Aegis 全 speaker 规则 micro-F1 49.2，接近 GPT-4.1 50.0，但 exact-set 1.5 vs 20.7；AFTraj 两者平均 50.3 但 injected/natural 强弱相反 | 记录未覆盖 | 记录未覆盖 |
| litscan:3617 DeltaBench | 人工标注长 CoT 全部错误 section，测 PRM/critic | Table2 | GPT-4-turbo macro-F1 40.76；Qwen-Math-PRM 7B 29.22 高于 72B 26.38 | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：审计样本与使用场景同分布；FP/FN 分开报。
- 失败模式：
  - 总体一致率掩盖方向性误差（2605.22148 relevance P52："judge应按假阳性/假阴性及动作阈值审计，整体一致率不足"）。
  - 规则基线可接近 judge 的总分，说明高分可能来自标签可预测性（2610.17747 Table3）。
  - 训练后的 judge 仍不完全可靠（litscan:77236 claimed_effect："不是完全可靠"）。
  - 更大的 PRM 不一定更会定位错误（litscan:3617 Table2）。
  - cue 干预只有一个注入管线；单步文本可能真能说明错，不全是伪迹（2610.17747 failure_boundary）。
- 旁证（非成员，F4 digest 主题）：过程 judge 的匹配参考被打乱后反而低于 outcome（HaPRL 2609.37190 Table5：shuffle 28.63 < outcome 33.98）；Weblica 的 judge 与人评仅 88% 一致（2605.06761 §4.1）；DistRL 给 Gemini 更长上下文反而降低与人评一致性（2410.14803 §6.3）。

## 审稿期望
- 分别测 judge 是否看对、看对后是否按证据判；不能用同一模型自洽代替人工 gold（litscan:77236 lesson）。
- 冻结 judge 的关联分数不等于因果收益，需随机 toggle 才能因果解释（2605.22148 known_failure_check）。

## 认知障碍
自动 judge 会在自己答对视觉探针时仍偏好流畅的错答案（litscan:77236 why_non_obvious）；误把失败判成功会偏移统计均值，这种偏差不能靠更多样本消除（2605.22148 why_non_obvious）。领域默认"judge 与人一致率高 = 可用"。

## 工程经验
- 当用 chosen 回答当 correct、用自动答案一致性过滤时，它不等于逐条视觉事实的人工验证（litscan:77236 pitfalls）。
- 当外部视觉 judge 读图失败会降级为纯文本时，必须记录 fallback 频率，频率上升即停（2609.37190 pitfalls，F4 digest）。

