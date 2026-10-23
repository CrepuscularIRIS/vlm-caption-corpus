---
id: PC-F5-06
name: 让独立于策略的判定器（偏好 verifier / 证据覆盖头 / PRM）决定继续还是停止
family: F5_stop_eval
status: needs_revision
problems: {P33: 2, P16: 2, P31: 1, P25: 1}
members: [litscan:52515, 2604.17866, 2511.19314]
rs_patterns: [heterogeneous_decomposition, self_supervised_signal_engineering]
---
## 操作
训练一个与生成策略分开的判定器，用外部监督（DPO 偏好对、gold 证据覆盖、MC 续写成功率）打分，推理时由它的分数或分数增量决定是否再调一次工具：
- VTS：$r_\phi(\tau)=\eta\sum_h\log\frac{V_\phi(t_h\mid s_h)}{V_0(t_h\mid s_h)}+\eta\sum_h\log\frac{V_\phi(a_h\mid t_h)}{V_0(a_h\mid t_h)}+Q(s_1)$；$r_\phi(s_{h+1})-r_\phi(s_h)<\epsilon$ 即停（litscan:52515 §3.3–3.4，Algorithm1）。
- 隐式检索控制头：$\hat y=\sigma(Wq+b)$，标签 $y^{(r)}=1[P\not\subseteq R^{(r)}]$（gold 未覆盖就继续），与对比检索、NTP 联合训练；$\hat y\ge.5$ 继续（2604.17866 Eqs1/4/5/7）。
- PRInTS：用续写 MC 成功率增量造 step 标签训练 PRM，推理时挑候选 step（2511.19314 signatures）——本卡把它作为**反例**收入。

## 信息

## 成立条件
- 生成策略已有工具行为：VTS 未经 SFT 的 Qwen2 接 VTS 后 BLINK 48.01→38.54，SFT 后 52.19（litscan:52515 Table1）。
- 有外部监督源（DPO 正负轨迹 / gold supporting docs）。
- VTS 的有限终止定理要求 verifier 期望有界、且相对 base 更接近 reasoner 的逐状态 KL 条件，未经真实 rollout 验证（litscan:52515 pitfalls）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:52515 VTS | DPO verifier log-ratio 增量阈值停 | Table1；Table2；§3.3 | Qwen2 BLINK 48.01→38.54（无 SFT）→52.19（SFT）；GPT-4o 62.25→69.15；Qwen2.5 MathVista 67.5→66.5 | 记录未覆盖 | 记录未覆盖 |
| 2604.17866 隐式检索控制头 | gold 覆盖 BCE 头决定继续检索 | Table4 | 3B 平均 EM .418；去控制头固定 5 doc .350；去 NTP mask .398；无 NTP 崩至 .003 | 所读范围未报告 | 记录未覆盖 |
| 2511.19314 PRInTS（反例） | MC 增量训练 PRM 选 step | Table1 | Qwen3-32B avg 29.5→38.8；但更大候选池可偏好表面有信息的探索而错过已正确的终答 | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：生成器先经 SFT；判定器训练分布与部署时的生成器一致。
- 失败模式（为何 needs_revision）：
  - PRInTS：过程判定器偏好"有信息的探索"而错过已正确的终答——判定器主导停止时恰好推向多看（2511.19314 failure_boundary；record relevance P33："是停止评测反例"）。
  - VTS：高分的错误动作会继续，低分的必要探索会早停；算法先执行一步再判停；无工具零步样本在数据过滤中被去除（litscan:52515 degenerate_cases）——即它系统性地不覆盖"直答"。
  - 控制头：去掉控制头的对照同时固定了预算，没有完全隔离状态判别；gold 覆盖不是必要性标签；控制标签时序存疑（2604.17866 failure_boundary、degenerate_cases）。

## 审稿期望
- 核验判定器是否读取了新观测：同一动作配不同返回时分数是否变化（litscan:52515 transfer_mapping、lesson）。
- 测"必要但即时分低"的恢复状态（litscan:52515 lesson）。
- 明确停止标签与当前模型成功价值的区别（2604.17866 lesson）。

## 认知障碍
把工具生成和"继续是否有收益"的判断分开训练看起来更干净（litscan:52515 why_non_obvious），但偏好分不是环境的真实信息增益；gold 覆盖标签也不是当前 actor 的成功差（2604.17866 why_non_obvious）。

## 工程经验
- 当把偏好 log-ratio 用于停止时，应核对增量是否读取了该步返回的观测，否则停止信号与新证据无关（litscan:52515 lesson）。
- 当 Lemma 的阈值省略了温度/尺度系数 η 时，阈值需按 η 重标，不能默认等价（litscan:52515 pitfalls）。

