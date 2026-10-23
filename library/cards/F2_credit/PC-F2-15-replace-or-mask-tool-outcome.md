---
id: PC-F2-15
family: F2_credit
status: needs_revision
problems: {P14: 3, P15: 3, P11: 2, P20: 2, P13: 2}
members: [2609.29050, 2606.30251, 2602.10863, 2606.05784, litscan:70458, 2509.14480, 2610.15840, 2609.35084, 2610.31544, 2604.02869]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

在工具段（调用及其前后思考）的 token 上，**不再**使用整条轨迹的结果优势，而是三选一：
3. **截断**：失败步的优势改成 $\min(A+\beta F,0)$（2606.05784 Eq4）。

## 信息

各成员的局部信号来源不同：probe 差、证据关联、judge、critic、过程匹配分。本卡把它们放在一起，因为**路由操作本身**（替换/置零 vs 保留）是 P14/P15 的决策变量，并且成员之间对该操作的效果有直接冲突。局部信号的信息差异见 PC-F2-09/12/14/04 等卡。

## 成立条件

- 局部信号必须比结果优势更可靠；否则替换等于把噪声换进来。
- 被置零的段在共享参数下仍然会变：去掉某个 token 的直接 loss，不保证它不被改变（2606.30251 签名 2 failure_boundary）。局部 advantage isolation 不等于共享参数隔离（2609.29050 REL P24:3）。

## 成员证据（支持 / 反对 两侧）

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 方向 |
|---|---|---|---|---|---|
| 2609.29050 | 工具段与 summary 段分通道，关闭 S→T | Table2 p9; Table22 AppD.9 | 7B Toucan Success .7660→.7913，BFCL .6841→.6977，tau2 .3187→.4102；关闭 S→T 主效应 tau2 +5.51pp（加性和未重缩放） | 3 independent runs | 支持置零（工具段不拿 summary 结果） |
| 2606.30251 | 按 Δ 掩码结果优势（OGAR） | Table3 p6 | 完整 72.0 vs 无 OGAR 70.0 | 未报告 | 支持掩码 |
| 2602.10863 | 工具轮优势被证据通道替换 | Table2 | ICA 整包 vs GSPO：GAIA 69.9 vs 60.2 等 | 未报告 | 支持替换（整包，未隔离） |
| 2610.15840 | 纯 ΔV/σ 作每步优势，端点守恒 | Table1 p7 | AppWorld 26.3 vs GRPO 19.8 | 3 训练 seed | 支持替换（冻结强 critic） |
| 2606.05784 | 失败匹配步 clamp ≤0 | Table2; Table3 | 4B 56.27→59.55；去 support 低于 GRPO | 未说明 | 支持局部截断 |
| litscan:70458 | 工具 token 无直接 PG，只训终答 | Table1 | 3B chart 51.8（直答）/ 24.6（prompt 工具）→ 64.0；32B 低于纯直答 | 记录未覆盖 | 中性（无工具段信用仍可学会调用） |
| 2609.35084 | step-only（去掉 AT） | Tables1,4 | step-only 92.5 低于完整 95.7 | 3 seeds | **反对**只用局部 |
| 2610.31544 | twin-only（去掉 episode 优势） | Table3 | twin-only 41.7 低于混合 42.7 | 3 seeds | **反对**只用局部 |
| 2604.02869 | 校准使例行 read 奖励 .3→0 | Table7 | IRC 69.5% vs hybrid 56.5% | 200 sim | 中性：零信用不必有害，也不保证安全 |

**本地证据**（反对）：
- 四情形 − 零信用：+0.028 [+.004,+.051]（P15）。

## 成功条件 / 失败模式

- 置零能成功的条件：被置零的段有另一条可靠信号（SLCA 的工具段有金标准调用匹配分；TACO 的过程通道），且置零只发生在少数格内。
- 替换能成功的条件：局部信号来自强、对齐的 critic（LVRL 用 Claude 级 critic），或来自整包设计。
- 失败：
  - 只保留局部信号时，三个独立消融都更差（TARL、GraphHCA、Twin，见表）。
  - Δ=0 时 TACO 的 A1 在 T1 上保留，而 C∪T2 被置零；Δ<0 时 A1 只给 C∪T2，且 A1 未必为负（2606.30251 invariance 与签名 2 failure_boundary）。
  - SLCA 3B/8B 的 matched GRPO summary 分更高，但任务成功更低（2609.29050 §5 negative_results）。

## 审稿期望

SLCA、TACO、ICA、LVRL 均为 low_evidence。"推断"：
- 必须给"保留结果优势的加法臂"对照（SLCA transfer 建议："必须包括保留终答优势的加法臂"）；
- 报告被置零或被替换的 token 比例；
- 拆开路由收益与归一化收益（SLCA lesson）。

## 认知障碍

- 把过程奖励加到总分上，仍会把摘要噪声传给工具段；拆通道的同时改变了归一化与 token 支持，需要额外的 support 对照（2609.29050 why_non_obvious）。
- 细粒度评审与细粒度梯度路由是两件事；实际中逐轮奖励分配不如轨迹聚合稳定（2509.14480 why_non_obvious）。

## 工程经验

- 当拆分信用通道时，要独立核对有效样本集、归一化之后的权重、token 边界与缺段处理，再用 support 对照区分归一化带来的收益（2609.29050 lesson）。
- 环境 mask 必须区分真实工具返回与策略文本；不能用 JSON 标签范围代替整个工具段（2609.29050 pitfalls A.1）。
- 当工具成功验证只看能否执行时，正负过程奖励都可能诱导退化：惩罚失败 → 调用率为 0；正确且成功工具 bonus → verifier hack（litscan:70458 negative_results §4）。
- 当 dense 奖励看似合理、表现却下降时，先审最终的优势与匹配语义，再锁训练配置（2604.02869 lesson）。

