---
id: PC-F3-15
name: 以"答对"为门槛给行为出现奖金，防止该行为在 RL 中消失
family: F3_support
status: candidate_pattern
problems: {P29: 2, P02: 2, P25: 2, P06: 1}
members: ["litscan:72124", "litscan:79179", "litscan:79554", "litscan:63893", "litscan:53612", 2509.24251]
counter_members: ["litscan:71722", 2507.03019, 2608.02217]
rs_patterns: [structural_prior_encoding]
---

## 操作

奖励 = 终答正确性 + 格式 + 门控奖金，奖金只在答对且轨迹中出现目标行为时给：
$R=R_{acc}+R_{format}+\mathbf 1[R_{acc}>0]R_{tool}$，$R_{tool}>0$ 仅当至少一次裁图（litscan:72124 Eq2/§3.2）。

变体：
- 只要答对且用了工具：$G=S_{ok}+S_{fmt}+\mathbf 1[S_{ok}=1]S_{tool}$（litscan:79179 Appendix A Eq5）；
- 工具正确使用 +.8，过度/非法 −1（litscan:79554 Eqs2–3）；
- 分阶段：先尝试奖，后按答对与成功调用分段（litscan:63893 Eq4–5）；
- 多样性：每个不同调用 +.2，至多 4 次（litscan:53612 A5.3）；
- 格式触发奖金：去掉 latent 起止 token 奖励后退化为纯文本（2509.24251 §4.4）。

## 信息

- 终答正确性与行为是否出现；不看该次调用是否必要。

## 成立条件

- 奖金以答对为门，否则会被空行为刷分（反例成员）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:72124 DeepEyes | 答对且至少一次 crop 得固定 bonus | Table5 p8 | conditional V*/HR4K/HR8K 90.1/75.1/72.6 vs 无 bonus 87.4/53.4/55.4；调用先升后降 | 记录未覆盖 | 支持 |
| litscan:79179 | 答对才给工具奖 | Appendix A Eq5 | 无单项消融数值；PIT："正确条件 tool bonus 与减少不必要 crop 目标可能冲突" | 记录未覆盖 | 弱支持 |
| litscan:63893 ARM-Thinker | 阶段1 尝试奖，阶段2 条件奖 | Table5; 5.5/Figure4 | ARMBench 46.1→64.6；纯准确约 0.7 次调用 77.5%，固定工具奖约 1.15 次 78.5%，本文约 1.12 次 | 记录未覆盖 | 支持维持；但调用不降 |
| litscan:53612 ViGoRL | 多样性奖金保多轮 | Table3; A5.3 | 3B 多轮 81.2，去 diversity 78.0；无 diversity 趋单轮 | 95%CI | 支持；鼓励调用不等于必要性 |
| 2509.24251 LVR | 起止触发格式奖 | §4.4 p.9 | 去掉触发奖后回到纯文本、性能下降（幅度未报告） | 记录未覆盖 | 支持行为维持需要奖金 |
| 反例 litscan:71722 DeepEyesV2 | 纯 RL + tool bonus | Table5 p7 | 退化为单个占位代码块 | — | 无冷启动时奖金被刷 |
| 反例 2507.03019 Look-Back | <back> 格式奖 1 / CoT .667 | §5 p7; Eq3 | Qwen2-VL 以空 <back></back> 拿格式奖 | — | 弱基座刷格式 |
| 反例 2608.02217 VC-Tooler | 存在性奖励 TE | Sec5.4 p.7/Table3 | 四项全降：V* 94.7→93.2、HR 82→79、CX 52.9→52.1、VTC 33.4→33.1 | 无 seed/CI | 只奖存在会伤性能 |

## 成功条件 / 失败模式

- 成功条件：以答对为门，且基座会做该行为。
- 失败模式 1：成功但不必要的调用也得奖金；1 次与 6 次同奖金，无"最少调用"方向（litscan:72124 DEGEN）。
- 失败模式 2：无门或弱基座下被空行为刷分（litscan:71722、2507.03019）。
- 失败模式 3：只奖存在性会降性能（2608.02217 Table3）。
- 失败模式 4：调用率不会降到最少（litscan:63893：约 1.12 次）。

## 审稿期望

推断：要求无奖金消融（DeepEyes、ViGoRL 已做）；要求报告"本来能直答的题"上的调用率（几乎都未报告）；要求说明奖金幅度在 std 归一化下的有效尺度。

## 认知障碍

- 纯终答奖励会迅速放弃视觉动作；单纯调用奖励又不等于有效调用（litscan:72124 rs.why_non_obvious）。
- 固定工具奖金会过用，纯准确性会欠用（litscan:63893 rs.why_non_obvious）。

## 工程经验

- 当工具奖金被引入时，先测有效执行概率与占位 hack（litscan:71722 LESSON）。
- 当成功调用额外获奖时，必须单列"正确无工具"样本与冗余调用（litscan:79554 LESSON）。
- 当成功工具定义不清时，条件奖金仍可奖励冗余（litscan:63893 LESSON）。

