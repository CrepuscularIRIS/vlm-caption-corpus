---
id: PC-F2-19
name: 训练前先用离线参考审计信用信号：同状态动作排序一致性、最终优势符号、收益/伤害分解
family: F2_credit
status: candidate_pattern
problems: {P13: 3, P69: 3, P16: 2, P11: 2, P05: 2, P14: 2}
members: [2606.32034, 2604.02869, litscan:76529, 2502.00271]
rs_patterns: [controlled_diagnostic_design]
---

## 操作

在把任何稠密/局部信用接进训练之前，先离线回答"这个信号排得对不对、最终变成了什么优势"：
- QVal：恢复同一状态，强制候选动作，用参考策略续写估值，对比 dense 分数与参考的排序。标量分数看 global Spearman，排序类方法看 state-local Spearman（2606.32034 §3.1 p5）。
- IRC：按 tier 的判别力校准奖励，并**检查最终的优势 A** 的符号，而不只看奖励（2604.02869 签名；lesson）。
- MED：在同一 checkpoint 上配对评估有/无工具，按无工具成败分层，把净工具增益拆成四项 gain/harm 与 Mass×Policy×Quality（litscan:76529 Eqs2–8）。
- Scaling Flaws：把搜索失败拆成"生成里没有有效候选"与"验证器剪掉了所有有效候选"两类（2502.00271 签名）。

## 信息

- 看得到：参考策略续写（QVal）、组内统计与最终优势（IRC）、同 checkpoint 两协议的输出（MED）、有限续写近似的前缀有效性（2502.00271）。
- 看不到：下游 RL 的收益。QVal 未建立"信号质量 → RL 增益"的定量关系（2606.32034 claimed_effect）。
- 估计者：离线参考；本身不进训练。

## 成立条件

- 参考本身要可信。QVal 的 MVMC 取 max，不是固定策略期望 Q 的无偏估计；对强参考对齐，不等于弱的当前策略可利用（2606.32034 conditions 与 failure_boundary）。
- MED 是协议级记账，不是调用随机化或像素替换的因果效应（litscan:76529 failure_boundary）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2606.32034 | 强制候选 + 参考续写，排序相关性 | §3.1 p5 | 完成 >1.2K 次评估；direct/ranking 类平均最强；简单增加复杂度常无收益 | 无训练 | 成员 |
| 2604.02869 | 奖励判别力校准 + 最终优势审计 | Table7; §7.1 | sparse 68%、dense 54%、hybrid 56.5%、IRC 69.5%；正文把 70% 的 gap 归因于 LR，未严格隔离 | 200 sim | 成员 |
| 2502.00271 | 失败分解为生成 vs 选择 | Table2 | MATH DeepSeekMath 失败中 selection 80.0%、generation 20.0%；GSM8K selection 88.6% | 未运行 | 成员 |

## 成功条件 / 失败模式

- 成功：审计在训练前完成，且有预注册的通过门槛。
- 失败：
  - 低 Q 对齐的探索奖励仍可能有效；对齐不是必要条件（2606.32034 failure_boundary）。
  - MED 中固定初始失败集的纠正质量上升，但当前/持续失败集改善有限（litscan:76529 negative_results）。
  - MED 中 schema-only（禁执行）比 no-schema 准确率低 5.8 / 13.0pp（litscan:76529 AppC / Table3）。
  - 有效前缀是有限 rollout 的代理，不是完美 oracle（2502.00271 failure_boundary）。

## 审稿期望

IRC、MED 为 low_evidence。"推断"：
- 审计门槛要在看结果之前写定；
- 要报告审计信号与下游训练效果的关联（QVal 承认没有建立）。

## 认知障碍

- 把信号质量与训练工程分开；但参考策略和 max-return 标签本身也会改变"质量"的含义（2606.32034 why_non_obvious）。
- 净工具增益不变，可以同时来自收益饱和与伤害减少；失败集的难度会随训练变化（litscan:76529 why_non_obvious）。
- 扩大候选数的同时，也扩大了误排序的风险；有正确候选不等于搜索能保住它（2502.00271 why_non_obvious）。

## 工程经验

- 当 dense 奖励看似合理、表现却下降时，先审最终优势与匹配语义，再锁训练配置，避免把优化器超参的差异归因于信用方案（2604.02869 lesson）。
- deep_equal 排序、数值字符串强制转换、空值处理都会影响 gold 匹配，须按任务语义核对归一化（2604.02869 pitfalls §4.3）。
- 当工具准确率上升时，先对齐同 checkpoint 的无工具参考与固定失败 cohort，并报告 gain 与 harm 两边；不要只看调用率或净差（litscan:76529 lesson）。
- 正文的 checkpoint 计数与附录口径不一致；附录 Eq25 的负面积与 Eq26 直接相加存在符号疑点（litscan:76529 pitfalls）。

