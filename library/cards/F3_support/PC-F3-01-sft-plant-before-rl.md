---
id: PC-F3-01
name: 先用目标行为示范做 SFT 冷启动，再让 RL 在该行为上试错
family: F3_support
status: candidate_pattern
problems: {P25: 3, P38: 2, P27: 2, P26: 1}
members: [2503.01307, "litscan:70410", "litscan:63682", "litscan:71722", "litscan:58400", "litscan:74330", "litscan:70604", 2604.17073, "litscan:53612", 2608.29374, "litscan:79179", "litscan:52782", "litscan:64855", "litscan:77773", "litscan:56056", "litscan:77746"]
boundary_members: ["litscan:72124", "litscan:61411"]
rs_patterns: [controlled_diagnostic_design, structural_prior_encoding]
---

## 操作

RL 之前，用含目标行为（工具调用、回退、纠偏、澄清等）的示范轨迹做 SFT；RL 只用终答（+格式）奖励，在 SFT 已覆盖的行为上重新分配概率。判别方式：同一配方去掉冷启动 SFT 做 RL-only 消融，看目标行为与准确率是否出现。

## 信息

- 冷启动示范来自外部教师 / 专家 / MCTS 搜索，看得到 GT 答案或参考证据（如 2503.01307 由 Claude3.5 按指定行为生成轨迹，§3.1 p5；litscan:58400 由 GPT-5 草稿经 3 位专家修订，Table4 p8）。
- RL 阶段策略只看自身 rollout 与终答验证结果；不估计逐次行为价值。
- 行为是否出现由行为分类器或调用计数统计，仅用于分析，不进奖励（2503.01307 §3.1）。

## 成立条件

- 示范的格式与 RL 协议一致（工具调用格式、观测回填、mask）。
- 示范只是"种行为"，不保证 RL 后保留；保留要另测（见 PC-F3-02、PC-F3-03）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2503.01307 | 1000 例行为 priming SFT 后 250 步 PPO；对照空 CoT / 等长占位 / 错误答案行为 | §3.1 p5 | 同 PPO 下 Qwen 约 60%、Llama 约 30%；空 CoT/等长空 CoT 仍约 30–35%；错误答案行为 priming 与正确行为版本相当（图示，记录未读精确终点） | 记录未覆盖 | 支持：行为先验而非答案正确性决定 RL 可学性 |
| litscan:70410 Mini-o3 | 6000 条多轮 SFT 冷启动 | Table2 | 无冷启动 hard 25.4，且正确轨迹均为 1 turn；有冷启动平均 5.5 turn | 每题多次采样，非训练种子 | 支持 |
| litscan:63682 CodeVision | 6K SFT（含 no-tool、单/多工具、multi-crop、error-handling） | §3.2; Table3 p7; Fig10 p8 | 直接 RL 不收敛；SFT 后 RL MVToolBench 60.1，SFT 26.6，base 18.1 | 记录未覆盖 | 支持 |
| litscan:71722 DeepEyesV2 | 纯 RL + tool bonus vs 执行核验教师轨迹冷启动 | Table5 p7 | 纯 RL 加 tool bonus 退化为单个占位代码块；SFT→完整 RL CharXiv reasoning 44.3→48.9 | 记录未覆盖 | 支持（复杂代码工具） |
| litscan:58400 Spec-o3 | ~1k 专家审校轨迹 SFT → GRPO | Table4 p8 | 7B macro-F1 完整 76.5；仅 RL 40.5；仅 SFT 41.6；无工具 55.8 | 记录未覆盖 | 支持 |
| litscan:70604 MindCube | 认知图 SFT warm start → RL | Table4 | SFT 57.81→RL 61.33；同结构裸 RL 50.86 | 记录未覆盖 | 支持 |
| 2604.17073 Abstain-R1 | SFT coldstart 后 RL（澄清行为） | Tables1–3 | 无 SFT 时 U-Clar 8.5，完整 55.1（rs.why_non_obvious）；AbstainTest URef 68.1 vs base 9.4 | 未报告 | 支持 |
| litscan:53612 ViGoRL | MCTS 线性化轨迹 SFT → 多轮 GRPO | Table3; Table4 | V*Bench 7B 78.0→86.4；记录称"无 warm start 不能产生有效格式"（relevance 字段，精确位置记录未覆盖） | 报 95%CI，训练种子未读到 | 支持 |
| 2608.29374 | 五类验证轨迹 SFT → GRPO | AppE Table6 | 3B CVBench 83.83；RL-only 75.34 | 未报告 | 支持 |
| litscan:79179 | 领域文本 CoT + 困难 VQA 预热 → zoom GRPO | Table4; §3.1–3.2 | pass@1 50.01→60.40、pass@32 82.58→96.25；一般 GRPO 不稳定优于 SFT，域知识仅 RL 注入可退步 | 记录未覆盖 | 支持 |
| litscan:52782 CPathAgent | 未训练的 Gemini 直接套 agent 模板 | Table A6 | 72.1→65.4（模板本身不保证收益） | 记录未覆盖 | 支持（prompt 不能代替训练） |
| litscan:64855 VISTA-Gym | SFT 后 GRPO | Table2 | InternVL3-8B 总均分 57.49→71.14；SFT +3.46、RL 再 +10.19 | 记录未覆盖 | 支持（SFT 是 RL 增益前提） |
| litscan:77773 LongGT | rich CoT SFT 后 DPO/GRPO | Table11; Table4 | SFT .716 → +GRPO 70k .757、129k 退至 .746；SFT+GRPO NiEH 39.10 低于 SFT 48.24 | 记录未覆盖 | 支持且提示过量 RL 退化 |
| litscan:56056 SimpleVGC | 146K 工具轨迹（reuse/zoom_in/focus_area）masked CE SFT，无 RL | Table1; Table6; §4 | V* 77.5→90.4，HR4K 68.8→76.2；记录 checked："工具数据比同题原始数据有效" | 记录未覆盖 | 支持（SFT 侧：行为示范而非同题 QA 带来增益） |
| litscan:77746 VisDeep | 视觉搜索 + 文本 deepresearch 桥接的长程轨迹 SFT → GRPO | Table4 p8 | 30B agent 平均 40.9→SFT 54.5→RL 56.9 | 记录未覆盖 | 支持：RL 增益建立在 SFT 造出的长程重试支持上 |
| 边界：litscan:72124 DeepEyes | 无冷启动 SFT，依赖 Qwen2.5-VL 原生 grounding + GT 区域可解过滤 | Table5 p8 | 条件 bonus 版 V*/HR4K/HR8K 90.1/75.1/72.6 | 记录未覆盖 | 边界：原生能力在时 RL-only 可行 |

## 成功条件 / 失败模式

- 成功条件：示范覆盖的行为在 RL 中被重新加权（litscan:70410、litscan:63682）；示范行为必须与终答正确性可分（2503.01307 用错误答案行为 priming 仍有效）。
- 失败模式 1：SFT 本身可能降分。litscan:63682 SFT 的 V* 71.7 低于 base 74.6（Table3 p7）；litscan:51030 warm-start InfoVQA 74.3 低于 base 80.7（Table1/§5.2）。冷启动收益只在后续 RL 管线下成立（2507.03019 SFT-only 58.5 低于 base 61.8，Table4 p6）。
- 失败模式 3：过量 RL 使 SFT 的跨域收益退化（litscan:77773 Table4）。
- 失败模式 4：冷启动只在示范的工具组合上有效，新工具可能出现刚性（litscan:72663 Table5 p8：推理时新增 A* 使 reflection 模型 91.36→68.55）。

## 审稿期望

记录中各篇 reviewer_concern 均为 low_evidence，以下为**推断**：
- 要求 RL-only 消融在同数据量、同步数下进行，并报告行为频率而不只报准确率（多数成员只报准确率）。
- 要求区分"格式熟悉"与"行为能力"：只给格式示范的对照（如 litscan:74330 的 OMS-only）。
- 要求报告种子数；本卡成员多数记录"未报告"。

## 认知障碍

- 普遍假设 RL 能"探索出"新行为；pass@1 提升被误读为能力扩展（2504.13837 的论点，见 PC-F3-02）。
- 2503.01307 的反直觉点：错误答案的行为示范也能 priming，说明种下的是行为先验而不是答案知识，因此"只收答对轨迹"的构造并不是必要条件（rs.why_non_obvious）。
- DeepEyes（litscan:72124）的 RL-only 成功让人误以为工具行为可以从零 RL 出来；其前提是原生 grounding 能力与可解样本过滤。

## 工程经验

- 当新工具比原生能力复杂时，纯 RL + 工具奖金会退化为占位调用，应先用执行核验的教师轨迹冷启动（litscan:71722 Table5 p7）。
- 当 SFT 后单独评测掉分时，不要直接判冷启动无效，应在同一 RL 预算下比较（litscan:63682 Table3、2507.03019 Table4）。
- 当做冷启动消融时，加"等长占位"对照，排除长度本身的作用（2503.01307 §3.1）。

