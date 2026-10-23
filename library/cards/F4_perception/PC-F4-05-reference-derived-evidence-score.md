---
id: PC-F4-05
name: 用由 GT/教师派生的参考（必要证据清单、rubric、参考推理）给轨迹过程打分
family: F4_perception
status: candidate_pattern
problems: {P43: 2, P42: 2, P40: 1, P11: 1, P05: 1}
members: [2609.03493, 2605.16416, litscan:65189, 2510.14738, litscan:75452]
rs_patterns: [heterogeneous_decomposition, self_supervised_signal_engineering]
---
## 操作

训练前或在线，用具有特权信息的教师（可见 GT 答案或成功轨迹）为每题构造参考：必要证据清单、rubric checkpoints、感知 probe 或参考推理。RL 时按轨迹对参考的覆盖程度打过程分，与终答奖励合成。各成员做法：

- **NTEP-R**（2609.03493 Eqs9–10）：
  - $R_{NTEP}=((1-\lambda_g)H_{info}+\lambda_gH_{goal}-\lambda_gM_{goal}-\lambda_dD_{dup})/N$；
  - $R=R_{ans}+R_{fmt}+.5R_{NTEP}$；
  - 取值 $\lambda_g=.3,\lambda_d=.1$（Eq11/Table5）。
- **CAVE $c^{ea}$**：对每个证据单元，算当前策略 teacher-forced 平均 log-prob 在相邻状态间的正增量（2605.16416 Sec.3.2.2）。
- **PEARL**：用感知 probe 均分门控推理优势，$A_{reason}\leftarrow A_{reason}\cdot\min(\bar R_p,.5)$，另加 .1 的感知 GRPO 项（litscan:65189 Eq2–3, Eq5）。
- **AutoRubric**：$r=\lambda r_{answer}+(1-\lambda)r_{rubric}$，rubric 由成功轨迹聚合而来（2510.14738 Table3）。
- **FOCUS-RL**：参考 CoT 的 hidden-state view 余弦 RVA，单独成一个优势通道后相加（litscan:75452 3.2；4.2）。

## 信息

- **参考来源（特权）**：
  - 教师 Gemini3.1Pro 见目标暖启动轨迹（2609.03493）；
  - GPT4.1 见图与含 GT 答案的 QA（litscan:65189）；
  - 用 GT 筛出的成功轨迹（2510.14738）；
  - 生成器或人工核验的证据单元（2605.16416）；
  - 已核验的参考 CoT（litscan:75452）。
- **打分者**：
  - 外部判官：Qwen3-VL-Plus（2609.03493）、纯文本判官（2510.14738）；
  - 策略自身：teacher-forced 似然（2605.16416）、作答 probe（litscan:65189）、hidden state（litscan:75452）。
- **看不到**：当前策略是否真的需要该证据；同状态的反事实。

## 成立条件

- 能廉价构造出可信的参考：
  - AutoRubric 的 rubric 覆盖率只有 67.26%（2510.14738 Table3）；
  - CAVE 明确拒绝直接用 AI rationale 作证据（2605.16416 App.B.3 pitfalls）。
- 参考与判官要与策略隔离，记账规则要写清：pending、重复、失败重试（2609.03493 lesson）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2609.03493 | 必要证据路径，计 Align/Acquire/重复，按路径长度归一 | Eqs4–11；Table1；§4.1 | 主表 70.34 vs 同接口 MARS 68.31；搜索 ATC 2.54→1.89，**视觉 ATC 1.86→1.08**；goal-only 塌缩 | 单训练 run + 一次固定种子评估 | 正（少调用） |
| 2605.16416 | 证据单元 teacher-forced 正增量 | Sec.3.2.2；Table4a p8 | 去 evidence：TV 29.6 vs 31.3，Baby 15.3 vs 17.3，TRACER-Core 34.7 vs 36.9，MME-RS 55.9 vs 59.2 | 记录未覆盖 | 正（需证据标注） |
| litscan:65189 | probe 均分门控推理优势 | Table3；Table4 | 7B 均分 44.2（GRPO）→47.9；MathVerse 46.4→50.8；QA 锚定 probe 47.9 vs dense 45.5 | 记录未覆盖 | 正；Table4 非单因素 |
| 2510.14738 | rubric 覆盖比例，纯文本判官 | Table3 | standard/strict 55.26/53.24；无 rubric 53.11/49.43；无 judge 53.75/47.06 | 记录未覆盖 | 正 |
| litscan:75452 | 参考 view 对齐的独立通道 | Table1 | Qwen7B 平均：GRPO 42.7 → Data 44.7 → Data+Policy 45.3 | data_seed42 | 弱正（+.6） |

## 成功条件 / 失败模式

- **成功条件**：
  - 参考证据确为必要且视觉可落地；
  - 过程分与终答分并存，不替代终答分。去掉 $R_{ans}$ 或只用 goal 会塌缩（2609.03493 §4.1/4.5）。
- **失败模式**：
  - **重试被罚**：失败重试仍扣 .1，成功概率须大于 1/7 时过程期望增益才为正（2609.03493 degenerate_cases）。
  - **只奖正增量**：只留正增量、不罚证据丢失，反复失而复得可累积正分；概率可恢复不等于像素被使用（2605.16416 failure_boundary）。
  - **probe 门控过弱**：probe 由 GT 答案逆推，存在捷径；$\bar R_p>0$ 是弱门，不证明每项正确（litscan:65189 pitfalls, failure_boundary）。
  - **判官不重看图**：rubric 可能继承共同的视觉错误（2510.14738 failure_boundary）。
  - **单 run 不能证明非劣**：单训练 run，小幅增益不足以支持非劣结论（2609.03493 seeds）。

## 审稿期望

推断：
- 参考的人工审计率与错误率；
- 打乱参考（换成别题的清单）作占位对照；
- 多种子；
- 过程分与终答分的相对权重扫描；
- 调用次数与直答比例。

## 认知障碍

- 结果奖励会给冗余调用记功（2609.03493 trigger_condition）。把"目标、取证、重复"拆开计分，比整条 teacher 轨迹模仿更宽松。
- 但参考是静态的。前人默认"教师认为必要 = 策略需要"，未做策略侧校准。

## 工程经验

- **以证据路径做监督时**：先写清 pending、重复、失败重试的记账规则；保留终答奖；把参考路径和判官与策略隔离（2609.03493 lesson）。
- **teacher-forced 打分时**：只在独立的 reward pass 里做，不注入 rollout 的后续状态；优化时环境 token 的 mask 设为 0（2605.16416 pitfalls）。
- **感知分平均多个二值 probe 后是多值奖励**：端点过滤识别不了中间值的常数组（litscan:65189 pitfalls）。

