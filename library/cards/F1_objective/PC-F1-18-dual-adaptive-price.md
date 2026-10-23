---
id: PC-F1-18
name: 把代价写成约束，用对偶变量 λ 按真实约束违背量在线更新（Lagrangian / PPO-Lagrangian）
family: F1_objective
status: candidate_pattern
problems: {P01: 2, P32: 2, P05: 2, P35: 1}
members: [1805.11074, 2310.12773, 2512.21540]
rs_patterns: [reframe_as_solvable_object]
---
## 操作
写成约束问题：$\max J_R$ s.t. $J_C\le\alpha$，按约束违背量在线更新 λ。三篇的写法：

**RCPO**（1805.11074 Eqs3/9–11）
- 奖励写成 $\hat r=r-\lambda c$。
- λ 按原始约束的蒙特卡洛估计慢速更新：$\lambda_{k+1}=\Gamma_\lambda[\lambda_k+\eta_1(\hat J_C-\alpha)]$。

**Safe RLHF**（2310.12773 Eq22–31）
- reward 与 cost 各自算 GAE 和 PPO 损失，合并为 $L=(L_R-\lambda L_C)/(1+\lambda)$。
- λ 在对数尺度上更新：$\log\lambda_{k+1}=\log\lambda_k+\alpha\lambda_kJ_C$。

**LEASH**（2512.21540 §2, Algorithm1）
- 只罚超长部分，$\tilde r=\mathrm{clip}(r-\lambda\max(0,L/L_t-1),-1,1)$，然后做组 mean/std。
- λ 用跨 batch 的有符号违背量更新：$\lambda\leftarrow\mathrm{clip}(\lambda+\alpha_\lambda\hat J_p,0,1)$。

## 信息
- 每条样本的成本，以及 batch 或 episode 级的真实约束统计。
- 看不到：每次调用是否必要。约束只限制平均量。
- 由谁估计：λ 由真实约束统计驱动；actor 和 critic 用代理成本。

## 成立条件
**代价如何进入优势，决定 λ 是否起作用**

| 方法 | 代价进入方式 | λ 是否被组 std 消去 |
|---|---|---|

**其他条件**
- 对偶上升需要时间尺度分离：critic 最快，actor 居中，λ 最慢（1805.11074 AppE）。
- 平均约束不限制单条样本（2310.12773 failure_boundary；2512.21540 failure_boundary）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 1805.11074 | RCPO 三时间尺度 | Eqs3/9–11；Table2 | Swimmer torque 30.4%→24%，reward 94.4→72.7；Walker2d RCPO reward 591.6，低于可行的固定 λ=.1 的 823.5；3 个域略超阈值 | seed 数未给 | 支持方法；有越界 |
| 2310.12773 | 独立 cost 通道 + log-λ 更新 | Eq10–12/22–31；§4.2.1 Fig5 | 三轮后人工评测有害率 53.08%→2.45%；helpfulness Elo +363.86 | 记录未覆盖 | 支持（尺度路由正确） |
| 2512.21540 | 单侧 clip 惩罚 + batch 对偶 | §2；Algorithm1；Table2/3 | 1.5B 准确率 33.1→33.9，token 15727→5873；4B 目标 8k 时准确率 75.5→70.1，token 实际只降到 12042 | 未报告 | 混合 |

## 成功条件 / 失败模式
**成功条件**
- 约束量可以测量，阈值可以预设。
- 代价从独立通道进入，或在 std 之后进入。

**失败模式**
- 固定步长下可能落在不可行的固定点；代理成本的局部极小不一定可行（1805.11074 degenerate_cases）。
- 静态权重偏高或偏低都会过优化单一目标（2310.12773 §4.2.3–4.2.4）。
- 小预算损伤准确率：4B 8k 时 −5.5pp（2512.21540 Table2）。
- 在 OOD 上，自适应 λ 不如常数 λ（2512.21540 Table3）。
- 正确但 $\lambda\Delta\ge2$ 的样本会被 clip 到 −1，与错误同分（2512.21540 degenerate_cases）。

## 审稿期望
- 记录为 low_evidence。
- 推断的要求：
  - λ 轨迹与约束违背曲线；
  - clip 比例；
  - 标准化后的优势中代价项的份额（2512.21540 lesson："不能只监控 λ"）。

## 认知障碍
- 相对偏好只能识别排序，不能给安全预算一个锚点；需要一个有零点的独立代价模型（2310.12773 why_non_obvious）。
- 常数惩罚跟不上随训练变化的长度（2512.21540 why_non_obvious）。

## 工程经验
- 用平滑代理训练约束策略时，对偶变量仍用真实约束统计；要明确代理的可行性与渐近时间尺度假设（1805.11074 lesson）。
- 代价尺度会被组 std 抵消时，先确认代价进入的是 reward 还是独立 loss；动态 λ 需要校准约束反馈（2310.12773 lesson）。
- 加长度惩罚时，同时记录原始违背量、clip 比例和标准化后的优势（2512.21540 lesson）。

