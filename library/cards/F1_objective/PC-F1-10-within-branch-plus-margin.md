---
id: PC-F1-10
name: 按动作分支（或工具次数层）在层内标准化，再显式加回跨分支的均值差作为路由优势
family: F1_objective
status: candidate_pattern
problems: {P02: 3, P12: 2, P01: 2, P29: 1}
members: [2609.00967, 2510.06214, "litscan:57190"]
rs_patterns: [heterogeneous_decomposition]
---
## 操作
把同一题的 rollout 按结构分层：CoBRA 按 internal/external 分支，Stratified GRPO 按搜索次数层。

1. 层内标准化：$A^{within}_i=(R_i-\bar R_{T_i})/(\sigma_{R,T_i}+\eta)$。
2. 跨层信号显式加回，两篇的做法不同：
   - CoBRA：$A^{MARS}_i=A^{within}_i+\beta\,\mathrm{sign}(T_i)\,\Delta_B(q)/(\sigma_B+\eta)$，其中 $\Delta_B=\bar R_{ext}-\bar R_{int}$。$\sigma_B$ 是 batch 内 margin 的 std，**不做 batch 中心化**（2609.00967 Eq4–6/11–12）。
   - Stratified GRPO：$A_i=\alpha A^{SAN}_i+(1-\alpha)A^{GN}_i$，即与全组归一化按 α 混合（2510.06214 Eqs2,4,7）。

## 信息
- 同题两层的终局回报。CoBRA 用 correctness − λ·cost。
- 看不到：同前缀、只改动作的反事实（2609.00967 relevance P67：同题对照不保证可识别）。
- 由谁估计：策略自身的样本。CoBRA 的分支由强制 prefix 保证。

## 成立条件
- 两层都有样本，缺一层则 Eq4 无定义（2609.00967 degenerate_cases）。
- 层内常数成本会被层内中心化完全抵消。固定的首调用费只能通过跨层项起作用（2609.00967 OBJ.invariance；2510.06214 invariance："层内常数成本 −λk 完全抵消"）。
- α=1 且按精确次数分层时，没有跨次数的成本信号（2510.06214 degenerate_cases）。
- CoBRA 的 BM 不做 batch 中心化。若所有题的 $\Delta_B$ 同号，BM 会给全体样本同方向的推力（2609.00967 OBJ.invariance："所有题同方向差仍有信号"）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2609.00967 | PBN 分支内 z-score + 跨分支 margin（β=1，λ=.10） | Eq4–6；Table4/3/2 p8 | 完整 jEM .5418/util .4250；去 BM .4817/.4179；只做 RS .2937/.2809；BM 让调用 .638→1.168；internal-favored 子集 jEM .5816，低于 Mwarm .6768 | 同一 checkpoint 3 次评测；训练 seed 未报告 | 支持路由效用；未减少调用 |
| 2510.06214 | SAN 按搜索次数层标准化，与 GN 混合 | Eqs2–7；Theorem3；Table1–2 | Base 平均 33.3→41.6，Instruct 29.2→40.5；只做 SAN 36.7/39.9；搜索增至约 2.5 次 | 记录未覆盖 | 支持准确率；明确不减搜索 |
| litscan:57190 | FULL/REGION 分别奖励；是否按 decision 中心化存在文本冲突 | Eq8–9 | 见 PC-F1-09 | 未报告 | 边界：按分支中心化会抹去 FULL 信号 |

## 成功条件 / 失败模式
**成功条件**
- 分支内有质量差异可学，同时分支之间确有平均收益差。
- β 放在两个归一化之后，不被自动抵消（2609.00967 invariance）。

**失败模式**
- BM 提高了准确率与效用，但调用数增加：.638→1.168（2609.00967 Table4）；ID 集调用 1.355，高于 Mwarm 的 .820（Table2）。
- 在直答优先的子集上，jEM 低于 warm 模型，直答能力没有全面保住（2609.00967 Table3）。
- 全错时，external 的成本会让 BM 推向 internal（2609.00967 degenerate_cases）。
- $\sigma_B≈0$ 时被 η 主导，信号被放大。
- SAN 移除了 $\sum\mu_k\nabla p_k$ 项，不保持原期望奖励目标；SAN-only 在 NQ 上 45.2→43.7（2510.06214 Theorem3 与 negative_results）。

## 审稿期望
- 记录为 low_evidence。
- 推断的要求：
  - BM 是否只是一个全局偏置，需要与"同幅度常数偏置"对照，同 P24；
  - 每层有效样本数；
  - 直答子集的非劣。

## 认知障碍
- 单一组归一化把"分支平均收益"和"分支内轨迹质量"混在一起；只强制支撑仍会塌到无工具（2609.00967 why_non_obvious）。
- 层内比较能保护低平均回报策略的探索，但会删掉"选哪一层"的收益信号（2510.06214 why_non_obvious）。

## 工程经验
- 当用分支差训练工具路由时，应把离线专家标签与在线 actor 信号分开记录。保留两支的采样支撑，再检查归一化是否删掉了分支常数成本。平均效用变好时，也要检查直答子集是否受损（2609.00967 lesson）。
- 当用工具次数分层时，应先看每层有效样本数和跨层的策略变化，再调混合系数，不能只看 advantage 方差（2510.06214 lesson）。

