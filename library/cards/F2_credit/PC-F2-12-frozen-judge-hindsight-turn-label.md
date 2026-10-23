---
id: PC-F2-12
name: 让冻结 LLM judge/critic 读完整轨迹（含 GT 或未来），给每轮打好坏标签或价值，再与结果优势合成
family: F2_credit
status: candidate_pattern
problems: {P16: 3, P11: 2, P18: 2, P43: 2, P15: 2, P14: 1}
members: [2511.12159, 2606.32017, 2608.24588, 2509.14480, 2505.11821, 2503.15478, litscan:3199, 2610.15840, litscan:63890, litscan:51201]
rs_patterns: [heterogeneous_decomposition, structural_prior_encoding, self_supervised_signal_engineering, outside_taxonomy]
---

## 操作

在训练期给一个冻结的大模型看"特权信息"（GT、完整轨迹、未来观测、参考答案），让它对每轮或每次工具调用给出标签或价值；然后把这个局部信号与结果优势合成。常见形式：

- 二值好/坏，按轨迹正分总和归一后，与组 mean/std 结果优势线性混合（2511.12159 CriticSearch）。
- 固定角色映射 $c=(1,.5,-.1,-.5)$，$A_{seg}=A_{GRPO}+\lambda c_{role}$，batch 白化（2606.32017 TRIAGE）。
- 冻结标注器抽出 support-use / failed-use 依赖图，按长度加权的正权重重分配原轨迹优势（2608.24588 IAPO）。
- 每轮 −1/0/1，最多一处 major −1，聚合过程分 + 10R，经组 mean/std 后广播（2509.14480 TARL）。
- 轮末注入 judge 过程奖励，终局给结果奖励，整条轨迹做 GAE（2505.11821 MT-PPO）。
- 可见参考答案的 critic 做逐轮排序 DPO（2503.15478 SWEET-RL）；judge 标关键策略，折扣回报加权策略 logloss（litscan:3199 EPO）。
- 冻结 LLM 价值函数：$V_0=\mu_G$，$V_T=R$，$A_{it}=D_{it}/\sigma_{step}$，满足端点守恒 $\sum_tD_{it}=R_i-\mu_G$（2610.15840 LVRL §3.2）。
- 72B judge 对视觉命题块（CRU）打分：.5 文本 + .4 视觉 + .1 pattern（litscan:63890 ViRC §3.4）。
- 同一历史下执行 5 个候选，由 verifier 选优构成 DPO 对（litscan:51201 SPORT Eq3）。

## 信息

- 看得到：judge 能看到 actor 看不到的东西，如 GT、完整轨迹、未来观测、参考方案。
- 看不到：actor 在同一状态下替代动作的真实结果；judge 与 actor 的能力差。

## 成立条件

- judge 的可靠性决定固定角色标签是在纠正偏差还是放大偏差（2606.32017 why_non_obvious）。
- 特权信息只在训练期使用，部署时不可得（2511.12159 why_non_obvious）。
- 细粒度评审与细粒度梯度路由是两件事（2509.14480 why_non_obvious）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2511.12159 | 冻结回顾 critic 二值标签，非负信用 + 组优势混合 | Table2; Table4 | 3B avgEM 34.3 vs StepSearch 29.6；7B 38.4 vs 36.2；noGT 36.6 / full 38.4 / sparse 35.3；7B MuSiQue 19.4 低于 22.6 | 记录未覆盖 | 成员 |
| 2606.32017 | 角色固定映射 + batch 白化 | Table6 | 7B ALF 87.5±2.4 / WS 77.2±2.2；无 regression 罚 81.4/73.1；无 exploration 85.8/75.5；no-think judge 低于 GRPO | 记录未覆盖 | 成员 |
| 2608.24588 | 冻结标注依赖图重分配优势 | Table1 | 8B tau2 29.61±3.56→42.18±2.55；4B 31.31 vs GRPO 27.81；4B BFCL 31.89 低于 GiGPO 32.42 | 记录未覆盖 | 成员 |
| 2505.11821 | 轮末 judge 奖励 + GAE；对比 turn 拆分 | Table3 p8 | MT-PPO 平均 EM .447，PPO-OR .432；turn-decomposed MT-PPO 仅 .293 | 部分基线抄原文 | 成员 |
| 2503.15478 | 参考可见 critic，逐轮 DPO | Table2; Table3 p10 | backend success 40.4 vs multi-turn DPO 34.4；不除长度仅 3.6；w/o train info 31.2 | 记录未覆盖 | 成员 |
| litscan:3199 | judge 标关键策略，折扣回报加权 | Table4 p8 | SOTOPIA HardGoal terminal RL 6.95 → PRM 7.20 → self-play 7.78 | 记录未覆盖 | 成员 |
| 2610.15840 | 冻结 LLM 价值，端点守恒 ΔV / step std | Table1 p7; §4.4; Table4 | Qwen3-8B AppWorld 26.3 vs GRPO 19.8；早期一致率 44%；Qwen235B critic 9.8 vs Claude 24.3 | AppWorld/BabyAI 3 训练 seed；SWE 1 seed | 成员（含自我否定证据） |
| litscan:51201 | 同历史 5 候选执行，verifier 选优 DPO | Table1,3; Table5 | GTA AnsAcc 53.85→60.26；GAIA 16.97→20.61；静态 DPO GTA 55.13 | AppE 五次，60.26±1.51 | 成员 |

## 成功条件 / 失败模式

- 成功：judge 强且与任务对齐；局部信号**加在**保留的结果优势上，而不是替换它。
- 失败：
  - TARL：每轮局部分配比轨迹聚合差，最佳方案保留终奖并广播（2509.14480 §5.1；REL P15:3）。
  - MT-PPO：把轮拆成独立样本后 EM 仅 .293（2505.11821 Table3）。
  - CriticSearch：Good 非负、Bad 为 0，不保证坏动作的总优势为负（2511.12159 failure_boundary）。
  - LVRL：冻结 critic 早期判断一致率仅 44%，且高估学生（2610.15840 §4.4）。
  - ViRC：CRU 可拿满分 1 而答案为 0，局部评分足以鼓励不终止（litscan:63890 degenerate_cases）。
  - SPORT：verifier 按"有用性"判定，不按结果真实性（litscan:51201 failure_boundary）。

## 审稿期望

TARL 为 decision=reject（记录未给具体审稿意见）；LVRL、ViRC、SPORT 为 low_evidence。"推断"：
- judge 与 actor 的同状态一致率；
- judge 换成更弱或不同族模型时的敏感度（LVRL 已给出 Qwen235B vs Claude）；
- 局部路由 vs 轨迹聚合的匹配对照（TARL 已给出）。

## 认知障碍

- 训练期可以用后见特权信息，但它是 judge 的监督，不是由干预确定的动作价值（2511.12159 why_non_obvious）。
- 全失败组仍可有内部的正负差，这提供了语义上的进步监督；但守恒只限于标量和，不保证梯度正确（2610.15840 why_non_obvious）。

## 工程经验

- 当 dense 奖励看似合理、表现却下降时，先审最终的优势与匹配语义，再锁训练配置（2604.02869 lesson，见 PC-F2-19）。
- 当用冻结 LLM 作价值时，要按真实当前策略的 MC 校验早期动作，并同时报告标量守恒、token 长度权重、critic 与 summary 的成本（2610.15840 lesson）。
- 当以中间命题作局部 RL 单位时，必须同时记录终答出现率、工具率与块长度；高局部分数可以与不终止共存（litscan:63890 lesson）。

