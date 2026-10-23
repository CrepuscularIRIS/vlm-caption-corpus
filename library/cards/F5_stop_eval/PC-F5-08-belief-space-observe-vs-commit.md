---
id: PC-F5-08
name: 把"再观察还是作答"写成信念状态上的决策：观察值 = 任务收益 + 期望信息增益 − 观察成本
family: F5_stop_eval
status: candidate_pattern
problems: {P33: 3, P34: 2, P19: 2, P31: 1}
members: [2607.16981, 2504.03245]
rs_patterns: [algebraic_equivalence_unification, structural_prior_encoding]
---
## 操作
维护对隐藏答案的信念 $b$，观察动作只用于未知部分；在信念树上比较"观察"与"承诺"：
- EFE（ρ-POMDP）：$I_a(b)=H(b)-\mathbb E_oH(b'_o)$，$V(obs_a,b)=-c_a+I_a(b)+\mathbb E_o\max_{a'}V(a',b'_o)$，$V(commit_i,b)=\mathbb E_bR_i$；ρ(obs)=期望熵减，ρ(commit)=0，权重 w=1（2607.16981 Eqs3–5，Props1/3）。
- Seeing is Believing：VLM 把谓词判为已知真/假/未知；PDDL 观察动作只对未知谓词可用；乐观确定化后执行，不符预期就重规划（2504.03245 rs.key_step）。

## 信息
真实 transition/observation likelihood、信念、成本、奖励（EFE，无 LLM）；VLM 当前多相机图像给出的三值谓词 + 人工动作前后置条件（Seeing is Believing）。

## 成立条件
- 观察不改变隐藏状态（静态 hidden state）；观测模型已知；同 horizon 比较（2607.16981 conditions、failure_boundary）。
- 动态确定、感知准确（2504.03245 failure_boundary）。
- 奖励单位与信息单位（nat/bit）一致或经过校准（2607.16981 invariance、lesson）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2607.16981 EFE | 精确 Bayes 树搜索，R + 期望信息增益 | Table4 p12；Table7；§5.4/6 | Diagnosis 97.1%/−1.50 vs Planning 89.2%/−2.37；Inspection N16 w5 在准确率 91.4/奖励 −43.51 双胜 w1 86.1/−45.71；N8 EFE −20.60 差于 Planning −17.85；γ=.90 时 Diagnosis 优势反转 −1.6pp | core 5 seeds；RS 11,11 仅 2 seeds | 记录未覆盖 |
| 2504.03245 Seeing is Believing | 三值信念 + 观察算子 + 重规划 | TableI p7 | 10 seeds Drawer success 80%/SPL .32±.16，SortWeight 70%/.46±.32；caption+LLM 分别 10%/0% | 10 seeds | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：观测模型已知、观察不改变世界、信念可精确更新。
- 失败模式：
  - 观测模型未知、动作改变隐藏状态、低 γ 时等价与收益主张都不成立（2607.16981 failure_boundary）。
  - w=1 不是普遍最优：Inspection N16 时 w=5 双胜（2607.16981 Table4/7）；"按 success 调出的 w 与按 reward 调出的 w 不同"（2607.16981 pitfalls）。
  - 纯 IG 无任务收益会随机提交（2607.16981 degenerate_cases）。
  - EFE 记录中 Table4 部分奖励与正文 bootstrap 点估计不一致（2607.16981 negative_results）。

## 审稿期望
- 先写清信念、观察是否改变世界、奖励单位与优化指标，不能用系数 1 代替校准（2607.16981 lesson）。
- 与非信念基线在同 horizon、同成本下比较（推断，自 2607.16981 conditions）。

## 认知障碍
代数等价依赖"观察不改变隐藏状态"这一特定结构；不能把 nat 尺度默认等同任意任务奖励数值（2607.16981 why_non_obvious）。保留"未知"而不是硬猜状态，规划器才会主动选择观察（2504.03245 why_non_obvious）。

## 工程经验
- 当把信息单位从 nat 改为 bit 时，需要同时缩放任务收益项（系数 ln2），否则权衡改变（2607.16981 invariance）。
- 当用搜索评估所有动作时，评估成本不等于执行成本，二者要分开列（2607.16981 pitfalls）。

