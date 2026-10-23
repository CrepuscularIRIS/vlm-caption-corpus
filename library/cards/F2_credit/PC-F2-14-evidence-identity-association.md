---
id: PC-F2-14
name: 按证据或工具参数的身份与组内成功的关联，给（包括失败轨迹中的）工具轮信用
family: F2_credit
status: candidate_pattern
problems: {P18: 3, P11: 2, P14: 2, P30: 1, P15: 1}
members: [2602.10863, 2606.05784, 2604.02869]
rs_patterns: [reframe_as_solvable_object, heterogeneous_decomposition, self_supervised_signal_engineering]
---

## 操作

给每次工具调用一个可跨轨迹比较的身份（检索到的 URL、图像切片、工具参数/框、工具类别），统计该身份在同题成功轨迹与失败轨迹中出现的差异，据此给工具轮信用：

- ICA：
  $$\Delta_e=P(\text{succ}\mid e\in E_i)-P(\text{succ}\mid e\notin E_i)$$
  每种工具只保留 Δ>0 的前 10%，凡取回过入选证据的工具轮记 $r_t=1$。工具轮与答案轮分通道 mean/std；**工具轮优势被替换**为证据通道的优势（2602.10863 Eqs8–14, Eq16）。
- TAPO：对失败轨迹中、与同题成功轨迹参数相似的工具步，转移正优势：
  $$F=\text{sim}\cdot\frac{n(C)}{G^+}\cdot\overline{A}_{C},\qquad A'_{jk}=\min(A_j+\beta F,0)$$
  只用于通过阈值的失败步（zoom IoU≥.7，文本 sim≥.8），失败步的信用仍 ≤0（2606.05784 Eqs3–4）。
- IRC：$\rho_c=\text{Corr}(\mathbf1[c\in\tau_i],o_i)$，$|\rho_c|>\delta$ 时 $r_c=\alpha\rho_c$，否则为 0，并反复按 rollout 统计校准（2604.02869 Alg1）。

## 信息

- 看得到：同题（或语料级）多条已完成轨迹的终局成功，以及每次调用返回证据或参数的身份。
- 看不到：同一前缀下的替代动作；因果必要性。ICA 的记录写明"no shared-prefix continuations, no fixed-state action alternatives, no do-intervention"（2602.10863 签名 1 information）。
- 估计者：旧策略 rollout 的经验关联统计，没有冻结读者。

## 成立条件

- 同题 rollout 中既有成功也有失败；证据身份可跨轨迹比较；出现与否有足够变化（2602.10863 conditions）。
- 参数等价近似于历史条件下的价值等价；但记录指出，参数相同并不排除"重复获取已知信息"（2606.05784 why_non_obvious、failure_boundary）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2602.10863 | 证据身份 Δ_e 排序二值化，工具轮优势替换 | Table2 | Qwen3-VL-8B-Thinking：ICA-Snapshot vs GSPO-Snapshot BC-100 25.0 vs 22.0，GAIA 69.9 vs 60.2，XDS 71.0 vs 68.0，Seal-0 25.2 vs 24.3（整包对比，非单部件） | 主训练 seed 未报告 | 成员 |
| 2606.05784 | 参数相似成功轨迹的优势转移给失败步，clamp ≤0 | Table2 p7; Table3 | 4B GRPO 平均 56.27→59.55（β=.25）；8B SAPO 62.48→65.21；β=.8 最佳 61.18，β=1 回落 59.71；去 support 低于 GRPO；额外 CPU 处理占训练时间 .06% | 评测 3 runs，训练 seed 未说明 | 成员 |
| 2604.02869 | 类别出现与结局相关性定奖励，反复校准 | Table7; Tables6–7 | MoE sparse 68%、dense 54%、hybrid 56.5%、IRC 69.5%；4B 高 LR 的 IRC 62.0 低于 base | 200 sim，非 4 训练 seed | 成员 |

## 成功条件 / 失败模式

- 成功：证据单元稳定可复现（URL、页面切片）；组内成败混合。
- 失败：
  - 全成功或全失败的组，全部工具优势为 0（2602.10863 failure_boundary）。
  - 关联可能反映混杂，或反映被打分样本本身的结局；没有 leave-one-out（同上）。
  - 每个样本都参与了自身的证据统计与基线（2602.10863 normalization）。
  - 已入选证据的重复取回仍有奖励资格，没有"只奖首次获取"（2602.10863 degenerate_cases，读完整记录）。
  - TAPO 在全错时没有参考；没有证明能降低调用，反而保留更多搜索（2606.05784 failure_boundary）。
  - IRC：routine read 判别力为 0 不代表读取不必要（2604.02869 degenerate_cases）。

## 审稿期望

ICA、TAPO、IRC 均为 reviewer_concern=low_evidence。"推断"：
- cross-fit 或 leave-one-out 排序；
- 打乱排序、随机证据的等预算对照（ICA transfer 建议）；
- 报告调用数的变化。

## 认知障碍

- 不估计相同前缀的动作值，而用低额外推理成本的跨轨迹关联替代逐步标签；弱的连续估计只用于排名，不直接用其幅值作奖励（2602.10863 why_non_obvious）。
- 正奖励不保证正优势；dense 奖励会让无判别力的例行 turn 也吸收梯度；零梯度不总是坏事（2604.02869 why_non_obvious）。

## 工程经验

- 当按完整轨迹中证据出现与成功的关联分配信用时，应先验证证据身份、组内出现/未出现的支撑与排名稳定性，再检查 turn-local mask（2602.10863 lesson）。
- 当同 batch 复用动作信用前，应验证历史条件可比，并分开报告匹配覆盖率、因果必要性与真实成本（2606.05784 lesson）。
- 同图输入会使反搜 support 近 1，比裁图更容易通过门（2606.05784 pitfalls AppB.3）。

