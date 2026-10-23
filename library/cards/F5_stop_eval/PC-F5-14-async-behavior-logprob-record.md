---
id: PC-F5-14
name: 分离或异步 rollout 时逐 token 记录行为策略概率与版本，把"陈旧校正"和"更新裁剪"拆成两个因子
family: F5_stop_eval
status: candidate_pattern
problems: {P60: 3, P56: 2, P55: 2, P58: 1, P10: 1}
members: [2410.14803, 2606.05597]
rs_patterns: [heterogeneous_decomposition, identify_hidden_assumption]
---
## 操作
采集与学习解耦后，样本来自旧策略。逐 token 保存行为策略概率 $\mu$ 与策略版本，用重要性比校正：
- AsyncWebRL：$\frac{\pi_\theta}{\pi_{behave}}=\frac{\pi_{prox}}{\pi_{behave}}\cdot\frac{\pi_\theta}{\pi_{prox}}$，陈旧因子 $\pi_{prox}/\pi_{behave}$ 不裁剪，当前更新因子 $\pi_\theta/\pi_{prox}$ 走 PPO clip；优势 $\hat A_i=(r_i-\mathrm{mean})/\mathrm{std}$；另把每条轨迹的步数分母 $1/\lvert\tau_i\rvert$ 改为常数 $1/k$（k=10）（2606.05597 §3.2）。
- DistRL：$\rho_t=\pi(a_t\mid s_t)/\mu(a_t\mid s_t)$，$A_t=r_t+\gamma V(s_{t+1})-V(s_t)$；$\mathcal L=-\mathbb E_\mu[\rho_tA_t\log\pi]-\beta\mathbb E_\mu[H]+\lambda\mathbb E_\mu[P_{invalid}]$，加 Retrace 与分布式优先回放（2410.14803 §5.1 Eq.1）。

## 信息
逐 token 行为策略概率、近端策略快照、策略版本号、终局奖励（AsyncWebRL 用 WebGym GPT-4o 终局判定；DistRL 用 Gemini 终局判定）、截图引用。

## 成立条件
- 行为概率在采样时记录，而不是事后重算；同一条轨迹内行为策略可能变化，不能只存起始快照（2606.05597 pitfalls）。
- 环境采集慢且异质，异步才有吞吐收益（2410.14803 trigger_condition）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2410.14803 DistRL | 异步 worker + 集中 learner + Retrace + DPER | §6.6；§6.3 | General test 73.2±1.1 vs DigiRL multi 61.2±2.4；去 DPER −8%，去 Retrace −6% | 3 repeats，mean±std | poster |
| 2606.05597 AsyncWebRL | 连续 worker + 截图引用 + 陈旧/当前因子分解 + 常数步数分母 | §4.2 Table1；§4.3 | Instruct OOD 峰值 45.4% vs WebGym 42.9%；吞吐约 3100/h vs 1300/1050（2.4–2.9×）；异步 RAFT++ 39.3 低于同步 WebGym 42.9 | single seed throughout | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：系统吞吐、off-policy 校正、奖励可靠性三者分别检验（2410.14803 lesson）。
- 失败模式：
  - 仅异步不提高正确率：异步 RAFT++ 低于同步基线（2606.05597 Table1）。
  - 单种子 + 峰值测试分数，不构成稳定收益或非劣（2606.05597 negative_results）。
  - 高滞后的不裁剪权重有方差风险；行为概率接近 0 时 IS 方差大（2606.05597 degenerate_cases；2410.14803 degenerate_cases）。
  - DistRL 的 Retrace/DPER 完整公式记录未覆盖（2410.14803 failure_boundary）。
  - AsyncWebRL 的加速口径自相矛盾：结论称额外 1.80× per-step，§4.3 报 18–19% walltime 下降（2606.05597 pitfalls）。

## 审稿期望
- 系统改动与 loss 改动分开消融（2606.05597 failure_boundary："系统与loss共同变化"）。
- 与 IMPALA/Retrace 的算法增量讲清；超参敏感性与奖励可信度要支持（2410.14803 reviewer_concern）。

## 认知障碍
提高吞吐同时引入旧策略轨迹，必须把系统异步与算法校正一起评估（2410.14803 why_non_obvious）；轨迹步数归一化是独立于 reward std 的隐藏尺度，容易被忽略（2606.05597 why_non_obvious）。

## 工程经验
- 当同一条轨迹的不同段由不同策略快照生成时，应逐 token 记录行为策略概率，不能只存 episode 起始快照（2606.05597 pitfalls）。
- 当把图像/截图张量放进跨 worker 共享存储时，会溢写磁盘拖慢训练；应传引用，并保证引用能按生命周期恢复对应观测（2606.05597 pitfalls、relevance P55）。
- 当环境异步产生旧轨迹时，保存行为概率与版本，分别检验吞吐、off-policy 修正和奖励可靠性（2410.14803 lesson）。
- 当视觉异步训练变慢时，先看图片搬运与尾部 worker 等待，再看算法（2606.05597 lesson）。
- 当给外部 judge 更长的轨迹上下文时，与人评的一致性可能下降（2410.14803 §6.3）。

