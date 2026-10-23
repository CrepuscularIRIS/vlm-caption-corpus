---
id: PC-F1-06
name: 用自然 rollout 组里"直答是否已成功"的计数来决定工具代价的方向
family: F1_objective
status: candidate_pattern
problems: {P02: 3, P29: 2, P01: 2, P06: 2}
members: ["litscan:arxiv:2505.15436", 2507.13348]
rs_patterns: [condition_intervention_on_boundary, heterogeneous_decomposition]
---
## 操作
不额外采样，只看本组自然 rollout 里直答与工具两类的成功情况，然后条件化地给工具或直答加罚。

**AGAR**（litscan:arxiv:2505.15436 Eqs4/6–7）

- 门控与奖励：$g=\mathbf 1[\exists i:c_id_i=1]$，$r_i=c_i[d_i+z_i(1-.2g)]+(1-c_i)(.1f_i)$。
- 含义：组里出现过正确直答，正确的 zoom 轨迹才从 1 打折到 .8。

**VisionThink**（2507.13348 Sec.3.4，Eq.5 前）

- 比例：$r=C_{direct}/(C_{direct}+C_{high})$。
- 方向切换：$r<0.2$ 时罚直答 0.1，否则罚请求原图 0.1。
- 两个方向都可能受罚。

## 信息
- 本组自然样本中，各动作的正确次数。
- 看不到：未采到的动作的表现，以及同状态的反事实。
- 由谁估计：当前策略的自然样本。VisionThink 的计数是在线还是离线、逐题还是批级，原文未明确（2507.13348 signature information）。

## 成立条件
- 两种动作在自然采样中都有非零概率。2507.13348 写明"两种动作初始有采样支持"，并借用 Qwen 官方 agent prompt 获得这一支撑（Appendix C.3）。
- $C_{direct}+C_{high}=0$ 时 Eq.5 无定义，原文未给分支（2507.13348 conditions）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:arxiv:2505.15436 | AGAR：组内有正确直答才折扣 zoom；SFT 用 2201 条 zoom + 2294 条 direct | Eqs4/6–7；§5/Table7/10 | V* 90.1，平均 crop .5（DeepEyes 2.0）；只做 SFT 89.5；普通 RL 84.8 | 未报告 | 支持；增益主要来自平衡 SFT，AGAR 相对冷启动仅 +.6 |
| 2507.13348 | VisionThink：按正确份额 θ=.2 双向切换惩罚 | Sec.3.4；Fig.3/7/8；Table8 | 无罚 → 全调用；一律罚调用 → 全直答；θ=.2 保持混合。RL 请求比例：ChartQA 79.1%、DocVQA 6.5%、RealWorldQA 29.9% | 未报告 | 支持（双向）；θ 过高仍塌到全调用 |

## 成功条件 / 失败模式
**成功条件**
- 初始策略同时采到两种动作（2507.13348 Fig.7：官方 prompt 调用率约 0.3–0.6）。
- 平衡的 SFT 已种下两种模式（litscan:arxiv:2505.15436 SFT 配方）。

**失败模式**
- 自制 prompt 的调用率迅速接近 0，最终全直答，原因是"absence of gradients"（2507.13348 pitfalls 引文）。
- 阈值过高时塌到全调用（2507.13348 Appendix C.4）。
- 一律罚调用或完全不罚都会塌缩（2507.13348 Fig.3 caption）。
- AGAR 不强制采样，所以 $p$(direct)≈0 时退化为普通 RL（litscan:arxiv:2505.15436 failure_boundary）。
- 普通 RL 比只做 SFT 低（84.8 vs 89.5，Table10）。在该设定下 RL 本身会伤害准确率。
- 2507.13348 的 r 是正确次数份额，受动作曝光量影响，不是成功概率（failure_boundary）。

## 审稿期望
**2507.13348 历史评审（记录 reviewer_concern）**
- Eq.5 的 C 是否在线计算，训练数据从哪里来（R3、R6）。
- 要求与简单规则路由对照（R4、R7）。
- ChartQA 时延与泛化（R5、R8）。

**推断**
- 必须报告 $p$(直答) 的轨迹曲线，以及门触发率随训练的变化。

## 认知障碍
- 只惩罚调用会让偶然猜中的直答被强化，从而塌到全直答；不惩罚则塌到全调用。代价方向必须依题而定（2507.13348 why_non_obvious）。

## 工程经验
- 当用组内成功直答触发效率偏好时，应持续监测直答支撑，以及全对组 std 对折扣的抵消。不能只看平均调用下降（litscan:arxiv:2505.15436 lesson）。
- 当自定义工具动作在自然 rollout 中几乎不出现时，结果 RL 建立不起动作对照。应先测协议支撑，并区分"数据需求均衡"与"每题动作采样均衡"（2507.13348 lesson）。

