---
id: PC-F3-04
name: 按随机或均衡模式造 warm-start 数据，只为保住各模式的初始支持，不按需求打标签
family: F3_support
status: candidate_pattern
problems: {P29: 3, P25: 2, P21: 2, P06: 2}
members: ["litscan:76860", 2606.02871, 2512.16883]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

构造 warm-start 时，不判断每题"该不该用工具"。对每题随机指定行动次数或模式（如 0/1/2 次搜索；每 turn 等概率 latent/explicit），只要求轨迹格式正确，用于让 RL 起点在各模式上都有非零概率。随后用含效率项的 RL 选择模式。

## 信息

- warm-start 不需要学生知识边界的标签（litscan:76860 rs.why_non_obvious："不需要先标注学生知识边界；warm-start 允许 35% 错误，其目的为行动多样性"）。
- RL 阶段：每题 G 条轨迹的正确性与调用次数（litscan:76860 SIG：G16）。

## 成立条件

- 有一个 RL 阶段负责把多样的初始支持变成状态相关的选择；warm-start 本身不教"何时用"。
- 效率奖励只在组内存在相应模式的样本时才起作用（litscan:76860 FAIL："strict 成功依赖组中出现正确无搜索样本"）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:76860 MASH | Qwen2.5-32B base 按随机 0/1/2 次搜索生成，1000 题 warm-start，再 OTC-Strict RL | Table1 p5; PIT 字段 | HotPotQA Acc 53.32 / TC 1.10 / TP 32.55；去 warm-start 的 strict 变 26.97 / 0 / 26.97 | 测试每题 4 samples，训练种子未知 | 支持：没有多样初始支持，RL 塌到 0 搜索 |
| 2606.02871 ALAR | action-anchored latent SFT 后，每 turn 等概率 latent/explicit 的 20K warmup，再 AR-GRPO | Table2 p7; notes | BFCL 平均 86.1/760 tokens → Stage2 89.2/117；search7B 42.7/236→41.7/133（EM −1） | 记录未覆盖 | 支持：只做 latent SFT 会压掉 explicit 支持，warmup 修复 |
| 2512.16883 AdaSearch | stage1 对同题分别用有/无 search 的 prompt 形成两组训练两模式；stage2 再学决策 | Table2 Qwen2.5-3B block; notes | 平均 EM 36.0 / F1dec 54.0；Search-R1 EM 38.1 / F1dec .1 | 记录未覆盖 | 支持（先分别训练两种能力），但有 EM 折衷 |

## 成功条件 / 失败模式

- 成功条件：RL 起点两种模式都有正概率，且效率奖励能在组内比较（litscan:76860）。
- 失败模式 1：warm-start 只给初始支持，没有持续强制；oracle helper 下 50 步内 always help（litscan:76860 Table4/§4.5）。
- 失败模式 2：效率换来准确率下降：litscan:76860 NQ 精度 56.37 低于 OTC 58.91（Table1）；2606.02871 search EM −1（Table1）；2512.16883 EM 36.0 低于 Search-R1 38.1。
- 失败模式 3：允许错误示范（35%）在代码/QA 中可行，在视觉 caption 上未验证（litscan:76860 TRANSFER 字段）。

## 审稿期望

推断：要求去 warm-start 的消融（MASH 已做）、要求报告各模式频率曲线、要求准确率非劣检验（三篇都有准确率下降，均未做非劣检验）。

## 认知障碍

- 通常认为 warm-start 数据要"对"、要按需求选择；MASH 的做法是按随机次数、只追求行为多样性（M12："应该确保你的轨迹有一些 diversity"）。
- 只做单一模式的 SFT（如 latent-only）会压掉另一模式的支持，这一点在 2606.02871 中被专门识别（rs.why_non_obvious）。

## 工程经验

- 当效率奖励只在"组内存在无工具正确样本"时生效时，先确认 warm-start 后每组的无工具样本数，否则 strict 奖励不触发（litscan:76860 FAIL 字段）。
- 当把模式选择与解题分阶段训练时，记录标签生成用的 checkpoint 与 prompt，标签会随训练过时（2512.16883 notes）。

