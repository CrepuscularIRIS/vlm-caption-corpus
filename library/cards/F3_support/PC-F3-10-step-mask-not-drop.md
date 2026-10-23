---
id: PC-F3-10
name: 按步打分后只屏蔽低质步的 SFT loss、保留其作上下文，不整条删除轨迹
family: F3_support
status: candidate_pattern
problems: {P37: 3, P36: 2, P38: 2, P18: 2}
members: [2512.10962, "litscan:72846", "litscan:3816", "litscan:70504"]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

对一条（通常是成功的）轨迹的每一步打质量分或相关性标签 m_t∈{0,1}。SFT 目标只计算 m_t=1 步的 thought/action token；m_t=0 的步骤仍留在历史里作为条件，不删除整条轨迹。

公式（2512.10962 §3.2）：$m_n=\mathbf 1[s_n>5]$，$L_{SFT}=-\sum_n m_n\log\pi_\theta(t_n,a_n\mid I,\text{past},\text{screenshots})$。

## 信息

- 步级分数来自外部评审：o4-mini 逐步评分（2512.10962）；70B LLM 判定与事后目标相关的动作 z_t（litscan:72846 Eq3）；GT 校验失败的 trial（litscan:3816）。
- 只用于决定监督位置，不进 RL 优势。

## 成立条件

- 评审对"必要但未成功的探索"不过严；否则 mask 会误删探索（2512.10962 NEG：人工核 73% 一致，grader 对探索但未错的动作过严）。
- 被 mask 的步骤仍需在上下文中，才能学到"失误后的恢复"。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2512.10962 WebSTAR | 成功轨迹中 s>5 的步训练，其余只作 context | Table2; Table5 | 97K 全部步骤平均 29.9，46K 正确步骤 39.6；teacher 与人 73% 一致 | 记录未覆盖 | 支持；评审误差是边界 |
| litscan:72846 Hindsight relabel | 事后重标达成目标，mask 无关动作，加权 buffer，与 GT demo 混合 | Table1; Eq3–4; 4.4 Fig7 | ALFWorld unseen SFT 78.36→97.76，DPO 82.84→94.78；人工 200 例中 180 例重标正确 | 主文称多 seed 附录复验，本记录未读 | 支持 |
| litscan:3816 S2R | 自身失败 trial 留上下文、mask 其 solution，只训 verify/最终 solve | Table2; notes | MATH500 51.0→81.6（BI）→84.4（ORL） | 记录未覆盖 | 支持 |
| litscan:70504 Thyme | SFT mask 沙箱输出，且只训最后一轮，防"先错再修" | §4.2; ROUTE 字段 | 记录称"SFT 最终采用 mask sandbox 和 only last round"；无单独数值 | 记录未覆盖 | 弱支持（反向变体：只训最后一轮） |

## 成功条件 / 失败模式

- 成功条件：mask 比删除保留了更多上下文多样性（2512.10962 Table2 的 46K 正确步 > 97K 全部步，说明去掉坏步的监督有用；而保留其上下文使恢复可学）。
- 失败模式 1：评审误杀必要探索（2512.10962 Table5）。
- 失败模式 3：重标错误 10%（litscan:72846 4.4 Fig7）。
- 失败模式 4：Thyme 的"只训最后一轮"避免学到先错再修，但同时丢掉中间步的监督；两种取舍记录中没有对照。

## 审稿期望

推断：要求"删整条 / mask 步 / 全保留"三档对照；要求人工核对被 mask 步中必要探索的比例。

## 认知障碍

- 轨迹成功不等于每个动作值得模仿；丢 loss 而保留 context 允许学习失误后的恢复（2512.10962 rs.why_non_obvious）。
- 失败于原目标的轨迹也可能成功于其他目标（litscan:72846 rs.why_non_obvious）。

## 工程经验

- 当成功轨迹含坏动作时，只 mask 目标、保留真实历史，但应单独审计必要探索的误杀（2512.10962 LESSON）。
- 当回收失败轨迹时，与 GT demo 混合以稳住支持（litscan:72846 Eq4：λ=.3）。

