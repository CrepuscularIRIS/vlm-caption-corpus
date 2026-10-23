---
id: PC-F3-13
name: 按同组内是否存在"更保守/更便宜且答对"的样本，切换各动作的奖励
family: F3_support
status: candidate_pattern
problems: {P02: 3, P06: 3, P03: 2, P29: 2, P28: 2}
members: [2604.22779, "litscan:76860", "litscan:63682"]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

同一题的 G 条 rollout 先按动作类型分组（答/弃答；搜索/不搜索；用工具/不用工具），再按组内统计切换奖励：
- KARL（2604.22779 Eq2–3）：$I=\mathbf 1[\exists i:\mathrm{correct}(o_i)]$；I=1 时 $(r_T,r_U,r_F)=(1,-1,-1)$，I=0 时 $(\text{N/A},1,-1)$。即组里有人答对，弃答与错答同罚；没人答对，弃答得奖。
- MASH OTC-Strict（litscan:76860 §2.2.2）：组内存在零搜索的正确样本时，搜索轨迹的 $r_{help}=0$；否则沿用 OTC。
- CodeVision（litscan:63682 Eq3）：$r_{nec}=\max(0,\bar r^{acc}_{G_{tool}}-\bar r^{acc}_{G_{notool}})$，为正且无工具成功≤1 时奖励成功使用工具的轨迹。

## 信息

- 同 prompt 的 G 条当前策略 rollout 的终答正确性与动作类型（KARL G8；MASH G16；CodeVision K8）。
- 不需要预标的"该不该用"标签，但需要组内**同时采到**两类动作。
- 不是同状态随机干预：自选 tool 与 no-tool 的成功率差不是因果必要性（litscan:63682 FAIL）。

## 成立条件

- 组内"有人答对"被当作"可答"的代理；采样组无正确不代表真实无能力（2604.22779 FAIL）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2604.22779 KARL | StageI 一半题 binary 一半 KAR；StageII 全 KAR | Tables1,3; Eq2–3; B Eq6 | NQ Llama8B 正确 38.7→42.7、幻觉 55.3→16.7；去 StageII 正确 50.6 但幻觉 31.4；α100% 时 StageII 无法恢复弃答（U=0） | 记录未覆盖 | 支持；依赖支持保护 |
| litscan:76860 MASH | 随机 0/1/2 搜索 warm-start + OTC-Strict | Table1 p5; Table4 | HotPotQA Acc 53.32 / TC 1.10 / TP 32.55，OTC 44.76 / .81 / 28.64；去 warm-start strict 26.97 / 0 / 26.97；NQ 精度 56.37 低于 OTC 58.91 | 测试每题 4 samples | 支持；准确率非劣未证明 |
| litscan:63682 CodeVision | 必用工具 1/N、crop 最佳 IoU 增量、可选工具 r_nec | Table3 p7; §3.3.2 | 去 strategy 后 MVToolBench 60.1→50.7；去 penalty 55.9 | 记录未覆盖 | 支持组合奖励；r_nec 单项未消融 |

## 成功条件 / 失败模式

- 成功条件：组内两类动作都有样本，组条件奖励给出"更便宜且同样答对"的方向。
- 失败模式 1：支持一旦归零就无法恢复（2604.22779 α100%；litscan:76860 无 warm-start 时 TC=0）。
- 失败模式 2：StageII 牺牲部分正确率（2604.22779 Tables1,3：正确 50.6→42.7；TriviaQA 71.6→67.9）。
- 失败模式 4：成功样本调用数相同时奖励相同，组相对优势为 0（litscan:76860 DEGEN）。

## 审稿期望

推断：要求分层报告（组内有/无正确样本两类题）；要求去掉支持保护阶段的消融（KARL α100% 已做）；要求准确率非劣界（MASH、KARL 都有准确率下降）。

## 认知障碍

- 错答+弃答组中只要弃答奖励更高，std 归一化就会持续强化弃答；光缩小弃答奖励幅度不能消除方向偏差（2604.22779 rs.why_non_obvious）。这正是我们 P01/P02 的镜像。
- 直接奖励求助/工具会塌到 always help；把"有便宜正确样本"作为条件才给出方向（litscan:76860）。

## 工程经验

- 当组条件奖励依赖"组内有某类样本"时，先统计每步满足条件的组比例；比例接近 0 时奖励改动等于没做（litscan:76860 FAIL）。
- 当用分阶段 schedule 保支持时，阶段切换是固定的，不是按边界事件自动切换（2604.22779 PIT）。

