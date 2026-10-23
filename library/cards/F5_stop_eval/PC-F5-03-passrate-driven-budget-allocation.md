---
id: PC-F5-03
name: 按当前策略的组内成功率在训练中收缩或分配预算（用约束代替代价项）
family: F5_stop_eval
status: candidate_pattern
problems: {P32: 2, P33: 2, P01: 2, P06: 1, P35: 1}
members: [2510.10168, 2501.17974]
rs_patterns: [reframe_as_solvable_object]
---
## 操作
不往奖励里加长度/调用代价，而是把"最省且正确率 ≥ C"写成约束问题，用当前策略在每题（或每 batch）上的组内成功率来调整可用预算：
- PALU：上一轮 8 个候选的通过率 ≥ C 时，把该题的长度上限缩小 $a_\tau=Q_1(\text{correct lengths})-Q_{1-\tau}(\text{correct lengths})$；未达标则重置为 $L_{max}$；策略仍用正确性 GRPO 优势 $A_i=(r_i-\mathrm{mean})/\mathrm{std}$（2510.10168 Eqs12–14, Eq1）。概念式 $\min_{\theta,L}\max_{\lambda\ge0}L+\lambda(C-R(\theta,L,q))$（Eq7）。
- IBPO：在"长回答总质量 ≤ q+"的 batch 约束下，把长回答名额分给"长组正确率 − 短组正确率"最大的题，只选正确且经验 KL 合格的回答做 SFT 投影（2501.17974 signatures）。

## 信息
当前策略对每题的组内通过率与正确回答长度（PALU）；长/短两组的采样正确率与对 reference 的样本 log-ratio（IBPO）。全部来自策略自身采样，无外部读者。

## 成立条件
- 每题有足够的组采样估计通过率（PALU 8 候选，2510.10168 information）。
- 约束阈值 C / q+ 预先给定（PALU C=.8；IBPO q+=50%/75%）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2510.10168 PALU | 每题按通过率 bang-bang 缩/重置预算；GRPO 无 KL | Table2；§5.4 | 1.5B 五 benchmark macro pass@1 48.6→56.2，token 10280→3537（−65.6%）；Minerva 26.0→24.2；更大分位数步幅缩得快但稍损准确率 | 记录未覆盖 | 记录未覆盖 |
| 2501.17974 IBPO | batch 级 LP/整数规划分配长回答名额，SFT 投影 | main comparison table（ASV-IuB 行） | MATH500 q+=50% 55.4（+4.14pp，2.16× trials）；q+=75% 57.0（+5.74pp，4.32×） | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 失败模式：
  - 平均提升不保证每任务：Minerva 下降（2510.10168 Table2）。
  - 旧通过率不是保守估计；全错题走重置，p≈0 时重置预算不创造支持（2510.10168 failure_boundary、degenerate_cases）。
  - 全对组 GRPO 优势为 0，但预算仍会缩（2510.10168 degenerate_cases）——行为改变来自截断而非梯度。
  - 训练密度约束不保证测试预算；q+=75% 的最终 checkpoint 几乎全是长回答，失去自适应（2501.17974 failure_boundary）。
  - "trial 倍率"不是总 token 倍率（2501.17974 failure_boundary）。

## 审稿期望
- 记录每题的滞后误差与重置频率；区分"截断学习"和"推理时自然停止"（2510.10168 lesson）。
- 推理时不给预算时行为是否保留（推断：两篇都在训练端控制预算，评测端是否同样受限需写清）。

## 认知障碍
连续 dual 推导只能启发一个 bang-bang 规则；直接控制可生成空间而不加惩罚，与"效率=奖励里扣分"的主流做法相反（2510.10168 why_non_obvious）。资源应给"长比短收益最大"的题，而不是统一按长度扣分（2501.17974 why_non_obvious）。

## 工程经验
- 当以过去成功率缩预算时，应按题记录滞后误差与重置频率，否则无法区分策略学会了还是被截断了（2510.10168 lesson）。

