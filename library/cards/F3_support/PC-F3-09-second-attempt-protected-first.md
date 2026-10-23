---
id: PC-F3-09
name: 以首答（或错误前缀）为条件在线训练二次尝试，首段分布受保护，并按正确性转移重配平样本
family: F3_support
status: candidate_pattern
problems: {P27: 3, P26: 2, P61: 2, P25: 2}
members: [2409.12917, "litscan:77335", 2502.02508]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

把一次回答拆成"首段 o1 → 二次尝试 o2"。训练时：
1. 只对 o2 计算策略梯度，o1 只受 KL 约束或冻结（SCoRe Stage I 对第一轮强 KL；Octopus Stage I 冻结 o1 的 PG、保留 KL）；
2. 第二阶段才放开 o1，但只放开 o1、o2 正确性一致的样本（Octopus Stage II）或只用即时奖励不回传（SCoRe γ=0）；
3. 稀缺的"错→对"样本通过组内重组（Octopus 拼 o1_i 与 o2_j）或从旧前缀重启（Satori）补足，并按四种正确性转移配平。

## 信息

- 当前策略自己的 rollout 与 GT 正确性（2409.12917 INFO：训练 GT/答案 checker，测试只有自己的前答案 + 固定纠错指令）。
- Octopus 冷启动混采含强模型 GT 辅助（litscan:77335 INFO）；Satori 的重启前缀来自 FT 模型（2502.02508 INFO）。
- 不使用冻结读者或价值估计。

## 成立条件

- 协议中存在可识别的"首段/二次尝试"边界（<sc> 标记、第二轮、reflect token）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2409.12917 SCoRe | Stage I：第一轮强 KL、第二轮正确奖励；Stage II：r̃2=r2+α(r2−r1)，α=10，γ=0 | Table2; §5.2/A.2/Table5; Eq3–4 | MATH t1/t2 60.0/64.4，净 +4.4；base 52.6/41.4（净 −11.2）；正确改错 15.8%→1.4%；HumanEval t1 53.7→52.4 | 记录未覆盖 | 支持；首轮仍可能小降 |
| litscan:77335 Octopus | 同题 o1_i 与 o2_j 重组，补至 16 并优先 wrong→correct；Stage I 冻结 o1 PG、Stage II 只放开一致对的 o1 | Table3; Eq3–6; §4.2/Fig5 | 平均 71.7；无增广 67.4；随机增广 68.6；无 Stage I 69.8；SFT-only 63.4；纯 shaping 奖励出现 reward hacking | 记录未覆盖 | 支持 |
| 2502.02508 Satori | FT 轨迹的正确/错误前缀回退至多 2 步作为新初始状态，PPO；r_bonus=±β | Table7; Table6; §4.2; E.4 | 有 RAE MATH500 85.6 / AMC 67.5，无 RAE 81.6 / 57.5；β=0 的 Olympiad 48.9 反优于默认 46.6；在线 restart 多数是正确前缀，缺错误恢复学习（E.4） | 记录未覆盖 | 支持重启；bonus 非全面改善 |

## 成功条件 / 失败模式

- 成功条件：首段被保护，避免"先故意答错再改"（litscan:77335 rs.why_non_obvious）；错误前缀被显式保留，否则在线训练里成功样本淹没纠错状态（2502.02508 LESSON）。
- 失败模式 1：只加纠错奖励会诱发 reward hacking（litscan:77335 §4.2/Fig5）。
- 失败模式 2：首轮准确率仍可能小降（2409.12917 Table3 HumanEval 53.7→52.4）。
- 失败模式 3：只训练两次尝试，更多轮可能分布漂移（2409.12917 §7/A.1）。
- 失败模式 4：拼接样本不是在新前缀下真实采样（litscan:77335 FAIL），离策略。
- 失败模式 5：纠错固定触发，与"按需补看"仍有差距（litscan:77335 relevance P26）。

## 审稿期望

推断：要求报告错→对与对→错（2409.12917 已报）；要求首轮准确率单独报告；要求与"不重组/随机重组"对照（Octopus 已做）。

## 认知障碍

- "两次都答对"与"真正改错"同样能拿满分，模型容易学成不改（2409.12917 rs.why_non_obvious）。
- 同一序列奖励对错误前缀和正确后缀含义冲突（litscan:77335 rs.why_non_obvious）。
- 在线 restart 越来越偏向正确前缀，必须分开存正确/错误前缀（2502.02508 rs.why_non_obvious）。

## 工程经验

- 当多轮奖励存在"先错再改"激励时，核清未来奖励是否回传前轮；写成 sum 不代表实现了跨轮 reward-to-go（2409.12917 PIT）。
- 当做在线重启时，正确/错误前缀分开存，并与原题合并采样（2502.02508 SIG）。
- 当重组样本时，o1 的 KL 在 Stage I 仍然保留，不是完全无梯度（litscan:77335 ROUTE）。

