---
id: PC-F3-06
name: 在 SFT 轨迹中注入合成的错误动作并接正确恢复，错误动作与其观测不进 loss
family: F3_support
status: candidate_pattern
problems: {P25: 3, P27: 2, P38: 2, P26: 1}
members: ["litscan:51030", "litscan:62697", "litscan:72663", "litscan:63682", "litscan:53612", "litscan:76340"]
rs_patterns: [heterogeneous_decomposition, self_supervised_signal_engineering]
---

## 操作

由教师或模拟器在正确轨迹中插入一个错误动作（错框、错帧、错误点击、失败工具调用、错误 rationale），随后接上发现错误并恢复的正确动作。SFT 时把错误动作 token 与执行返回 mask 掉，只监督恢复部分与正常文本；之后再做 RL。

## 信息

- 错误位置与正确恢复由造数据方决定，可见 GT（litscan:51030：GPT4o 见全图/GT 参考 cue；litscan:62697：GT mask 的 FP/FN 区域与正确下一 click）。
- 学生推理时看不到这些特权信息（litscan:62697 PIT：教师见 GT FP/FN，学生只看 overlay）。
- 错误来自合成，不是学生自己的真实失败分布；这是与 PC-F3-07 的区别。

## 成立条件

- 有可执行的环境，能对错误动作产生真实返回（错框返回错误区域）。
- 错误动作必须被 mask，否则模型会学到"先错再改"或学会调用错误工具拿奖励（litscan:51030 NEG："无 correction 会错误调用拿 bonus 且绕过工具答对"）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:51030 Pixel Reasoner | 插入错 box/frame 后接正确 cue；SFT mask 错误工具与执行输出 | §3–5/Table1/AppC | V* 84.3；无纠偏 80.1；无 curiosity 81.1 | 未给主表多 seed | 支持 |
| litscan:62697 IBISAgent | 模拟与用户 mask 不一致的错误动作，撤回重做；错误动作与工具观测不训练 | §3.2; Table4 | inhouse SFT 53.42 IoU → 加 reflection 57.16；SFT+RL 68.92 → 完整 72.09 | 记录未覆盖 | 支持 |
| litscan:72663 AdaReasoner | 人工抽象轨迹加入回退/工具失败，真实执行补观测 | Table5 p8 | 7B VSP 31.64→97.64；无 A* 时 reflection 91.36 vs 67.27；但推理时新增 A* 使 reflection 模型 91.36→68.55 | 记录未覆盖 | 支持，带刚性副作用 |
| litscan:63682 CodeVision | SFT 中显式加入 error-handling 轨迹 | §3.2 pp3–4; Fig10 p8 | 与其他行为一起使 RL 收敛（无 SFT RL 失败） | 记录未覆盖 | 支持（未单独消融 error-handling） |
| litscan:53612 ViGoRL | 72B teacher MCTS 成功/失败支路拼接成回退轨迹 → SFT | Table3; Table4 | V*Bench 7B 78.0→86.4；线性 teacher rollout BLINK 降 2.32 点 | 95%CI，未读到多训练 seed | 支持 |
| litscan:76340 MIND | 正/负 rationale 都作条件，目标是正确答案与解释 | §3/Table4 | ScienceQA 基线 90.29→92.29；单独 MCA 仅 90.36 | 固定 seed42 | 弱支持：负例是合成逻辑反转，非真实错误观测 |

## 成功条件 / 失败模式

- 成功条件：错误 mask 正确，恢复示范接在真实执行返回之后。
- 失败模式 1：SFT 对新工具产生刚性（litscan:72663 Table5：新增 A* 后 91.36→68.55）。
- 失败模式 2：warm-start 本身可能低于 base（litscan:51030 InfoVQA 74.3 vs 80.7）。
- 失败模式 3：合成错误分布与学生真实错误不同（litscan:76340 FAIL："合成逻辑反转非真实错 crop 观测"）。
- 失败模式 4：教师可见 GT，示范中的"发现错误"可能依赖学生看不到的信息（litscan:62697 PIT）。

## 审稿期望

推断：要求无纠偏示范的消融（Pixel Reasoner、IBISAgent 已做）；要求在学生真实错误上测恢复率，而不只是合成错误；要求报告错→对与对→错两个方向。

## 认知障碍

- 近最优的规则轨迹缺少学生的真实错误状态，所以模型从未见过"错了怎么办"（litscan:13033 rs.why_non_obvious，同理见 PC-F3-07）。
- 直觉是"只要奖励纠错就行"，但工具弱时 RL 会绕开工具，只奖励尝试又会出现执行错误但凭语言答对的投机（litscan:51030 rs.why_non_obvious）。

## 工程经验

- 当插入错误动作时，必须保持实际图像绑定，再裁的 bbox 与错误 cue 都要绑定真实返回（litscan:51030 PIT）。
- 当 reward 使用"动作后的错误区"时，注意与"动作前"的区别（litscan:62697 PIT：正文 click reward 在执行后算 FP/FN，可能与修正冲突）。

