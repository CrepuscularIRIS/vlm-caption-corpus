---
id: PC-F1-07
name: 用当前策略的受控双分支（禁工具 / 强制工具）在线判定题级必要性，再据此给自然 rollout 定价或定号
family: F1_objective
status: candidate_pattern
problems: {P02: 3, P05: 3, P03: 2, P22: 2, P17: 2, P29: 2}
members: [2605.29796, "litscan:60137", 2607.08572]
rs_patterns: [condition_intervention_on_boundary, controlled_diagnostic_design]
---
## 操作
每题额外对当前策略做两组受控采样：一组强制或允许直答，一组强制工具。由两组成功率差给题打标签，再用标签改变自然 rollout 的奖励。

**SAAS**（2605.29796 Eq3–8）
- 每题采 4 条禁搜、4 条可搜，按禁搜成功数 $n_d$ 与可搜成功数 $n_e$ 分三类：
$$S(q)=\begin{cases}\text{NoSearch}&n_d\ge2\\\text{NeedSearch}&n_d=0,n_e>0\\\text{Undetermined}&\text{otherwise}\end{cases}$$
- 奖励：$R_i=F1_i+\mathbf 1[F1_i=1]c_i$。NoSearch 题对每次调用罚 .05·N；NeedSearch 题只罚超过 $N_{min}$ 的部分；Undetermined 题不罚。
- 先只用 F1 训练，等准确率不再改善后才开启代价。

**LookLess**（litscan:60137 Eq5–10）
- 每题 4 条强制工具、4 条禁止工具、8 条自由。
- 必要性：$N=\mathbf 1[acc_{tool}>acc_{no\,tool}]$。
- 自由 rollout 按"正确 × 是否与 N 匹配"四格给 $r_{align}=(+1.6,+1.2,-0.8,-1.0)$，再加一致性惩罚 $-0.1\mathrm{Var}(\mathbf 1_{zoom})$。

**Switch-Reasoner**（2607.08572 Sec.3.5 Eq16/17）
- 强制 direct、强制 think 各 $K=4$ 条。
- 打标：$\Delta\ge.5$ 记 must-think；$s_{direct}\ge.75$ 且 $\Delta\le-.25$ 记 safe-direct；其余记 uncertain。
- 自然 rollout 匹配标签 +.03，不匹配 −.03，然后整组 mean/std。

## 信息
- 当前策略在两种受控条件下的 GT 成功率。
- 由谁估计：策略自身。但每支只有 4 个样本，标签粒度是 .25。

## 成立条件

| 论文 | 受控分支的去向 | 记录出处 |
|---|---|---|
| SAAS | 禁搜分支自成一组计算优势并参与训练，不只是打标 | 2605.29796 signal_routing |
| LookLess | necessity 8 与 adaptive 8 都进入更新 | litscan:60137 signal_routing |
| Switch-Reasoner | 2K 条 forced-route 轨迹只用于打标；原文"未写将 forced-route 轨迹加入 GRPO" | 2607.08572 signal_routing |


**其他条件**

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.29796 | 4 禁搜 + 4 可搜，三分类，边界定价，两阶段 | Eq3–8/B.1；B.3 Table4；§4.5 | 与 matched GRPO 比：7B ACC 50.2→48.7、SC 2.94→.97；3B 46.5→45.8、SC 2.26→1.13；δ=1 时 SC 1.05、ACC 43.1，低于默认的 45.8 | 未报告 | 支持减调用；准确率 −0.7~−1.5pp |
| litscan:60137 | 4 + 4 + 8，四格对齐奖励 | Eq5–10/TableA2；Table1 p6；Table3 | 五任务平均 74.9 vs PixelReasoner 74.1，工具比例 36.0% vs 65.4%；HR4K 73.4/20.1%；全不用工具 72.4、全用工具 72.5 | SFT seed 49；RL 多 seed 未报告 | 支持 |
| 2607.08572 | K=4 双模式打标 ±.03，加全局控制器 | Sec.3.3–3.5；Table1 p7；Table4 p18 | 4B 70.79→71.60，think 85.73%→51.53%；8B 72.00→72.22，think 30.25%→37.73%；放宽 safe-direct 后 4B 68.32、think 13.28% | Table1 有 ±（4B 70.79±.68）；完整方法 seed 未报告 | 支持路由分化；仍是 think/direct，不是 crop |

## 成功条件 / 失败模式
**成功条件**
- 策略能遵循强制或禁止指令。
- 题目中确有"直答够用"与"必须看"两类，且分支成功率差够大，大于 K=4 的标签噪声。

**失败模式**
- 减调用伴随掉点：SAAS 3 个尺寸平均分别 −.7、−1.5、−.8pp（2605.29796 Table4）。
- 两分支打平或都错，一律记为 no-tool（N=0）。4 次采样可能误判（litscan:60137 degenerate_cases）。
- 宽松的 safe-direct 标准让思考率大降，同时 score 也降 3.28pp（2607.08572 Table4）。
- K=8 不比 K=4 好，权重也不单调（2607.08572 negative_results）。
- $n_d=1$ 时，即使可搜成功也记为 Undetermined（2605.29796 degenerate_cases）。
- 强制与自然 prompt 上下文不同，标签与自然路由之间的可迁移性没有校准（2607.08572 pitfalls）。
- 一致性惩罚是组内共享标量，组中心化后可能被抹去（litscan:60137 OBJ.invariance）。

## 审稿期望
- 记录均为 low_evidence。
- 推断的要求：
  - 打乱标签对照：分支标签是否真的承重（2607.08572 failure_boundary："未用打乱标签/同 think 率常数偏置对照证明逐题信号承重"）；
  - 标签分半一致率；
  - 预设的非劣界。

## 认知障碍
- 统一减调用会惩罚必要探索；成功最少调用只是组内充分路径的上界（2605.29796 why_non_obvious）。
- 全局维持两种模式，不等于逐题选对；强制分支看得到稀有路线的表现，却不自动给主策略提供梯度样本（2607.08572 why_non_obvious）。

## 工程经验
- 当按必要性收费时，边界要与当前策略同步，并分别报告搜索压缩与准确率损失。不能用较弱的文献基线掩盖 matched 对照（2605.29796 lesson）。
- 当用受控分支监督自由分支时，应把三种来源区分开：提示变化、采样噪声、梯度支撑收益（litscan:60137 lesson）。
- 应把 natural 主组与 forced 测量分支分开记录：有效与无效计数、逐题标签、控制器前后的奖励（2607.08572 lesson）。

