---
id: PC-F3-20
name: 教师可见信息多于学生时，只用特权信息在学生自己的状态上打分/监督，不直接蒸馏教师的动作或视图
family: F3_support
status: candidate_pattern
problems: {P39: 3, P36: 2, P16: 2, P38: 1}
members: [2512.01188, 2610.23378, 2606.08719, "litscan:77773", "litscan:3139"]
rs_patterns: [heterogeneous_decomposition, controlled_diagnostic_design]
---

## 操作

训练时存在一方（教师/critic/数据构造器）看得到学生部署时看不到的信息（额外传感器、GT 区域、高分辨率原图、dense caption）。做法是：学生按自己的部分观测采样，用特权信息评价学生的状态-动作（特权 critic 加权回归；冻结特权教师在学生前缀上逐 token 给分布），或把监督对齐到学生实际会到达的状态；而不是让学生模仿教师在完整信息下做出的动作。

公式（2512.01188 Eq2）：$L_{actor}=\mathbb E_{(s,z),a\sim\mu}[\exp((Q(s,z,a)-V(s,z))/\beta)\log\pi(a|z)]$，Q、V 收特权观测 s，actor 只收部分观测 z。

## 信息

- 特权一侧：额外传感器/位置/bbox（2512.01188）；GT crops 与答案（2606.08719）；部署 AP 模块的真实终点状态（2610.23378）。
- 学生一侧：部分观测与自身历史。
- 关键区分：特权信息只进评价/监督分布，不进学生输入（2512.01188 ROUTE："privileged obs 仅 critic/value，actor logprob 只 partial obs/history"）。

## 成立条件

- 能在学生自己的分布上采样（online 或从学生状态出发）。
- 特权评价要可信；litscan:3139 与 litscan:77773 的反例说明教师信息优势会被写进轨迹而学生无法复现。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2512.01188 AAWR | 特权 IQL Q/V → 指数加权 actor 回归；offline 后 online | Table2; 4.3 | 真实 BlindPick online AAWR grasp 94 / pick 89 vs online AWR 71/55；模拟 AP AAWR 100% vs distillation 80%；distillation 只搜中间、漏角落 | simulation 10 seeds | 支持：直接蒸馏会跳过必要观察 |
| 2610.23378 Look Before You Act | 从部署 AP 模块的真实终点起，匹配 demo 前缀、闭环对齐、成功 suffix replay，构造 VLA 监督 | Table IV | π0.5 平均 46.3 → naive 11.5 → aligned 72.7；Spatial matched state 54.6 vs aligned 78.2 | 记录未覆盖 | 支持：只换更好图像不够，学生要能消费 |
| 2606.08719 Imagine-OPD | 冻结特权教师（见 GT crops + 答案）在学生前缀上 KL | Table4; Table3 | 4B V* 80.1/83.8/88.0（base/GRPO/OPD）；self boxes 86.4 低于 GT boxes 88.0 | 未报告 | 支持 |
| litscan:77773 LongGT（反例） | 文本 reasoner 看 dense caption 写 CoT，学生只见图像 | PIT 字段; Table12 p22 | 记录："caption teacher 信息非 student 视觉观测"；禁止引用 caption 措辞不消除信息优势 | 记录未覆盖 | 边界：特权信息写进示范 |
| litscan:3139 MM-Verify（反例） | 纯文本 QwQ 读几何文本描述生成长 CoT，学生配原图训练 | §3.3; Tables1–3 | MathVista sample8 + Stage2 verifier 65.3；FAIL："教师拥有结构化文本几何信息，学生像素感知仍可能失败" | 记录未覆盖 | 边界 |

## 成功条件 / 失败模式

- 成功条件：特权信息只出现在评价侧，学生在自己的状态分布上被训练。
- 失败模式 1：训练依赖特权传感器；现实中仍需 detector 切换（2512.01188 FAIL）。
- 失败模式 2：VIB 部署无特权时塌缩（2512.01188 NEG）。
- 失败模式 3：特权评价不是真实价值；IQL expectile 是乐观值（2512.01188 ROUTE）。
- 失败模式 4：成功过滤后的训练分布只是可行子集（2610.23378 FAIL）。
- 失败模式 5：特权教师若在线同步更新会崩溃（2606.08719 Table4，见 PC-F3-18）。

## 审稿期望

推断：要求"直接蒸馏教师动作"的对照（AAWR 已做）；要求学生视图下的信息可见性审计；要求特权信息消融（Imagine-OPD 的 self boxes vs GT boxes）。

## 认知障碍

- 特权专家直接蒸馏可能跳过必要的观察动作；而用特权 critic 评价部分观测策略的探索，可以学到"看"的动作（2512.01188 rs.why_non_obvious）。
- 更好的视角同时改变机器人状态，原策略不一定能消费（2610.23378 rs.why_non_obvious）。

## 工程经验

- 当 teacher 能直接看到目标而 student 不能时，优先用 teacher 状态评价 student 的采信息动作，不直接蒸馏跳过观察的 expert 动作（2512.01188 LESSON）。
- 当主动观察改变后续状态时，同时记录从该状态出发的可执行动作，单换图片不够（2610.23378 LESSON）。

