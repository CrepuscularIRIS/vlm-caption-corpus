---
id: PC-F3-14
name: 只在某行为的使用率低于下限时给条件奖金（率下限 / 行为频率反馈控制）
family: F3_support
status: candidate_pattern
problems: {P29: 3, P02: 2, P61: 2, P28: 1}
members: ["litscan:51030", "litscan:65560", 2607.10738]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

在终答奖励上加一项，只在该题（或 batch）上目标行为的使用率低于下限 H 时才给奖金，且只给实际执行了该行为的轨迹：

$R_{new}=r+\alpha\max(H-\mathrm{RaPR}(x),0)\,\mathbf 1_{PR}(y)+\beta\min(N-n_{vo}(y),0)$，$\alpha=.5,\beta=.05,H=.3,N=1,G=8$（litscan:51030 Eqs3–5, AppC.3）。

变体：
- 再加一个质量门：$R_{diag}=\mathbf 1[R_{rubrics}>\eta]\,\alpha\max(H-C_u(x),0)\,\mathbf 1_{tool}$（litscan:65560 Eq7）。
- 反向控制（压低过度行为）：按 batch 拒答率相对目标 µ 的超额 $E=(\text{refuse}-\mu)/\mu$ 对拒答奖励减分或补偿，EMA α=.5 后按 τ=.1 量化（2607.10738 §2.3, AppB, notes）。

## 信息

- 当前策略在同一题（RaPR 按同 query 期望定义，AppC 示例 1/8 支持组内估计）或当前 batch 上的行为频率。

## 成立条件

- 行为在当前组内至少被采到一次；RaPR=0 的组没有 PR 样本，也就没有奖金（litscan:51030 DEGEN）。所以必须在塌缩前启用。
- 需要另一个约束防止过度使用：litscan:51030 用 β 项压 >N 次调用。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:51030 Pixel Reasoner | 按 query 的 RaPR 下限给工具奖金，超过 N 次扣分 | §3–5/Table1/AppC | 无 curiosity 时工具率约 .55→0（240 步）；V* 84.3 vs 无 curiosity 81.1 | 未给主表多 seed/CI | 支持 |
| litscan:65560 OralGPT-Plus | rubric 过阈值才给，率下限形式相同 | Eq7–8; Table2 | 7B MMOral-X 简单 23.06 SFT→43.16、复杂 14.40→24.96；H、η、C_u 数值正文未明 | 五次评测（非训练种子） | 弱支持（无去掉 R_diag 的消融记录） |
| 2607.10738 | 按 batch 拒答率超额动态调奖励 | §2.3; Table3 p3; AppB | 冷启动 γ=.2：Acc .529、拒答 .192、Prec .662、RA-F1 .585；γ0 基线 .552 / .012 / .559 / .556；静态 .05 拒答奖励即 99.9% 拒答（KF 字段） | 记录未覆盖 | 支持反馈控制；准确率 −2.3pp |

## 成功条件 / 失败模式

- 成功条件：在行为还没消失时启用，率下限把它稳在 H 附近（litscan:51030：无此项时 240 步归零）。
- 失败模式 1：已经达标时（RaPR≥H）奖金为 0；在 N=1 下 0 次与 1 次同奖励，不推向 0 次（litscan:51030 DEGEN、relevance P06）。
- 失败模式 2：采不到该行为时奖金无支持（litscan:51030 FAIL）。
- 失败模式 3：只奖励"尝试"会出现执行错误但凭语言答对的投机，需要恢复示范（litscan:51030 NEG）。
- 失败模式 4：反馈控制不保证准确率非劣（2607.10738：−2.3pp）。
- 失败模式 5：judge 同时用于奖励和评测，存在耦合（litscan:65560 NEG）。

## 审稿期望

推断：要求报告行为率随步曲线与 H 的关系；要求率下限的敏感性（H 扫描）；要求说明 RaPR 的估计方式（组内还是历史）。

## 认知障碍

- 不会工具时结果 RL 会绕开工具；只奖励尝试又会产生投机（litscan:51030 rs.why_non_obvious）。率下限是两者之间的折中：只在行为稀缺时奖励。
- 固定小正奖励也会把策略推到一侧（2607.10738 rs.why_non_obvious）；需要按频率反馈的控制。

## 工程经验

- 当新行为早期弱时，先给正确恢复示范并屏蔽错误动作 loss，再观察是否错误调用拿探索奖（litscan:51030 LESSON）。
- 当反馈信号来自 batch 统计时，用 EMA 加量化稳定，并注意量化后是否再 clip（2607.10738 notes）。
- 使用率达标后，另行定义 0 vs 1 次的成本，率下限本身不提供这个方向（litscan:51030 LESSON）。

