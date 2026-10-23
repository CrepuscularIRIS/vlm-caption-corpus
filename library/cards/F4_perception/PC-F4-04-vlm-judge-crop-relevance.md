---
id: PC-F4-04
name: 让外部 VLM 判官看裁图输出、判"含目标/相关"，给工具分
family: F4_perception
status: candidate_pattern
problems: {P43: 2, P44: 2, P16: 2, P52: 1}
members: [litscan:63126, litscan:63255, 2512.03438, 2602.08346, 2505.15879]
rs_patterns: [self_supervised_signal_engineering, heterogeneous_decomposition]
---
## 操作

把每次工具的返回（裁图、坐标统计）交给固定的外部 VLM 判官，判断其中是否含问题目标或是否相关，得到 $r_{tool}$，再与终答奖励加权：

$$R=\lambda_{acc}r_{acc}+\lambda_{tool}\tfrac1{|T|}\sum_t r_{tool,t},\qquad A=R-\text{mean}_{group}(R)$$

（litscan:63126 Eq5–6）。

AdaptVision 用 GPT4o 判 crop 相关性得到 $R_{crop}$（litscan:63255 Eq8–10）。Argos 按样本选择多种核验器，并以答案正确为门控（2512.03438 §5.1）。

## 信息

- **判官能看到**：问题、裁图或其描述、坐标统计。CodeV 的判官看不到 CoT 和代码（litscan:63126 §4.3）。
- **估计者**：冻结外部模型，如 Qwen2.5-VL-32B、GPT4o。
- **看不到**：
  - 策略是否读懂了这块图；
  - 同状态不裁时的结果；
  - 必要性。

## 成立条件

- 判官对"目标是否在图中"的判断可靠。2602.08346 显示现成 LVLM 作过程评估器有系统偏差：
  - 有正向偏置（p.6 Finding 1）；
  - 正确类 78.89 vs 错误类 38.81（Gemini，Table3）。
- 冷启动 SFT 已含直答与多步图操作（litscan:63126 §5.1 pitfalls）。
- 预算允许每次调用都请判官一次。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:63126 | 逐工具判官分取均值 + 终答，均值基线 | Eq5–6；§5.4 Table2 | reasoning/perception 54.2/69.7 vs accuracy-only 51.2/67.5；accuracy+consistency 50.4 < 51.2；Zero RL 时工具使用塌缩到纯文字 | 记录未覆盖 | 正 |
| litscan:63126 | （评测）GPT4o 判答对样本的裁图是否含目标 | §3；§5.3 | 正确答案中被判 faithful：DeepEyes 57%、PixelReasoner 43%；CodeV 相对约 1.3–2 倍 | 记录未覆盖 | 目标存在与答对相互分离 |
| litscan:63255 | GPT4o crop 相关性作为 $R_{crop}$ | Eq8–10；§5.3 | 见 PC-F4-03 | 记录未覆盖 | 组件 |
| 2512.03438 | 多工具核验、正确性门控聚合 | §5.1/Table1 | BLINK 56.0、MindCube-t 39.6、CV-Bench 78.2、CV-Bench3D 82.0；基座 54.4/34.9/77.0/77.9 | 非单因素消融 | 弱正 |

## 成功条件 / 失败模式

**成功条件**：判官准确，且奖励只作为终答奖的小权重附加项（$|\lambda_{tool}|<|\lambda_{acc}|$，litscan:63126 Eq5）。

**失败模式**

- **任一裁图含目标即可通过。** 多目标时只需含其中一个；这不能证明学生读懂或用到了这块图（litscan:63126 §3 failure_boundary）。
- **权重约束不足以保证排序。** $\lambda_{tool}<\lambda_{acc}$ 不能保证"错答+工具"低于"对答−工具"，还要看各分量取值范围（litscan:63126 pitfalls）。
- **一致性奖励反而降分。** accuracy+consistency 50.4，低于 accuracy-only 51.2（litscan:63126 Table2）。
- **判官本身失准。**
  - 有正向偏置；
  - 工具错误检出率低：LLaVA7B TE 0.20，InternVL78B TE 0.32（2602.08346 Table2）；
  - 图像步骤弱于文字步骤（2602.08346 p.7）。
- **不需要工具的分支没有定义。** 无工具时 $|T|=0$，公式未定义（litscan:63126 degenerate_cases）。

## 审稿期望

推断：

- 判官与人工的一致率，按正/错类分别报告（2602.08346 的做法）；
- 判官不看图（只看文字）的对照；
- 把 $r_{tool}$ 换成打乱值的占位臂；
- 判官调用成本。

## 认知障碍

可观察的工具输出比语言理由更容易核验（litscan:63126 why_non_obvious），所以"判官看裁图"显得客观。但判官的"可读"与学生的"读到并使用"是两件事。前人很少测判官对策略的代表性。

## 工程经验

- **用判官奖励工具时**：同时记录当前策略读入证据后的答案变化，并明确空工具分支、分量取值范围和梯度路由（litscan:63126 lesson）。
- **用现成 LVLM 打分前**：先在人工核验的图文步骤上，按正/错类和工具错误类分别测，并说明前缀与 GT 的可见性（2602.08346 lesson）。

