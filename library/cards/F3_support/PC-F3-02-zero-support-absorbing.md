---
id: PC-F3-02
name: 把行为支持当作可测状态量：RL 前测 pass@k 覆盖，RL 中监测动作频率，频率归零视为不可逆
family: F3_support
status: candidate_pattern
problems: {P29: 3, P25: 3, P21: 2, P61: 2, P28: 1}
members: [2504.13837, "litscan:75826", 2604.22779, "litscan:76860", "litscan:51030", "litscan:61931", "litscan:76968", 2607.10738, "litscan:70300"]
rs_patterns: [controlled_diagnostic_design, reframe_as_solvable_object]
---

## 操作

1. RL 前：在同一模板下用较大 k 采样，比较 base/SFT 与 RL 后的 pass@k 及"可解题集合"，判断目标行为是否在支持内。
2. RL 中：逐步记录每种动作（直答 / 裁图 / 弃答 / 改口）的频率。频率一旦掉到 0 附近，就把它当成吸收态：之后任何只作用于已采样动作的奖励或优势改写都不会把它拉回。

## 信息

- GT 验证器给出的终答正确性；有限 k 的经验覆盖（2504.13837 Table2 p8）。
- 理论层面：每个 prompt 的生成模式视为 categorical bandit，用总体 mean/std 代替有限组统计（litscan:75826 §4.3）。
- 看不到"严格零概率"；有限 k 未出现不等于 p=0（2504.13837 FAIL 字段；litscan:76968 PIT：0/128 的题换种子 pass@32 仍有 7.5%）。

## 成立条件

- 策略梯度类方法（GRPO/RLOO/PPO），奖励只作用于被采到的样本。
- 单模型、动作共享参数；litscan:75826 的理论只覆盖逐 prompt 独立 bandit、block-symmetric 噪声、无限小步（§3、§7），共享参数情形未被理论覆盖。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2504.13837 | base vs RL 的 pass@k（k 到 128/1024）与覆盖集合 | Table2 p8 | AIME k1024：双方 63.3%、仅 base 13.3%、仅 RL 0%；MATH500 k128：双方 92.4%、仅 base 3.6%、仅 RL 1.0% | 记录未覆盖 | 支持：RLVR 主要重排已有支持 |
| litscan:75826 NoisyVR | 二值噪声验证器下的模式质量 ODE | §4.3 Thm4.2; Eq3–5; Table1 | J>0 时坏模式质量趋 0，J<0 趋 1；初始好模式质量为 0 不能自举（吸收态）；Qwen2.5-3B 两 epoch J=−.1 pass@1 .16%、J=0 13.4%、J=1 20.8% | 5 seeds | 支持（理论 + 实验） |
| 2604.22779 KARL | 两阶段：StageI 一半 binary 一半 KAR，StageII 全 KAR | §4.5/Table3 | α100%（不混 binary）时 StageII 无法恢复弃答，最终 U=0 | 记录未覆盖 | 支持：弃答支持归零后不可恢复 |
| litscan:76860 MASH | 去掉随机行为 warm-start；改用 oracle helper | Table1 p5; Table4/§4.5 | 去 warm-start 后 strict 变 26.97/0/26.97（Acc/TC/TP）；oracle 版每个 run 50 步内变成 always help；Ternary 25 步内全拒答（§3.2） | 测试每题 4 samples，训练种子未知 | 支持：坍塌发生在几十步内 |
| litscan:51030 Pixel Reasoner | 去掉 curiosity bonus | §3–5/Table1/AppC | 工具率约 .55→0（240 步）；无 SSR 时 reward uniformity 达 90%（AppC.3/Fig9） | 未给主表多 seed | 支持 |
| litscan:61931 Glance-or-Gaze | SFT 含 43.5% 无搜索 → 难例 GRPO | Figure3 | 无搜索比例 Qwen3 9.0→2.7%，Qwen2.5 30.4→2.9% | 记录未覆盖 | 支持：SFT 支持被 RL 侵蚀 |
| litscan:76968 SOAR | 0/128 失败题的支持判断 | AppC.2; KF 字段 | 0/128 是采样筛选，base 新 seed pass@32 仍 7.5%，不是严格 p=0 | 多 teacher/student seed | 边界：有限采样不能证明零支持 |
| 2607.10738 | 从零 RL 用静态正拒答奖励 | notes（AppB/§2.3） | 静态 .05 拒答奖励即 99.9% 拒答（记录 known_failure_check 字段） | 记录未覆盖 | 支持：反方向也会塌 |
| litscan:70300 | 50% 不可答训练 | §6.4 | 塌缩为 always-abstain | 记录未覆盖 | 支持 |

## 成功条件 / 失败模式

- 失败模式 1：有限 k 覆盖被误当作能力上界（2504.13837 FAIL 字段：v5 承认新交互/课程可突破当前设置）。
- 失败模式 2：J>0（整体奖励方向正确）仍可能在好模式内部出现集中塌缩，"保准确"不等于"保多样性"（litscan:75826 DEGEN 字段）。
- 失败模式 3：同一 J 下不同噪声结构在有限步内结果不同（litscan:75826 Table1：J=.3 时 FPR0/FN.7 为 16.0，FPR.7/FN0 为 14.6）。

## 审稿期望

推断（记录无审稿）：
- 要求说明 pass@k 的 k、温度、模板是否与训练一致（2504.13837 COND 字段）。
- 要求用独立种子重估"0 次出现"的题，避免把采样失败当零支持（litscan:76968）。

## 认知障碍

- pass@1 提升会掩盖高 k 覆盖的下降（2504.13837 rs.why_non_obvious）。
- 噪声总率不能决定方向，TPR−FPR 才决定；而且正确模式内部的多样性是另一回事（litscan:75826）。
- 很多方法默认"加奖励就能把行为拉回来"，但奖励只作用于被采到的样本（litscan:51030 FAIL："采不到工具时 bonus 无支持"）。

## 工程经验

- 当效率奖励把策略推向单一行为时，几十步内就会塌缩（litscan:76860 §4.5：50 步内 always help），应在训练早期每步记录动作频率，而不是只看最终 checkpoint。
- 当用 0/k 判定"不可解"时，换种子重采一次（litscan:76968）。
- 当使用 GRPO 时，统计全同奖励组比例（litscan:51030 AppC.3 无 SSR 时达 90%），这部分组不提供任何梯度。

