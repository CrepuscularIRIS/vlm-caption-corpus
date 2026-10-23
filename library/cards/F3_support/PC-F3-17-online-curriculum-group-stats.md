---
id: PC-F3-17
name: 用训练中的组统计（|A|、正确率、行为占比）在线调度题目采样比例
family: F3_support
status: candidate_pattern
problems: {P65: 3, P06: 2, P07: 1, P61: 1}
members: [2505.14970, "litscan:71725", 2601.06860]
rs_patterns: [reframe_as_solvable_object]
---

## 操作

把题目按类别/难度分臂，用当前训练产生的统计更新各臂的采样概率：
- SEC（2505.14970）：臂奖励 = 该类 rollout 的平均 |A|，TD(0)/EMA 更新，Boltzmann 采类、类内均匀。
- Overthinking（litscan:71725 Eq11）：$\kappa_m=\mathrm{clip}(\kappa_{prev}+\beta(R_m-R_{prev}),0,\kappa^0_m)$，按 NRP 比例调全对 prompt 的占比。
- ET-Agent（2601.06860）：按组内正确性与工具调用数的离散度做 Pareto 选题。

## 信息

- 训练中已经算出的组统计（优势、正确率、工具调用数）；无测试集在线反馈（2505.14970 INFO）。

## 成立条件

- 组统计能反映"可学性"。在 GRPO 下全对/全错组 |A|=0，课程信号为 0（2505.14970 DEGEN）。
- 类别标签预先给定（2505.14970 INFO）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2505.14970 SEC | mean\|A\| 臂奖励 + Boltzmann | HTML §3.2 | 3B Countdown OOD .48→.54；AIME .075→.10；7B Countdown 与 ARC 接近 random | 记录未覆盖 | 弱支持；公式/超参本地 HTML 缺失 |
| litscan:71725 | NRP 保护 + 后续长度罚 + 按 NRP 调 easy 比例 | Table3; Table1; Eq11 | 1.5B 平均 47.78 / 4000 tokens vs GRPO 49.15 / 6814；DS7B 62.48 低于 GRPO 63.86 | 记录未覆盖 | 支持效率；准确率低于 GRPO |
| 2601.06860 ET-Agent | RFT 后 Pareto 选题 + curriculum ARPO | §5/Table2 | 平均 performance 60.1 / Effi 46.0；无 Pareto 54.1 / 40.1 | 记录未覆盖 | 支持（lite 记录） |

## 成功条件 / 失败模式

- 成功条件：组统计与可学性相关；底座不太强（2505.14970：7B 边际收益低）。
- 失败模式 1：全对/全错组 |A|=0，被课程忽略；困难但当前无成功的题可能长期不被采到（2505.14970 DEGEN）。
- 失败模式 2：|A| 依赖归一化方式，高代理值不等于真实学习收益（2505.14970 LESSON）。
- 失败模式 3：效率课程以准确率为代价（litscan:71725 Table1）。

## 审稿期望

推断：要求与随机采样的同步数对照（SEC 已做）；要求说明 |A| 的归一化；要求报告课程对易题准确率的影响。

## 认知障碍

- 以当前可学性替代固定难度顺序，但绝对优势不等于梯度范数或最终泛化增益（2505.14970 rs.why_non_obvious）。

## 工程经验

- 当用优势作为采样收益时，先记录其归一化与成功率依赖，避免把奖励方差当学习进步（2505.14970 LESSON）。
- 当用首次出现正确答案作截止点时，区分充分证据与碰巧猜中（litscan:71725 LESSON；与 P66 相关）。

