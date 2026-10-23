---
id: PC-F4-12
name: 同一策略去掉原上下文后只读自己的中间分析再答一次，以此作为充分性验证奖励
family: F4_perception
status: case
problems: {P40: 2, P41: 2, P11: 1}
members: [litscan:78316]
rs_patterns: [self_supervised_signal_engineering, controlled_diagnostic_design]
---
## 操作

原轨迹在完整上下文 C 下生成分析 $T_a$ 和答案。然后拿掉 C，只把 $T_a$ 与问题 Q 交给**同一个** $\pi_\theta$ 再答一次，得到 $A_v$。只有当原答案和验证答案都正确时，才给额外奖励（litscan:78316 Eq5–7）：

$$r=.5r_{fmt}+r_{acc}+r_c\,r_{acc},\qquad r_c=\mathbb1[A_v=y^*],\ A_v\sim\pi_\theta(T_a,Q)$$

此外，对每题的 N 个语义等价 context 变体，分别在变体内和全局做 z-score，再相加（Eq8）。

## 信息

- 验证时看不到原 context C，只看自己写的 $T_a$。
- 用到 GT 答案。
- 无法防止 $T_a$ 泄露答案（failure_boundary）。

## 成立条件

- 原答案正确时才计验证分，原答案错误的轨迹拿不到额外分（signature failure_boundary）。
- 语义等价变体真的等价（同上，第二个 signature）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:78316 | 去 context 自读验证 × 正确门 | Table4 pp7–8 | 只加 context 奖励：34.59，vanilla GRPO：33.20；完整 CAR：38.14，base：16.05；HAE 净增 1.40pp（另含 augmentation 2.15pp） | 记录未覆盖 | 正 |

## 成功条件 / 失败模式

- **成功条件**：中间分析把原 context 中的关键信息写成了可读文本，且没有直接写出答案。
- **失败模式**：
  - **泄题或靠先验**：验证可能读到 $T_a$ 中的答案或先验（litscan:78316 failure_boundary）。
  - **组内无方差**：G=1 或组内全同时 std=0，未说明 ε（litscan:78316 degenerate_cases）。
  - **任务回退**：SFT 后 VLT 25.40→23.01，STL 35→15，不是所有任务都保住（litscan:78316 negative_results）。

## 审稿期望

推断：
- 泄题屏蔽与打乱 $T_a$ 的对照；
- 冻结读者的对照；
- 把 HAE 与数据扩增的贡献分开（作者已部分做到）。

## 认知障碍

作者同时区分两件事：分析中的信息是否可用，以及对表面 context 扰动是否鲁棒（litscan:78316 why_non_obvious）。但"自己读得懂自己写的东西"是自洽，不是事实。前人常把这类自验证当作独立真值。

## 工程经验

- **奖励中间文本的可解性时**：保留原答案正确这一门槛，并检测泄题；优势消融要把数据扩增与归一化的贡献分开（litscan:78316 lesson）。
- **组样本筛选**：训练时剔除了过易和过难的样本，阈值未知，因此不能把收益全部归给奖励（litscan:78316 pitfalls）。

