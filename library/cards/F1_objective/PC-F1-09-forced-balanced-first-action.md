---
id: PC-F1-09
name: 在首决策处强制均衡采样两种动作，在训练全程保住直答与工具的支撑
family: F1_objective
status: candidate_pattern
problems: {P29: 3, P02: 3, P21: 2, P23: 2, P06: 2}
members: [2505.13417, 2510.12838, 2609.00967, 2608.20256, 2507.15844, "litscan:57190", "litscan:62146"]
rs_patterns: [generative_process_redesign, heterogeneous_decomposition]
---
## 操作
每组 rollout 中，规定一部分样本的首动作。各论文的做法如下：

| 论文 | 强制方式 | 优势/校正 | 出处 |
|---|---|---|---|
| AdaptThink | 行为分布在首 token 处给两种模式各 .5，之后跟随 old policy | $A=R-\bar R_{ref}(x)+\delta\mathbf 1[\text{NoThinking}]$，其中 $\bar R_{ref}$ 是固定参考模型每题 16 样本的均值，不除 std；clipped IS 比值为 $\pi_\theta/\pi_{IS}$ | 2505.13417 Eqs5–9 |
| A2FM | 每题每模式强制 3 条，另加 3 条自然 | 强制前缀从 loss 中 mask 掉，router 只由自然样本更新 | 2510.12838 §3.3 与 signal_routing |
| CoBRA | 强制 reference-split，internal 与 external 各 4 条 | 见 PC-F1-10 | 2609.00967 Eq4–6 |
| Learning When to Think | G=8 强制 warmup 45 步 | 强制路由词从 prompt 尾移到 response 首部，使其获得梯度；未见采样分布校正 | 2608.20256 Algorithm1/AppB 与 signal_routing |
| HBPO | 16 条按 512/1024/2048/2560 四个预算分层强制 | 预算组均值减预算基准，再跨样本标准化 | 2507.15844 key_step |
| Region-R1 | 每题采两种决策 | 采样机制未给 | litscan:57190 Eq5–9 |
| MGPO | prompt 强制首轮先出框（单侧强制，无直答选项） | — | litscan:62146 |

## 信息
- 当前策略在两种被强制的首动作下的终局回报。AdaptThink 另有固定参考模型的逐题准确率。
- 看不到：自然解码下的首动作分布本身。强制前缀与自然事件并不等价（2505.13417 pitfalls："固定 wstart 不是所有 Thinking 事件"；P23）。
- 由谁估计：策略自身的 MC 回报。

## 成立条件
**强制样本是否进入梯度，以及有没有 IS 校正**

| 论文 | 强制样本的去向 |
|---|---|
| AdaptThink | 进入，带 IS 校正（序列比值写法，token 级实现未说明） |
| A2FM | 强制前缀不进 loss，router 只靠自然样本 |
| 2608.20256 | 进入，但无校正 |

- 只用于"执行"训练的强制样本，不训练路由（2510.12838 why_non_obvious："强制 prefix 本身不训练 router，需自然 rollout 补路由梯度"）。

**光有支撑不够**
- CoBRA 只做 reference-split（RS-only）时仍几乎不用工具，jEM .2937（2609.00967 Table4）。
- 还需要一个能区分两支的优势信号。

**其他条件**
- $\pi$ 严格为 0 时，IS 仍可能给出无穷或极小的梯度（2505.13417 degenerate_cases）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2505.13417 | 50/50 IS，δ=.05，固定参考基线 | Eqs5–9；p6 Table1；p7 Table2 | 1.5B 平均准确率 +2.4pp、长度 −53%；7B +2.3pp/−40.1%；δ=0 时 +5.5pp/−32.8%，δ=.1 时 −.5pp/−64.5% | 未报告 | 支持 |
| 2510.12838 | 每模式强制 3 条 + 自然 3 条；简单题非 instant 乘 $1-p^\alpha$ | §3.3；§5 | SuperGPQA cost/pass：reasoning .00889、agentic .00732 → adaptive .00487；聚合准确率 53.8，最佳单模式 55.4；GAIA 57.3 < agentic 60.7 | 未报告 | 支持保支撑；准确率不严格非劣 |
| 2609.00967 | 强制 4+4 | Table4 p8 | 完整 MARS jEM .5418；只做 RS 为 .2937/.2809 | 同一 checkpoint 3 次评测，非训练 seed | 支持"支撑必要但不充分" |
| 2608.20256 | 强制 warmup + mean-only + 平衡项 | AppD Table5；AppA | MATH .782±.006/2810 token；先导任务中各配置在 30–50 步内塌缩 | 3 seeds | 混合 |
| 2507.15844 | 预算分层强制采样 | Table3 | 四预算 63.7%/2364 token，单预算 59.8%/1842；六、八预算 62.9% | 记录未覆盖 | 支持保支撑（长度变长） |
| litscan:57190 | 确保两种决策都被采样（FULL/REGION） | Eq5–9；Tables2,5 | CondRecall@1：E-VQA 已有最佳 .75→.90，InfoSeek .75→.81 | 未报告 | 弱：强制机制未给 |
| litscan:62146 | 单侧强制先出框 | Eq1–2；Tables1,5 | 7B V* 76.4 vs GRPO 71.2；MME-RW 60.5 vs 55.1 | 未报告 | 边界：只保工具支撑，学不会何时裁 |

## 成功条件 / 失败模式
**成功条件**
- 两种模式在能力上确有差异（2608.20256 failure_boundary："任务同质或便宜/贵模式没有能力差时坍塌"）。
- 支撑与区分性优势信号同时具备。

**失败模式**
- δ 加大后准确率转负（2505.13417 Table2，δ=.1 −.5pp）。
- 7B 的隐式思考比例 4.2%，高于原模型（2505.13417 Tables2–3）。
- RS-only 塌缩（2609.00967 Table4）。
- AppB 写每模式 2 条，Algorithm1 写 1 条（2608.20256 pitfalls）。
- 强制单一动作（MGPO）只能训练执行，学不会选择（litscan:62146 failure_boundary）。
- Region-R1 中，按 decision 中心化会让同题 FULL 的奖励恒定、$A_{FULL}=0$；原文 Eq9 全组与"conditional-on-d"的说法冲突（litscan:57190 degenerate_cases）。

## 审稿期望
- 记录的 reviewer_concern 均为 low_evidence。
- 推断的要求：
  - 强制前缀与自然解码的 logprob 一致性审计（P23）；
  - 多种子。

## 认知障碍
- 必须同时改变采样支撑和优势，单加长度罚不够（2505.13417 why_non_obvious）。
- 强制样本只能观察稀有路线的表现，不自动提供路由梯度（2510.12838；2607.08572 why_non_obvious）。

## 工程经验
- 当用强制前缀保障分支覆盖时，应分别统计自然首决策和前缀之后的能力，避免把强制分支的成功当成 router 已恢复（2510.12838 lesson）。
- 当直答采样消失时，先保住竞争分支，再测自然选择；固定偏好代替不了非劣检验（2505.13417 lesson）。
- 当离散模式标签可能与真实计算脱钩时，先测模式之间的能力差和生成长度，再设计奖励；训练时的硬上限与部署时无上限的行为要分别报告（2608.20256 lesson）。
- 当通过固定模板补动作支撑时，要另测自由决策下的迁移和直答保持（litscan:62146 lesson）。

