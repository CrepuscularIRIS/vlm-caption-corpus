---
id: PC-F5-02
name: 在预算边界把"不可执行的继续"改写成一次可评分的强制作答
family: F5_stop_eval
status: candidate_pattern
problems: {P33: 2, P31: 2, P17: 2, P15: 2, P11: 1}
members: [2607.14547, litscan:50558, 2510.05069]
rs_patterns: [heterogeneous_decomposition, generative_process_redesign]
---
## 操作
当轨迹到达预算边界（轮次上限、token 截断点、模式切换上限）时，不把它记错或 mask 掉，而是回到最后一个可执行前缀，加一段"必须作答"的控制前缀，再生成一个终答并按正确性评分；训练时这个终答的结果优势回传给之前的搜索 token（AdaTurn 默认），或对每个截断前缀单独训练答案摘要（BRPO）。这是改变边界处样本分布的**包装器**，不是学出来的停止。

## 信息
- 评分：GT 正确性（AdaTurn 用 Qwen3-32B 按 GT 语义判，不看图，2607.14547 information）；BRPO 用 GT verifier 在多个预算截断点打分（litscan:50558 Eqs3,6）。
- SwiReasoning 为推理期：熵趋势决定显式/隐式切换，切换计数达上限即注入结束信号（2510.05069 rs.key_step）。

## 成立条件
- BRPO：同一前缀派生多个答案时用 tree attention/cache 并 mask 插入的提示 token（litscan:50558 signal_routing、lesson）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:50558 BRPO | 在预算截断点分支 summary；思考 token 拿 future-budget 回报 $R_t=\sum_{j\ge j_t}P_j r_\phi(x,z_{\le b_j})$ 减混合基线；summary 单独分组 | Eqs3,6–9；AppendixD Tables1–2 | final 8000 token macro AR_base 52.7 vs GRPO 50.7；anytime 32 档 AR_uniform 46.0 vs 43.0；AR_base 的 anytime 44.9 低于 uniform 46.0 | 记录未覆盖 | 记录未覆盖 |
| 2510.05069 SwiReasoning | 推理期：熵下降转显式、上升转隐式；切换上限触发作答 | Table1 | Qwen3-8B math/STEM avg 78.91→80.94；Qwen3-1.7B 60.20→62.88；过强 exit bias 使 AIME24 降到 8.33% | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：边界处原本被截断、无答案的轨迹占比不小，且已收集证据可答。
- 失败模式：
  - 强制有答案不保证正确：AdaTurn AppH/Fig12 中模型锚定错误的人后幻觉作答（2607.14547 negative_results）。
  - 过强的结束干预严重掉点（2510.05069 AIME24 8.33%）。
  - 额外 format reward 轻微有害，AdaTurn 默认置 0（2607.14547 AppC p.13）。
  - BRPO 的预算目标存在权衡：final 与 anytime 指标不能同时最好（litscan:50558 AppendixD）。
  - 全对/全错组 std=0、分子=0，强制作答只有在组内产生对错差时才增加学习信号（2607.14547 degenerate_cases）。

## 审稿期望
- 把被丢弃的工具 token、强制 prefill、自然终答分别计费，不能只记"最终有效轮数"（2607.14547 lesson）。
- 区分训练收益与推理包装器收益（推断，自 2607.14547 Fig7 claimed_effect："不能从该整体比较独立量化"）。
- 区分"截断学习"和"推理时自然停止"（2510.10168 lesson，见 PC-F5-03）。

## 认知障碍
直觉是把预算耗尽记为错或直接 mask；但这样边界状态永远得不到可答样本，策略学不到在边界前收束（2607.14547 why_non_obvious）。同一前缀可廉价派生多个答案，这一点在 GRPO 的"整条轨迹一个奖励"框架下不显然（litscan:50558 why_non_obvious）。

## 工程经验
- 当预算边界回滚并重新生成终答时，被丢弃的工具 token、强制 prefill、保留的历史图像、自然终答各自的 mask/logprob 必须对齐，否则 actor 打分与采样分布不一致（2607.14547 lesson）。
- 当一个前缀派生多个答案时，应使用 tree attention/cache 并 mask 插入的提示 token，避免重复计算长前缀（litscan:50558 lesson）。
- 当强制作答 prefill 以未闭合 `<think>` 的第一人称文字实现时，要核对它在训练中被当作 prompt 还是 action（2607.14547 signal_routing）。

