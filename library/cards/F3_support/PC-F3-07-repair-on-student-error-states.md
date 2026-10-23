---
id: PC-F3-07
name: 在学生自己的错误状态上，由教师/模拟器/规则补正确续写，作为 SFT 或偏好数据
family: F3_support
status: candidate_pattern
problems: {P27: 3, P25: 3, P38: 2, P36: 2}
members: ["litscan:13033", 2507.03019, "litscan:75661", "litscan:77773", "litscan:3816", "litscan:35435", 2508.04088]
rs_patterns: [generative_process_redesign, self_supervised_signal_engineering]
---

## 操作

先让学生（SFT 后模型）自己 rollout，用 GT/验证器找出出错的步骤或前缀；保留学生的错误前缀作为上下文，由教师、模拟器或规则写出正确的后续（局部修正或从首错步重写），把"学生错误前缀 → 正确续写"加入 SFT，或组成"修正续写 ≻ 原错误"的偏好对。可迭代多轮。

## 信息

- 错误状态来自学生自身分布（与 PC-F3-06 的合成错误不同）。
- 定位错误需要 GT 或外部判定：litscan:13033 用 GT mask 的 IoU 变化（Algorithm1）；2507.03019 的教师看到图像、学生 CoT 与 GT 答案（SIG 字段）；litscan:35435 用每个前缀 8 条续写的成功率训练 stepwise ORM（§3.1）。
- 正确续写由谁写：模拟器 Fsim（litscan:13033）、GPT-o4-mini（2507.03019）、规则反馈（litscan:75661）、文本 reasoner（litscan:77773）、学生自身最终正确 trial（litscan:3816）。

## 成立条件

- 有可验证的错误定位信号。
- 续写者看到的信息要么学生也能看到，要么要单独审计信息泄漏（litscan:77773 PIT："学生从未见 caption"）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:13033 SegAgent | 学生 rollout 后按每步 IoU 变化保留或用 Fsim 替换退步动作，D0∪Dn 重训 | §4.1,4.3 Algorithm1; §5.4 | ThinObject5K IoU 71.45→86.57（一轮 StaR+） | 记录未覆盖 | 支持 |
| 2507.03019 Look-Back | 选高方差难题，保留学生 CoT，教师插入 back 验证/纠错段，SFT 一轮后 GRPO | Table4 p6; §3 p4 | 完整 Semantic-back AvgAll 67.6 vs GRPO 65.7；SFT-only 58.5 低于 base 61.8 | 记录未覆盖 | 支持（只在后续 RL 下成立） |
| litscan:75661 DocVAL | 规则验证器 Q>.85 过滤，学生错误 + 规则反馈迭代 SFT | Table2; Table3 | DocVQA ANLS 91.4 / mAP 82.4；无 validation 88.1/63.7；5 次 B2 FUNSD 89.9 略低于 B1 90.1 | 记录未覆盖 | 支持过滤；迭代修正收益有限 |
| litscan:77773 LongGT | VLM 初答 z1 + 文本 reasoner 扩展 z2；错 z1→正确 z2 ≻ 错答；z1 已对则偏好更短 z1 | §2.4/§3.3; Table11 | SFT .716 → +DPO .740 → +GRPO 70k .757 | 记录未覆盖 | 支持；保留"已对则短答"偏好 |
| litscan:3816 S2R | 自身失败 trial 留作上下文、mask 其 solution，SFT 只训 verify/最终 solve | Table2; notes | Qwen2.5Math7B MATH500 51.0→BI 81.6→ORL 84.4 | 记录未覆盖 | 支持 |
| litscan:35435 GLoRe | 首个低分 step 标 [BAD] 训练局部修正，与全局重写候选用 ORM 重排 | §3.1; Table3 p7 | GSM8K 13B 错误初稿修正率 global .281、local+SORM .283、合并 .412（子集覆盖，不是总体准确率） | 记录未覆盖 | 支持局部+全局互补 |
| 2508.04088 GM-PRM | 保留正确前缀、替换首错步，policy 补全 N/2 候选 | Table2 Llama row | Llama3.2-11B 五集 Pass@8 62.7→64.0 | 记录未覆盖 | 弱支持（推理时外部 judge） |

## 成功条件 / 失败模式

- 成功条件：学生错误前缀真实；续写正确且与学生表达分布一致（见 PC-F3-08）。
- 失败模式 1：SFT-only 低于 base，只有接 RL 才有收益（2507.03019 Table4）。
- 失败模式 3：迭代修正收益递减甚至略降（litscan:75661 Table3）。
- 失败模式 4：低即时收益的探索步骤被误判为错误（litscan:13033 FAIL："低增益过滤可能误删排除式搜索"）。
- 失败模式 5：外部 judge 的修正不是 actor 自主纠偏（2508.04088 KF 字段）。

## 审稿期望

推断：要求区分"错误定位"与"续写"两部分的贡献；要求在无 GT 的推理时测纠错率；要求报告对→错的副作用。

## 认知障碍

- 专家轨迹近最优，缺学生真实错误状态；分步修复能为学生实际到达的状态提供正确后续（litscan:13033 rs.why_non_obvious）。
- 用 GPT-4o 原生 CoT 替换学生底稿会退步，学生同源底稿更合适（2507.03019 §5 p7，见 PC-F3-08）。

## 工程经验

- 当保留失败 trial 作上下文时，只 mask 其 solution，单独评估错→对与对→错（litscan:3816 notes）。
- 当 validator 用 GT 框与检测区域时，把修正集记为训练暴露集，不称独立验证（litscan:75661 LESSON）。
- 当做错误前缀续写偏好时，同时保留"已答对则偏好短答"的偏好对，否则直答会被续写挤掉（litscan:77773 EQ §2.4）。

