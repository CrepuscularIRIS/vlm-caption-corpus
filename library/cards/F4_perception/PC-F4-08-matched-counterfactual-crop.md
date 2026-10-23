---
id: PC-F4-08
name: 在当前策略下比较"真实区域"与"同形/加噪反事实区域"的答案读数差，测内容的因果作用
family: F4_perception
status: candidate_pattern
problems: {P43: 3, P11: 2, P41: 2, P16: 2, P02: 1}
members: [2608.06270, litscan:76688]
rs_patterns: [controlled_diagnostic_design, heterogeneous_decomposition]
---
## 操作

保持前缀和调用绑定不变，只替换工具返回的像素内容。分别读出当前策略在真实区域和反事实区域下的答案读数，取差值。

- 固定前缀、调用 $T_i$ 和 literal `<answer>`。
- 在选项受限的 softmax 上取 $M=p(o^*)-\max_{o\ne o^*}p(o)$。
- 反事实为 3 个从原图其他位置随机取的同形裁块，对它们的 M 取均值。

**CofactGVR（litscan:76688 Eq2–8）**
- 真实框和随机加噪框各采样答案，得到组均正确率 $\mu$ 与 $\mu_c$。
- $d=[\mu-\mu_c]_+$，$b=\mathbb1[d>\gamma]\operatorname{clip}(d,b_{min},b_{max})$。
- 将 b 加到正确或 top-k 的真实 rollout 上。

## 信息

- **CofactGVR** 用答案正确率，不用 GT 框（litscan:76688 information）。
- **干预性质**：替换的是内容，属于因果干预；但只测局部读数，不是动作价值。

## 成立条件

- 白盒 next-token logits 可用，候选标签能映射到选项（2608.06270 conditions）。
- 真实与反事实之间只变观测内容，前缀与调用绑定一致（同上）。
- 随机裁块不由语义标注保证与目标无关；R=3 时平均的是概率差，不是 logits（同上）。
- CofactGVR 在两种条件下都保留原图（litscan:76688 conditions）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2608.06270 | 策略级干预：工具 / 直答 / 随机裁块 / 强制作答 | App B.4；Tables1,2,9–11 | V* Qwen3-VL-8B 工具/直答 91.1/84.2（+6.9pp）；随机裁块 30.4；强制作答 73.0；DeepEyes 83.3→83.8 | 记录未覆盖 | 工具净效应有限 |
| 2608.06270 | 按 Calibrated / CWL / LWP 分组分解 ATE | Sec4.3；Alg1/Table4 p8 | V* Qwen8 Calibrated 组占 20.9%，贡献 +7.6pp，总 ATE +6.9；HR4K Calibrated 10.1% 贡献 +4.4 | 后验诊断 | 少数调用承担全部收益 |
| litscan:76688 | 组级真/反事实正确率差作 bonus，加 Q-PAS 重采样 | Table4/§4.3；Table5 | 去反事实：MME 2428.5→2349.1，RWQA 66.9→63.8；bonus 给所有样本时 RWQA 61.7；反事实选择：无证据 2306、合理候选 2386.4、随机加噪 2428.5 | 记录未覆盖 | 正（训练） |

## 成功条件 / 失败模式

**成功条件**
- 反事实与真实区域同形、同前缀，只变内容。
- 门控或奖励只作用于有内容效应的调用；bonus 带边界并加门控。
  - 不设 bonus 边界时 MME 2341.6（litscan:76688 Table4）。

**失败模式**
- **CofactGVR 的对照不严格**：反事实不同形，是加噪框；是组级效应而非逐次；不是裁图相对直答的价值（litscan:76688 failure_boundary）。
- **重采样的 bias**：按 |A| 重采样时没有 IS 修正（litscan:76688 signal_routing）。

## 审稿期望

推断：
- 匹配框形且不加噪时收益是否消失（litscan:76688 falsifier）；
- 预填读数与自然解码是否一致（P17）；
- 饱和分层报告。


## 认知障碍

"用了工具"不等于"用了像素"。前人多用"有工具 vs 无工具"的总体效应来评价，这个对照同时改变了提示、可用动作和观测（2608.06270 failure_boundary）。同形换位置的反事实把内容效应单独分离出来，但只是局部读数，迟迟没有被接进训练。CofactGVR 接进了训练，用的却是组级加噪对照。

## 工程经验

  - 平均的是概率差，不是 logits 后再 softmax（2608.06270 conditions）；
- **反事实 bonus 能改善答案时**：要分别审计三件事：奖励的输入、实际被更新的 token、采样分布。否则无法推断裁图动作的信用（litscan:76688 lesson）。
- **正文与附录不一致时**：奖励归一化输入与优化符号在正文和附录间不一致，不能按论文名假定是标准 GRPO（litscan:76688 pitfalls：Eq9/12/14）。

