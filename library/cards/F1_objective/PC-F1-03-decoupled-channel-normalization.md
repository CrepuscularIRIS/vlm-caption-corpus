---
id: PC-F1-03
name: 多奖励通道各自归一化，把权重放在标准化之后（或放到 loss 层）
family: F1_objective
status: candidate_pattern
problems: {P01: 3, P04: 2, P06: 2, P42: 1}
members: [2601.05242, 2509.22047, 2604.08545, 2607.16244, "litscan:66297", "litscan:78074"]
rs_patterns: [heterogeneous_decomposition]
---
## 操作
不要先把 correctness、cost 等加成一个标量再除 std，而是对每个通道 $k$ 单独组内标准化，再在标准化之后加权：

$$A_k(i)=\frac{r_k(i)-\mathrm{mean}_g r_k}{\mathrm{std}_g r_k},\qquad S(i)=\sum_k w_kA_k(i)$$

（2601.05242 Eqs4,5,7）。可选的最后一步是批级标准化（Eq6）。

两种等价的权重放法：
- 两个通道各自算 PPO clipped loss，再以 $L=w_{acc}L_{acc}+w_{tool}L_{tool}$ 合并（2604.08545 Eq11；默认 $w_{tool}=.15$）；
- 在标准化后的 A 上乘一个结构权重 $A'=A(1+W)$（litscan:78074 Eqs6–9）。

## 信息
- 每条轨迹的多路标量奖励：正确性、格式、工具次数、执行成败、IG 等。
- 看不到各通道之间的真实价值权衡；等权或手设权重不等于真实偏好（2509.22047 failure_boundary）。
- 由谁估计：组内统计。

## 成立条件
- 权重必须放在 std 之后，才不被约掉。
- 最终若再做批级 std，所有 $w$ 共同乘一个正常数也会被抵消（2601.05242 invariance）。
- 效率通道只有在组内存在不同成本的样本时才非零。HDPO 还要求同题至少 2 个正确样本（2604.08545 §3.2.1 Eqs8–10）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2601.05242 | GDPO：逐通道组 std → 加权和 → 批 std | Eqs4–7；Table1 | BFCL 1.5B 平均准确率 32.81 vs GRPO 30.18，format 80.66 vs 76.33；去 std 的 GRPO format 为 0 | tool calling 5 runs；math/code 训练 seed 未明 | 支持 |
| 2509.22047 | MO-GRPO：$A=\sum_k(R_k-\bar R_k)/\sigma_k$ 等权 | Table2 Llama En–Ja | GPT-Eval 35.6%→68.8%，BLEURT .60→.66，readability .90→.69 | 记录未覆盖 | 支持（等权有代价） |
| 2607.16244 | CIGPO：中间 turn 的 IG 与终局 F1 分别 std，IG 权重 .1→.3 | Eq4–7；Table3 p7 | 1000 测试 F1 .518 vs GRPO 最好 .430；EM 在 step100 为 .242，step200 降到 .150 | 1 seed | 弱支持（λ 在 std 前还是后，原文不清） |
| litscan:66297 | CodeDance：序列通道组 std + turn 执行失败通道批 std，相加 | Eq1–2；Table3 | 准确率/平均轮数：outcome-only 66.8/1.42，RBAT 68.1/1.38；执行成功率 .99；去 turn 通道 67.5/1.38/.91 | 未报告 | 弱支持 |
| litscan:78074 | DR-MMSearchAgent SPAI：std 后乘 $(1+W_i)$ | Eqs1–9；Table3 p7 | FVQA 基础 57.7→+Bridge 59.7→+SPAI 63.4→+BGAS 64.9 | 主表 3 次推理平均；训练 seed 未报告 | 支持"std 后权重不被抵消"；$A=0$ 时仍为 0 |

## 成功条件 / 失败模式
**成功条件**
- 通道之间尺度差异大，先求和会让某一通道主导（2601.05242 why_non_obvious）。

**失败模式**
- HDPO 的权重不单调。$w=.10$ 与 $.20$ 时 V* 为 88.0/87.4，都低于 GRPO 的 88.7；$.20$ 在全部五项上都低于 $.15$（2604.08545 Table3）。
- 通道独立归一化不使梯度正交，共享参数仍会干扰（2604.08545 OBJ.invariance）。
- 互补通道在等权下可以相加为 0。读者代数：$r_1=(1,1,0)$、$r_2=(0,0,1)$ 时 $A_1+A_2=0$（2601.05242 degenerate_cases）。
- 条件长度奖励提高了 AIME，但超预算率从 0.2% 升到 12.3%（2601.05242 Table4）。
- CIGPO 的 EM 随 F1 上升反而下降，格式违规 4.4→12.3%（2607.16244 Tables4–5）。
- 若 IG 权重在 std 之前，curriculum 会被抵消（2607.16244 invariance）。
- SPAI 的乘性权重不能为全同奖励组造出梯度（litscan:78074 degenerate_cases）。

## 审稿期望
- 记录的 reviewer_concern 都是 low_evidence。
- 推断的要求：
  - 权重扫描，不能只报一个最佳 $w$（HDPO 的 Table3 已显示不单调）；
  - 与"标量化 + mean-only"的同预算对照（2604.08545 Table3 失败边界写明缺这一对照）；
  - 报告 $|Q|$ 和 Q 内的 T 方差。

## 认知障碍
- "先 sum 再 normalize"和"先 normalize 再 sum"在多数实现里只是一行顺序差，容易被当成等价（2601.05242 lesson："当多奖励标准化前加权时，权重可能消失"）。
- HDPO 的洞察是"改变效率比较的参考集合"，即只在成功子集内比较，而不是加一个成本项（2604.08545 why_non_obvious）。

## 工程经验
- 当效率只在成功集合中标准化时，应同时记录四项：$|Q|$、Q 内 T 方差、零调用成功样本数、各通道 token 质量（2604.08545 lesson）。
- 当多奖励先加权后标准化时，权重会消失。应当记录每个通道的尺度与活跃比例，再把权重放到标准化之后（2601.05242 lesson）。
- 当辅助信号权重与 std 的先后顺序不明时，curriculum 可能整体无效。应当打印标准化前后的 λ（2607.16244 lesson）。

